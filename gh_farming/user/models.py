from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('agronomist', 'Главный агроном'),
        ('assistant', 'Помощник агронома'),
        ('viewer', 'Наблюдатель'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        verbose_name='Роль'
    )
    phone = PhoneNumberField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    @property
    def is_agronomist(self):
        return self.role == 'agronomist'

    @property
    def is_assistant(self):
        return self.role == 'assistant'

    @property
    def can_edit_planting(self):
        return self.role in ['agronomist', 'assistant']

    @property
    def can_manage_users(self):
        return self.role == 'agronomist'

    def __str__(self):
        return f"{self.username} ({self.role})"
