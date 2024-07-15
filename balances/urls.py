from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('balances/', GetUserBalance.as_view(), name='balances'),
    path('add_funds/', AddFunds.as_view(), name='add_funds'),
    path('reserve_funds/', ReserveFunds.as_view(), name='reserve_funds'),
    path('deduct_funds/', DeductFunds.as_view(), name='deduct_funds'),
    path('transfer_funds/', TransferFunds.as_view(), name='transfer_funds'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # создание токена
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление токена
]
