
from django.db import models
from django.contrib.auth.models import User

class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reserved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('reservation', 'Reservation'),
        ('deduction', 'Deduction'),
        ('revenue_recognition', 'Revenue Recognition'),  # добавим новый тип транзакции
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.transaction_type} - {self.amount}'

class FinancialReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_id = models.IntegerField()
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recognized_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - Service: {self.service_id} - Order: {self.order_id} - Amount: {self.amount}'
