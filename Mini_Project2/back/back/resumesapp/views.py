# miniproject2/miniproject/miniproject/resumesapp/views.py

import json
import re
from datetime import datetime

import docx2txt
import openai
import PyPDF2
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from usersapp.permissions import IsUserOrAdmin

from .models import (Education, Experience, Job, Resume, ResumeFeedback,
                     ResumeJobMatch, Skill)
from .serializers import (JobSerializer, ResumeFeedbackSerializer,
                          ResumeJobMatchSerializer, ResumeSerializer,
                          SkillSerializer)

User = get_user_model()

# Configure OpenAI API Key
openai.api_key = settings.OPENAI_API_KEY


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text


def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    return docx2txt.process(docx_file)


def extract_resume_text(file_object, content_type):
    """Extract text from resume file based on content type"""
    if content_type == 'application/pdf':
        return extract_text_from_pdf(file_object)
    elif content_type in [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    ]:
        return extract_text_from_docx(file_object)
    else:
        # For text files or unknown types, try to read directly
        return file_object.read().decode('utf-8', errors='ignore')


def parse_resume_with_openai(resume_text):
    """Use OpenAI to parse a resume and extract structured information"""
    prompt = """
    Parse the following resume text and extract key information in JSON format.
    Include the following sections:
    1. Contact Information (name, email, phone)
    2. Skills (as a list of strings)
    3. Education (list of objects with institution, degree, field_of_study, start_date, end_date, is_current)
    4. Experience (list of objects with company, title, location, start_date, end_date, is_current, description, skills_used)
    
    Format dates as YYYY-MM-DD if full date is available, or YYYY-MM if only month and year.
    If a date is not available, use null.
    For ongoing education or jobs, set is_current to true and end_date to null.
    
    Resume text:
    ```
    {resume_text}
    ```
    
    Return only the JSON without any other text or explanations.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a resume parsing assistant."},
                {"role": "user", "content": prompt.format(resume_text=resume_text)}
            ],
            temperature=0.2
        )
        
        result = response.choices[0].message.content.strip()
        # Remove any markdown code formatting if present
        result = re.sub(r'^```json\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        
        # Parse the JSON response
        parsed_data = json.loads(result)
        return parsed_data
    except Exception as e:
        # Log the error and return a basic structure
        print(f"Error parsing resume with OpenAI: {str(e)}")
        return {
            "contact_information": {},
            "skills": [],
            "education": [],
            "experience": []
        }


def match_resume_with_job(resume, job):
    """
    Match a resume with a job using NLP and return a match score
    along with detailed metrics and feedback
    """
    # Get the skills from both the resume and job
    resume_skills = set(skill.name.lower() for skill in resume.skills.all())
    job_skills = set(skill.name.lower() for skill in job.skills_required.all())
    
    # Calculate skill match percentage
    total_required_skills = len(job_skills)
    if total_required_skills == 0:
        skill_match_percentage = 100  # No skills required, so 100% match
    else:
        matched_skills = resume_skills.intersection(job_skills)
        skill_match_percentage = (len(matched_skills) / total_required_skills) * 100
    
    # Calculate experience match
    job_experience_required = job.experience_required
    resume_experience = 0
    
    # Sum up months of experience from the resume
    for exp in resume.experience.all():
        if exp.end_date:
            end_date = exp.end_date
        elif exp.is_current:
            end_date = timezone.now().date()
        else:
            continue
            
        start_date = exp.start_date
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        resume_experience += max(0, months)
    
    # Convert months to years
    resume_experience_years = resume_experience / 12
    
    # Calculate experience match percentage
    if job_experience_required == 0:
        experience_match_percentage = 100  # No experience required, so 100% match
    else:
        experience_ratio = min(resume_experience_years / job_experience_required, 1.5)
        experience_match_percentage = experience_ratio * 100
        if experience_ratio > 1:
            # Cap at 100% but still allow for some bonus
            experience_match_percentage = min(experience_match_percentage, 100)
    
    # Generate feedback using OpenAI
    feedback = generate_match_feedback(resume, job, resume_skills, job_skills)
    
    # Calculate overall match score (weighted average)
    match_score = (skill_match_percentage * 0.7) + (experience_match_percentage * 0.3)
    
    return {
        'match_score': match_score,
        'skill_match_percentage': skill_match_percentage,
        'experience_match_percentage': experience_match_percentage,
        'feedback': feedback
    }


def generate_match_feedback(resume, job, resume_skills, job_skills):
    """Generate detailed feedback for a resume-job match using OpenAI"""
    # Get missing skills
    missing_skills = job_skills - resume_skills
    
    # Create a prompt for OpenAI
    prompt = f"""
    I need feedback on how well a candidate's resume matches a job description.
    
    Job Title: {job.title}
    Company: {job.company}
    Job Description: {job.description}
    Job Requirements: {job.requirements}
    Required Skills: {', '.join(job_skills)}
    
    Resume Skills: {', '.join(resume_skills)}
    Missing Skills: {', '.join(missing_skills)}
    
    Resume Experience Summary:
    {'; '.join([f"{exp.title} at {exp.company} ({exp.start_date.strftime('%Y-%m')} to {exp.end_date.strftime('%Y-%m') if exp.end_date else 'Present'})" for exp in resume.experience.all()])}
    
    Provide concise, actionable feedback on:
    1. The strength of the match
    2. Key missing qualifications if any
    3. Suggestions for improvement
    
    Keep the feedback professional, constructive, and within 250 words.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a job matching assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        feedback = response.choices[0].message.content.strip()
        return feedback
    except Exception as e:
        # Log the error and return a basic feedback
        print(f"Error generating match feedback with OpenAI: {str(e)}")
        missing_skills_str = ", ".join(missing_skills) if missing_skills else "None"
        return f"The resume matches some of the job requirements. Missing skills: {missing_skills_str}. Consider adding more relevant experience to improve the match."


