from jinja2 import Environment, PackageLoader
from django.middleware.csrf import get_token
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render

from .models import User
# from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.urls import path, include

from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse

from .forms import UserForm, CarForm, CarUpdateForm
from .forms import UpdateParkingRecordForm, ParkingRecordDetailForm

from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from datetime import timedelta
from django.core import serializers
from django.conf import settings
import os
from .models import User, ParkingSlot, Car, ParkingRecord, Invoice
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa  # Tao pdf hoa don
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CarSerializer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from jinja2 import Environment, FileSystemLoader

from .forms import CreateParkingRecordForm, MyRegistrationForm
from .forms import EmailVerificationForm
import smtplib
from django.views.generic import ListView, CreateView, UpdateView, FormView

from django.views import View
from django.core.mail import send_mail
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

from decimal import Decimal
from django.forms.models import model_to_dict

from django.conf.urls import handler404
from google.cloud import storage
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView

# Create your views here.

from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)
from google.cloud import storage

client = storage.Client.from_service_account_json('firebase/serviceAccount.json')

import pyrebase

config = {
    'apiKey': "AIzaSyA8KtGeNIWQHYx1dNMeaGSOl79yKE9XqIk",
    'authDomain': "carparkingsystem-8d374.firebaseapp.com",
    'databaseURL': "https://carparkingsystem-8d374-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "carparkingsystem-8d374",
    'storageBucket': "carparkingsystem-8d374.appspot.com",
    'messagingSenderId': "1005066593906",
    'appId': "1:1005066593906:web:82d2553f9b090e7b64c4eb",
    'measurementId': "G-3Z7W45QS83",
    'serviceAccount': 'firebase/serviceAccount.json',
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
storage = firebase.storage()


class SignupView(FormView):
    model = get_user_model()
    template_name = 'home/register.html'
    form_class = MyRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password1 = form.cleaned_data.get('password1')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        phone_number = form.cleaned_data.get('phone_number')
        card_number = form.cleaned_data.get('card_number')
        username = form.cleaned_data.get('username')
        # print(form.cleaned_data['username'])
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            card_number=card_number
        )
        user.is_active = False
        user.save()
        send_email_verification(user)
        print("valid")
        return redirect('success_message')

    def form_invalid(self, form):
        print("invalid")
        # print(form.cleaned_data['username'])
        # username_errors = form.errors.get('username')
        # if username_errors:
        #     username_error = username_errors[0]
        # else:
        #     username_error = None
        # print(username_error)
        return render(self.request, self.template_name, {'form': form})
    # def post(self, request, *args, **kwargs):
    #     form = self.get_form()
    #     if form.is_valid():
    #         email = request.POST.get('email')
    #         password1 = request.POST.get('password1')
    #         firstname = request.POST.get('first_name')
    #         lastname = request.POST.get('last_name')
    #         phone_number = request.POST.get('phone_number')
    #         card_number = request.POST.get('card_number')
    #         user = User.objects.create_user(
    #             email=email,
    #             username=email,
    #             password=password1,
    #         )
    #         user.is_active = False
    #         user.save()
    #         customer = Customer.objects.create(
    #             first_name=firstname,
    #             last_name=lastname,
    #             phone_number=phone_number,
    #             card_number=card_number,
    #             user=user
    #         )
    #         customer.save()
    #         send_email_verification(user)
    #
    #         print("valid")
    #         return redirect('success_message')
    #     else:
    #         print("invalid")
    #         return redirect('signup')


def send_email_verification(user):
    env = Environment(loader=PackageLoader('myapp', 'templates'))
    template = env.get_template('home/email_verification.html')
    verification_url = 'http://localhost:8000/email_verification/' + \
                       str(user.token)
    # form_action = 'http://localhost:8000/email_verification/', form_action=form_action
    message = template.render(
        user=user, verification_url=verification_url)
    msg = MIMEMultipart()
    msg['Subject'] = 'Activate your account'
    msg['From'] = 'nhom9qlda2223@gmail.com'  # nhập email của bạn vào đây
    msg['To'] = user.email
    part = MIMEText(message, 'html')
    msg.attach(part)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        # nhập mật khẩu email của bạn vào đây
        smtp.login('nhom9qlda2223@gmail.com', 'zpqxzpdcbzqgxefk')
        smtp.sendmail('nhom9qlda2223@gmail.com',
                      user.email, msg.as_string())


def email_verification(request, token):
    # csrf_token = get_token(request) ,'csrf_token':csrf_token
    form = EmailVerificationForm({'token': token})
    if form.is_valid():
        user = User.objects.get(token=token)
        user.is_active = True
        user.save()
        # login(request, user)
        return redirect('login')
    else:
        # token = get_token(request)
        return render(request, 'home/email_verification.html', {'form': form})


def show_success_signup(request):
    return render(request, 'home/success_message.html')


def google_login(request):
    # Lấy địa chỉ email từ dữ liệu trả về sau khi đăng nhập bằng Google
    email = request.GET.get('email')

    # Kiểm tra xem địa chỉ email đã tồn tại trong cơ sở dữ liệu hay chưa
    try:
        user = User.objects.get(email=email)
        redirect('google_signup')

    except User.DoesNotExist:
        redirect('google_signup')


#
# class GoogleCallbackView(OAuth2CallbackView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client
#     callback_url = '/accounts/google/login/callback/'
# def google_callback(request):
#     adapter = GoogleOAuth2Adapter(request)
#     callback_url = reverse('google_login_callback')
#     return redirect(adapter.get_authorize_url(request, callback_url))
# Địa chỉ email chưa tồn tại, hiển thị thông báo lỗi hoặc chuyển hướng đến trang đăng ký
# ...

def home(request):
    return render(request, 'home/home.html')


def about(request):
    return render(request, 'home/about.html')


def pricing(request):
    return render(request, 'home/pricing.html')


def whyus(request):
    return render(request, 'home/why.html')


def testimonial(request):
    return render(request, 'home/testimonial.html')


def custom_page_not_found(request, exception):
    # Xử lý yêu cầu 404 ở đây
    # Trả về HttpResponseNotFound hoặc render template 404 tùy ý
    return render(request, 'utils/404.html', status=404)


