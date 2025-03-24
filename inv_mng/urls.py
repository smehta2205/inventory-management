from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_info, name='item_info'),
    path('add_item', views.add_item, name='add_item'),
    path('add_vendor', views.add_vendor, name='add_vendor'),
    path('inward_stock', views.inward_stock, name='inward_stock'),
    path('outward_stock', views.outward_stock, name='outward_stock'),
    path('add_conversion_metric_with_id/<int:item_id>/', views.add_conversion_metric_with_id, name='add_conversion_metric_with_id'),
    path('add_conversion_metric', views.add_conversion_metric, name='add_conversion_metric'),
    path('add_department', views.add_department, name='add_department'),
    path('get_stock_entries/', views.get_stock_entries, name='get_stock_entries'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('filter_items/', views.filter_items, name='filter_items'),
    path('filter_items_outward/', views.filter_items_outward, name='filter_items_outward'), 
    path('get_gst/', views.get_gst, name='get_gst'),
    path('log_wastage/', views.log_wastage, name='log_wastage'),

    # path('get_items_from_stock/', views.get_items_from_stock, name='get_items_from_stock'),

]