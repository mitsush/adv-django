from django.urls import path
from django.views.generic import TemplateView

from .views import contact_view

urlpatterns = [

    path('contact/', contact_view, name='contact'),
    path('contact/success_page/', TemplateView.as_view(template_name="contact/success.html")),

]