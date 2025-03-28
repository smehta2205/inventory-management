from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import InwardStock, Item, Stock, InwardOutwardConv, Vendor, OutwardStock, WastageStock, InwardBill
from .forms import ItemForm, LoginForm, RegisterForm, VendorForm, StockForm, OutwardStockForm, ConversionMetricForm, DepartmentForm, VendorSelectionForm, DepartmentSelectionForm, ConversionMetricFormWithoutId, InwardBillForm, WastageForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import F, Sum, Count, Case, When
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import date, timedelta

# Create your views here.
def item_info(request):
    items = Item.objects.all()
    vendors = Vendor.objects.all()
    # inwardstocks = InwardStock.objects.all()
    # outwardstocks = OutwardStock.objects.all()
    # total_wastage = WastageStock.objects.aggregate(Sum('wastage_amount'))
    # total_purchase = InwardStock.objects.annotate(difference=F('total_price') - F('gst_amount')).aggregate(total_difference=Sum('difference'))
    # total_gst = InwardStock.objects.aggregate(Sum('gst_amount'))
    # total_expenditure = OutwardStock.objects.aggregate(Sum('outward_spent_amount'))
    pending_payments = InwardBill.objects.aggregate(bool_col=Count(Case(When(is_paid=False, then=1))))
    results = Stock.objects.values('item_id__name').annotate(count=Sum('total_quantity'))
    item_names = [entry['item_id__name'] for entry in results]
    item_quantities = [entry['count'] for entry in results]
    items_json = json.dumps(item_names, cls=DjangoJSONEncoder)
    quantities_json = json.dumps(item_quantities, cls=DjangoJSONEncoder)
    total_stock_worth = (
        Stock.objects.filter(total_quantity__gt=0)
        .annotate(product=F('price') * F('quantity'))
        .aggregate(total_product=Sum('product'))
    )
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print(start_date)
    print(end_date)
    print(not start_date or not end_date)
    if not start_date or not end_date:
        # Default to 30 days ago and today if not provided
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        print(start_date)
        print(end_date)

    # Filter using these dates
    items = InwardStock.objects.all()
    inwardstocks = filter_items(items, start_date, end_date)
    items = OutwardStock.objects.all()
    outwardstocks = filter_items(items, start_date, end_date)
    items = WastageStock.objects.all()
    items = filter_items(items, start_date, end_date)
    total_wastage = items.aggregate(Sum('wastage_amount'))
    items = InwardStock.objects.all()    
    items = filter_items(items, start_date, end_date)
    total_purchase = items.annotate(difference=F('total_price') - F('gst_amount')).aggregate(total_difference=Sum('difference'))
    items = InwardStock.objects.all()
    items = filter_items(items, start_date, end_date)
    total_gst = items.aggregate(Sum('gst_amount'))
    items = OutwardStock.objects.all()
    items = filter_items(items, start_date, end_date)
    total_expense = items.aggregate(Sum('outward_spent_amount'))
    context = {
        'items': items,
        'vendors': vendors,
        'inwardstocks': inwardstocks,
        'outwardstocks': outwardstocks,
        'total_wastage' : total_wastage,
        'total_purchase' : total_purchase,
        "total_gst" : total_gst,
        "total_expenditure" : total_expense,
        "pending_payments":pending_payments,
        "items_json": items_json,  # JSON for pie chart labels
        "quantities_json": quantities_json,  # JSON for pie chart data
        "total_stock_worth": total_stock_worth,
        "default_start_date": start_date, 
        "default_end_date": end_date
        
    }
    # print(context)
    return render(request, 'inv_mng/item_info.html', context)
    

def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()  # Save the new item
            # Redirect to the "Add Conversion Metric" page for this item
            return redirect('add_conversion_metric_with_id', item_id=item.item_id)
    else:
        form = ItemForm()
    
    return render(request, 'inv_mng/add_item.html', {'form': form})

