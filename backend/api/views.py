from django.db.models import Sum
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import (status, viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from Users.models import User, Follow
from Recipes.models import Tag, Ingredient, Recipes, IngredientRecipe, Carts, Favorites
from .permissions import AuthorStaffOrReadOnly, IsAuthenticated, AdminOrReadOnly
from .serializers import UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer, UserSubscribeSerializer, \
    ShoppingCartSerializer, CreateRecipeSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    add_serializer = UserSerializer
    permission_classes = (DjangoModelPermissions,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = UserSubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AuthorStaffOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f'\n{ingredient["ingredient__name"]}'
                f'({ingredient["ingredieny__measurement_unit"]}) - '
                f'{ingredient["amount"]}'
            )
            file = 'shopping_list.txt'
            response = HttpResponse(shopping_list, content_type='text/plain')
            response['Content-Disposition'] = f'filename: {file}'
            return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        self.send_message(IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')))

    def shopping_cart(self, request, pk):
        serializer = ShoppingCartSerializer(
            data={
                'user': request.user.id,
                'recipe': get_object_or_404(Recipes, id=pk).id
            },
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            Carts,
            user=request.user.id,
            recipe=get_object_or_404(Recipes, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['POST'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        serializer = Favorites(
            data={
                'user': request.user.id,
                'recipe': get_object_or_404(Recipes, id=pk).id
            },
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorites,
            user=request.user,
            recipe=get_object_or_404(Recipes, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
