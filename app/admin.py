from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as baseUserAdmin
from . import models
from django.utils.translation import gettext, gettext_lazy as _

class MySchoolAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('sub_domen','id', 'school_name', 'creator_id')
    fieldsets = (
        (None, {'fields': ('school_name', 'sub_domen', 'creator_id')}),
        (_('Files'), {'fields': ('school_logo_1', 'school_logo_2')}),
    )

class MyUserAdmin(baseUserAdmin):
    search_fields = ('first_name', 'last_name', 'email')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    raw_id_fields=["school_id"]
    ordering = ('id',)
    # autocomplete_fields=["school_id"]
    list_display = ('email','id', 'phone', 'first_name', 'last_name', 'is_staff',"school_id")
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'fathername')}),
        (_('Additional info'), {'fields': ('gender', 'phone' ,'birth_date','card','country','lead_activity','client_activity',"school_id")}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # inlines = [CourseInline,]

admin.site.register(models.User,MyUserAdmin)
admin.site.register(models.Course)
admin.site.register(models.Lesson)
admin.site.register(models.Comment)
admin.site.register(models.HomeWork)
admin.site.register(models.Exercise)
admin.site.register(models.Exercise_list)
admin.site.register(models.School,MySchoolAdmin)
admin.site.register(models.KnowledgeBase)
admin.site.register(models.Vector)
admin.site.register(models.Course_user)
# Register your models here.
