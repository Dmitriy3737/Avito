from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import UserBalance, Transaction, FinancialReport
from .serializers import UserBalanceSerializer, TransactionSerializer, ReserveFundsSerializer, AddFundsSerializer, \
    DeductFundsSerializer, TransferFundsSerializer
from decimal import Decimal, InvalidOperation

class GetUserBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.id != int(user_id):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_balance = UserBalance.objects.get(user_id=user_id)
            serializer = UserBalanceSerializer(user_balance)
            return Response(serializer.data)
        except UserBalance.DoesNotExist:
            return Response({'error': 'User balance not found'}, status=status.HTTP_404_NOT_FOUND)

class AddFunds(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddFundsSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            amount = serializer.validated_data['amount']

            if request.user.id != user_id:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

            if amount <= 0:
                return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_balance = UserBalance.objects.get(user_id=user_id)
                user_balance.amount += amount
                user_balance.save()

                transaction_record = Transaction(
                    user=request.user,
                    amount=amount,
                    transaction_type='deposit'
                )
                transaction_record.save()

            except UserBalance.DoesNotExist:
                return Response({'error': 'User balance not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(TransactionSerializer(transaction_record).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReserveFunds(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReserveFundsSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            amount = serializer.validated_data['amount']

            if request.user.id != user_id:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

            if amount <= 0:
                return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_balance = UserBalance.objects.get(user_id=user_id)
            except UserBalance.DoesNotExist:
                return Response({'error': 'User balance not found'}, status=status.HTTP_404_NOT_FOUND)

            if user_balance.amount < amount:
                return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

            # Списываем средства с баланса и резервируем их
            user_balance.amount -= amount
            user_balance.reserved_amount += amount
            user_balance.save()

            # Записываем транзакцию типа "reservation"
            transaction = Transaction(
                user=request.user,
                amount=amount,
                transaction_type='reservation'
            )
            transaction.save()

            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeductFunds(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeductFundsSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            service_id = serializer.validated_data['service_id']
            order_id = serializer.validated_data['order_id']
            amount = serializer.validated_data['amount']

            if request.user.id != user_id:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

            if amount <= 0:
                return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_balance = UserBalance.objects.get(user_id=user_id)
            except UserBalance.DoesNotExist:
                return Response({'error': 'User balance not found'}, status=status.HTTP_404_NOT_FOUND)

            if user_balance.reserved_amount < amount:
                return Response({'error': 'Insufficient reserved funds'}, status=status.HTTP_400_BAD_REQUEST)

            # Списываем резервированные средства
            user_balance.reserved_amount -= amount
            user_balance.save()

            # Записываем транзакцию типа "revenue_recognition" (признание выручки)
            transaction = Transaction(
                user=request.user,
                amount=amount,
                transaction_type='revenue_recognition'  # Лучше использовать понятное название для типа транзакции
            )
            transaction.save()

            # Создаем запись в отчете для бухгалтерии
            financial_report = FinancialReport(
                user=request.user,
                service_id=service_id,
                order_id=order_id,
                amount=amount,
                recognized_at=timezone.now()
            )
            financial_report.save()

            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferFunds(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferFundsSerializer(data=request.data)
        if serializer.is_valid():
            sender_id = serializer.validated_data['sender_id']
            recipient_id = serializer.validated_data['recipient_id']
            amount = serializer.validated_data['amount']

            if sender_id == recipient_id:
                return Response({'error': 'Sender and recipient must be different users'},
                                status=status.HTTP_400_BAD_REQUEST)

            if amount <= 0:
                return Response({'error': 'Amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    # Block rows for update
                    sender_balance = UserBalance.objects.select_for_update().get(user_id=sender_id)
                    recipient_balance = UserBalance.objects.select_for_update().get(user_id=recipient_id)

                    if sender_balance.amount < amount:
                        return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

                    # Perform the transfer
                    sender_balance.amount -= amount
                    recipient_balance.amount += amount

                    sender_balance.save()
                    recipient_balance.save()

                    # Log transactions
                    sender_transaction = Transaction(
                        user_id=sender_id,
                        amount=-amount,
                        transaction_type='transfer'
                    )
                    sender_transaction.save()

                    recipient_transaction = Transaction(
                        user_id=recipient_id,
                        amount=amount,
                        transaction_type='transfer'
                    )
                    recipient_transaction.save()

            except UserBalance.DoesNotExist:
                return Response({'error': 'User balance not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'sender_transaction': TransactionSerializer(sender_transaction).data,
                'recipient_transaction': TransactionSerializer(recipient_transaction).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

