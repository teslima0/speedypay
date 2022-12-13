from rest_framework.exceptions import AuthenticationFailed 
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from .models import User,Transactions,BankAccount
from django.contrib import auth

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model= User
        fields=['email','username','password']

    def validate(self, attrs):
        email= attrs.get('email', '')
        username= attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('The username can only contain alphanumeric character')
        return attrs

    def create (self, validated_data):
        return User.objects.create_user(**validated_data)

class LogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField()
    default_error_messages={
        'bad_token':('Token is expired or invalid')
    }
    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
        
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255,min_length=3)
    password=serializers.CharField(max_length=68, min_length=6,write_only=True)
    username=serializers.CharField(max_length=255,min_length=3, read_only=True)
    tokens=serializers.SerializerMethodField()

    def get_tokens(self,obj):
        user = User.objects.get(email=obj['email'])

        return {
            'access':user.tokens()['access'],
            'refresh':user.tokens()['refresh']
        }
    class Meta:
        model=User
        fields=['email','password','username','tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password=attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)
      
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
  
        if not user.is_active:
            raise AuthenticationFailed('account disabled, contact admin')
        

        
        return {
            'email': user.email,
            'username':user.username,
            'tokens':user.tokens
        } 
class TransactionSerializer(serializers.ModelSerializer):
    
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=False,)
    account_type = serializers.PrimaryKeyRelatedField(queryset=BankAccount.objects.all(),many=False,)
    
    class Meta:
        model = Transactions
        fields = [ 'id', 'transaction_date', 'account_type', 'user', 'transaction_type', 'transaction_amount', ]
        


class BankAccountSerializer(serializers.ModelSerializer):
    
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=False,)
    accounttransactions = TransactionSerializer(many=True, read_only=True, )
    
    class Meta:
        model = BankAccount
        fields = ['id', 'date', 'account_type', 'user', 'account_balance', 'accounttransactions']
        extra_kwargs = {
            'account_balance': {'read_only': True},
            
            }