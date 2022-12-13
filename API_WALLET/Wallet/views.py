from .serializers import UserSerializer,LoginSerializer,LogoutSerializer,BankAccountSerializer,TransactionSerializer
from rest_framework import viewsets, generics,status,views
from rest_framework.response import Response
from .permission import IsLoggedInUserOrAdmin, IsAdminUser
from rest_framework.permissions import AllowAny
from .models import User,BankAccount,Transactions
from rest_framework import permissions
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import F
import csv
from django.http.response import HttpResponse

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

        # Add this code block
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class LoginAPIView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    permission_classes=[permissions.AllowAny]
    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception= True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class=LogoutSerializer
    permission_classes=(permissions.IsAuthenticated,)

    def post(self, request):
        serializer= self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
# CREATE BANK ACCOUNT VIA API
class CreateBankAccountAPI(generics.CreateAPIView):
    '''
    CURL COMMAND TO CREATE SAVINGS BANK ACCOUNT FOR USER WITH ID 14
    curl --data "account_type=savings&user=14" http://127.0.0.1:8000/createbankaccountapi/
    CURL COMMAND TO CREATE CREDIT BANK ACCOUNT FOR USER WITH ID 14
    curl --data "account_type=credit&user=14" http://127.0.0.1:8000/createbankaccountapi/
    '''
   
    serializer_class = BankAccountSerializer
    # permission_classes = [permissions.IsAdminUser]  UNCOMMENT IF REQUIRED FOR ADMIN USERS ONLY
    
    def post(self, request, format=None):
        serializer = BankAccountSerializer(data=request.data)
                
        if serializer.is_valid():
            account_type = serializer.validated_data['account_type']
            if account_type == 'savings':
                serializer.validated_data['account_balance'] = 50           # INITIAL BALANCE
            elif account_type == 'credit':
                serializer.validated_data['account_balance'] = -20000       # INITIAL BALANCE
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# UPDATE BANK ACCOUNT VIA API

class BankAccountUpdate(APIView):
    """
    
    ACCOUNT BALANCE ARE INTENTIONALLY MADE READ-ONLY AND CANNOT BE CHANGED VIA API
    EXCEPT VIA TRANSACTIONS SO THERE WILL BE RECORDS TO SHOW FOR ANY BALANCE CHANGES; THIS CAN HOWEVER BE CHANGED IF REQUIRED
    CURL COMMAND TO UPDATE BANK ACCOUNT TYPE FOR USER WITH ID 1 AND BANK ACCOUNT ID OF 1.
    curl -X PUT -d "account_type=credit&user=1" http://127.0.0.1:8000/bankaccountupdate/1/
    """
    def get(self, request, pk, format=None):
        account = self.get_object(pk)
        serializer = BankAccountSerializer(account)
        return Response(serializer.data)

    def get_object(self, pk, ):
        
        try:
            user_id = self.request.data.get('user')
            return BankAccount.objects.get(pk=pk, user_id = user_id)    # THE USER ID AND ACCOUNT ID MUST MATCH AN EXISTING ACCOUNT
        except BankAccount.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        account = self.get_object(pk)
        serializer = BankAccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# MAKE DEPOSITS AND WITHDRAWALS VIA API