def add_vendor(request):
    if request.method == "POST":
        form = VendorForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('item_info')
    else:
        form = VendorForm()
    
    return render(request, 'inv_mng/add_vendor.html', {'form':form})


def inward_stock(request):
    StockFormSet = formset_factory(StockForm, extra=1)
    
    if request.method == "POST":
        vendor_form = VendorSelectionForm(request.POST)
        bill_form = InwardBillForm(request.POST, request.FILES)
        formset = StockFormSet(request.POST)

        
        if vendor_form.is_valid() and formset.is_valid() and bill_form.is_valid():
            vendor = vendor_form.cleaned_data['vendor']  # Get selected vendor
            bill = bill_form.save(commit=False)
            bill.vendor = vendor  # Assign vendor to the bill
            bill_id = bill.bill_id
            bill_image_path = bill.bill_image.name if bill.bill_image else None
            bill_paid_status = bill.is_paid
            bill_price_with_gst = bill.price_with_gst
            bill.save()
            print("Bill saved")

            for form in formset:
                if form.cleaned_data:
                    expiry_date = form.cleaned_data.pop('expiry_date')
                    gst = form.cleaned_data.pop('gst')
                    inward_stock_entry = form.save(commit=False)
                    inward_stock_entry.vendor = vendor  # Assign the selected vendor
                    inward_stock_entry.bill_id = bill_id
                    inward_stock_entry.bill_image_path = f"media/bills/{bill_image_path}" if bill_image_path else None
                    inward_stock_entry.is_paid = bill_paid_status
                    inward_stock_entry.price_with_gst = bill_price_with_gst
                    try:
                        conv_entry = InwardOutwardConv.objects.get(item_id=inward_stock_entry.item_id)
                        conversion_metric = conv_entry.outward_item_quantity
                    except InwardOutwardConv.DoesNotExist:
                        conversion_metric = 1  

                    if(inward_stock_entry.price_with_gst):
                        total_price_w_gst = inward_stock_entry.quantity*(inward_stock_entry.price/ (1+(gst/100)))
                        inward_stock_entry.gst_amount = (total_price_w_gst*gst/100)
                        inward_stock_entry.total_price = total_price_w_gst + inward_stock_entry.gst_amount


                    else:
                        total_price_wo_gst = inward_stock_entry.quantity*inward_stock_entry.price
                        inward_stock_entry.gst_amount = (total_price_wo_gst*gst/100)
                        inward_stock_entry.total_price = total_price_wo_gst + (total_price_wo_gst*gst/100)

                    # print(inward_stock_entry.total_price)
                    inward_stock_entry.save()
                    stock = Stock(
                        vendor=vendor,
                        item_id=inward_stock_entry.item_id,
                        quantity=inward_stock_entry.quantity,
                        price = inward_stock_entry.price,
                        expiry_date = expiry_date,
                        total_quantity = inward_stock_entry.quantity*conversion_metric
                    )
                    stock.save()
            return redirect('item_info')
    else:
        vendor_form = VendorSelectionForm()
        bill_form = InwardBillForm()
        formset = StockFormSet()

    return render(request, 'inv_mng/inward_stock.html', {'vendor_form': vendor_form, 'bill_form': bill_form, 'formset': formset})



def outward_stock(request):
    OutwardStockFormSet = formset_factory(OutwardStockForm, extra=1)  # Allows adding multiple forms
    formset = OutwardStockFormSet(request.POST or None)
    department_form = DepartmentSelectionForm(request.POST or None)  # Define department_form for both GET and POST requests

    if request.method == "POST":
        if department_form.is_valid() and formset.is_valid():
            department = department_form.cleaned_data['department']
            for form in formset:
                if form.cleaned_data:  # Check if the form has data
                    # Extract cleaned data from the form
                    item = form.cleaned_data['item']
                    stock_entry = form.cleaned_data['stock_entry']
                    quantity = form.cleaned_data['quantity']

                    # Example: Create a new OutwardStock record
                    if quantity <= stock_entry.total_quantity:
                        # Create an OutwardStock record
                        outward_stock = OutwardStock(
                            department=department,
                            item_id=item,
                            # stock_entry=stock_entry,
                            quantity=quantity,
                            outward_spent_amount = stock_entry.price * quantity
                        )
                        outward_stock.save()

                        # Deduct the quantity from the Stock entry
                        stock_entry.total_quantity -= quantity
                        stock_entry.save()

            return redirect('item_info')  # Redirect after successful submission
        else:
            print("Form errors:", formset.errors)
            print("Department form errors:", department_form.errors)

    return render(request, "inv_mng/outward_stock.html", {
        "department_form": department_form,
        "formset": formset,
    })    