def custom_server_error(request):
    # Xử lý lỗi server ở đây
    # Trả về HttpResponseServerError hoặc render template 500 tùy ý
    return render(request, 'utils/500.html', status=500)


from django.http import HttpResponse


def login(request):
    if request.method == 'GET':
        return render(request, 'home/login.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember', False) == 'on'
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                if user.is_admin or user.is_superuser:
                    response = redirect('dashboard')
                elif user.is_customer:
                    response = redirect('home')
                if remember:
                    response.set_cookie('username', username, max_age=30 * 24 * 60 * 60)

            else:
                messages.error(request, 'Tài khoản chưa được kích hoạt')
                response = redirect('login')
        else:
            messages.error(request, 'Tài khoản hoặc mật khẩu không đúng')
            response = redirect('login')
        return response


def signup_view1(request):
    return render(request, "home/register.html")


@login_required
@user_passes_test(lambda u: u.is_admin)
def dashboard(request):
    return render(request, 'admin/dashboard.html')


def logout(request):
    auth_logout(request)  # Đăng xuất user sử dụng hàm logout của Django
    # Thực hiện các thao tác khác ở đây, ví dụ xoá cookie
    response = redirect('home')  # Chuyển hướng về trang home
    response.delete_cookie("my_cookie")  # Xoá cookie "my_cookie"
    return response


def is_admin(user):
    return user.groups.filter(name='Admin').exists()


@user_passes_test(is_admin)
def admin_view(request):
    # Code xử lý cho trang quản trị ở đây
    return render(request, 'admin_dashboard.html')


