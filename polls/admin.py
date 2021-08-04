from django.contrib import admin

from .models import Choice, Inventory, Question

# Register your models here.
admin.site.register(Choice)
admin.site.register(Inventory)
admin.site.register(Question)
