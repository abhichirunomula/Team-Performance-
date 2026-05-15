from django.urls import path
from . import views

urlpatterns = [
    # Self-assessment
    path(
        'cycles/<int:cycle_pk>/self-assessment/',
        views.self_assessment_submit,
        name='self_assessment_submit'
    ),
    path(
        'cycles/<int:cycle_pk>/self-assessment/view/',
        views.self_assessment_detail,
        name='self_assessment_detail'
    ),

    # Manager reviews
    path(
        'reviews/',
        views.manager_review_list,
        name='manager_review_list'
    ),
    path(
        'reviews/cycles/<int:cycle_pk>/employees/<int:employee_pk>/',
        views.manager_review_submit,
        name='manager_review_submit'
    ),
    path(
        'reviews/cycles/<int:cycle_pk>/employees/<int:employee_pk>/detail/',
        views.manager_review_detail,
        name='manager_review_detail'
    ),
]