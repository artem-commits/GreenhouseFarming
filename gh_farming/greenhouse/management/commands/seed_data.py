import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from greenhouse.models import (
    VegetableType, Greenhouse, WorkType, ScheduleTemplate,
    Planting, WorkSchedule, ResourceUsage, Harvest
)


class Command(BaseCommand):
    help = 'Populates database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Harvest.objects.all().delete()
            ResourceUsage.objects.all().delete()
            WorkSchedule.objects.all().delete()
            Planting.objects.all().delete()
            ScheduleTemplate.objects.all().delete()
            Greenhouse.objects.all().delete()
            WorkType.objects.all().delete()
            VegetableType.objects.all().delete()

        self.stdout.write('Seeding database...')
        self.create_vegetable_types()
        self.create_work_types()
        self.create_schedule_templates()
        self.create_greenhouses()
        self.create_plantings()
        self.create_work_schedules()
        self.create_resource_usage()
        self.create_harvests()

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_vegetable_types(self):
        vegetables = [
            {'name': 'Томаты', 'description': 'Помидоры черри и обычные'},
            {'name': 'Огурцы', 'description': 'Гибридные сорта для теплиц'},
            {'name': 'Перец', 'description': 'Сладкий болгарский перец'},
            {'name': 'Салат', 'description': 'Листовые салаты'},
            {'name': 'Зелень', 'description': 'Петрушка, укроп, базилик'},
            {'name': 'Клубника', 'description': 'Ремонтантная клубника'},
            {'name': 'Баклажаны', 'description': 'Синенькие'},
            {'name': 'Редис', 'description': 'Ранние сорта'},
        ]

        for veg in vegetables:
            VegetableType.objects.get_or_create(
                name=veg['name'],
                defaults={'description': veg['description']}
            )
        self.stdout.write(f'Created {len(vegetables)} vegetable types')

    def create_work_types(self):
        work_types = [
            {'name': 'Подготовка почвы', 'description': 'Вспашка, удобрение'},
            {'name': 'Посев семян', 'description': 'Посадка семян'},
            {'name': 'Полив', 'description': 'Капельный полив'},
            {'name': 'Подкормка', 'description': 'Внесение удобрений'},
            {'name': 'Прополка', 'description': 'Удаление сорняков'},
            {'name': 'Обработка от вредителей', 'description': 'Биологическая защита'},
            {'name': 'Обрезка', 'description': 'Формирование куста'},
            {'name': 'Сбор урожая', 'description': 'Ручной сбор'},
        ]

        for work in work_types:
            WorkType.objects.get_or_create(
                name=work['name'],
                defaults={'description': work['description']}
            )
        self.stdout.write(f'Created {len(work_types)} work types')

    def create_schedule_templates(self):
        vegetable_types = VegetableType.objects.all()
        work_types = WorkType.objects.all()

        templates = []

        for vegetable in vegetable_types:
            # Different schedules for different vegetables
            if vegetable.name == 'Томаты':
                schedule = [
                    (0, 'Подготовка почвы'),
                    (1, 'Посев семян'),
                    (7, 'Полив'),
                    (14, 'Подкормка'),
                    (21, 'Полив'),
                    (28, 'Обработка от вредителей'),
                    (35, 'Обрезка'),
                    (42, 'Подкормка'),
                    (49, 'Полив'),
                    (56, 'Обработка от вредителей'),
                    (63, 'Обрезка'),
                    (70, 'Сбор урожая'),
                ]
            elif vegetable.name == 'Огурцы':
                schedule = [
                    (0, 'Подготовка почвы'),
                    (1, 'Посев семян'),
                    (5, 'Полив'),
                    (10, 'Подкормка'),
                    (15, 'Полив'),
                    (20, 'Обработка от вредителей'),
                    (25, 'Подкормка'),
                    (30, 'Полив'),
                    (35, 'Сбор урожая'),
                ]
            else:
                schedule = [
                    (0, 'Подготовка почвы'),
                    (1, 'Посев семян'),
                    (10, 'Полив'),
                    (20, 'Подкормка'),
                    (30, 'Полив'),
                    (40, 'Сбор урожая'),
                ]

            for days, work_name in schedule:
                work_type = WorkType.objects.get(name=work_name)
                ScheduleTemplate.objects.get_or_create(
                    vegetable_type=vegetable,
                    work_type=work_type,
                    days_after_planting=days,
                    defaults={'duration_days': random.randint(1, 3)}
                )

        self.stdout.write(f'Created schedule templates')

    def create_greenhouses(self):
        vegetable_types = VegetableType.objects.all()

        for i in range(1, 21):  # Create 20 greenhouses
            greenhouse_number = f"GH-{i:03d}"
            vegetable = random.choice(vegetable_types)
            area = random.uniform(50, 200)

            Greenhouse.objects.get_or_create(
                number=greenhouse_number,
                defaults={
                    'vegetable_type': vegetable,
                    'area': round(area, 2),
                    'is_active': random.choice([True, True, True, False])  # 75% active
                }
            )
        self.stdout.write('Created 20 greenhouses')

    def create_plantings(self):
        greenhouses = Greenhouse.objects.filter(is_active=True)
        vegetable_types = VegetableType.objects.all()

        today = timezone.now().date()

        for greenhouse in greenhouses:
            # Create 1-3 plantings per greenhouse
            for _ in range(random.randint(1, 3)):
                planting_date = today - timedelta(days=random.randint(0, 120))
                vegetable_type = random.choice(vegetable_types)

                # Calculate harvest date based on vegetable type
                if vegetable_type.name == 'Томаты':
                    days_to_harvest = 70
                elif vegetable_type.name == 'Огурцы':
                    days_to_harvest = 35
                elif vegetable_type.name == 'Редис':
                    days_to_harvest = 25
                else:
                    days_to_harvest = random.randint(40, 60)

                planned_harvest_date = planting_date + timedelta(days=days_to_harvest)

                # Determine status
                if planned_harvest_date < today:
                    status = 'harvested'
                    actual_harvest_date = planned_harvest_date
                elif planting_date < today:
                    status = random.choice(['planted', 'growing'])
                    actual_harvest_date = None
                else:
                    status = 'planned'
                    actual_harvest_date = None

                Planting.objects.create(
                    greenhouse=greenhouse,
                    vegetable_type=vegetable_type,
                    planting_date=planting_date,
                    planned_harvest_date=planned_harvest_date,
                    actual_harvest_date=actual_harvest_date,
                    status=status
                )

        self.stdout.write(f'Created plantings for active greenhouses')

    def create_work_schedules(self):
        plantings = Planting.objects.all()

        for planting in plantings:
            # Get schedule templates for this vegetable type
            templates = ScheduleTemplate.objects.filter(
                vegetable_type=planting.vegetable_type
            )

            for template in templates:
                planned_date = planting.planting_date + timedelta(days=template.days_after_planting)

                # Determine status
                if planned_date < timezone.now().date():
                    if random.choice([True, False]):  # 50% chance of completion
                        status = 'completed'
                        actual_date = planned_date + timedelta(days=random.randint(0, 2))
                    else:
                        status = 'in_progress'
                        actual_date = None
                else:
                    status = 'planned'
                    actual_date = None

                WorkSchedule.objects.create(
                    planting=planting,
                    work_type=template.work_type,
                    planned_date=planned_date,
                    actual_date=actual_date,
                    status=status
                )

        self.stdout.write(f'Created work schedules')

    def create_resource_usage(self):
        work_schedules = WorkSchedule.objects.filter(status='completed')

        for work in work_schedules:
            # Different resources for different work types
            if work.work_type.name == 'Полив':
                water = random.uniform(100, 500)
                fertilizer = random.uniform(0, 5)
                labor = random.uniform(1, 3)
                notes = f"Полив выполнен. Температура воды: {random.randint(18, 25)}°C"
            elif work.work_type.name == 'Подкормка':
                water = random.uniform(50, 200)
                fertilizer = random.uniform(5, 20)
                labor = random.uniform(2, 4)
                notes = f"Внесены удобрения: NPK {random.randint(10, 20)}-{random.randint(10, 20)}-{random.randint(10, 20)}"
            elif work.work_type.name == 'Сбор урожая':
                water = 0
                fertilizer = 0
                labor = random.uniform(4, 8)
                notes = f"Собрано урожая. Качество: {random.choice(['хорошее', 'отличное', 'среднее'])}"
            else:
                water = random.uniform(0, 100)
                fertilizer = random.uniform(0, 10)
                labor = random.uniform(1, 5)
                notes = f"Работа выполнена. Погодные условия: {random.choice(['ясно', 'пасмурно', 'дождь'])}"

            ResourceUsage.objects.create(
                work_schedule=work,
                water_volume=round(water, 2),
                fertilizer_amount=round(fertilizer, 2),
                labor_hours=round(labor, 2),
                notes=notes
            )

        self.stdout.write(f'Created resource usage records')

    def create_harvests(self):
        plantings = Planting.objects.filter(status='harvested')

        for planting in plantings:
            # Create 1-3 harvest records per planting
            for i in range(random.randint(1, 3)):
                harvest_date = planting.actual_harvest_date + timedelta(days=i * 7)

                if planting.vegetable_type.name == 'Томаты':
                    quantity = random.uniform(50, 200)
                    unit = 'kg'
                elif planting.vegetable_type.name == 'Огурцы':
                    quantity = random.uniform(30, 150)
                    unit = 'kg'
                elif planting.vegetable_type.name == 'Редис':
                    quantity = random.uniform(10, 50)
                    unit = 'piece'
                else:
                    quantity = random.uniform(20, 100)
                    unit = random.choice(['kg', 'piece', 'box'])

                Harvest.objects.create(
                    planting=planting,
                    harvest_date=harvest_date,
                    quantity=round(quantity, 2),
                    unit=unit,
                    quality=random.choice(['excellent', 'good', 'average', 'poor'])
                )

        self.stdout.write(f'Created harvest records')
