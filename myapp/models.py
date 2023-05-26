from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from django.utils.html import escape, mark_safe
from django.urls import path, include
# from storages.backends.firebase import FirebaseStorage
from django.conf import settings
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from django.core.files.storage import default_storage

# Khóa dự án Firebase
cred = credentials.Certificate('firebase/serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'carparkingsystem-8d374.appspot.com'
})


# # Tải tệp lên Cloud Storage
# bucket = storage.bucket()
# blob = bucket.blob('/image.jpg')
# blob.upload_from_filename('car_image/image.jpg')
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_customer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    avatar = models.ImageField(upload_to='avatar_images/', default='avatar_images/image.jpg')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.is_superuser:
            self.is_customer = False
            self.is_admin = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # quá chi là áp lực
        # Nếu user được đánh dấu là customer hoặc admin, thêm vào các group tương ứng
        if self.is_customer:
            group, created = Group.objects.get_or_create(name='Customer')
            if created:
                group.save(using='default')
            self.groups.add(group)
        if self.is_admin:
            group, created = Group.objects.get_or_create(name='Admin')
            if created:
                group.save(using='default')
            self.groups.add(group)
        # super(User, self).save(*args, **kwargs)        
    # class Meta:
    #     swappable = 'AUTH_USER_MODEL'


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    comment = models.TextField(max_length=5000, blank=True)
    card_number = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    reg_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id) +': '+self.first_name +' '+ self.last_name


class Car(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    car_model = models.CharField(max_length=100)
    car_color = models.CharField(max_length=100)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cars', to_field='id')
    reg_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='car_images/') # Không được null
    image_url = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)
    is_parking = models.BooleanField(default=False)

    def __str__(self):
        return self.license_plate

    def save(self, *args, **kwargs):
        if self.owner.user is not None:
            self.owner.user.is_customer = True
            self.owner.user.save()

        # bucket = storage.bucket()
        # if not setting.DEBUG:
        #     file_name = 'car_images/' + self.license_plate + '.jpg'
        #     with default_storage.open(self.image.name, 'rb') as image_file:
        #         blob = bucket.blob(file_name)
        #         blob.upload_from_file(image_file)
        #     self.image.name = file_name
        super(Car, self).save(*args, **kwargs)


class ParkingSlot(models.Model):
    PARKING_TYPES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large')
    )

    slot_number = models.IntegerField(unique=True)
    parking_type = models.CharField(max_length=1, choices=PARKING_TYPES)
    is_available = models.BooleanField(default=True)
    cost_per_hour = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_parking_type_display()} slot {self.slot_number}"


class ParkingRecord(models.Model):
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(blank=True, null=True)
    total_cost = models.IntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)


# class Reservation(models.Model):
#     parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     car = models.ForeignKey(Car, on_delete=models.CASCADE)
#     start_time = models.DateTimeField(default=timezone.now)
#     end_time = models.DateTimeField()
#
#     def __str__(self):
#         return f"Reservation for {self.user.username} on {self.start_time}"
class Invoice(models.Model):
    parking_record = models.ForeignKey(ParkingRecord, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    payment_date = models.DateField(null=True)
    parking_start_time = models.DateTimeField()
    parking_end_time = models.DateTimeField()
    parking_duration = models.DecimalField(max_digits=10, decimal_places=2)
    parking_fee = models.DecimalField(max_digits=10, decimal_places=2)
    extra_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=(
        ('direct', 'Direct Payment'),
        ('online', 'Online Payment'),
    ))
    payment_status = models.CharField(max_length=20, choices=(
        ('unpaid', 'Chưa thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy')
    ))
