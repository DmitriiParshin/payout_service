from django.db import migrations

RECIPIENTS = [
    {
        'full_name': 'ООО "ТехноСфера"',
        'bank_name': 'Сбербанк',
        'account_number': '40817810900000000001',
        'inn': '7701000001',
        'kpp': '770101001',
        'bik': '044525225',
        'corr_account': '30101810400000000225'
    },
    {
        'full_name': 'ИП Иванов И.П.',
        'bank_name': 'Тинькофф Банк',
        'account_number': '40817810000000000002',
        'inn': '7702000002',
        'kpp': '770201002',
        'bik': '044525974',
        'corr_account': '30101810100000000974'
    },
    {
        'full_name': 'АО "ГлобалТрейд"',
        'bank_name': 'ВТБ',
        'account_number': '40817810500000000003',
        'inn': '7703000003',
        'kpp': '770301003',
        'bik': '044525187',
        'corr_account': '30101810000000000187'
    },
    {
        'full_name': 'ООО "МедиаЛайн"',
        'bank_name': 'Альфа-Банк',
        'account_number': '40817810600000000004',
        'inn': '7704000004',
        'kpp': '770401004',
        'bik': '044525593',
        'corr_account': '30101810400000000593'
    },
    {
        'full_name': 'ИП Сидорова А.В.',
        'bank_name': 'Росбанк',
        'account_number': '40817810700000000005',
        'inn': '7705000005',
        'kpp': '770501005',
        'bik': '044526123',
        'corr_account': '30101810500000000123'
    }
]


def add_recipient_details(apps, schema_editor):
    RecipientDetails = apps.get_model('payouts', 'RecipientDetails')
    for data in RECIPIENTS:
        RecipientDetails.objects.get_or_create(**data)


def remove_recipient_details(apps, schema_editor):
    RecipientDetails = apps.get_model('payouts', 'RecipientDetails')
    RecipientDetails.objects.filter(inn__in=[r['inn'] for r in RECIPIENTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('payouts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_recipient_details, remove_recipient_details),
    ]
