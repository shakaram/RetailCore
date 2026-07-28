from django.utils import timezone
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
import os

def company_image_path(instance, filename):
    """تولید مسیر یکتا برای تصاویر شرکت"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('companies', str(timezone.now().year), str(timezone.now().month), filename)

def product_image_path(instance, filename):
    """تولید مسیر یکتا برای ذخیره تصاویر محصولات"""
    ext = filename.split('.')[-1]
    return f"ImageProducts/product_{instance.product.id}_{instance.product.name}.{ext}"

class CompanyModel(models.Model):
    """مدل شرکت‌های تولیدکننده محصولات
    اطلاعات شرکت‌هایی که محصولات را تولید می‌کنند."""
    name=models.CharField(_("name"), max_length=50)
    description=models.TextField(_("description"),null=True,blank=True,help_text=_('Company description'))
    image=models.ImageField(_("image company"), upload_to=company_image_path,null=True,blank=True)

    def __str__(self):
        return self.name

class CategoryModel(models.Model):
    """مدل دسته‌بندی محصولات (سلسله‌مراتبی)
    دسته‌بندی‌ها می‌توانند زیرمجموعه داشته باشند."""
    name=models.CharField(_("name"), max_length=150)
    subset=models.ForeignKey("self", verbose_name=_("subset"), on_delete=models.PROTECT,
                             null=True,blank=True,related_name='superset')
    
    class Meta:
        # ✅ اضافه کردن constraint برای یکتایی
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'subset'],
                name='unique_category_name_per_subset'
            )
        ]

    def __str__(self):
        return self.name

class ProductModel(models.Model):
    """مدل اصلی محصولات
    اطلاعات کامل محصول شامل نام، قیمت، موجودی، دسته‌بندی و شرکت سازنده."""
    name=models.CharField(_("name"), max_length=50,db_index=True)
    description=models.TextField(_("description")) #توضیحات
    price=models.PositiveIntegerField(_("price")) #قیمت
    quantity=models.PositiveIntegerField(_("quantity"), default=0, db_index=True) #تعداد کل
    category=models.ManyToManyField(CategoryModel, verbose_name=_("categories"),related_name='products')
    company=models.ForeignKey(CompanyModel, verbose_name=_("Company product"), on_delete=models.CASCADE, related_name='products', null=True)
    create_dt=models.DateTimeField(_("creation time"), auto_now_add=True, auto_now=False)
    is_available=models.BooleanField(_("is available"),default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['create_dt']),
            models.Index(fields=['quantity']),
            models.Index(fields=['is_available']),
        ]
        unique_together = [['name', 'company']]
    
    
    def update_inventory_fields(self):
        """به‌روزرسانی فیلدهای موجودی از منابع مختلف
        موجودی کل = انبار + فروشگاه - ضایعات"""
        from store.models import StoreModel, WarehouseModel, WasteModel

        warehouse_qty = WarehouseModel.objects.filter(product=self).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        
        store_qty = StoreModel.objects.filter(product=self).select_for_update().aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        
        waste_qty = WasteModel.objects.filter(product=self).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        
        # موجودی قابل فروش = انبار + فروشگاه - ضایعات
        self.quantity = warehouse_qty + store_qty - waste_qty
        self.is_available = self.quantity > 0
        
        super().save(update_fields=['quantity', 'is_available'])
        return self.quantity, self.is_available
    
    def __str__(self):
        return self.name


class ImageProductModel(models.Model):
    """عکس های محصول"""
    product=models.ForeignKey(ProductModel, verbose_name=_("product"), on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(_("images"), upload_to=product_image_path,null=True,blank=True)

    def __str__(self):
        return str(self.product)


class SoldModel(models.Model):
    """فاکتور"""
    user=models.ForeignKey(User, verbose_name=_("user"),on_delete=models.CASCADE,related_name='solds')
    update_dt=models.DateTimeField(_("date update"), auto_now=True)
    create_dt=models.DateTimeField(_(" date create"),auto_now_add=True)
    price=models.PositiveIntegerField(_("total price")) #قیمت فاکتور
    description=models.TextField(_("description"),null=True,blank=True)   #توضیحات اضافی
    
    def __str__(self):
        return f'{self.user}: {self.price}'


class SoldItemModel(models.Model):
    """ محصولات فروخته شده"""
    product=models.ForeignKey(ProductModel, verbose_name=_("product"),on_delete=models.CASCADE,related_name='sold_items')
    sold=models.ForeignKey(SoldModel, verbose_name=_("sold"),on_delete=models.CASCADE,related_name='sold_items')
    price=models.PositiveIntegerField(_("unit price"), help_text=_('Price of the product at the time of placing the order')) #قیمت کالا در لحظه ثبت سفارش
    total_price=models.PositiveIntegerField(_("total price"),help_text=_('We multiply the number of products and the unit price of the product.')) #جمع اخر بر اساس قسمت واحد و تعداد کالا
    quantity=models.PositiveIntegerField(_("quantity"), help_text=_('Number of products in the order')) # تعداد کالاها
    update_dt=models.DateTimeField(_("date"), auto_now=True)

    

    def __str__(self):
        return f'{self.product}: {self.quantity}'

