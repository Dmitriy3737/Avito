from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserBalance

class UserBalanceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.balance = UserBalance.objects.create(user=self.user, amount=100)

    def test_balance_creation(self):
        self.assertEqual(self.balance.user.username, 'test_user')
        self.assertEqual(self.balance.amount, 100)