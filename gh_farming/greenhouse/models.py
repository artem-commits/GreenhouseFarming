from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class VegetableType(models.Model):
    """Тип овощной культуры"""
    name = models.CharField(max_length=100, verbose_name="Название культуры")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип овощной культуры"
        verbose_name_plural = "Типы овощных культур"

    def __str__(self):
        return self.name


class Greenhouse(models.Model):
    """Теплица"""
    number = models.CharField(max_length=10, verbose_name="Номер теплицы")
    vegetable_type = models.ForeignKey(
        VegetableType,
        on_delete=models.PROTECT,
        verbose_name="Тип выращиваемой культуры"
    )
    area = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Площадь (кв.м)"
    )
    image = models.ImageField(upload_to='greenhouses', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Теплица"
        verbose_name_plural = "Теплицы"

    def __str__(self):
        return f"Теплица {self.number} ({self.vegetable_type})"


class WorkType(models.Model):
    """Тип работ (посев, полив и т.д.)"""
    name = models.CharField(max_length=100, verbose_name="Вид работ")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Вид работ"
        verbose_name_plural = "Виды работ"

    def __str__(self):
        return self.name


class ScheduleTemplate(models.Model):
    """Шаблон графика работ для типа культуры"""
    vegetable_type = models.ForeignKey(
        VegetableType,
        on_delete=models.CASCADE,
        verbose_name="Тип культуры"
    )
    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.CASCADE,
        verbose_name="Вид работ"
    )
    days_after_planting = models.IntegerField(
        verbose_name="Дней после посадки",
        help_text="0 - день посадки"
    )
    duration_days = models.IntegerField(
        default=1,
        verbose_name="Продолжительность (дней)"
    )

    class Meta:
        verbose_name = "Шаблон графика"
        verbose_name_plural = "Шаблоны графиков"
        ordering = ['vegetable_type', 'days_after_planting']

    def __str__(self):
        return f"{self.vegetable_type} - {self.work_type} (день {self.days_after_planting})"


class Planting(models.Model):
    """Посадка культуры в теплице"""
    greenhouse = models.ForeignKey(
        Greenhouse,
        on_delete=models.CASCADE,
        verbose_name="Теплица"
    )
    vegetable_type = models.ForeignKey(
        VegetableType,
        on_delete=models.PROTECT,
        verbose_name="Культура"
    )
    planting_date = models.DateField(verbose_name="Дата посадки")
    planned_harvest_date = models.DateField(
        verbose_name="Планируемая дата сбора урожая"
    )
    actual_harvest_date = models.DateField(
        null=True, blank=True,
        verbose_name="Фактическая дата сбора урожая"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Запланирована'),
            ('planted', 'Посажена'),
            ('growing', 'Растет'),
            ('harvested', 'Собрана'),
        ],
        default='planned',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Посадка"
        verbose_name_plural = "Посадки"

    def __str__(self):
        return f"{self.greenhouse} - {self.vegetable_type} ({self.planting_date})"


class WorkSchedule(models.Model):
    """График работ"""
    planting = models.ForeignKey(
        Planting,
        on_delete=models.CASCADE,
        verbose_name="Посадка"
    )
    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.PROTECT,
        verbose_name="Вид работ"
    )
    planned_date = models.DateField(verbose_name="Плановая дата")
    actual_date = models.DateField(
        null=True, blank=True,
        verbose_name="Фактическая дата"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Запланировано'),
            ('in_progress', 'В работе'),
            ('completed', 'Выполнено'),
            ('cancelled', 'Отменено'),
        ],
        default='planned',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "График работ"
        verbose_name_plural = "Графики работ"
        ordering = ['planned_date']

    def __str__(self):
        return f"{self.planting} - {self.work_type}"


class ResourceUsage(models.Model):
    """Затраты ресурсов при выполнении работ"""
    work_schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        verbose_name="Работа"
    )
    water_volume = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Объем воды (л)"
    )
    fertilizer_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Количество удобрений (кг)"
    )
    labor_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Трудозатраты (часы)"
    )
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        verbose_name = "Затраты ресурсов"
        verbose_name_plural = "Затраты ресурсов"


class Harvest(models.Model):
    """Урожай"""
    planting = models.ForeignKey(
        Planting,
        on_delete=models.CASCADE,
        verbose_name="Посадка"
    )
    harvest_date = models.DateField(verbose_name="Дата сбора")
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Количество"
    )
    unit = models.CharField(
        max_length=20,
        choices=[
            ('kg', 'кг'),
            ('piece', 'шт'),
            ('box', 'ящик'),
        ],
        default='kg',
        verbose_name="Единица измерения"
    )
    quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Отличное'),
            ('good', 'Хорошее'),
            ('average', 'Среднее'),
            ('poor', 'Плохое'),
        ],
        default='good',
        verbose_name="Качество"
    )

    class Meta:
        verbose_name = "Урожай"
        verbose_name_plural = "Урожай"

    def __str__(self):
        return f"{self.planting} - {self.quantity} {self.get_unit_display()}"