from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('register/',                              views.register,              name='register'),

    # Manager team management
    path('team/',                                  views.team_list,             name='team_list'),
    path('team/add-employee/',                     views.add_employee,          name='add_employee'),
    path('team/remove/<int:pk>/',                  views.remove_employee,       name='remove_employee'),

    # Admin Panel (superuser only)
    path('admin-panel/',                           views.admin_dashboard,       name='admin_dashboard'),
    path('admin-panel/managers/create/',           views.admin_create_manager,  name='admin_create_manager'),
    path('admin-panel/managers/<int:pk>/delete/',  views.admin_delete_manager,  name='admin_delete_manager'),
    path('admin-panel/managers/<int:pk>/',         views.admin_manager_detail,  name='admin_manager_detail'),
    path('admin-panel/employees/<int:employee_pk>/assign-manager/',
                                                   views.admin_assign_manager,  name='admin_assign_manager'),
    path('admin-panel/employees/<int:pk>/delete/', views.admin_delete_employee, name='admin_delete_employee'),
]