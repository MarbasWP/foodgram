from django.contrib import admin

from .models import (Favorites, Ingredient, Recipes,
                     Carts, Tag)


admin.site.register(Recipes)
admin.site.register(Carts)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Favorites)