class CarAPIList(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    # template = ''


from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime


@api_view(['POST'])
def car_entry(request):
    license_plate = request.data.get('license_plate')
    # start_date = request.data.get('start_date')
    current_date = datetime.now().date()

    try:
        pr = ParkingRecord.objects.get(license_plate=license_plate)
        # car = Car.objects.get(license_plate=license_plate)
        if car.exit_time:
            # Xe đã ra khỏi bãi
            return Response({'message': 'Xe đã ra khỏi bãi.'})
        else:
            # Xe đang trong bãi
            return Response({'message': 'Xe đã có trong bãi.'})
    except Car.DoesNotExist:
        # Tạo mới một record cho xe
        car = Car(license_plate=license_plate, start_date=start_date)
        car.save()
        return Response({'message': 'Đỗ xe thành công.'})


from django.db.models import Q


def showCarList(request):
    orderType = request.GET.get('order-list')
    search_query = request.GET.get('search')
    status_filter = request.GET.get('status')  # Tham số lọc theo trạng thái
    cars = Car.objects.order_by('id').filter(status=1)

    if search_query:
        filtered_cars = cars.filter(
            Q(license_plate__icontains=search_query) |
            Q(car_model__icontains=search_query) |
            Q(car_color__icontains=search_query) |
            Q(owner__first_name__icontains=search_query) |
            Q(owner__last_name__icontains=search_query)
        )
    else:
        search_query = ''
        filtered_cars = cars
    if status_filter:
        # Lọc theo trạng thái
        if status_filter == 'activated':
            filtered_cars = filtered_cars.filter(is_active=True)
        elif status_filter == 'deactivated':
            filtered_cars = filtered_cars.filter(is_active=False)

    if orderType == '1':
        filtered_cars = filtered_cars.order_by('id')
    elif orderType == '2':
        filtered_cars = filtered_cars.order_by('car_model')
    elif orderType == '3':
        filtered_cars = filtered_cars.order_by('reg_date')
    elif orderType == '4':
        filtered_cars = filtered_cars.order_by('owner__last_name')
    paginator = Paginator(filtered_cars, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # context = {'cars': cars, 'page_obj': page_obj, 'orderType': orderType, 'search_query': search_query}  # Thêm context
    context = {'cars': page_obj,
               'page_obj': page_obj,
               'orderType': orderType,
               'search_query': search_query,
               'is_paginated': page_obj.has_other_pages(),
               'paginator': paginator,
               'status_filter': status_filter}
    return render(request, 'cars/car_list.html', context)


def car_update(request, id_car):
    car = get_object_or_404(Car, pk=id_car)
    print('car_update', car)
    return render(request, 'cars/car_update.html', {'my_car': car})


def car_delete(request, id_car):
    car = get_object_or_404(Car, pk=id_car)
    return render(request, 'cars/car_delete.html', {'my_car': car})


def car_detail(request, id_car):
    # car = Car.objects.filter(id=id_car)
    car = get_object_or_404(Car, pk=id_car)
    return render(request, 'cars/car_view.html', {'my_car': car})


class CarDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class CreateCarView(generics.CreateAPIView):
    serializer_class = CarSerializer
    queryset = Car.objects.all()

    def get(self, request):
        form = CarForm()
        return render(request, 'create_car.html', {'form': form})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Read
class CarInactiveView(BSModalUpdateView):
    model = Car
    template_name = 'cars/inactive_car.html'
    form_class = CarForm
    success_message = 'Success: Car was inactive.'
    success_url = reverse_lazy('car_list')

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        car = Car.objects.get(id=pk)
        car.is_active = False
        car.save()
        return redirect('car_list')


class CarActiveView(BSModalUpdateView):
    model = Car
    template_name = 'cars/active_car.html'
    form_class = CarForm
    success_message = 'Success: Car was active.'
    success_url = reverse_lazy('car_list')

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        car = Car.objects.get(id=pk)
        car.is_active = True
        car.save()
        return redirect('car_list')


# Template call in vehicles

from django.core.files.storage import default_storage
from .forms import CreateCarForm


class CarCreateView(BSModalCreateView):
    template_name = 'cars/create_car.html'
    form_class = CreateCarForm
    success_message = 'Success: Car was created.'
    success_url = reverse_lazy('car_list')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid:
            owner_name = request.POST.get('owner')
            start_index = owner_name.index(":") + 1
            end_index = owner_name.index(":", start_index)
            number = owner_name[start_index:end_index].strip()
            license_plate = request.POST.get('license_plate')
            car_model = request.POST.get('car_model')
            car_color = request.POST.get('car_color')
            image = request.FILES.get('image')

            # Tìm đối tượng khách hàng dựa trên tên
            try:
                owner = Customer.objects.get(id=int(number))
            except Customer.DoesNotExist:
                owner = None
            car = Car(
                license_plate=license_plate,
                car_model=car_model,
                car_color=car_color,
                owner=owner,
            )
            if image:
                # Lưu file ảnh vào hệ thống lưu trữ (storage)
                file_path = default_storage.save('car_images/' + image.name, image)

                # Gán đường dẫn của file ảnh vào thuộc tính image của car
                car.image = file_path

            car.save()
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['form'] = form
        return self.render_to_response(context)


class CarDetailView(BSModalReadView):
    model = Car
    template_name = 'cars/car_view.html'
    form_class = CarForm


class CarUpdateView(UpdateView):
    model = Car
    template_name = 'cars/car_update.html'
    form_class = CarForm
    success_message = 'Car update succesfully'
    success_url = reverse_lazy('car_list')

    def get(self, request, *args, **kwargs):
        car = self.get_object()
        context = {'form': CarUpdateForm(instance=car), 'car': car}
        return render(request, self.template_name, context)

    # def get_success_url(self):
    #     return reverse_lazy('car_list',kwargs={'pk': self.get_object().id})


class CarDeleteView(BSModalDeleteView):
    model = Car
    template_name = 'cars/car_delete.html'
    form_class = CarForm
    success_message = 'Car delete succesfully'
    success_url = reverse_lazy('car_list')


#
# def showCustomerList(request):
#     orderType = request.GET.get('order-list')
#     search_query = request.GET.get('search')
#     if not orderType:
#         orderType = 1
#     if not search_query:
#         search_query = ''
#     customers = Customer.objects.order_by('id')
#
#     if search_query:
#         customers = customers.filter(
#             Q(first_name__icontains=search_query) |
#             Q(last_name__icontains=search_query) |
#             Q(phone_number__icontains=search_query) |
#             Q(card_number__icontains=search_query)
#         )
#
#     if orderType == '1':
#         customers = customers.order_by('id')
#     elif orderType == '2':
#         customers = customers.order_by('first_name')
#     elif orderType == '3':
#         customers = customers.order_by('reg_date')
#
#     paginator = Paginator(customers, 5)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {'customers': page_obj, 'page_obj': page_obj, 'orderType': orderType,
#                'search_query': search_query, 'is_paginated': page_obj.has_other_pages(),
#                'paginator': paginator}  # Thêm context
#     return render(request, 'customers/customer_list.html', context)
#
#
# class CustomerCreateView(BSModalCreateView):
#     template_name = 'customers/create_customer.html'
#     form_class = CustomerForm
#     success_message = 'Success: Customer was created.'
#     success_url = reverse_lazy('customer_list')
#
#
# class CustomerDetailView(BSModalReadView):
#     model = Customer
#     template_name = 'customers/customer_view.html'
#     form_class = CustomerForm
#
#
# class CustomerUpdateView(BSModalUpdateView):
#     model = Customer
#     template_name = 'customers/customer_update.html'
#     form_class = CustomerForm
#     success_message = 'Customer update succesfully'
#     success_url = reverse_lazy('customer_list')
#     # def get_success_url(self):
#     #     return reverse_lazy('car_list',kwargs={'pk': self.get_object().id})
#
#
# class CustomerDeleteView(BSModalDeleteView):
#     model = Customer
#     template_name = 'customers/customer_delete.html'
#     form_class = CustomerForm
#     success_message = 'Customer delete succesfully'
#     success_url = reverse_lazy('customer_list')
#

def get_parking_record(request, pk):
    try:
        parking_slot = ParkingSlot.objects.get(pk=pk)
        if parking_slot.is_available:
            return JsonResponse({'error': 'This parking slot is empty.'})
        else:
            parking_record = parking_slot.parkingrecord_set.get(exit_time=None)
            data = {
                'parking_record_id': parking_record.id,
                'car': parking_record.car,
                'entry_time': parking_record.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'cost_per_hour': parking_slot.cost_per_hour,
            }
            return JsonResponse(data)
    except ParkingSlot.DoesNotExist:
        return JsonResponse({'error': 'This parking slot does not exist.'})


def showParkingLot(request):
    parkingslots = ParkingSlot.objects.all()
    customer = Customer.objects.get(user=request.user)
    cars = Car.objects.filter(owner=customer)
    context = {'parking_slots': parkingslots}
    return render(request, 'parkingslots/parking_slot.html', context)


# def save_parking_record(request):
#     # if request =="POST":


class CreateParkingSlotView(CreateView):
    template_name = 'create_parking_slot_view.html'
    form_class = CreateParkingRecordForm
    success_message = 'Create Parking Slot succesfully'
    success_url = 'parking_slot.html'


# Create Parking Record View

def ParkingRecordListView(request):
    orderType = request.GET.get('order-list')
    search_query = request.GET.get('search')
    parking_records = ParkingRecord.objects.order_by('id').all()

    if search_query:
        parking_records = parking_records.filter(
            Q(car__license_plate__icontains=search_query) |
            Q(total_cost__icontains=search_query)
        )
    else:
        search_query = ''
    if orderType == '1':
        parking_records = parking_records.order_by('id')
    elif orderType == '2':
        parking_records = parking_records.order_by('entry_time')
    elif orderType == '3':
        parking_records = parking_records.order_by('exit_time')
    elif orderType == '4':
        parking_records = parking_records.order_by('total_cost')
    elif orderType == '5':
        parking_records = parking_records.order_by('is_paid')

    paginator = Paginator(parking_records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'parking_records': page_obj, 'page_obj': page_obj, 'orderType': orderType, 'search_query': search_query,
               'is_paginated': page_obj.has_other_pages(),
               'paginator': paginator}  # Thêm context
    return render(request, 'parkingrecord/parking_record_list.html', context)


class CreateParkingRecordView(CreateView):
    cars = Car.objects.all()
    # parking_slots = ParkingSlot.objects.filter(is_available=True)
    template_name = 'parkingrecord/create_parking_record.html'
    form_class = CreateParkingRecordForm
    success_url = reverse_lazy('parking_record_list')

    def get(self, request):
        available_slots = ParkingSlot.objects.filter(is_available=True)
        context = {'cars': self.cars, 'parking_slots': available_slots}
        return render(request, self.template_name, context)

    # def get ----

    def post(self, request):
        # Lấy thông tin car và parking_slot theo id
        car_id = request.POST.get('car_id')
        parking_slot_id = request.POST.get('parking_slot_id')
        car = Car.objects.get(id=car_id)
        parking_slot = ParkingSlot.objects.get(id=parking_slot_id)

        # Set trạng thái của parking_slot là không còn trống
        parking_slot.is_available = False
        print("OK")
        parking_slot.save()

        # Tạo mới parking record cho car và parking_slot đã chọn
        parking_record = ParkingRecord.objects.create(
            parking_slot=parking_slot,
            car_number=car.license_plate,
            entry_time=timezone.now(),
            car=car,
            total_cost=0,
            is_paid=False
        )

        return redirect('parking_record_list')

    def form_valid(self, form):
        car = form.cleaned_data['car']
        parking_slot = form.cleaned_data['parking_slot']

        # Set trạng thái của parking_slot là không còn trống
        parking_slot.is_available = False
        parking_slot.save()

        # Tạo mới parking record cho car và parking_slot đã chọn
        parking_record = ParkingRecord.objects.create(
            parking_slot=parking_slot,
            car_number=car.license_plate,
            entry_time=timezone.now(),
            car=car,
            total_cost=0,
            is_paid=False
        )

        parking_record.save()

        return super().form_valid(form)


class ParkingRecordDetailView(BSModalReadView):
    model = ParkingRecord
    template_name = 'parkingrecord/parking_record_detail.html'
    form_class = ParkingRecordDetailForm


class ParkingRecordUpdateView(BSModalUpdateView):
    model = ParkingRecord
    template_name = 'parkingrecord/update_parking_record.html'
    form_class = UpdateParkingRecordForm
    success_message = 'Parking record update successfully'
    success_url = reverse_lazy('parking_record_list')


class ParkingRecordDeleteView(BSModalDeleteView):
    model = ParkingRecord
    template_name = 'parkingrecord/delete_parking_record.html'
    # form_class = ParkingRecordDetailForm
    success_message = 'Parking record delete succesfully'
    success_url = reverse_lazy('parking_record_list')

    def delete(self, request, *args, **kwargs):
        # Lấy bản ghi ParkingRecord cần xóa
        parking_record = self.get_object()
        print(parking_record)
        # Set is_available của parking_slot của ParkingRecord thành true
        parking_record.parking_slot.is_available = True
        parking_record.parking_slot.save()
        # Xóa bản ghi ParkingRecord
        return super().delete(request, *args, **kwargs)


def show_parking_overview(request):
    parking_slots = ParkingSlot.objects.all()
    cars = None
    user = request.user
    try:
        if user.is_active:
            # customer = Customer.objects.get(user=user)
            cars = Car.objects.filter(owner=user, is_parking=False, is_active=True) if user else []

    except user.DoesNotExist:
        # Handle the case when the user is not a customer
        pass
    return render(request, 'parking_overview.html', {'parking_slots': parking_slots, 'cars': cars})


def display_invoice(request, parking_record_id):
    try:
        parking_record = ParkingRecord.objects.get(id=parking_record_id)
        invoice = Invoice.objects.create(parking_record=parking_record, total_cost=parking_record.total_cost)
        # do any additional processing of the invoice object here, such as adding line items
        return render(request, 'invoice.html', {'invoice': invoice})
    except ParkingRecord.DoesNotExist:
        messages.error(request, 'No parking record found for this parking slot.')
        return redirect(reverse('show_parking_overview'))


def exit(request):
    if request.method == 'POST':
        try:
            parking_slot_pk = request.POST.get('parking_slot_pk')
            # Do something with the parking_slot_pk, for example:
            parking_slot = ParkingSlot.objects.get(pk=parking_slot_pk)

            # Get parking _record
            parking_record = ParkingRecord.objects.get(parking_slot=parking_slot, exit_time=None)
            parking_record.exit_time = timezone.now()
            timedelta = parking_record.exit_time - parking_record.entry_time
            total_seconds = timedelta.total_seconds()
            rounded_hours = Decimal(total_seconds / 3600)

            parking_record.total_cost = rounded_hours * parking_slot.cost_per_hour
            parking_record.save()

            parking_slot.is_available = True
            # parking_slot.exit_time = timezone.now()
            parking_slot.save()

            car = Car.objects.get(id=parking_record.car.id)
            print(car.id)
            car.is_parking = False
            car.save()
            customer = Customer.objects.filter(cars__id=car.id).first()
            # invoice = Invoice.objects.create(customer=customer, parking_record= parking_record ,entry_time= parking_record.entry_time, exit_time=parking_record.exit_time, total_amount=total_amount)
            invoice = Invoice.objects.create(
                parking_record=parking_record,
                customer=customer,
                invoice_number="INV-" + str(parking_record.id),
                invoice_date=timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=7),  # Set payment deadline to 7 days from now
                parking_start_time=parking_record.entry_time,
                parking_end_time=parking_record.exit_time,
                parking_duration=rounded_hours,
                parking_fee=parking_record.total_cost,
                extra_fee=0,
                total_fee=parking_record.total_cost + 0,
                payment_status="unpaid"
            )
            messages.success(request, 'Cập nhật trạng thái chỗ đậu xe thành công.')
            # Render invoice modal
            invoice_dict = model_to_dict(invoice)
            context = {
                'invoice': invoice_dict,
                'parking_record': parking_record,
            }
            return render(request, 'invoice/invoice_modal.html', context)
            # return redirect('display_invoice', parking_record_id=parking_record.id)

        except ParkingRecord.DoesNotExist:
            # Handle the case where there is no matching ParkingRecord object
            messages.error(request, 'No parking record found for this parking slot.')
            return redirect(reverse('show_parking_overview'))


class UserCarList(ListView):
    model = Car
    template_name = 'user_car/user_car_list.html'
    context_object_name = 'cars'

    def get(self, request):
        orderType = request.GET.get('order-list')
        search_query = request.GET.get('search')
        # customer = Customer.objects.get(user=self.request.user)
        cars = Car.objects.filter(owner=self.request.user)

        if search_query:
            cars = cars.filter(
                Q(license_plate__icontains=search_query) |
                Q(car_model__icontains=search_query) |
                Q(car_color__icontains=search_query)
            )
        else:
            search_query = ''

        if orderType == '1':
            cars = cars.order_by('id')
        elif orderType == '2':
            cars = cars.order_by('car_model')
        elif orderType == '3':
            cars = cars.order_by('reg_date')
        paginator = Paginator(cars, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'cars': page_obj, 'page_obj': page_obj, 'orderType': orderType,
                   'search_query': search_query, 'is_paginated': page_obj.has_other_pages(),
                   'paginator': paginator}  # Thêm context
        return render(request, self.template_name, context)


from .forms import CreateUserCarForm
from uuid import uuid4


class CreateUserCarView(BSModalCreateView):
    model = Car
    form_class = CreateUserCarForm
    template_name = 'user_car/create_user_car.html'
    success_url = reverse_lazy('user_car_list')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = self.request.user
            license_plate = form.cleaned_data['license_plate']
            car_model = form.cleaned_data['car_model']
            car_color = form.cleaned_data['car_color']
            image = form.cleaned_data['image']
            print("image: ", image)
            if image is not None:
                # Tạo tên file mới ngẫu nhiên
                filename = f"{license_plate}-{uuid4().hex}.jpg"

                # Lưu file vào bucket trên Firebase Storage
                bucket_name = "carparkingsystem-8d374.appspot.com"  # not include gs://
                bucket = client.bucket(bucket_name)
                folder_path = "car_images/"
                blob = bucket.blob(folder_path + filename)
                blob.upload_from_string(image.read(), content_type='image/jpeg')

                # Lấy URL của ảnh từ Firebase Storage
                image_url = blob.public_url

                # Tạo instance mới để lưu vào database
                car = Car(
                    license_plate=license_plate,
                    car_model=car_model,
                    car_color=car_color,
                    owner=user,
                    image=image,
                    image_url=image_url,
                    status=1
                )
                car.save()

            # Process the form data and return JSON response
            return redirect('user_car_list')
        else:
            # Handle invalid form data and return JSON response
            return redirect('create_user_car')


from .forms import UserCarModelForm, UpdateUserCarForm


# Update
class UserCarUpdateView(BSModalUpdateView):
    model = Car
    template_name = 'user_car/update_user_car.html'
    form_class = UpdateUserCarForm
    success_message = 'Success: Car was updated.'
    success_url = reverse_lazy('user_car_list')

    def get_object(self, queryset=None):
        """Retrieve the object to be updated."""
        return self.get_queryset().get(pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            # Process the valid form data and return JSON response
            license_plate = form.cleaned_data['license_plate']
            car_model = form.cleaned_data['car_model']
            car_color = form.cleaned_data['car_color']
            try:
                image = form.cleaned_data['image']
                if image:
                    # Tạo tên file mới ngẫu nhiên
                    filename = f"{license_plate}-{uuid4().hex}.jpg"

                    # Lưu file vào bucket trên Firebase Storage
                    bucket_name = "carparkingsystem-8d374.appspot.com"  # not include gs://
                    bucket = client.bucket(bucket_name)
                    folder_path = "car_images/"
                    blob = bucket.blob(folder_path + filename)
                    blob.upload_from_string(image.read(), content_type='image/jpeg')

                    # Lấy URL của ảnh từ Firebase Storage
                    image_url = blob.public_url
                    print(image_url)
                    # Tạo instance mới để lưu vào database
                    self.object.image.name = filename
                    self.object.image_url = image_url
            except KeyError:
                image = None
                image_url = None
                self.object.image = image
                self.object.image_url = image_url

            # Cập nhật các thông tin khác của instance trong database
            self.object.license_plate = license_plate
            self.object.car_model = car_model
            self.object.car_color = car_color
            self.object.owner = self.request.user
            self.object.is_active = False
            self.object.save()
            return redirect('user_car_list')
        else:
            return self.render_to_response(self.get_context_data(form=form))
            # return redirect(reverse('update_user_car', kwargs={'pk': self.kwargs['pk']}))


# Read
class UserCarReadView(BSModalReadView):
    model = Car
    form_class = UserCarModelForm
    template_name = 'user_car/user_car_detail.html'


# Delete
class UserCarDeleteView(BSModalDeleteView):
    model = Car
    template_name = 'user_car/delete_user_car.html'
    success_message = 'Success: Car was deleted.'
    success_url = reverse_lazy('user_car_list')


from django.core.exceptions import ObjectDoesNotExist


class ProfileView(ListView):
    model = User
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        card_number = request.POST.get('card_number')
        location = request.POST.get('location')

        if not first_name or not last_name or not phone_number or not card_number or not location:
            return render(request, 'profile.html', {'error': 'All fields are required'})

        if len(phone_number) != 10 or not phone_number.isdigit():
            return render(request, 'profile.html', {'error': 'Invalid phone number'})

        if len(card_number) != 12 or not card_number.isdigit():
            return render(request, 'profile.html', {'error': 'Invalid card number'})

        # Check if phone number or card number already exists for another user
        if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
            return render(request, 'profile.html', {'error': 'Phone number is already taken'})

        if User.objects.filter(card_number=card_number).exclude(id=user.id).exists():
            return render(request, 'profile.html', {'error': 'Card number is already taken'})

        # Update user's profile here

        return render(request, 'profile.html', {'success': 'Profile updated successfully'})


def save_profile(request):
    if request.method == "POST":
        my_user = request.user
        if my_user.is_admin:  # TRường hợp 1 là admin không có customer
            my_user.first_name = request.POST.get('first_name')
            my_user.last_name = request.POST.get('last_name')
            my_user.username = request.POST.get('username')
            my_user.email = request.POST.get('email')
            avatar = request.FILES.get('avatar')
            if avatar:
                my_user.avatar = avatar
            my_user.save()

        else:
            my_user.first_name = request.POST.get('first_name')
            my_user.last_name = request.POST.get('last_name')
            my_user.phone_number = request.POST.get('phone_number')
            my_user.card_number = request.POST.get('card_number')
            my_user.location = request.POST.get('location')
            avatar = request.FILES.get('avatar')
            my_user.username = request.POST.get('username')
            if avatar:
                my_user.avatar = avatar
            if my_user.reg_date is None:
                my_user.reg_date = timezone.now()
            my_user.save()
            messages.success(request, 'Your profile has been updated successfully.')

        return redirect('profile')


from django.contrib.auth.forms import PasswordChangeForm


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('login')  # Replace 'profile' with the appropriate URL name for the user's profile page
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'home/change_password.html', {'form': form})


class UserView(ListView):
    model = User
    template_name = 'user_management/user_list.html'

    def get(self, request):
        users = User.objects.filter(is_customer=True)
        orderType = request.GET.get('order-list')
        search_query = request.GET.get('search')
        if orderType is None:
            orderType = 1
        if orderType == '1':
            users = users.order_by('id')
        elif orderType == '2':
            users = users.order_by('username')
        elif orderType == '3':
            users = users.order_by('date_joined')
        elif orderType == '4':
            users = users.filter(is_active=True)
        elif orderType == '5':
            users = users.filter(is_active=False)
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query)
            )
        else:
            search_query = ''

        paginator = Paginator(users, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'users': page_obj, 'page_obj': page_obj, 'orderType': orderType, 'search_query': search_query,
                   'is_paginated': page_obj.has_other_pages(),
                   'paginator': paginator}  # Thêm context
        return render(request, self.template_name, context)