def get_stock_entries(request):
    item_id = request.GET.get("item_id")
    print(item_id)
    items_data = []
    if not item_id:
        return JsonResponse({"items": []})

    # Use select_related to optimize vendor fetching
    stock_entries = Stock.objects.filter(item_id=item_id).select_related("vendor").values("id", "expiry_date", "vendor__vendor_name")

    items_data = []
    for item in stock_entries:
        try:
            items_data.append({
                "id": item["id"],  # Include ID for the frontend dropdown
                "expiry_date": item["expiry_date"].strftime("%Y-%m-%d"),
                "vendor_name": item["vendor__vendor_name"],
            })
        except Exception as e:
            print(f"Error processing stock entry {item}: {e}")

    print(f"Returning stock entries: {items_data}")  # Debugging log
    return JsonResponse({"items": items_data})



def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('item_info')
    else:
        form = DepartmentForm()
    
    return render(request, 'inv_mng/add_department.html', {'form':form})

def add_conversion_metric(request):
    if request.method == "POST":
        form = ConversionMetricForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data.get('item')  # Get the item from the form
            
            # Check if a conversion metric already exists for this item
            # print(len(InwardOutwardConv.objects.filter(item_id=item))==0)
            if (len(InwardOutwardConv.objects.filter(item_id=item))==0):
                messages.warning(request, 'A conversion metric for this item already exists!')
            else:
                # Save the new conversion metric
                conversion_metric = form.save(commit=False)
                conversion_metric.save()
                messages.success(request, 'Conversion metric added successfully!')
                return redirect('item_info')

    else:
        form = ConversionMetricForm()
    
    return render(request, 'inv_mng/add_conversion_metric_without_id.html', {'form':form})

def add_conversion_metric_with_id(request, item_id):
    item = get_object_or_404(Item, item_id=item_id)  # Get the item
    
    if request.method == "POST":
        form = ConversionMetricFormWithoutId(request.POST)
        if form.is_valid():
            conversion_metric = form.save(commit=False)
            conversion_metric.item_id = item  # Associate the conversion metric with the item
            conversion_metric.save()
            return redirect('item_info')  # Redirect to item info page after saving
    else:
        form = ConversionMetricFormWithoutId()
    
    return render(request, 'inv_mng/add_conversion_metric.html', {
        'form': form,
        'item': item,  # Pass the item to the template
    })

def signup_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')  # Redirect to login page
    else:
        form = RegisterForm()
    return render(request, "inv_mng/signup.html", {"form": form})

# User Login View
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('item_info')  # Redirect to home page
        messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "inv_mng/login.html", {"form": form})

# User Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def filter_items(items, start_date, end_date):
    if start_date:
        items = items.filter(date__gte=start_date)
    if end_date:
        items = items.filter(date__lte=end_date)
    return items

