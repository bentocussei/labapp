from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from escolas import views

router = routers.DefaultRouter()
router.register('escolas', views.EscolaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
