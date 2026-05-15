from django.urls import path
from . import views

urlpatterns = [
    path('', views.cycle_list, name='cycle_list'),
    path('create/', views.cycle_create, name='cycle_create'),
    path('<int:pk>/', views.cycle_detail, name='cycle_detail'),
    path('<int:pk>/transition/', views.cycle_transition, name='cycle_transition'),
]