# @csrf_exempt  # Remove this if using the CSRF token in AJAX
def filter_items_inward(request):
    print("Inward")
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        print(start_date)
        items = InwardStock.objects.all()
        items = filter_items(items, start_date, end_date)
        items_data = []
    
        for item in items.values("item_id", "quantity", "vendor_id", "price", "total_price", "date"):
            item_rec = Item.objects.get(item_id=item['item_id'])
            item_name = item_rec.name
            
            # Get the related Vendor object (assuming Item has a ForeignKey to Vendor)
            vendor = Vendor.objects.get(id=item['vendor_id'])
            vendor_name = vendor.vendor_name
            items_data.append({
            "item_name": item_name,
            "quantity": item["quantity"], 
            "vendor_name": vendor_name,
            "price" : item["price"],
            "total_price" : item["total_price"],
            "date":item["date"]

            })
        
        return JsonResponse({"items": items_data})

    return JsonResponse({"error": "Invalid request"}, status=400)


def filter_items_outward(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        items = OutwardStock.objects.all()
        
        items = filter_items(items, start_date, end_date)
        items_data = []
    
        for item in items.values("item_id", "quantity", "department", "date"):
            item_rec = Item.objects.get(item_id=item['item_id'])
            item_name = item_rec.name
            
            # Get the related Vendor object (assuming Item has a ForeignKey to Vendor)
           
            items_data.append({
            "item_name": item_name,
            "quantity": item["quantity"], 
            "department": item["department"],
            "date":item["date"]

            })
        
        return JsonResponse({"items": items_data})

    return JsonResponse({"error": "Invalid request"}, status=400)

def get_gst(request):
    item_id = request.GET.get('item_id')
    print(item_id)
    try:
        item = Item.objects.get(item_id=item_id)
        print(item.gst)
        return JsonResponse({'gst': item.gst})  # Assuming `gst` is an attribute of `Item`
    except Item.DoesNotExist:
        return JsonResponse({'gst': 0})  
    

def log_wastage(request):
    WastageStockFormSet = formset_factory(WastageForm, extra=1)  # Allows adding multiple forms
    formset = WastageStockFormSet(request.POST or None)

    if request.method == "POST":
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:  # Check if the form has data
                    # Extract cleaned data from the form
                    item = form.cleaned_data['item']
                    stock_entry = form.cleaned_data['stock_entry']
                    quantity = form.cleaned_data['quantity']
                    
                    if quantity <= stock_entry.total_quantity:
                        # Create an OutwardStock record
                        wastage_stock = WastageStock(
                            item_id=item,
                            quantity=quantity,
                            wastage_amount = stock_entry.price * quantity,
                        )
                        wastage_stock.save()

                        # Deduct the quantity from the Stock entry
                        print(stock_entry.total_quantity)
                        stock_entry.total_quantity -= quantity
                        print(stock_entry.total_quantity)
                        stock_entry.save()

            return redirect('item_info')  # Redirect after successful submission
        else:
            print("Form errors:", formset.errors)

    return render(request, "inv_mng/log_wastage.html", {
        "formset": formset,
    })    


def get_total_wastage(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        print(start_date)
        items = WastageStock.objects.all()
        
        items = filter_items(items, start_date, end_date)
        total_wastage = items.aggregate(Sum('wastage_amount'))
        print("total_wastage")
        print(total_wastage)
        return JsonResponse({"total_wastage": total_wastage})
    # return JsonResponse({"error": "Invalid request"}, status=400)


def get_total_purchase(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        items = InwardStock.objects.all()
        
        items = filter_items(items, start_date, end_date)
        total_purchase = items.annotate(difference=F('total_price') - F('gst_amount')).aggregate(total_difference=Sum('difference'))
        print("total_purchase")
        print(total_purchase)
        return JsonResponse({"total_purchase": total_purchase})


def get_total_gst(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        items = InwardStock.objects.all()
        
        items = filter_items(items, start_date, end_date)
        total_gst = items.aggregate(Sum('gst_amount'))
        print("total_gst")
        print(total_gst)
        return JsonResponse({"total_gst": total_gst})
    

def get_total_expense(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        items = OutwardStock.objects.all()
        
        items = filter_items(items, start_date, end_date)
        total_expense = items.aggregate(Sum('outward_spent_amount'))
        print("total_expense")
        print(total_expense)
        return JsonResponse({"total_expense": total_expense})