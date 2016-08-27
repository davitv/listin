from django.contrib import admin
from market import models


admin.site.register(models.Product)
admin.site.register(models.AttributeValue)
admin.site.register(models.Attribute)
