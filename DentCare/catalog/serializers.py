from rest_framework import serializers
from .models import Doctor, Service, Appointment, Message

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'last_name']

class ServiceSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'price', 'doctor', 'description']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'