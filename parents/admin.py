from django.contrib import admin
from .models import Parent, StudentParent

class StudentParentInline(admin.TabularInline):
    model = StudentParent
    extra = 1
    fields = ('student', 'relationship')
    autocomplete_fields = ('student',)

class ParentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'occupation', 'children_count')
    list_filter = ('occupation',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone')
    inlines = [StudentParentInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Parent Details', {
            'fields': ('occupation', 'phone')
        }),
    )
    
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = 'Parent Name'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email Address'
    
    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Number of Children'

class StudentParentAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'student', 'relationship')
    list_filter = ('relationship',)
    search_fields = ('parent__user__first_name', 'student__user__first_name')
    autocomplete_fields = ('parent', 'student')

admin.site.register(Parent, ParentAdmin)
admin.site.register(StudentParent, StudentParentAdmin)