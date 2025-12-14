from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView

from .forms import PlantingForm, WorkScheduleForm, HarvestForm
from .models import Greenhouse, Planting, WorkSchedule, Harvest, ScheduleTemplate, ResourceUsage



class DashboardView(TemplateView):
    """Главная панель управления"""
    template_name = 'greenhouse/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Статистика для дашборда
        context.update({
            'total_greenhouses': Greenhouse.objects.filter(is_active=True).count(),
            'active_plantings': Planting.objects.filter(
                status__in=['planted', 'growing']
            ).count(),
            'today_works': WorkSchedule.objects.filter(planned_date=today).count(),
            'upcoming_works': WorkSchedule.objects.filter(
                planned_date__gte=today,
                status='planned'
            ).order_by('planned_date')[:10],
            'recent_harvests': Harvest.objects.order_by('-harvest_date')[:5],
        })
        return context


# ==================== СПИСКИ ====================

class GreenhouseListView(LoginRequiredMixin, ListView):
    """Список всех теплиц"""
    model = Greenhouse
    template_name = 'greenhouse/greenhouse_list.html'
    context_object_name = 'greenhouses'

    def get_queryset(self):
        return Greenhouse.objects.filter(is_active=True).select_related('vegetable_type')


class PlantingListView(LoginRequiredMixin, ListView):
    """Список посадок с фильтрацией"""
    model = Planting
    template_name = 'greenhouse/planting_list.html'
    context_object_name = 'plantings'
    paginate_by = 10

    def get_queryset(self):
        queryset = Planting.objects.select_related(
            'greenhouse', 'vegetable_type'
        ).order_by('-planting_date')

        # Фильтрация по статусу
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class WorkScheduleListView(LoginRequiredMixin, ListView):
    """Список работ с фильтрацией"""
    model = WorkSchedule
    template_name = 'greenhouse/workschedule_list.html'
    context_object_name = 'works'
    paginate_by = 10

    def get_queryset(self):
        queryset = WorkSchedule.objects.select_related(
            'planting__greenhouse',
            'planting__vegetable_type',
            'work_type'
        ).order_by('planned_date')

        # Фильтрация по статусу
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Фильтрация по дате
        date_filter = self.request.GET.get('date')
        if date_filter:
            queryset = queryset.filter(planned_date=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['date_filter'] = self.request.GET.get('date', '')
        return context


class GreenhouseDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о теплице"""
    model = Greenhouse
    template_name = 'greenhouse/greenhouse_detail.html'
    context_object_name = 'greenhouse'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        greenhouse = self.object

        # Активные посадки в этой теплице
        context['active_plantings'] = greenhouse.planting_set.filter(
            status__in=['planted', 'growing']
        ).select_related('vegetable_type')

        # История посадок
        context['planting_history'] = greenhouse.planting_set.order_by('-planting_date')[:10]

        return context


class PlantingDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о посадке"""
    model = Planting
    template_name = 'greenhouse/planting_detail.html'
    context_object_name = 'planting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        planting = self.object

        # График работ для этой посадки
        context['work_schedules'] = planting.workschedule_set.select_related(
            'work_type'
        ).order_by('planned_date')

        # Урожай с этой посадки
        context['harvests'] = planting.harvest_set.order_by('-harvest_date')

        # Статистика по работам
        total_works = context['work_schedules'].count()
        completed_works = context['work_schedules'].filter(status='completed').count()
        context['work_progress'] = {
            'total': total_works,
            'completed': completed_works,
            'percent': int((completed_works / total_works * 100)) if total_works > 0 else 0
        }

        return context



class ReportsView(LoginRequiredMixin, TemplateView):
    """Страница отчетов"""
    template_name = 'greenhouse/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статистика по урожаю
        context['harvest_stats'] = Harvest.objects.values(
            'planting__vegetable_type__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            harvest_count=Count('id')
        ).order_by('-total_quantity')

        # Статистика по работам
        context['work_stats'] = WorkSchedule.objects.values(
            'work_type__name'
        ).annotate(
            total_completed=Count('id', filter=Q(status='completed')),
            total_planned=Count('id', filter=Q(status='planned'))
        )

        # Ресурсы за последний месяц
        month_ago = timezone.now().date() - timedelta(days=30)
        context['resource_stats'] = {
            'total_water': ResourceUsage.objects.aggregate(
                total=Sum('water_volume')
            )['total'] or 0,
            'total_fertilizer': ResourceUsage.objects.aggregate(
                total=Sum('fertilizer_amount')
            )['total'] or 0,
            'total_labor': ResourceUsage.objects.aggregate(
                total=Sum('labor_hours')
            )['total'] or 0,
        }

        return context


class HarvestReportView(LoginRequiredMixin, ListView):
    """Отчет по урожаю"""
    model = Harvest
    template_name = 'greenhouse/harvest_report.html'
    context_object_name = 'harvests'

    def get_queryset(self):
        queryset = Harvest.objects.select_related(
            'planting__greenhouse',
            'planting__vegetable_type'
        ).order_by('-harvest_date')

        # Фильтрация по дате
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            queryset = queryset.filter(harvest_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(harvest_date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Общая статистика
        context['total_quantity'] = queryset.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')

        return context


class PlantingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой посадки"""
    model = Planting
    form_class = PlantingForm
    template_name = 'greenhouse/planting_form.html'
    success_url = reverse_lazy('greenhouse:planting_list')

    def form_valid(self, form):
        """После сохранения посадки создаем график работ"""
        response = super().form_valid(form)

        # Автоматически создаем график работ из шаблонов
        from datetime import timedelta
        templates = ScheduleTemplate.objects.filter(
            vegetable_type=self.object.vegetable_type
        )

        works_created = 0
        for template in templates:
            WorkSchedule.objects.create(
                planting=self.object,
                work_type=template.work_type,
                planned_date=self.object.planting_date + timedelta(
                    days=template.days_after_planting
                ),
                status='planned'
            )
            works_created += 1

        messages.success(
            self.request,
            f'Посадка создана! Автоматически создано {works_created} работ в графике.'
        )
        return response


class WorkScheduleCreateView(LoginRequiredMixin, CreateView):
    """Создание новой работы вручную"""
    model = WorkSchedule
    form_class = WorkScheduleForm
    template_name = 'greenhouse/workschedule_form.html'

    def get_success_url(self):
        return reverse_lazy('greenhouse:planting_detail',
                            kwargs={'pk': self.object.planting.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Работа добавлена в график!')
        return response


class HarvestCreateView(LoginRequiredMixin, CreateView):
    """Добавление урожая"""
    model = Harvest
    form_class = HarvestForm
    template_name = 'greenhouse/harvest_form.html'

    def get_success_url(self):
        return reverse_lazy('greenhouse:planting_detail',
                            kwargs={'pk': self.object.planting.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Урожай учтен!')
        return response



class PlantingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование посадки"""
    model = Planting
    form_class = PlantingForm
    template_name = 'greenhouse/planting_form.html'

    def get_success_url(self):
        return reverse_lazy('greenhouse:planting_detail',
                            kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Посадка обновлена!')
        return response


class WorkScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование работы"""
    model = WorkSchedule
    form_class = WorkScheduleForm
    template_name = 'greenhouse/workschedule_form.html'

    def get_success_url(self):
        return reverse_lazy('greenhouse:planting_detail',
                            kwargs={'pk': self.object.planting.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Работа обновлена!')
        return response


class HarvestUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование урожая"""
    model = Harvest
    form_class = HarvestForm
    template_name = 'greenhouse/harvest_form.html'

    def get_success_url(self):
        return reverse_lazy('greenhouse:planting_detail',
                            kwargs={'pk': self.object.planting.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Данные урожая обновлены!')
        return response



class CompleteWorkView(LoginRequiredMixin, UpdateView):
    """Быстрое завершение работы"""
    model = WorkSchedule
    fields = []  # Не нужно показывать форму
    http_method_names = ['post']  # Только POST запросы

    def get_success_url(self):
        return reverse_lazy('greenhouse:planting_detail',
                            kwargs={'pk': self.object.planting.pk})

    def form_valid(self, form):
        self.object.actual_date = timezone.now().date()
        self.object.status = 'completed'
        response = super().form_valid(form)
        messages.success(self.request, 'Работа отмечена как выполненная!')
        return response