def generate_resume_feedback(resume):
    """Generate detailed resume feedback using OpenAI"""
    # Create a prompt for OpenAI
    prompt = f"""
    Provide detailed feedback on the following resume:
    
    Resume Title: {resume.title}
    Resume Text:
    ```
    {resume.raw_text[:2000]}  # Limit text length
    ```
    
    Please analyze the resume and provide feedback in the following format:
    
    1. Skill Gaps: Identify skills that are missing or could be improved based on current job market trends.
    
    2. Formatting Suggestions: Identify any formatting issues or improvements that could make the resume more effective.
    
    3. Keyword Optimization: Suggest keywords that could be added to make the resume more attractive to Applicant Tracking Systems (ATS).
    
    4. Overall Suggestions: Provide general suggestions to improve the resume's effectiveness.
    
    Make your feedback specific, actionable, and constructive. Focus on how the candidate can improve their resume to increase their chances of getting interviews.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        feedback_text = response.choices[0].message.content.strip()
        
        # Extract sections using regex
        skill_gaps = ""
        formatting = ""
        keywords = ""
        overall = ""
        
        skill_match = re.search(r"Skill Gaps:(.*?)(?=Formatting Suggestions:|$)", feedback_text, re.DOTALL)
        if skill_match:
            skill_gaps = skill_match.group(1).strip()
            
        format_match = re.search(r"Formatting Suggestions:(.*?)(?=Keyword Optimization:|$)", feedback_text, re.DOTALL)
        if format_match:
            formatting = format_match.group(1).strip()
            
        keyword_match = re.search(r"Keyword Optimization:(.*?)(?=Overall Suggestions:|$)", feedback_text, re.DOTALL)
        if keyword_match:
            keywords = keyword_match.group(1).strip()
            
        overall_match = re.search(r"Overall Suggestions:(.*?)$", feedback_text, re.DOTALL)
        if overall_match:
            overall = overall_match.group(1).strip()
        
        return {
            'skill_gaps': skill_gaps,
            'formatting_suggestions': formatting,
            'keyword_optimization': keywords,
            'overall_suggestions': overall
        }
    except Exception as e:
        # Log the error and return basic feedback
        print(f"Error generating resume feedback with OpenAI: {str(e)}")
        return {
            'skill_gaps': "Could not analyze skill gaps at this time.",
            'formatting_suggestions': "Review your resume formatting for clarity and consistency.",
            'keyword_optimization': "Consider adding industry-specific keywords to your resume.",
            'overall_suggestions': "Make sure your resume is concise, error-free, and tailored to your target jobs."
        }


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Skill.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__icontains=category)
            
        # Filter by technical/non-technical
        is_technical = self.request.query_params.get('is_technical', None)
        if is_technical is not None:
            is_technical = is_technical.lower() == 'true'
            queryset = queryset.filter(is_technical=is_technical)
            
        # Search by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset


class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all resumes
        if user.is_staff or user.role == User.ADMIN:
            queryset = Resume.objects.all()
        # Recruiters can see resumes that have been matched with their jobs
        elif user.role == User.RECRUITER:
            recruiter_jobs = Job.objects.filter(recruiter=user)
            resume_ids = ResumeJobMatch.objects.filter(
                job__in=recruiter_jobs
            ).values_list('resume_id', flat=True).distinct()
            queryset = Resume.objects.filter(id__in=resume_ids)
        # Job seekers can only see their own resumes
        else:
            queryset = Resume.objects.filter(user=user)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Parse a resume to extract information",
        responses={200: ResumeSerializer}
    )
    @action(detail=True, methods=['post'])
    def parse(self, request, pk=None):
        resume = self.get_object()
        
        # Check if resume is already parsed
        if resume.is_parsed:
            return Response(
                {"message": "Resume is already parsed"},
                status=status.HTTP_200_OK
            )
        
        try:
            # Process the file based on its content type
            with resume.file.open('rb') as file:
                resume_text = extract_resume_text(file, resume.content_type)
                
            # Save extracted text to resume
            resume.raw_text = resume_text
            resume.save()
            
            # Parse the resume using OpenAI
            parsed_data = parse_resume_with_openai(resume_text)
            
            # Process extracted skills
            if 'skills' in parsed_data:
                for skill_name in parsed_data['skills']:
                    skill_name = skill_name.strip()
                    if skill_name:
                        skill, created = Skill.objects.get_or_create(
                            name=skill_name
                        )
                        resume.skills.add(skill)
            
            # Process extracted education
            if 'education' in parsed_data:
                for edu in parsed_data['education']:
                    try:
                        # Parse dates
                        start_date = datetime.strptime(
                            edu.get('start_date') or '2000-01-01', 
                            '%Y-%m-%d'
                        ).date()
                        
                        if edu.get('end_date'):
                            end_date = datetime.strptime(
                                edu['end_date'], '%Y-%m-%d'
                            ).date()
                        else:
                            end_date = None
                            
                        Education.objects.create(
                            resume=resume,
                            institution=edu.get('institution', ''),
                            degree=edu.get('degree', ''),
                            field_of_study=edu.get('field_of_study', ''),
                            start_date=start_date,
                            end_date=end_date,
                            is_current=edu.get('is_current', False),
                            description=edu.get('description', '')
                        )
                    except (KeyError, ValueError) as e:
                        print(f"Error processing education: {str(e)}")
                        continue
            
            # Process extracted experience
            if 'experience' in parsed_data:
                for exp in parsed_data['experience']:
                    try:
                        # Parse dates
                        start_date = datetime.strptime(
                            exp.get('start_date') or '2000-01-01', 
                            '%Y-%m-%d'
                        ).date()
                        
                        if exp.get('end_date'):
                            end_date = datetime.strptime(
                                exp['end_date'], '%Y-%m-%d'
                            ).date()
                        else:
                            end_date = None
                            
                        experience = Experience.objects.create(
                            resume=resume,
                            company=exp.get('company', ''),
                            title=exp.get('title', ''),
                            location=exp.get('location', ''),
                            start_date=start_date,
                            end_date=end_date,
                            is_current=exp.get('is_current', False),
                            description=exp.get('description', '')
                        )
                        
                        # Add skills to experience
                        if 'skills_used' in exp and exp['skills_used']:
                            for skill_name in exp['skills_used']:
                                skill_name = skill_name.strip()
                                if skill_name:
                                    skill, created = Skill.objects.get_or_create(
                                        name=skill_name
                                    )
                                    experience.skills_used.add(skill)
                    except (KeyError, ValueError) as e:
                        print(f"Error processing experience: {str(e)}")
                        continue
            
            # Mark resume as parsed
            resume.is_parsed = True
            resume.save()
            
            # Return the updated resume
            serializer = self.get_serializer(resume)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to parse resume: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Generate feedback for a resume",
        responses={200: ResumeFeedbackSerializer}
    )
    @action(detail=True, methods=['post'])
    def generate_feedback(self, request, pk=None):
        resume = self.get_object()
        
        # Check if resume is parsed
        if not resume.is_parsed:
            return Response(
                {"error": "Resume must be parsed before generating feedback"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate feedback using OpenAI
            feedback_data = generate_resume_feedback(resume)
            
            # Create or update feedback
            feedback, created = ResumeFeedback.objects.update_or_create(
                resume=resume,
                defaults=feedback_data
            )
            
            serializer = ResumeFeedbackSerializer(feedback)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to generate feedback: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Get all feedback for a resume",
        responses={200: ResumeFeedbackSerializer}
    )
    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        resume = self.get_object()
        
        try:
            feedback = ResumeFeedback.objects.filter(resume=resume)
            serializer = ResumeFeedbackSerializer(feedback, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve feedback: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Match resume with jobs",
        responses={200: ResumeJobMatchSerializer(many=True)}
    )
    @action(detail=True, methods=['post'])
    def match_jobs(self, request, pk=None):
        resume = self.get_object()
        
        # Check if resume is parsed
        if not resume.is_parsed:
            return Response(
                {"error": "Resume must be parsed before matching with jobs"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get job IDs to match, or match with all active jobs
            job_ids = request.data.get('job_ids', [])
            
            if job_ids:
                jobs = Job.objects.filter(id__in=job_ids, status=Job.ACTIVE)
            else:
                jobs = Job.objects.filter(status=Job.ACTIVE)
            
            matches = []
            
            # Match resume with each job
            for job in jobs:
                match_result = match_resume_with_job(resume, job)
                
                # Create or update match record
                match, created = ResumeJobMatch.objects.update_or_create(
                    resume=resume,
                    job=job,
                    defaults={
                        'match_score': match_result['match_score'],
                        'skill_match_percentage': match_result['skill_match_percentage'],
                        'experience_match_percentage': match_result['experience_match_percentage'],
                        'feedback': match_result['feedback']
                    }
                )
                
                matches.append(match)
            
            serializer = ResumeJobMatchSerializer(matches, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to match resume with jobs: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Get all job matches for a resume",
        responses={200: ResumeJobMatchSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def job_matches(self, request, pk=None):
        resume = self.get_object()
        
        try:
            matches = ResumeJobMatch.objects.filter(resume=resume)
            serializer = ResumeJobMatchSerializer(matches, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve job matches: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.all()
        
        # If not admin/staff, filter jobs
        if not user.is_staff and user.role != User.ADMIN:
            # Recruiters can see all active jobs and their own jobs
            if user.role == User.RECRUITER:
                queryset = queryset.filter(
                    Q(status=Job.ACTIVE) | Q(recruiter=user)
                )
            # Job seekers can only see active jobs
            else:
                queryset = queryset.filter(status=Job.ACTIVE)
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        # Filter by title
        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)
            
        # Filter by company
        company = self.request.query_params.get('company', None)
        if company:
            queryset = queryset.filter(company__icontains=company)
            
        # Filter by required skills
        skill = self.request.query_params.get('skill', None)
        if skill:
            queryset = queryset.filter(skills_required__name__icontains=skill)
            
        # Filter by experience required
        min_experience = self.request.query_params.get('min_experience', None)
        max_experience = self.request.query_params.get('max_experience', None)
        
        if min_experience:
            try:
                queryset = queryset.filter(experience_required__gte=int(min_experience))
            except ValueError:
                pass
                
        if max_experience:
            try:
                queryset = queryset.filter(experience_required__lte=int(max_experience))
            except ValueError:
                pass
                
        return queryset
    
    def perform_create(self, serializer):
        # Only recruiters and admins can create jobs
        user = self.request.user
        if user.role not in [User.RECRUITER, User.ADMIN] and not user.is_staff:
            raise permissions.PermissionDenied("Only recruiters can create jobs")
            
        serializer.save(recruiter=user)
    
    @swagger_auto_schema(
        operation_description="Match job with resumes",
        responses={200: ResumeJobMatchSerializer(many=True)}
    )
    @action(detail=True, methods=['post'])
    def match_resumes(self, request, pk=None):
        job = self.get_object()
        
        try:
            # Get resume IDs to match, or match with all parsed resumes
            resume_ids = request.data.get('resume_ids', [])
            
            if resume_ids:
                resumes = Resume.objects.filter(id__in=resume_ids, is_parsed=True)
            else:
                resumes = Resume.objects.filter(is_parsed=True)
            
            matches = []
            
            # Match job with each resume
            for resume in resumes:
                match_result = match_resume_with_job(resume, job)
                
                # Create or update match record
                match, created = ResumeJobMatch.objects.update_or_create(
                    resume=resume,
                    job=job,
                    defaults={
                        'match_score': match_result['match_score'],
                        'skill_match_percentage': match_result['skill_match_percentage'],
                        'experience_match_percentage': match_result['experience_match_percentage'],
                        'feedback': match_result['feedback']
                    }
                )
                
                matches.append(match)
            
            serializer = ResumeJobMatchSerializer(matches, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to match job with resumes: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Get all resume matches for a job",
        responses={200: ResumeJobMatchSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def resume_matches(self, request, pk=None):
        job = self.get_object()
        
        try:
            matches = ResumeJobMatch.objects.filter(job=job).order_by('-match_score')
            serializer = ResumeJobMatchSerializer(matches, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve resume matches: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResumeJobMatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResumeJobMatch.objects.all()
    serializer_class = ResumeJobMatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all matches
        if user.is_staff or user.role == User.ADMIN:
            queryset = ResumeJobMatch.objects.all()
        # Recruiters can see matches for their jobs
        elif user.role == User.RECRUITER:
            queryset = ResumeJobMatch.objects.filter(job__recruiter=user)
        # Job seekers can see matches for their resumes
        else:
            queryset = ResumeJobMatch.objects.filter(resume__user=user)
            
        # Filter by minimum match score
        min_score = self.request.query_params.get('min_score', None)
        if min_score:
            try:
                queryset = queryset.filter(match_score__gte=float(min_score))
            except ValueError:
                pass
                
        # Sort by match score
        queryset = queryset.order_by('-match_score')
            
        return queryset


class ResumeFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResumeFeedback.objects.all()
    serializer_class = ResumeFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all feedback
        if user.is_staff or user.role == User.ADMIN:
            return ResumeFeedback.objects.all()
        # Other users can only see feedback for their resumes
        return ResumeFeedback.objects.filter(resume__user=user)