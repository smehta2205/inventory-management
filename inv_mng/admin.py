from django.contrib import admin
from .models import Vendor, Item, Stock, InwardOutwardConv, Department, InwardStock, OutwardStock, InwardBill, WastageStock
# Register your models here.
admin.site.register(Vendor)
admin.site.register(Item)
admin.site.register(Stock)
admin.site.register(InwardOutwardConv)
admin.site.register(Department)
admin.site.register(InwardStock)
admin.site.register(OutwardStock)
admin.site.register(InwardBill)
admin.site.register(WastageStock)