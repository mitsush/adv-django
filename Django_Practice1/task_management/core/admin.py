from django.contrib import admin

from .models import Task, Priority, Category, Project, User


# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'due_date')
    search_fields = ('title',)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = []


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = []


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')