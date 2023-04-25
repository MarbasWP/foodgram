from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from PIL import Image
from Users.models import User
TEXT_RECIPES = (
    'Название рецепта: {name}, Автор: {author}'
    'Приём пищи: {tag}, время приготовления: {time}'
    'Продукты: {products}'
    'Описание: {description}'
)
TEXT_PRODUCT = (
    'Название продукта: {name}'
    'Единицы измерения: {measure_unit}'
)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=256,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return TEXT_PRODUCT.format(
            name=self.name,
            measure_unit=self.measurement_unit
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        validators=[RegexValidator(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')],
        unique=True,
        verbose_name='hex-code'
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name='Уникальный фрагмент'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now=True,
        editable=False
    )
    image = models.ImageField(
        upload_to='recipes',
        verbose_name='Картинка'
    )
    text = models.TextField(
        blank=True, null=True,
        verbose_name='Описание',
        default='None')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Продукты',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Прием пищи'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=(MinValueValidator(0, 'Ваше блюдо уже готово!'),)
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return TEXT_RECIPES.format(
            name=self.name, author=self.author,
            tag=self.tags, time=self.cooking_time,
            prodocts=self.ingredients, description=self.text
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Image.open(
            self.image.path).resize(500).save(self.image.path)


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='В каких рецептах'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Связанные ингредиенты'
    )
    mount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(MinValueValidator(0, 'Добавь больше'),)
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.mount} {self.ingredients}'


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Понравившиеся рецепты'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Carts(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепты в корзине',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец корзины'
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
