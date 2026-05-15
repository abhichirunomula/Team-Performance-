from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.goal_list,          name='goal_list'),
    path('create/',                 views.create_goal,        name='create_goal'),
    path('assign/',                 views.assign_task,        name='assign_task'),
    path('<int:pk>/edit/',          views.edit_goal,          name='edit_goal'),
    path('<int:pk>/delete/',        views.delete_goal,        name='delete_goal'),
    path('<int:pk>/status/',        views.update_goal_status, name='update_goal_status'),
]