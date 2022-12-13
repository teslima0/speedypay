from django.urls import path, re_path
from rest_framework_simplejwt.views import (TokenRefreshView,TokenObtainPairView,)
from .views import *

urlpatterns = [
          
    path ('login/',LoginAPIView.as_view(), name = 'login'),
    path ('logout/',LogoutAPIView.as_view(), name = 'logout'),
    path ('token/refresh',TokenRefreshView.as_view(), name = 'token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     # API ENDPOINT TO SHOW ACCOUNT DETAILS FOR LOGGED-IN USER USING CUSTOMUSER SERIALIZER
    path('viewuseraccount/', ViewUserAccount.as_view()),

    # ADMIN VIEW TO SHOW ACCOUNT DETAILS FOR SPECIFIC USER ID
    path('adminviewuser/<id>/', AdminViewUser.as_view()),
    
    # CREATE BANK ACCOUNT VIA API
    path('createbankaccountapi/', CreateBankAccountAPI.as_view()),

    # UPDATE BANK ACCOUNT VIA API
    path('bankaccountupdate/<int:pk>/', BankAccountUpdate.as_view()),

    # MAKE DEPOSITS AND WITHDRAWALS VIA API
    path('createtransactionapi/', CreateTransactionAPI.as_view()),

    # VIEW ACCOUNT DETAILS FOR CUSTOMER VIA CURL COMMAND. MUST PROVIDE ADMIN USERNAME:PASSWORD
       
    path('viewbankaccountapi/',ViewBankAccountAPI.as_view()),

    # API ENDPOINT TO SHOW ACCOUNT DETAILS FOR LOGGED-IN USER USING BANKACCOUNT SERIALIZER
    path('viewbankaccountuser/', ViewBankAccountUser.as_view()),
    
    # CSV DOWNLOAD
    path('downloadbankaccounts/', downloadBankAccounts),

    ]