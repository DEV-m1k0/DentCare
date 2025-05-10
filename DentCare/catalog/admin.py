from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import  Doctor, Service, Appointment, Position, Comments, Message, Condition,  UserProfile 

admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Position)
admin.site.register(Message)
admin.site.register(Comments)
admin.site.register(Condition)
admin.site.register(UserProfile, UserAdmin)