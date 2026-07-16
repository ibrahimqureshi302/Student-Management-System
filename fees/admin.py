from django.contrib import admin
from .models import Fee

class FeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'amount', 'paid_amount', 'remaining_amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('student__registration_no', 'student__user__first_name')
    
    def remaining_amount(self, obj):
        return obj.remaining_amount
    remaining_amount.short_description = 'Remaining Amount'

admin.site.register(Fee, FeeAdmin)