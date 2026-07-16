from django.db import models
from students.models import Student

class Fee(models.Model):
    STATUS_CHOICES = [('paid', 'Paid'), ('unpaid', 'Unpaid'), ('partial', 'Partial')]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    payment_date = models.DateField(null=True, blank=True)
    
    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount