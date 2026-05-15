from django.contrib import admin

from .models import SelfAssessment, Review


admin.site.register(SelfAssessment)
admin.site.register(Review)