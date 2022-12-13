from django.db import models
from django.contrib.auth.models import( AbstractBaseUser, BaseUserManager,PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.functional import cached_property
from django.urls import reverse
from django.conf import settings
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None,**extra_fields):
        if username is None:
            raise TypeError('Users should have a username')

        if email is None:
            raise TypeError("Users should have an Email")

        user = self.model(username=username, email= self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        #user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')

        user = self.create_user( email, username, password=None)
        user.is_superuser = True
        user.is_staff =True
        user.save()
        return user

      
class User(AbstractBaseUser,PermissionsMixin):
    username= models.CharField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(verbose_name='First Name', max_length=100, )
    last_name = models.CharField(verbose_name='Last Name', max_length=100, )
    email= models.EmailField(max_length=255, unique=True, db_index=True)
    #password=models.CharField(max_length=25)
    #is_verified= models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['username','first_name', 'last_name' ]
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.email

    def tokens(self):
        refresh= RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
class BankAccount(models.Model):
    account_type = (
        ('savings', 'Savings'),
        ('credit', 'Credit'),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bankaccount', on_delete=models.CASCADE, )
    account_type = models.CharField(max_length=20, choices=account_type, db_index=True )
    account_balance = models.FloatField(default=0)
    date = models.DateTimeField(auto_now=True, verbose_name='Transaction Date')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.account_type

    def get_absolute_url(self):
        return reverse('bank-detail', kwargs={'pk': self.pk})

    

class Transactions(models.Model):

    transaction_type = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='transactions', on_delete=models.CASCADE, )
    account_type = models.ForeignKey(BankAccount, related_name='accounttransactions', to_field='id', on_delete=models.CASCADE,)
    transaction_type = models.CharField(max_length=20, choices=transaction_type)
    transaction_amount = models.FloatField()
    transaction_date = models.DateTimeField(auto_now=True, db_index=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']


    def __str__(self):
        return self.transaction_type

    def get_absolute_url(self):
        return reverse('transaction-detail', kwargs={'pk': self.pk})