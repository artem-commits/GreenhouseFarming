from django.urls import path
from . import views

app_name = 'greenhouse'

urlpatterns = [
    # Главная страница
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Списки
    path('greenhouses/', views.GreenhouseListView.as_view(), name='greenhouse_list'),
    path('plantings/', views.PlantingListView.as_view(), name='planting_list'),
    path('works/', views.WorkScheduleListView.as_view(), name='workschedule_list'),

    # Детальные просмотры
    path('greenhouse/<int:pk>/', views.GreenhouseDetailView.as_view(), name='greenhouse_detail'),
    path('planting/<int:pk>/', views.PlantingDetailView.as_view(), name='planting_detail'),

    # Создание
    path('planting/create/', views.PlantingCreateView.as_view(), name='planting_create'),
    path('work/create/', views.WorkScheduleCreateView.as_view(), name='workschedule_create'),
    path('harvest/create/', views.HarvestCreateView.as_view(), name='harvest_create'),

    # Редактирование
    path('planting/<int:pk>/edit/', views.PlantingUpdateView.as_view(), name='planting_edit'),
    path('work/<int:pk>/edit/', views.WorkScheduleUpdateView.as_view(), name='workschedule_edit'),
    path('harvest/<int:pk>/edit/', views.HarvestUpdateView.as_view(), name='harvest_edit'),

    # Быстрые действия
    path('work/<int:pk>/complete/', views.CompleteWorkView.as_view(), name='workschedule_complete'),

    # Отчеты
    path('reports/', views.ReportsView.as_view(), name='reports'),
]
