from django.contrib import admin

from .models import (
    Direction,
    Stage,
    Company,
    Deal,
    Calls
)


admin.site.register(Direction)
admin.site.register(Stage)
admin.site.register(Company)
admin.site.register(Deal)
admin.site.register(Calls)

