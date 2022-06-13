from django.contrib import admin

from .models import (
    Direction,
    Stage,
    Company,
    Deal
)


admin.site.register(Direction)
admin.site.register(Stage)
admin.site.register(Company)
admin.site.register(Deal)

