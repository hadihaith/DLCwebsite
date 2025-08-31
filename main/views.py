
from .models import Application, User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta

import random
from decimal import Decimal
# Create your views here.
def home(request):
    return render(request, 'frontend/index.html')

def apply(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        student_id = request.POST.get('student_id')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        GPA = request.POST.get('GPA')
        major = request.POST.get('major')
        anything_else = request.POST.get('anything_else')
        applications = Application.objects.all()
        if applications.filter(student_id=student_id).exists():
            return render(request, 'frontend/apply.html', {'error': 'You have already submitted an application. Please wait for a response before submitting another.'})
        application = Application(
            name=name,
            student_id=student_id,
            phone=phone,
            email=email,
            GPA=GPA,
            major=major,
            anything_else=anything_else
        )
        
        application.save()
        return render(request, 'frontend/success.html', {'application': application})
    return render(request, 'frontend/apply.html')


def members(request):
    members = User.objects.filter(is_member=True)
    # order members by role, president first, vice president second, etc.
    new_order = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER', 'MEMBER']
    members = sorted(members, key=lambda x: new_order.index(x.role) if x.role in new_order else 100)
    return render(request, 'frontend/members.html', {'members': members})

@login_required
def portal(request):
    return render(request, 'frontend/portal.html')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("portal"))
        else:
            return render(request, "frontend/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "frontend/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))



@user_passes_test(lambda u: u.is_staff)
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = "sss@sss.com"
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "frontend/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "frontend/register.html", {
                "message": "Username is already previously taken."
            })
        return HttpResponseRedirect(reverse("index"))
    else:
        if request.user.is_staff:
            return render(request, "frontend/register.html")
