from django.urls import path
from . import views

urlpatterns = [
    path('',               views.goal_list,   name='goal_list'),
    path('create/',        views.create_goal, name='create_goal'),
    path('<int:pk>/edit/', views.edit_goal,   name='edit_goal'),
    path('<int:pk>/delete/', views.delete_goal, name='delete_goal'),
]