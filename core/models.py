from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    first_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)]
    )
    last_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)]
    )
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