class UserActiveView(BSModalUpdateView):
    model = User
    template_name = 'user_management/active_user.html'
    form_class = UserForm
    success_message = 'Success: User was active.'
    success_url = reverse_lazy('user_list')

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        user = User.objects.get(id=pk)
        user.is_active = True
        user.save()
        return redirect('user_list')


# Read
class UserInactiveView(BSModalUpdateView):
    model = User
    template_name = 'user_management/inactive_user.html'
    form_class = UserForm
    success_message = 'Success: User was inactive.'
    success_url = reverse_lazy('user_list')

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        user = User.objects.get(id=pk)
        user.is_active = False
        user.save()
        return redirect('user_list')


# Delete
class UserDeleteView(BSModalDeleteView):
    model = User
    template_name = 'user_management/delete_user.html'
    success_message = 'Success: User was deleted.'
    success_url = reverse_lazy('user_list')


class UserDetailView(BSModalDeleteView):
    model = User
    template_name = 'user_management/user_detail.html'
    success_message = 'Success: User was deleted.'
    success_url = reverse_lazy('user_list')


class ReserveSlotView(BSModalReadView):
    def post(self, request):
        car_id = request.POST.get('car')
        slot_number = request.POST.get('slot_number')
        car = Car.objects.get(id=car_id)
        slot = ParkingSlot.objects.get(slot_number=slot_number)

        parkingRecord = ParkingRecord.objects.create(
            car=car,
            parking_slot=slot,
            entry_time=datetime.now(),
            total_cost=0
        )
        parkingRecord.save()
        slot.is_available = False
        slot.save()
        car.is_parking = True
        car.save()
        return redirect('show_parking_overview')


