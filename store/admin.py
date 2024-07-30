from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student
from .models import Assignment, Exam
from .models import Certificate


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'course', 'status', 'grade')
    list_filter = ('status', 'course')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'status', 'exam_date')
    list_filter = ('status', 'course')

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Verification', {'fields': ('is_verified',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'phone_number', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'issued_date')
    search_fields = ('student__user__username', 'course__title')
    list_filter = ('issued_date',)


admin.site.register(User, UserAdmin)
admin.site.register(Student)

# Register your models here.
