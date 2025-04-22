# miniproject2/miniproject/miniproject/resumesapp/admin.py

from django.contrib import admin
from .models import Job, Skill, Resume, JobApplication, Education, Experience, ResumeFeedback, ResumeJobMatch

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'type', 'posted_date', 'status')
    list_filter = ('type', 'status', 'posted_date')
    search_fields = ('title', 'company', 'location', 'description')
    date_hierarchy = 'posted_date'
    filter_horizontal = ('skills_required',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_technical')
    list_filter = ('is_technical', 'category')
    search_fields = ('name',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'uploaded_at', 'is_parsed')
    list_filter = ('is_parsed', 'uploaded_at')
    search_fields = ('user__username', 'user__email', 'title')
    date_hierarchy = 'uploaded_at'
    filter_horizontal = ('skills',)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('institution', 'degree', 'field_of_study')
    
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company', 'title', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('company', 'title', 'description')
    filter_horizontal = ('skills_used',)

@admin.register(ResumeFeedback)
class ResumeFeedbackAdmin(admin.ModelAdmin):
    list_display = ('resume', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    search_fields = ('resume__title', 'skill_gaps', 'overall_suggestions')

@admin.register(ResumeJobMatch)
class ResumeJobMatchAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job', 'match_score', 'skill_match_percentage', 'experience_match_percentage', 'created_at')
    list_filter = ('match_score',)
    search_fields = ('resume__title', 'job__title', 'feedback')
    date_hierarchy = 'created_at'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'applied_at', 'status')
    list_filter = ('status', 'applied_at')
    search_fields = ('user__username', 'job__title', 'job__company')
    date_hierarchy = 'applied_at'