"""CarParkingSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from myapp import views
from django.contrib.auth import views as auth_views  # khong su dung
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required, user_passes_test
# from
# django.urls import handler404
from django.conf.urls import handler404, handler500
from allauth.account import views as account_views
from django.conf.urls import url
from  django.conf import settings
from django.views.static import serve
def is_admin(user):
    return user.is_authenticated and user.is_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin_dashboard/', views.admin_view, name='admin_dashboard'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('whyus/', views.whyus, name='whyus'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # name to call at views
    path('dashboard/', login_required(user_passes_test(is_admin)(views.dashboard)), name='dashboard'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('email_verification/', views.email_verification,
         name='success_message'),

    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('api/cars/', views.CarAPIList.as_view(), name='api_car_list'),
    path('cars/<int:pk>', views.CarDetailView.as_view(), name='api_car_detail'),
    path('car_list/', user_passes_test(is_admin)(views.showCarList), name='car_list'),
    path('car_list/<int:pk>', login_required(user_passes_test(is_admin)(views.CarDetailView.as_view())),
         name='car_view'),  # id_car
    path('create_car/', user_passes_test(is_admin)(views.CarCreateView.as_view()), name='create_car'),
    path('update_car/<int:pk>', user_passes_test(is_admin)(views.CarUpdateView.as_view()), name='car_update'),
    path('delete_car/<int:pk>', user_passes_test(is_admin)(views.CarDeleteView.as_view()), name='car_delete'),
    path('inactive_car/<int:pk>', user_passes_test(is_admin)(views.CarInactiveView.as_view()), name='inactive_car'),
    path('active_car/<int:pk>', user_passes_test(is_admin)(views.CarActiveView.as_view()), name='active_car'),

    path('customer_list/', user_passes_test(is_admin)(views.showCustomerList), name='customer_list'),
    path('customer_list/<int:pk>', user_passes_test(is_admin)(views.CustomerDetailView.as_view()),
         name='customer_view'),  # id_car
    path('create_customer/', user_passes_test(is_admin)(views.CustomerCreateView.as_view()), name='create_customer'),
    path('update_customer/<int:pk>',
         user_passes_test(is_admin)(views.CustomerUpdateView.as_view()), name='customer_update'),
    path('delete_customer/<int:pk>',
         user_passes_test(is_admin)(views.CustomerDeleteView.as_view()), name='customer_delete'),
    path('parking_slot/',
         views.showParkingLot, name='show_parking_lot'),
    path('create_parking_slot/',
         views.CreateParkingSlotView.as_view(), name='create_parking_lot'),

    # Parking Record
    path('parking_record/parking_record_list',
         user_passes_test(is_admin)(views.ParkingRecordListView), name='parking_record_list'),
    path('parking_record/create_parking_record',
         user_passes_test(is_admin)(views.CreateParkingRecordView.as_view()), name='create_parking_record'),
    path('parking_record/update_parking_record/<int:pk>',
         user_passes_test(is_admin)(views.ParkingRecordUpdateView.as_view()), name='update_parking_record'),
    path('parking_record/delete_parking_record/<int:pk>',
         user_passes_test(is_admin)(views.ParkingRecordDeleteView.as_view()), name='delete_parking_record'),
    path('parking_record_detail/<int:pk>/',
         views.ParkingRecordDetailView.as_view(), name='parking_record_detail'),
    path('parking-record/<int:pk>/',
         views.get_parking_record, name='get_parking_record'),
    path('show_parking_overview/', views.show_parking_overview, name='show_parking_overview'),
    path('exit/', user_passes_test(is_admin)(views.exit), name='exit'),
    # path('exit_by_user/', views.exitUserSide, name='exit_user'),
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('email_verification/<str:token>',
         views.email_verification, name='email_verification'),
    path('success_message/', views.show_success_signup, name='success_message'),
    # User Car for user
    path('user_car_list/', views.UserCarList.as_view(), name='user_car_list'),
    path('create_user_car/', views.CreateUserCarView.as_view(), name='create_user_car'),
    path('update_user_car/<int:pk>/', views.UserCarUpdateView.as_view(), name='update_user_car'),
    path('delete_user_car/<int:pk>/', views.UserCarDeleteView.as_view(), name='delete_user_car'),
    path('user_car_detail/<int:pk>/', views.UserCarReadView.as_view(), name='user_car_detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('save_profile/', views.save_profile, name='save_profile'),
    path('password-change/', views.password_change_view, name='password_change'),

    # User management:
    path('user_list/', user_passes_test(is_admin)(views.UserView.as_view()), name='user_list'),  # id_car
    path('active_user/<int:pk>', user_passes_test(is_admin)(views.UserActiveView.as_view()), name='active_user'),
    path('inactive_user/<int:pk>', user_passes_test(is_admin)(views.UserInactiveView.as_view()), name='inactive_user'),
    path('delete_user/<int:pk>', user_passes_test(is_admin)(views.UserDeleteView.as_view()), name='delete_user'),
    path('user_view/<int:pk>', user_passes_test(is_admin)(views.UserDetailView.as_view()), name='user_view'),

    #Đặt chỗ
    path('reserve_slot/', views.ReserveSlotView.as_view(), name='reserve_slot'),

    # parking history
    path('my_parking_history/', views.parking_history, name='parking_history'),

    # Invoices Admin Management:
    path('invoices/', user_passes_test(is_admin)(views.InvoiceListView.as_view()), name='invoice_list'),
    path('invoice/<int:pk>/', user_passes_test(is_admin)(views.InvoiceDetailView.as_view()), name='invoice_detail'),
    path('update_invoice/<int:pk>/', user_passes_test(is_admin)(views.InvoiceUpdateView.as_view()), name='update_invoice'),
    path('delete_invoice/<int:pk>/', user_passes_test(is_admin)(views.InvoiceDeleteView.as_view()), name='delete_invoice'),

    path('pay-invoice/<int:invoice_id>/', views.pay_invoice, name='pay_invoice'),
    # Invoices Of Customer:
    path('customer_invoices/', views.customer_invoices, name='customer_invoice_list'),
    path('customer_invoices/<int:pk>/', views.CustomerInvoiceDetail.as_view(), name='customer_invoice_detail'),
    # đường dẫn để in hóa đơn
    path('invoice-print/<int:invoice_id>/', views.invoice_print, name='invoice_print'),
    path('get_customer_info/',views.get_customer_info,name='get_customer_info'),
    path('direct_payment_view/',views.direct_payment_view,name='direct_payment_view'),
    path('online_payment_view/',views.online_payment_view,name='online_payment_view'),

    path('accounts/', include('allauth.urls'),name='provider_login_url'),
    path('accounts/google/login/', account_views.LoginView.as_view(template_name='account/socialaccount/google_login.html'), name='google_login'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'myapp.views.custom_page_not_found'
# handler500 = 'myapp.views.custom_server_error'
