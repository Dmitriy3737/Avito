from rest_framework import serializers
from .models import UserBalance, Transaction, FinancialReport

class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalance
        fields = ('user', 'amount')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'transaction_type', 'created_at', 'user_id']
        read_only_fields = ['user', 'transaction_type', 'created_at']

class AddFundsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class ReserveFundsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class DeductFundsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class FinancialReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialReport
        fields = ['user', 'service_id', 'order_id', 'amount', 'recognized_at']

class TransferFundsSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)