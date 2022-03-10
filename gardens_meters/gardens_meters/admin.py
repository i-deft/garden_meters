from django.contrib import admin
from .models import Garden, Owner, MonthMeters, PhotoOfPay


admin.site.register(Garden)
admin.site.register(Owner)
admin.site.register(MonthMeters)
admin.site.register(PhotoOfPay)