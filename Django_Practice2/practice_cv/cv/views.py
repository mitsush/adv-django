from django.shortcuts import render, redirect

from .forms import ProfileForm
from .models import Profile
import pdfkit
from django.http import HttpResponse
from django.template import loader
import io
from django.core.mail import send_mail

from django.shortcuts import get_object_or_404, redirect

from django.contrib import messages

from django.conf import settings



def accept(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            form.save()
            return redirect('list')
    else:
        form = ProfileForm()
        return render(request, 'cv/profile_form.html', {'form': form})
    # return render(request, 'cv/accept.html')



def resume(request,id):
    user_profile = Profile.objects.get(pk=id)
    template = loader.get_template('cv/resume.html')
    html = template.render({'user_profile':user_profile})
    options = {
        'page-size':'Letter',
        'encoding':"UTF-8",}
    pdf = pdfkit.from_string(html,False,options)
    response = HttpResponse(pdf,content_type='application/pdf')
    response['Content-Disposition'] ='attachment'
    filename = "resume.pdf"
    return response


def list(request):
    profiles = Profile.objects.all()
    return render(request,'cv/list.html',{'profiles':profiles})


def share_cv_email(request, cv_id):
    cv = get_object_or_404(Profile, id=cv_id)

    recipient_email = request.POST.get('email')

    if recipient_email:

        subject = f"{cv.name}'s CV"

        message = f"Check out {cv.name}'s CV at {request.build_absolute_uri(cv.profile_picture.url)}"

        sender_email = settings.EMAIL_HOST_USER

        send_mail(subject, message, sender_email, [recipient_email])

        messages.success(request, "CV shared successfully via email.")

    else:

        messages.error(request, "Please provide a valid email.")

    return redirect('list')


