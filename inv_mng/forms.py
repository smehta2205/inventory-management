from django import forms
from django.contrib.admin import widgets
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import InwardBill, Item, Vendor, Stock, InwardOutwardConv, Department, OutwardStock, InwardStock
import datetime
from django.forms import BaseFormSet


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'company', 'location', 'gst', 'iw_unit', 'ow_unit', 'minimum_quantity')
        labels = {
            'name': 'Item name',
            'company': 'Company',
            'location': 'Physical location',
            'gst':'GST percentage',
            'iw_unit':'Purchase unit (inward)',
            'ow_unit':'Consumption unit (outward)',
            'minimum_quantity':'Minimum quantity for notification'
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


class BaseStockFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)

class StockForm(forms.ModelForm):
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gst = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )  #
    gst_amount = forms.DecimalField(
        max_digits=6, decimal_places=2, required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    total_price = forms.DecimalField(
        max_digits=10, decimal_places=2, required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 👈 extract user
        super(StockForm, self).__init__(*args, **kwargs)
        print("User")
        print(user)
        if user and hasattr(user, 'org'):
            self.fields['item_id'].queryset = Item.objects.filter(org=user.org)
        self.fields['item_id'].widget.attrs.update({'class': 'form-control select-item'})
        self.fields['expiry_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control quantity-field'})
        self.fields['price'].widget.attrs.update({'class': 'form-control price-field'})
        self.fields['gst'].widget.attrs.update({'class': 'form-control gst-field'})  # Make GST editable
        self.fields['gst_amount'].widget.attrs.update({'class': 'form-control gst-amount-field', 'readonly': 'readonly'})
        self.fields['total_price'].widget.attrs.update({'class': 'form-control net-amount-field', 'readonly': 'readonly'})

    class Meta:
        model = InwardStock
        fields = ('item_id', 'expiry_date', 'quantity', 'mrp', 'price', 'price_with_gst')
        labels = {
            'item_id': 'Item ID',
            'expiry_date': 'Expiry date',
            'quantity': 'Quantity',
            'price': 'Price',
            'mrp': 'MRP',
            'price_with_gst': 'Price with GST?',
            
        }

class VendorSelectionForm(forms.Form):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.none())  # default to empty

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        print(user)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'org'):
            self.fields['vendor'].queryset = Vendor.objects.filter(org=user.org)

class InwardBillForm(forms.ModelForm):
    class Meta:
        model = InwardBill
        fields = ['bill_id', 'bill_image', 'is_paid', 'price_with_gst', 'bill_date']
        widgets = {
            'bill_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk: 
            self.fields['bill_date'].initial = datetime.date.today()

class BaseOutwardStockFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)

        
class OutwardStockForm(forms.Form):
    # department = forms.ModelChoiceField(
    #     queryset=Department.objects.all(),
    #     label="Department",
    #     empty_label="Select a Department",
    #     required=True
    # )

    item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
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
        self.user = kwargs.pop('user', None)  # 👈 Get user from kwargs
        super().__init__(*args, **kwargs)

        # Filter items by user's organization
        if self.user:
            self.fields['item'].queryset = Item.objects.filter(org=self.user.org)


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

class ConversionMetricFormWithoutId(forms.ModelForm):
    class Meta:
        model = InwardOutwardConv
        fields = ('inward_item_quantity', 'outward_item_quantity')
        labels = {
            
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
    # department = forms.ModelChoiceField(queryset=Department.objects.filter(), label="Department", empty_label="Select a department")
    department = forms.ModelChoiceField(queryset=Department.objects.none(), label="Department", empty_label="Select a department")  # default to empty

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        print(user)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'org'):
            self.fields['department'].queryset = Department.objects.filter(org=user.org)


User = get_user_model()
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'org', 'password']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', "Passwords do not match.")

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class WastageForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        label="Item",
        empty_label="Select an Item",
        required=True
    )

    stock_entry = forms.ModelChoiceField(
        queryset=Stock.objects.none(),  # Initially empty
        label="Stock Entry",
        required=True
    )
    total_quantity = forms.IntegerField(
        label="Current total quantity", 
        required=False,
        widget=forms.NumberInput(attrs={'readonly': 'readonly'})  # Make it read-only
    )
    quantity = forms.IntegerField(label="Quantity")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # 👈 Get user from kwargs
        super().__init__(*args, **kwargs)

        # Filter items by user's organization
        if self.user:
            self.fields['item'].queryset = Item.objects.filter(org=self.user.org)
        
        # Check if the form is bound (i.e., has data)
        if self.is_bound:
            try:
                item_id = int(self.data.get(self.prefix + '-item'))  # Use the form's prefix to get the item ID
                self.fields['stock_entry'].queryset = Stock.objects.filter(item_id=item_id)
            except (ValueError, TypeError):
                self.fields['stock_entry'].queryset = Stock.objects.none()  # Fallback to empty queryset
        else:
            self.fields['stock_entry'].queryset = Stock.objects.none()
