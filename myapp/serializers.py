from rest_framework import serializers
from .models import Car, ParkingRecord

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

#

class ParkingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingRecord
        fields = '__all__'