## Hiển thị lịch sử:
def parking_history(request):
    try:
        # customer = Customer.objects.get(user=request.user)
        cars = request.user.cars.all()
        parking_records = ParkingRecord.objects.filter(car__in=cars)

        orderType = request.GET.get('order-list')
        search_query = request.GET.get('search')

        if orderType == '1':
            parking_records = parking_records.order_by('id')
        elif orderType == '2':
            parking_records = parking_records.order_by('entry_time')
        elif orderType == '3':
            parking_records = parking_records.order_by('exit_time')
        elif orderType == '4':
            parking_records = parking_records.order_by('total_cost')
        elif orderType == '5':
            parking_records = parking_records.order_by('is_paid')

        if search_query:
            parking_records = parking_records.filter(
                Q(car__license_plate__icontains=search_query) |
                Q(total_cost__icontains=search_query)
            )
        else:
            search_query = ''
        paginator = Paginator(parking_records, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'parking_records': page_obj, 'page_obj': page_obj, 'orderType': orderType,
                   'search_query': search_query,
                   'is_paginated': page_obj.has_other_pages(),
                   'paginator': paginator}  # Thêm context
        return render(request, 'user_parkinglot/parking_history_list.html', context)
    except ObjectDoesNotExist:
        customer = None
        messages.error(request, "Không tìm thấy khách hàng")
        return redirect('profile')


