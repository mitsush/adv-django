# miniproject2/miniproject/miniproject/resumesapp/serializers.py

from rest_framework import serializers
from .models import Job, Skill, Resume, JobApplication, Education, Experience, ResumeFeedback, ResumeJobMatch

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'is_technical']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description']

class ExperienceSerializer(serializers.ModelSerializer):
    skills_used = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Experience
        fields = ['id', 'company', 'title', 'location', 'start_date', 'end_date', 'is_current', 'description', 'skills_used']

class ResumeSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resume
        fields = ['id', 'user', 'title', 'file', 'content_type', 'raw_text', 'is_parsed', 
                 'uploaded_at', 'updated_at', 'skills', 'education', 'experience']
        read_only_fields = ['user', 'raw_text', 'is_parsed', 'uploaded_at', 'updated_at']

class JobSerializer(serializers.ModelSerializer):
    skills_required = SkillSerializer(many=True, read_only=True)
    salary_range = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'location', 'type', 'salary_min', 'salary_max', 
                 'salary_range', 'description', 'requirements', 'experience_required', 
                 'posted_date', 'status', 'recruiter', 'skills_required']
        read_only_fields = ['posted_date', 'recruiter']

class JobApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    resume = ResumeSerializer(read_only=True)
    
    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'user', 'resume', 'cover_letter', 'applied_at', 'status']
        read_only_fields = ['applied_at', 'user']

class ResumeFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFeedback
        fields = ['id', 'resume', 'skill_gaps', 'formatting_suggestions', 
                 'keyword_optimization', 'overall_suggestions', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ResumeJobMatchSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = ResumeJobMatch
        fields = ['id', 'resume', 'job', 'match_score', 'skill_match_percentage', 
                 'experience_match_percentage', 'feedback', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']