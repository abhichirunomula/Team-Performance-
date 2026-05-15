from django.db import models
from django.conf import settings

from cycles.models import ReviewCycle


class SelfAssessment(models.Model):

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    review_cycle = models.ForeignKey(
        ReviewCycle,
        on_delete=models.CASCADE
    )

    text = models.TextField()

    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'review_cycle')

    def __str__(self):
        return f"{self.employee.username} - {self.review_cycle.title}"
    
class Review(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('FINALIZED', 'Finalized'),
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_reviews'
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='manager_reviews'
    )

    review_cycle = models.ForeignKey(
        ReviewCycle,
        on_delete=models.CASCADE
    )

    manager_assessment = models.TextField(
        blank=True,
        null=True
    )

    rating = models.IntegerField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    finalized_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.employee.username} Review"