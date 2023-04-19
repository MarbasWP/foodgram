from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

TEXT_VALIDATOR = ('Имя пользователя должно содержать только буквы, '
                  'цифры или символы подчеркивания')
TEXT_USER = ('Username: {username}, Имя: {first_name}, '
             'Фамилия: {last_name}, Почта: {email},')


class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]{3,30}$',
                message=TEXT_VALIDATOR,
            )
        ],
        verbose_name='username'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
        verbose_name='почта'
    )
    password = models.CharField(
        max_length=128,
        verbose_name='Пароль'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Состояние'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return TEXT_USER.format(
            username=self.username, first_name=self.first_name,
            last_name=self.last_name, email=self.email
        )


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author',
        null=True
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
        null=True
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('follower', 'author'),
                name='unique_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.follower} -> {self.author}'
