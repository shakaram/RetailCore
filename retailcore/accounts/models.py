from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    '''مدل کاربر سفارشی با نقش‌های مختلف'''
    ROLE_CHOICES =[
        ('user',_('user')),
        ('sales',_('sales')),
        ('cashier',_('cashier')),
        ('supervisor',_('supervisor')),
        ('manager',_('manager')),
    ]
    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default='user',db_index=True)
    profile=models.ImageField(_("profile"), upload_to='profile',null=True,blank=True)
    bio=models.TextField(_("biography"),null=True,blank=True)
    age=models.PositiveIntegerField(_("age"),
            null=True,blank=True,
            validators=[MinValueValidator(10), MaxValueValidator(120)])

    def __str__(self):
        return f'{self.username} - {self.role}'
    