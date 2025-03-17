from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render
from .models import InwardStock, Item, Stock, InwardOutwardConv, Vendor, OutwardStock
from .forms import ItemForm, VendorForm, StockForm, OutwardStockForm, ConversionMetricForm, DepartmentForm, VendorSelectionForm, DepartmentSelectionForm
from django.shortcuts import redirect


# Create your views here.
def item_info(request):
    items = Item.objects.all()
    vendors = Vendor.objects.all()
    context = {
        'items': items,
        'vendors': vendors
    }
    print(context)
    return render(request, 'inv_mng/item_info.html', context)
    

def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('item_info')
    else:
        form = ItemForm()
    
    return render(request, 'inv_mng/add_item.html', {'form':form})

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
        formset = StockFormSet(request.POST)
        
        if vendor_form.is_valid() and formset.is_valid():
            vendor = vendor_form.cleaned_data['vendor']  # Get selected vendor
            for form in formset:
                if form.cleaned_data:
                    stock_entry = form.save(commit=False)
                    stock_entry.vendor = vendor  # Assign the selected vendor

                    try:
                        conv_entry = InwardOutwardConv.objects.get(item_id=stock_entry.item_id)
                        conversion_metric = conv_entry.outward_item_quantity
                    except InwardOutwardConv.DoesNotExist:
                        conversion_metric = 1  

                    stock_entry.total_quantity = stock_entry.quantity * conversion_metric
                    stock_entry.save()
                    inward_entry = InwardStock(
                        # stock=stock_entry,  # Associate with stock entry
                        vendor=vendor,
                        item_id=stock_entry.item_id,
                        quantity=stock_entry.quantity
                    )
                    inward_entry.save()
            return redirect('item_info')
    else:
        vendor_form = VendorSelectionForm()
        formset = StockFormSet()

    return render(request, 'inv_mng/add_item.html', {'vendor_form': vendor_form, 'formset': formset})



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
                            quantity=quantity
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
    if item_id:
        stock_entries = Stock.objects.filter(item_id=item_id).values("id", "expiry_date")
        return JsonResponse(list(stock_entries), safe=False)
    return JsonResponse([], safe=False)



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

# def get_stock_entries(request):
#     item_id = request.GET.get('item_id')
#     if item_id:
#         stocks = Stock.objects.filter(item_id=item_id).values('id', 'expiry_date')  
#         return JsonResponse(list(stocks), safe=False)
#     return JsonResponse([], safe=False)

def add_conversion_metric(request):
    if request.method == "POST":
        form = ConversionMetricForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('item_info')
    else:
        form = ConversionMetricForm()
    
    return render(request, 'inv_mng/add_conversion_metric.html', {'form':form})