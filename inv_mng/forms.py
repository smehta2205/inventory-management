from django import forms
from django.contrib.admin import widgets

from .models import Item, Vendor, Stock, InwardOutwardConv, Department, OutwardStock

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'company', 'location', 'iw_unit', 'ow_unit')
        labels = {
            'name': 'Item name',
            'company': 'Company',
            'location': 'Physical location',
            'iw_unit':'Inward unit',
            'ow_unit':'Outward unit'
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ('vendor_name', 'agency_name', 'gst_no', 'address')
        labels = {
            'vendor_name': 'Vendor name',
            'agency_name': 'Agency name',
            'gst_no': 'GST number',
            'address':'Address'
        }



class StockForm(forms.ModelForm):
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        self.fields['item_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['expiry_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Stock
        fields = ('item_id', 'expiry_date', 'quantity', 'price')
        labels = {
            'item_id': 'Item ID',
            'expiry_date': 'Expiry date',
            'quantity': 'Quantity',
            'price': 'Price'
        }

class VendorSelectionForm(forms.Form):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), label="Vendor", empty_label="Select a Vendor")


class OutwardStockForm(forms.Form):
    # department = forms.ModelChoiceField(
    #     queryset=Department.objects.all(),
    #     label="Department",
    #     empty_label="Select a Department",
    #     required=True
    # )

    item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        label="Item",
        empty_label="Select an Item",
        required=True
    )

    stock_entry = forms.ModelChoiceField(
        queryset=Stock.objects.none(),  # Initially empty
        label="Stock Entry",
        required=True
    )

    quantity = forms.IntegerField(label="Quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Check if the form is bound (i.e., has data)
        if self.is_bound:
            try:
                item_id = int(self.data.get(self.prefix + '-item'))  # Use the form's prefix to get the item ID
                self.fields['stock_entry'].queryset = Stock.objects.filter(item_id=item_id)
            except (ValueError, TypeError):
                self.fields['stock_entry'].queryset = Stock.objects.none()  # Fallback to empty queryset
        else:
            self.fields['stock_entry'].queryset = Stock.objects.none()

            
class ConversionMetricForm(forms.ModelForm):
    class Meta:
        model = InwardOutwardConv
        fields = ('item_id', 'inward_item_quantity', 'outward_item_quantity')
        labels = {
            'item_id' : 'Item ID',
            'inward_item_quantity' : 'Inward Quantity',
            'outward_item_quantity' : 'Outward Quantity',
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('department_name', 'poc_name', 'poc_contact')
        labels = {'department_name' : 'Department Name',
                'poc_name' : 'Person of contact', 
                'poc_contact' : 'Contact number of POC'
                }
        
class DepartmentSelectionForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label="Department", empty_label="Select a department")