## Xử lý phương thức thanh toán:

def pay_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)

    if request.method == 'POST':
        # Process the form data
        amount_paid = float(request.POST['amount_paid'])
        invoice.amount_paid = amount_paid
        invoice.save()

        return redirect('invoice_detail', invoice_id=invoice_id)

    # Render the template with the invoice object
    return render(request, 'pay_invoice.html', {'invoice': invoice})


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoice/invoice_detail.html'  # tên template hiển thị
    context_object_name = 'invoice'  # tên biến context để truyền dữ liệu sang template


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoice/invoice_list.html'  # tên template hiển thị
    context_object_name = 'invoices'  # tên biến context để truyền dữ liệu sang template

    def get(self, request):
        orderType = request.GET.get('order-list')
        search_query = request.GET.get('search')
        if search_query is None:
            search_query = ''
        invoices = Invoice.objects.all()

        if search_query:
            filtered_invoices = invoices.filter(
                Q(invoice_number__icontains=search_query) |
                Q(customer__first_name__icontains=search_query) |
                Q(customer__last_name__icontains=search_query)
            )
        else:
            filtered_invoices = invoices

        if orderType == '1':
            filtered_invoices = filtered_invoices.order_by('id')
        elif orderType == '2':
            filtered_invoices = filtered_invoices.order_by('customer__first_name')
        elif orderType == '3':
            filtered_invoices = filtered_invoices.order_by('payment_date')
        elif orderType == '4':
            filtered_invoices = filtered_invoices.order_by('total_fee')
        print("invoices", filtered_invoices)
        paginator = Paginator(filtered_invoices, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'invoices': page_obj, 'page_obj': page_obj, 'orderType': orderType,
                   'search_query': search_query, 'is_paginated': page_obj.has_other_pages(),
                   'paginator': paginator}  # Thêm context
        return render(request, self.template_name, context)


