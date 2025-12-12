import time
import random
import logging
from typing import Dict, Any

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction

from payouts.models import Payout

logger = logging.getLogger(__name__)


def process_payout_logic(payout_id: str) -> Dict[str, Any]:
    """Логика обработки заявки на выплату."""
    try:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)

            if payout.status != Payout.Status.PENDING:
                logger.warning(
                    f"Задача process_payout_task: заявка {payout_id} не в статусе PENDING, текущий статус: {payout.status}"
                )
                return {"status": "skipped", "payout_id": payout_id}

            payout.status = Payout.Status.PROCESSING
            payout.save(update_fields=["status"])

        logger.info(f"Начата обработка заявки {payout_id}")

        # Имитация обработки
        time.sleep(random.uniform(2, 5))

        # Проверка данных
        if not validate_payout(payout):
            payout.status = Payout.Status.FAILED
            payout.error_message = "Проверка данных не пройдена"
            payout.save(update_fields=["status", "error_message"])
            logger.warning(f"Заявка {payout_id} не прошла валидацию")
            return {"status": "failed", "payout_id": payout_id}

        # Имитация банковской операции (10% ошибок)
        if random.random() < 0.1:
            raise Exception("Ошибка при выполнении банковской операции")

        # Успешное завершение
        payout.status = Payout.Status.COMPLETED
        payout.save(update_fields=["status"])
        logger.info(f"Заявка {payout_id} успешно обработана")

        return {"status": "completed", "payout_id": payout_id}

    except Payout.DoesNotExist:
        logger.error(f"Задача process_payout_task: заявка с ID {payout_id} не найдена")
        return {"status": "error", "error": "Заявка не найдена"}
    except Exception as exc:
        logger.exception(f"Ошибка при обработке заявки {payout_id}: {exc}")
        raise


@shared_task(bind=True, max_retries=3)
def process_payout_task(self, payout_id):
    """Celery задача-обертка для process_payout_logic."""
    try:
        return process_payout_logic(payout_id)
    except Exception as exc:
        logger.exception(f"Ошибка при обработке заявки {payout_id}: {exc}")
        try:
            self.retry(exc=exc, countdown=60)
        except MaxRetriesExceededError:
            try:
                p = Payout.objects.get(id=payout_id)
                p.status = Payout.Status.FAILED
                p.error_message = str(exc)
                p.save(update_fields=["status", "error_message"])
            except Exception as save_exc:
                logger.error(f"Не удалось пометить заявку как FAILED: {save_exc}")
            return {"status": "failed_final", "payout_id": payout_id, "error": str(exc)}


def validate_payout(payout: Payout) -> bool:
    """Валидация заявки на выплату."""
    try:
        if payout.amount <= 0:
            return False

        if not payout.currency or not payout.recipient_details:
            return False

        details = payout.recipient_details

        required_fields = [
            details.full_name,
            details.bank_name,
            details.account_number,
            details.inn,
            details.bik,
        ]

        return all(required_fields)

    except Exception as e:
        logger.warning(f"Ошибка при валидации заявки {payout.id}: {e}")
        return False
