from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (JobViewSet, ResumeFeedbackViewSet, ResumeJobMatchViewSet,
                    ResumeViewSet, SkillViewSet)

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'resumes', ResumeViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'matches', ResumeJobMatchViewSet)
router.register(r'feedback', ResumeFeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
