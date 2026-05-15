from django.db import models
from django.conf import settings


class ReviewCycle(models.Model):

    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('UNDER_REVIEW', 'Under Review'),
        ('CLOSED', 'Closed'),
    )

    title = models.CharField(max_length=255)

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title