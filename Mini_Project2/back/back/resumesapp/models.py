# miniproject2/miniproject/miniproject/resumesapp/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    is_technical = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resumes/')
    content_type = models.CharField(max_length=100, null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)
    is_parsed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.ManyToManyField(Skill, related_name='resumes', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s resume - {self.title}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    skills_used = models.ManyToManyField(Skill, related_name='experiences', blank=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"

class Job(models.Model):
    ACTIVE = 'active'
    CLOSED = 'closed'
    DRAFT = 'draft'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
        (DRAFT, 'Draft'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    type = models.CharField(max_length=50)  # Full-time, Part-time, etc.
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    requirements = models.TextField()
    experience_required = models.FloatField(default=0.0)  # in years
    posted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    skills_required = models.ManyToManyField(Skill, related_name='jobs', blank=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        return "Salary not specified"

class ResumeFeedback(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='feedback')
    skill_gaps = models.TextField()
    formatting_suggestions = models.TextField()
    keyword_optimization = models.TextField()
    overall_suggestions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback for {self.resume.title}"

class ResumeJobMatch(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resume_matches')
    match_score = models.FloatField()
    skill_match_percentage = models.FloatField()
    experience_match_percentage = models.FloatField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['resume', 'job']
    
    def __str__(self):
        return f"{self.resume.title} - {self.job.title} (Match: {self.match_score:.2f}%)"

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    cover_letter = models.TextField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    
    class Meta:
        unique_together = ['job', 'user']
    
    def __str__(self):
        return f"{self.user.username} applied to {self.job.title}"