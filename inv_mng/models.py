from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, AbstractUser

class Organization(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name}"

class CustomUser(AbstractUser):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    vendor_name = models.CharField(max_length=200)
    agency_name = models.CharField(max_length=200)
    gst_no = models.CharField(max_length=200)
    address = models.TextField()

    def __str__(self):
        return f"{self.agency_name} ({self.vendor_name})"

class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    gst = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=0)
    iw_unit = models.CharField(max_length=200)
    ow_unit = models.CharField(max_length=200)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f"{self.name} ({self.company})"


class Stock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    expiry_date = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()
    total_quantity = models.IntegerField(default=0)
    price = models.IntegerField()
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.item_id} {self.vendor} ({self.expiry_date})"


class InwardOutwardConv(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    inward_item_quantity = models.IntegerField()
    outward_item_quantity = models.IntegerField()


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=200)
    poc_name = models.CharField(max_length=200)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    poc_contact = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.department_name}"
    

class OutwardStock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    outward_spent_amount = models.IntegerField(default=0)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    

class InwardStock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)
    date = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    mrp = models.IntegerField(default=0)
    gst_amount = models.FloatField(default=0.0)
    bill_id = models.CharField(max_length=50, default='')  # Bill Number
    bill_image_path = models.CharField(max_length=200, default='')  # Bill Image location
    price_with_gst = models.BooleanField(default=False)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)


    
    def __str__(self):
        return f"{self.item_id}"


class InwardBill(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)  # Link to Vendor
    bill_id = models.CharField(max_length=50, unique=True)  # Bill Number
    bill_image = models.ImageField(upload_to='bills/')  # Invoice Upload
    is_paid = models.BooleanField(default=False)
    price_with_gst = models.BooleanField(default=False)
    bill_date = models.DateField(default=timezone.now)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f"Bill {self.bill_id} - {self.vendor.vendor_name}"
    

class WastageStock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    wastage_amount = models.IntegerField(default=0)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)




class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Notify a user (or admin)
    stock_entry = models.ForeignKey(Stock, on_delete=models.CASCADE)  # Link to a specific stock entry
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.stock_entry}"