class CreateTransactionAPI(generics.CreateAPIView):
    '''
    ACCOUNT TYPE (i.e. ACCOUNT ID) AND USER (i.e. USER ID) MUST BE SUPPLIED AND
    MUST MATCH AN EXISTING ACCOUNT
    CURL COMMAND TO MAKE DEPOSITS/WITHDRAWALS VIA API
    curl --data "transaction_type=deposit&transaction_amount=10000&account_type=6&user=1" http://127.0.0.1:8000/createtransactionapi/
    curl --data "transaction_type=withdrawal&transaction_amount=500&account_type=6&user=1" http://127.0.0.1:8000/createtransactionapi/
    '''
   
    serializer_class = TransactionSerializer
    # permission_classes = [permissions.IsAdminUser]        UNCOMMENT IF REQUIRED FOR ADMIN USERS ONLY
    
    def post(self, request, format=None):
        serializer = TransactionSerializer(data=request.data)
                
        if serializer.is_valid():
            user_id = serializer.validated_data['user']
            account_type = serializer.validated_data['account_type']
            transaction_type = serializer.validated_data['transaction_type']
            transaction_amount = serializer.validated_data['transaction_amount']
            bank_account = BankAccount.objects.get(id=account_type.pk, user_id=user_id)
                        
            if bank_account:   # CONFIRM IF THIS ACCOUNT EXISTS BEFORE MAKING ANY CHANGES
                if transaction_type == 'deposit':
                    bank_account.account_balance = F('account_balance') + transaction_amount
                    bank_account.save()
                    serializer.save()
                    return Response(status=status.HTTP_201_CREATED)
                    
                elif transaction_type == 'withdrawal':
                    if bank_account.account_type == 'savings':
                        if bank_account.account_balance > 50 and bank_account.account_balance > transaction_amount:
                            new_savings_balance = bank_account.account_balance - transaction_amount 
                            if new_savings_balance >= 50:                                                # CHECK THAT NEW BALANCE WON'T BE LESS THAN 50
                                bank_account.account_balance = F('account_balance') - transaction_amount
                                bank_account.save()
                                serializer.save()
                                return Response(status=status.HTTP_201_CREATED)
                            else:
                                return Response(status=status.HTTP_400_BAD_REQUEST)                            
                        else:
                            return Response(status=status.HTTP_400_BAD_REQUEST)
                    
                    elif bank_account.account_type == 'credit':
                        if bank_account.account_balance > -20000:
                            new_credit_balance = bank_account.account_balance - transaction_amount
                            if new_credit_balance >= -20000:                                              # CHECK THAT NEW BALANCE WON'T BE LESS THAN -20000
                                bank_account.account_balance = F('account_balance') - transaction_amount
                                bank_account.save()
                                serializer.save()
                                return Response(status=status.HTTP_201_CREATED)
                            else:
                                return Response(status=status.HTTP_400_BAD_REQUEST) 
                        else:
                            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# VIEW ACCOUNT DETAILS FOR CUSTOMER VIA CURL COMMAND. MUST PROVIDE ADMIN USERNAME:PASSWORD
class ViewBankAccountAPI(generics.ListAPIView):
    '''
    CURL COMMAND TO VIEW ACCOUNT INFO VIA API FOR ADMIN ONLY:
    
    curl -u bb@bb.com:123456  http://127.0.0.1:8000/viewbankaccountapi/?id=10
    
    '''

    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('id')
        
        if user_id:                                
            user = User.objects.get(id=user_id)
            queryset = user.bankaccount.all()
            
        return queryset


# API ENDPOINT TO SHOW ACCOUNT DETAILS FOR LOGGED-IN USER USING BANKACCOUNT SERIALIZER
class ViewBankAccountUser(generics.ListAPIView):
    '''
    VIEW ACCOUNT INFO FOR LOGGED IN USER
    http://127.0.0.1:8000/viewbankaccountuser/
    
    '''
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        logged_in_user = self.request.user     # FOR LOGGED IN USERS      
        queryset = logged_in_user.bankaccount.all()
        return queryset


# CSV DOWNLOAD OF ACCOUNT DATA

def downloadBankAccounts(request):
    '''
    DOWNLOAD ACCOUNT INFO FOR ALL USERS
    http://127.0.0.1:8000/downloadbankaccounts/
    
    '''
       
    data = BankAccount.objects.all()
    if data:
        
        file = 'bank_accounts.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename='+ file},
        )
        writer = csv.writer(response)
        writer.writerow(['ID', 'Account Type', 'Account Balance', 'Transaction Date', 'User_ID'])

        for f in data:
            writer.writerow([f.id, f.account_type, f.account_balance, f.date, f.user_id])
            print([f.id, f.account_type, f.account_balance, f.date, f.user_id])
        return response

# API ENDPOINT TO SHOW ACCOUNT DETAILS FOR LOGGED-IN USER USING CUSTOMUSER SERIALIZER

class ViewUserAccount(generics.ListAPIView):
    '''
    VIEW ACCOUNT INFO FOR LOGGED IN USER:\n
    URL: 'http://127.0.0.1:8000/viewuseraccount/'
    
    '''
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        logged_in_user = self.request.user.id  
        queryset = User.objects.filter(id = logged_in_user)
        return queryset


# ADMIN VIEW TO SHOW ACCOUNT DETAILS FOR SPECIFIC USER ID
class AdminViewUser(generics.ListAPIView):
    '''
    VIEW ACCOUNT INFO FOR SPECIFIC USER. (in the case below details of user with id 1 will be shown):
    http://127.0.0.1:8000/adminviewuser/8/
    I HAVE ALSO CONFIGURED DJANGO ADMIN URL TO DO SAME THING: 
    http://127.0.0.1:8000/admin/
    
    '''
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
        
    def get_queryset(self):
        id = self.kwargs['id']
        queryset = User.objects.filter(id = id)
        return queryset
