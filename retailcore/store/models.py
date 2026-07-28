from django.db import models
from accounts.models import User
from django.utils.translation import gettext_lazy as _


class WarehouseModel(models.Model):
    """مدل موجودی انبار
    
    مدیریت موجودی کالاها در انبار اصلی."""
    product = models.ForeignKey('products.ProductModel', verbose_name=_("product"),
                on_delete=models.CASCADE,related_name='warehouse', db_index=True)
    quantity = models.PositiveIntegerField(_("quantity"))
    is_available = models.BooleanField(_("is available"), default=False)

    class Meta:
        indexes = [models.Index(fields=['product']),]
        constraints=[models.UniqueConstraint(fields=['product'],name='unique_product_warehouse')]

    def save(self, *args, **kwargs):
        """
        ذخیره‌سازی با محاسبه خودکار وضعیت موجودی
        """
        self.is_available = self.quantity > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'

class WasteModel(models.Model):
    """مدل ضایعات محصولات
    
    ثبت کالاهای ضایعاتی و معیوب."""
    product=models.ForeignKey('products.ProductModel', verbose_name=_("product"), on_delete=models.PROTECT, related_name='waste')
    user=models.ForeignKey(User, verbose_name=_("user"), on_delete=models.PROTECT,related_name='waste')
    quantity=models.PositiveIntegerField(_("quantity"))
    description=models.TextField(_("description "), null=True, blank=True)
    update_dt=models.DateTimeField(_("date update"), auto_now=True)
    create_dt=models.DateTimeField(_("date create"), auto_now_add=True)
    
    class Meta:
        indexes = [models.Index(fields=['create_dt']),
                   models.Index(fields=['product']),]
        constraints=[models.UniqueConstraint(fields=['product'],name='unique_product_waste')]

    def __str__(self):
        return f'{self.product.name} - {self.quantity} - {self.user.username}'

class ReturnsModel(models.Model):
    """محصولات برگشت خورده"""
    product=models.ForeignKey('products.ProductModel', verbose_name=_("product"), on_delete=models.PROTECT, related_name='returns')
    user=models.ForeignKey(User, verbose_name=_("user"), on_delete=models.PROTECT, related_name='returns')
    quantity=models.PositiveIntegerField(_("quantity"))
    create_dt=models.DateTimeField(_("date create"), auto_now_add=True)
    update_dt=models.DateTimeField(_("date update"), auto_now=True)
    class Meta:
        indexes = [models.Index(fields=['user', 'product']),
            models.Index(fields=['create_dt']),]

    def __str__(self):
        return f'{self.product.name} - {self.create_dt}'

class TransfersModel(models.Model):
    """مدل انتقال محصولات از انبار به فروشگاه
    
    ثبت انتقال کالاها بین انبار و فروشگاه."""
    product=models.ForeignKey('products.ProductModel', verbose_name=_("product"), on_delete=models.PROTECT, related_name='transfers')
    user=models.ForeignKey(User, verbose_name=_("user"), on_delete=models.PROTECT,related_name='transfers')
    quantity=models.PositiveIntegerField(_("quantity"))
    create_dt=models.DateTimeField(_("date create"), auto_now_add=True)
    update_dt=models.DateTimeField(_("date update"), auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'product']),
            models.Index(fields=['create_dt']),]

    def __str__(self):
        return self.product.name

class StoreModel(models.Model):
    """مدل موجودی فروشگاه
    
    مدیریت موجودی کالاها در فروشگاه."""
    product = models.ForeignKey('products.ProductModel',verbose_name=_("product"),
         on_delete=models.PROTECT,related_name='store_inventories')
    quantity = models.PositiveIntegerField(_("quantity"))
    is_available = models.BooleanField(_("is available"), default=False)
    create_dt = models.DateTimeField(_("date create"), auto_now_add=True)
    update_dt = models.DateTimeField(_("date update"), auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['product']),
            models.Index(fields=['create_dt']),]
        constraints=[models.UniqueConstraint(fields=['product'],name='unique_product_store')]

    def save(self, *args, **kwargs):
        """ذخیره‌سازی با محاسبه خودکار وضعیت موجودی"""
        self.is_available = self.quantity > 0
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'

class UpdatedInformationModel(models.Model):
    """مدل تاریخچه تغییرات سیستم
    
    ثبت تمام تغییرات در سیستم برای گزارش‌گیری و پیگیری."""
    ACTION_CHOICES = [
        ('CREATE', 'ایجاد'),
        ('UPDATE', 'ویرایش'),
        ('DELETE', 'حذف'),
        ('TRANSFER', 'انتقال'),
        ('SOLD', 'فروش'),
        ('WASTE', 'ضایعات'),
        ('RETURN', 'مرجوعی'),
    ]

    user=models.ForeignKey(User, verbose_name=_("user"), on_delete=models.PROTECT,related_name='updates')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    text=models.TextField(_("Updated information"))
    create_dt=models.DateTimeField(_("date create"), auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'create_dt']),
                   models.Index(fields=['action_type']),]

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.create_dt}"
