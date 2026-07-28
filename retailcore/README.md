
# 🏪 Retail Core - سیستم مدیریت خرده‌فروشی

یک API قدرتمند و جامع برای مدیریت فروشگاه، انبار، محصولات، فاکتورها و گزارش‌گیری با استفاده از Django REST Framework.

---

## ✨ ویژگی‌های برجسته

- **مدیریت کاربران و نقش‌ها**: احراز هویت امن با JWT و نقش‌های مختلف (مدیر، سوپروایزر، صندوقدار، فروشنده)
- **مدیریت محصولات**: ثبت، ویرایش، جستجو و فیلتر پیشرفته با قابلیت گروه‌بندی دسته‌بندی
- **مدیریت انبار و فروشگاه**: کنترل موجودی انبار و فروشگاه با قابلیت انتقال بین آن‌ها
- **فاکتورهای فروش**: ثبت فاکتور با محاسبه خودکار قیمت و مدیریت موجودی لحظه‌ای
- **ضایعات و مرجوعی**: مدیریت کالاهای معیوب و برگشتی با ثبت تاریخچه کامل
- **تاریخچه تغییرات**: ثبت تمام عملیات‌ها برای گزارش‌گیری و ممیزی
- **مستندسازی خودکار API**: با Swagger UI و ReDoc
- **امنیت**: احراز هویت مبتنی بر JWT با کوکی، کنترل دسترسی بر اساس نقش

---

## 🛠 تکنولوژی‌ها

- **Django 5.2.15** – فریم‌ورک اصلی
- **Django REST Framework 3.15.2** – ساخت API
- **auth-kit** – احراز هویت JWT با کوکی
- **drf-spectacular** – مستندسازی خودکار API
- **django-filter** – فیلتر و جستجوی پیشرفته
- **django-environ** – مدیریت متغیرهای محیطی
- **django-cleanup** – حذف خودکار فایل‌های مدیا
- **crum** – دریافت کاربر جاری در سیگنال‌ها
- **factory-boy** – ساخت داده‌های تست
- **coverage** – پوشش کد در تست‌ها

---

## 🚀 نصب و راه‌اندازی

### ۱. کلون کردن پروژه

```bash
git clone https://github.com/shakaram/retailcore.git
cd retailcore
۲. ایجاد و فعال‌سازی محیط مجازی
bash
# ویندوز
python -m venv venv
venv\Scripts\activate

# لینوکس/مک
python3 -m venv venv
source venv/bin/activate
۳. نصب وابستگی‌ها
bash
pip install -r requirements.txt
۴. تنظیم فایل .env
فایل .env.example را کپی کرده و به .env تغییر نام دهید:

bash
cp .env.example .env
سپس فایل .env را ویرایش کرده و اطلاعات خود را وارد کنید:

env
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
MEDIA_ROOT=media/
نکته: برای تولید SECRET_KEY می‌توانید از djecrety.ir استفاده کنید.

۵. اجرای مایگریشن‌ها
bash
python manage.py migrate
۶. ایجاد کاربر ادمین
bash
python manage.py createsuperuser
۷. اجرای سرور توسعه
bash
python manage.py runserver
پروژه روی آدرس http://localhost:8000 در دسترس خواهد بود.

👥 نقش‌های کاربری
نقش	توضیح
مدیر (Manager)	دسترسی کامل به تمام بخش‌های سیستم
سوپروایزر (Supervisor)	مدیریت محصولات، انبار، ضایعات و مرجوعی
صندوقدار (Cashier)	ثبت و مدیریت فاکتورهای فروش
فروشنده (Sales)	مشاهده محصولات، انبار و ضایعات
کاربر عادی (User)	مشاهده عمومی محصولات
📂 ساختار پروژه
text
retailcore/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── accounts/              # مدیریت کاربران
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── signals.py
│   └── tests/
├── products/              # مدیریت محصولات و فاکتورها
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── signals.py
│   └── tests/
├── store/                 # مدیریت انبار و فروشگاه
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── signals.py
│   └── tests/
└── retailcore/            # تنظیمات اصلی پروژه
    ├── settings.py
    ├── urls.py
    └── wsgi.py
📚 مستندات API
پس از اجرای پروژه، مستندات کامل API در آدرس‌های زیر قابل مشاهده است:

ابزار	آدرس
Swagger UI	http://localhost:8000/api/schema/swagger-ui/
ReDoc	http://localhost:8000/api/schema/redoc/
Schema JSON	http://localhost:8000/api/schema/
مثال درخواست
ورود به سیستم:

http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "123456"
}
پاسخ:

json
{
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "role": "manager",
    "username": "admin"
}
دریافت لیست محصولات:

http
GET /api/products/
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
🧪 تست‌ها
برای اجرای تست‌ها:

bash
# اجرای همه تست‌ها
python manage.py test

# اجرای تست‌های یک اپ خاص
python manage.py test accounts
python manage.py test products
python manage.py test store

# اجرای تست‌ها با نمایش جزئیات بیشتر
python manage.py test --verbosity=2

# اجرای تست‌ها با نگهداری دیتابیس
python manage.py test --keepdb

# بررسی پوشش کد (نیاز به coverage)
coverage run manage.py test
coverage report
🤝 مشارکت
پروژه را Fork کنید.

یک Branch جدید بسازید (git checkout -b feature/amazing-feature).

تغییرات خود را Commit کنید (git commit -m 'Add some amazing feature').

به Branch خود Push کنید (git push origin feature/amazing-feature).

یک Pull Request باز کنید.

📝 مجوز
این پروژه تحت مجوز MIT License منتشر شده است.

📧 ارتباط با من
گیت‌هاب: shakaram
ایمیل: m.shakram936@gmail.com
```
