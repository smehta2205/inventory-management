from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
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
    iw_unit = models.CharField(max_length=200)
    ow_unit = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.company})"


class Stock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    expiry_date = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()
    total_quantity = models.IntegerField(default=0)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.vendor} ({self.expiry_date})"


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

    def __str__(self):
        return f"{self.department_name}"
    

class OutwardStock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)

class InwardStock(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
