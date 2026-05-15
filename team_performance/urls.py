from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', include('django.contrib.auth.urls')),  # login / logout
    path('', include('users.urls')),                # register + team mgmt
    path('goals/', include('goals.urls')),
    path('cycles/', include('cycles.urls')),
    path('', include('reviews.urls')),
]
