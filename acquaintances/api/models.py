from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
    )
from django.core.files import File

import tempfile

from PIL import Image


class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Вы не ввели Email")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password):
        return self._create_user(email, password)

    def create_superuser(self, email, password):
        return self._create_user(
            email,
            password,
            is_staff=True,
            is_superuser=True
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30,)
    last_name = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='долгота'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True, null=True,
        verbose_name='широта'
    )

    def user_directory_path(instance, filename):
        return 'avatars/user_{0}_{1}'.format(instance, filename)
    avatar = models.ImageField(
        verbose_name="Avatar",
        null=True,
        blank=True,
        upload_to=user_directory_path
    )

    sex_Choices = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    sex = models.CharField(
        max_length=1,
        choices=sex_Choices,
        default='F',
        help_text="Enter your gender",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.id:  # Проверяем, что id не существует
            if self.avatar:
                original_image = Image.open(self.avatar.file)
                watermark = Image.open('static/watermark.png').convert("RGBA")
                transparency = 0.5
                watermark = watermark.convert("RGBA")
                watermark.putalpha(int(255 * transparency))
                x = original_image.width - watermark.width - 10
                y = original_image.height - watermark.height - 10
                watermarked_image = original_image.copy().convert("RGBA")
                watermarked_image.alpha_composite(watermark, (x, y))
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                output_image = watermarked_image.convert("RGBA")
                output_image.save('static/output.png')
                output_image.save(temp_file.name, format='PNG')
                self.avatar.save('watermarked_image.png',
                                 File(open(temp_file.name, "rb")), save=False)
                temp_file.close()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name


class Like(models.Model):
    participant = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='likes_given')
    liked_participant = models.ForeignKey(User, on_delete=models.CASCADE,
                                          related_name='likes_received')

    class Meta:
        unique_together = ('participant', 'liked_participant')
