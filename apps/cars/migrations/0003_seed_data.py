from django.db import migrations


def seed_data(apps, schema_editor):
    Car = apps.get_model('cars', 'Car')
    Fix = apps.get_model('cars', 'Fix')

    cars_data = [
        {'marka': 'Toyota',  'model': 'Camry',  'gos_munber': 'А123ВС77', 'year': 2019, 'note': 'Служебный автомобиль директора'},
        {'marka': 'BMW',     'model': 'X5',     'gos_munber': 'М456КТ77', 'year': 2021, 'note': ''},
        {'marka': 'Lada',    'model': 'Vesta',  'gos_munber': 'О789НЕ52', 'year': 2020, 'note': 'Доставка'},
        {'marka': 'Hyundai', 'model': 'Tucson', 'gos_munber': 'Р321АМ78', 'year': 2018, 'note': ''},
        {'marka': 'Kia',     'model': 'Rio',    'gos_munber': 'С654УХ99', 'year': 2022, 'note': 'Новый'},
    ]
    cars = [Car.objects.create(**data) for data in cars_data]

    repairs_data = [
        {'car': cars[0], 'repair_type': 'Масло',        'date': '2025-12-10', 'next_date': '2026-03-10', 'description': 'Замена масла 5W-40 полная'},
        {'car': cars[0], 'repair_type': 'Ходовая',      'date': '2025-11-05', 'next_date': '2026-05-05', 'description': 'Замена амортизаторов передних'},
        {'car': cars[1], 'repair_type': 'ТО (плановое)','date': '2025-10-15', 'next_date': '2026-04-15', 'description': 'Плановое ТО 60 000 км'},
        {'car': cars[2], 'repair_type': 'Тормоза',      'date': '2026-01-20', 'next_date': '2026-07-20', 'description': 'Замена тормозных колодок'},
        {'car': cars[3], 'repair_type': 'Двигатель',    'date': '2025-09-30', 'next_date': '2026-03-15', 'description': 'Чистка форсунок, диагностика'},
        {'car': cars[4], 'repair_type': 'Масло',        'date': '2026-02-01', 'next_date': '2026-08-01', 'description': 'Первая замена масла'},
        {'car': cars[1], 'repair_type': 'Шины',         'date': '2025-11-01', 'next_date': '2026-05-01', 'description': 'Смена на зимнюю резину'},
        {'car': cars[3], 'repair_type': 'Электрика',    'date': '2025-08-10', 'next_date': '2026-02-10', 'description': 'Замена аккумулятора'},
    ]
    for data in repairs_data:
        Fix.objects.create(**data)


def unseed_data(apps, schema_editor):
    Car = apps.get_model('cars', 'Car')
    Car.objects.filter(gos_munber__in=[
        'А123ВС77', 'М456КТ77', 'О789НЕ52', 'Р321АМ78', 'С654УХ99'
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_update_car_fix'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