def customer_invoices(request):
    # customer = Customer.objects.get(user=request.user)
    cus_name = str(request.user.first_name) + str(request.user.last_name)
    customer_invoices = Invoice.objects.filter(customer_name=cus_name)

    orderType = request.GET.get('order-list')
    search_query = request.GET.get('search')
    if search_query is None:
        search_query = ''

    if search_query:
        filtered_invoices = customer_invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(customer__last_name__icontains=search_query)
        )
    else:
        filtered_invoices = customer_invoices

    if orderType == '1':
        filtered_invoices = filtered_invoices.order_by('id')
    elif orderType == '2':
        filtered_invoices = filtered_invoices.order_by('customer__first_name')
    elif orderType == '3':
        filtered_invoices = filtered_invoices.order_by('payment_date')
    elif orderType == '4':
        filtered_invoices = filtered_invoices.order_by('total_fee')
    paginator = Paginator(filtered_invoices, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'customer_invoices': page_obj, 'page_obj': page_obj, 'orderType': orderType,
               'search_query': search_query, 'is_paginated': page_obj.has_other_pages(),
               'paginator': paginator}  # Thêm context

    return render(request, 'invoice/customer_invoice_list.html', context)


class CustomerInvoiceDetail(DetailView):
    model = Invoice
    template_name = 'invoice/invoice_detail.html'  # tên template hiển thị
    context_object_name = 'invoice'  # tên biến context để truyền dữ liệu sang template


from .forms import UpdateInvoiceForm


class InvoiceUpdateView(BSModalUpdateView):
    model = Invoice
    template_name = 'invoice/update_invoice.html'
    form_class = UpdateInvoiceForm
    success_message = 'Success: Đã cập nhật invoice.'
    success_url = reverse_lazy('invoice_list')


class InvoiceDeleteView(BSModalDeleteView):
    model = Invoice
    template_name = 'invoice/delete_invoice.html'
    success_message = 'Success: Invoice was deleted.'
    success_url = reverse_lazy('invoice_list')


from django.template.loader import render_to_string
from weasyprint import HTML


def invoice_print(request, invoice_id):
    # Lấy đối tượng hóa đơn cần in
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    # Render template thành một đối tượng HTML
    html_string = render_to_string('invoice/invoice_detail_content.html', {'invoice': invoice})

    # Tạo đối tượng HTML từ chuỗi HTML trên
    html = HTML(string=html_string)

    # Tạo file PDF từ đối tượng HTML
    pdf_file = html.write_pdf()

    # Trả về response là file PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    return response


def get_customer_info(request, pk):
    if request.method == "POST":
        parkingSlot = ParkingSlot.objects.get(id=pk)
        parkingRecord = ParkingRecord.objects.get(parkingSlot=parkingSlot, exit_time=None)
        customer = parkingRecord.car.owner
        # Chuẩn bị dữ liệu thông tin khách hàng
        customer_info = {
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone
        }

        # Trả về thông tin khách hàng dưới dạng JSON
        return JsonResponse({'customer': customer_info})


def direct_payment_view(request):
    if request.method == "POST":
        try:
            parking_slot_pk = request.POST.get('parking_slot_id')
            # Do something with the parking_slot_pk, for example:
            parking_slot = ParkingSlot.objects.get(pk=parking_slot_pk)

            # Get parking _record
            parking_record = ParkingRecord.objects.get(parking_slot=parking_slot, exit_time=None)
            parking_record.exit_time = timezone.now()
            timedelta = parking_record.exit_time - parking_record.entry_time
            total_seconds = timedelta.total_seconds()
            rounded_hours = Decimal(total_seconds / 3600)

            parking_record.total_cost = rounded_hours * parking_slot.cost_per_hour
            parking_record.is_paid = True
            parking_record.save()

            parking_slot.is_available = True
            parking_slot.save()

            car = Car.objects.get(id=parking_record.car.id)
            print(car.id)
            car.is_parking = False
            car.save()
            customer = Customer.objects.filter(cars__id=car.id).first()
            invoice = Invoice.objects.create(
                parking_record=parking_record,
                customer=customer,
                invoice_number="INV-" + str(parking_record.id),
                invoice_date=timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=7),  # Set payment deadline to 7 days from now
                parking_start_time=parking_record.entry_time,
                parking_end_time=parking_record.exit_time,
                parking_duration=rounded_hours,
                parking_fee=parking_record.total_cost,
                extra_fee=0,
                total_fee=parking_record.total_cost + 0,
                payment_status="paid",
                payment_method='direct'
            )
            invoice.save()
            messages.success(request, 'Cập nhật trạng thái chỗ đậu xe thành công.')
            # Render invoice modal
            invoice_dict = model_to_dict(invoice)
            context = {
                'invoice': invoice_dict,
                'parking_record': parking_record,
                'customer': customer
            }
            return render(request, 'invoice/invoice_modal.html', context)
            # return redirect('display_invoice', parking_record_id=parking_record.id)

        except ParkingRecord.DoesNotExist:
            # Handle the case where there is no matching ParkingRecord object
            messages.error(request, 'No parking record found for this parking slot.')
            return redirect(reverse('show_parking_overview'))


