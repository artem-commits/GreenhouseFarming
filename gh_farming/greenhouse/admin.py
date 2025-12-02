from django.contrib import admin
from .models import VegetableType, Greenhouse, WorkType, ScheduleTemplate, Planting, WorkSchedule, ResourceUsage, \
    Harvest


class WorkScheduleInline(admin.TabularInline):
    model = WorkSchedule
    extra = 0
    fields = ['work_type', 'planned_date', 'actual_date', 'status']


class ResourceUsageInline(admin.TabularInline):
    model = ResourceUsage
    extra = 1
    fields = ['water_volume', 'fertilizer_amount', 'labor_hours']


class HarvestInline(admin.TabularInline):
    model = Harvest
    extra = 1
    fields = ['harvest_date', 'quantity', 'unit', 'quality']


class ScheduleTemplateInline(admin.TabularInline):
    model = ScheduleTemplate
    extra = 2
    fields = ['work_type', 'days_after_planting', 'duration_days']


@admin.register(VegetableType)
class VegetableTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    inlines = [ScheduleTemplateInline]


@admin.register(Greenhouse)
class GreenhouseAdmin(admin.ModelAdmin):
    list_display = ['number', 'vegetable_type', 'area', 'is_active']
    list_filter = ['vegetable_type', 'is_active']
    search_fields = ['number']


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    list_display = ['vegetable_type', 'work_type', 'days_after_planting', 'duration_days']
    list_filter = ['vegetable_type', 'work_type']


@admin.register(Planting)
class PlantingAdmin(admin.ModelAdmin):
    list_display = ['greenhouse', 'vegetable_type', 'planting_date', 'status']
    list_filter = ['vegetable_type', 'status']
    search_fields = ['greenhouse__number']
    inlines = [WorkScheduleInline, HarvestInline]

    def save_model(self, request, obj, form, change):
        """Автоматически создаем график работ при создании посадки"""
        super().save_model(request, obj, form, change)

        if not change:  # Только для новых посадок
            from datetime import timedelta
            templates = ScheduleTemplate.objects.filter(vegetable_type=obj.vegetable_type)

            for template in templates:
                WorkSchedule.objects.create(
                    planting=obj,
                    work_type=template.work_type,
                    planned_date=obj.planting_date + timedelta(days=template.days_after_planting),
                    status='planned'
                )


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['planting', 'work_type', 'planned_date', 'actual_date', 'status']
    list_filter = ['work_type', 'status']
    inlines = [ResourceUsageInline]


@admin.register(ResourceUsage)
class ResourceUsageAdmin(admin.ModelAdmin):
    list_display = ['work_schedule', 'water_volume', 'fertilizer_amount', 'labor_hours']


@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ['planting', 'harvest_date', 'quantity', 'unit', 'quality']
    list_filter = ['quality', 'unit']