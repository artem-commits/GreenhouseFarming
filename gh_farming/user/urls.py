from django.urls import path

from .views import ProfileDetailView, UpdateProfileView

app_name = 'user'

urlpatterns = [
    path('edit-profile/', UpdateProfileView.as_view(), name='edit_profile'),
    path('<str:username>/', ProfileDetailView.as_view(), name='profile'),
]