def online_payment_view(request):
    if request.method == "POST":
        try:
            parking_slot_pk = request.POST.get('parking_slot_id')
            # Do something with the parking_slot_pk, for example:
            parking_slot = ParkingSlot.objects.get(pk=parking_slot_pk)

            # Get parking _record
            parking_record = ParkingRecord.objects.get(parking_slot=parking_slot, exit_time=None)
            parking_record.exit_time = timezone.now()
            timedelta = parking_record.exit_time - parking_record.entry_time
            total_seconds = timedelta.total_seconds()
            rounded_hours = Decimal(total_seconds / 3600)

            parking_record.total_cost = rounded_hours * parking_slot.cost_per_hour
            parking_record.save()
            parking_slot.is_available = True
            # parking_slot.exit_time = timezone.now()
            parking_slot.save()

            car = Car.objects.get(id=parking_record.car.id)
            print(car.id)
            car.is_parking = False
            car.save()
            customer = Customer.objects.filter(cars__id=car.id).first()
            print("customer", customer)
            invoice = Invoice.objects.create(
                parking_record=parking_record,
                customer=customer,
                invoice_number="INV-" + str(parking_record.id),
                invoice_date=timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=7),  # Set payment deadline to 7 days from now
                parking_start_time=parking_record.entry_time,
                parking_end_time=parking_record.exit_time,
                parking_duration=rounded_hours,
                parking_fee=parking_record.total_cost,
                extra_fee=0,
                total_fee=parking_record.total_cost + 0,
                payment_status="unpaid",
                payment_date=timezone.now().date(),
                payment_method='online'
            )
            invoice.save()
            messages.success(request, 'Cập nhật trạng thái chỗ đậu xe thành công.')
            # Render invoice modal
            invoice_dict = model_to_dict(invoice)
            context = {
                'invoice': invoice_dict,
                'parking_record': parking_record,
                'customer': customer
            }
            return render(request, 'invoice/invoice_modal.html', context)
            # return redirect('display_invoice', parking_record_id=parking_record.id)

        except ParkingRecord.DoesNotExist:
            # Handle the case where there is no matching ParkingRecord object
            messages.error(request, 'No parking record found for this parking slot.')
            return redirect(reverse('show_parking_overview'))


@api_view(['POST'])
def create_car(request):
    serializer = CarSerializer(data=request.data)
    if serializer.is_valid():
        car = serializer.save(is_active=True, is_parking=True, status=2)
        # Tạo một ParkingRecord mới cho Car
        parking_record = ParkingRecord.objects.create(car=car)
        return Response({'success': True})
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def update_parking_record(request):
    car_license_plate = request.data.get('license_plate')
    car_uuid = request.data.get('uuid')

    try:
        car = Car.objects.get(license_plate=car_license_plate, uuid=car_uuid)
    except Car.DoesNotExist:
        return Response({'error': 'Car not found'}, status=404)

    parking_record = ParkingRecord.objects.filter(car=car, exit_time=None).first()
    if parking_record:
        # Xe đã ra khỏi bãi đỗ
        parking_record.exit_time = timezone.now()
        parking_record.save()
        return Response({'success': True})

    return Response({'error': 'Parking record not found'}, status=404)


from .serializers import CarSerializer, ParkingRecordSerializer


def checking_full_slot():
    return ParkingSlot.objects.filter(is_available=1) > 0  # tra ve true neu con cho


def find_empty_parking_slot():
    try:
        # Lấy record đầu tiên có vị trí còn trống
        parking_slot = ParkingSlot.objects.filter(is_available=True).first()
        return parking_slot
    except ParkingSlot.DoesNotExist:
        return None


@api_view(['POST'])
def entry_car(request):
    if checking_full_slot:
        license_plate = request.data.get('license_plate')
        uuid = request.data.get('uuid')

        try:
            car = Car.objects.get(license_plate=license_plate)
            print(1)
            if car.status == 1:
                if car.uuid != uuid:
                    return Response('Thong tin uuid khong hop le doi voi nguoi dang ky', status=400)
                else:
                    pass
            elif car.status == 2:
                car.uuid = uuid
                car.save()
        except Car.DoesNotExist:
            car = Car.objects.create(license_plate=license_plate, uuid=uuid, is_active=True, is_parking=True, status=2)
            # car.save()
        parking_slot = find_empty_parking_slot()  # Tìm vị trí đỗ xe trống
        if parking_slot is None:
            return Response("Đã hết chỗ", status=400)
        parking_record_data = {
            'car': car.id,
            'exit_time': None,
            'parking_slot': parking_slot.id
        }
        parking_record_serializer = ParkingRecordSerializer(data=parking_record_data)
        if parking_record_serializer.is_valid():
            parking_record = parking_record_serializer.save()
            parking_slot.is_available = 0
            parking_slot.save()
            return Response({'success': True, 'parking_spot': parking_slot.slot_number})
        else:
            return Response(parking_record_serializer.errors, status=400)
    else:
        return Response("Đã hết chỗ", status=400)


@api_view(['POST'])
def exit_car(request):
    license_plate = request.data.get('license_plate')
    uuid = request.data.get('uuid')
    try:
        car = Car.objects.get(license_plate=license_plate)
        if car.uuid == uuid:
            car.is_parking = False
            car.save()
            parking_record = ParkingRecord.objects.filter(car=car, exit_time=None)
            parking_record.exit_time = timezone.now()
            parking_slot = parking_record.parking_slot
            if car.status == 2:
                timedelta = parking_record.exit_time - parking_record.entry_time
                total_seconds = timedelta.total_seconds()
                rounded_hours = Decimal(total_seconds / 3600)
                parking_record.total_cost = rounded_hours * parking_slot.cost_per_hour
                parking_record.is_paid = True
                parking_record.save()
                # Tao hoa don
                invoice = Invoice.objects.create(
                    parking_record=parking_record,
                    invoice_number="INV-" + str(parking_record.id),
                    invoice_date=timezone.now().date(),
                    due_date=timezone.now().date() + timezone.timedelta(days=7),  # Set payment deadline to 7 days from now
                    parking_start_time=parking_record.entry_time,
                    parking_end_time=parking_record.exit_time,
                    parking_duration=rounded_hours,
                    parking_fee=parking_record.total_cost,
                    payment_status="paid",
                    payment_method='direct'
                )
                invoice.save()
            else:
                pass
            parking_slot.is_available = True
            parking_slot.save()
            return Response('Xe số ' + car.license_plate + ' đã đi ra', status=200)
        else:
            return Response("UUID của xe không trùng khớp", status=400)


    except Car.DoesNotExist:
        return Response("Có lỗi trong khâu nhận diện", status=400)
