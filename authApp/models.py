from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

from django.conf import settings

class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email')
        user = self.model(email=email) #model se hereda de BaseUserManager
        user.set_password(password)
        user.save(using=self._db) # ORM inserta usuario en base de datos
        return user
            
    def create_superuser(self, email, password):

        user = self.create_user(
            email=      email,
            password=   password,
        ) # rehuso el primer metodo
        user.is_admin = True # Le ofrezco privilegios de admin
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    GENDERS = (
        ('MA','Male'),
        ('FE','Female'),
        ('OT','Other'),
    )
    ROLES =(
        ('CL','Cliente'),
        ('AD','Administrador'),
    )
    dni             = models.CharField(max_length=20, null=False, unique=True)
    name            = models.CharField(max_length=50, null=False)#
    last_name       = models.CharField(max_length=50, null=False)
    email           = models.EmailField(unique=True, null=False)
    password        = models.CharField(max_length=100, null=False)
    birth           = models.DateField()
    phone           = models.BigIntegerField(null=False)
    other_contact   = models.BigIntegerField(null=True, blank=True)
    gender          = models.CharField(max_length=7, choices=GENDERS, default='Other')
    role            = models.CharField(max_length=14, choices=ROLES, default='Cliente') #
    active          = models.BooleanField(default=False) #
    payment_ok      = models.BooleanField(default=False) #

    def save(self, **kwargs): # ** -> recibe un diccionario
        # if not self.password:
        #     raise ValueError('Users must have an password')
        some_salt       = settings.SOME_SALT # Valor secreto para cifrado
        self.password   = make_password(self.password, some_salt) # Cifra la contraseña ingresada
        super().save(**kwargs)
        
    objects =           UserManager()
    USERNAME_FIELD =    'email'