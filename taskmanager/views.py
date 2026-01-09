

from django.shortcuts import render, redirect
from .models import Task
from django import forms
from django.contrib.auth.decorators import login_required


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'duration', 'priority']


@login_required
def task_list(request):
    if request.user.is_superuser:
        # ✅ Admin can see all tasks
        tasks = Task.objects.all()
    else:
        # ✅ Normal user only sees their own tasks
        tasks = Task.objects.filter(user=request.user)

    return render(request, 'taskmanager/task_list.html', {"tasks": tasks})
from .utils import generate_roadmap
from .forms import TaskForm
from .models import TaskRoadmap
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()

            # Generate roadmap
            prompt = f"Generate a step-by-step roadmap for the task: {task.title}"
            roadmap_text = generate_roadmap(prompt)

            # Save roadmap
            TaskRoadmap.objects.create(task=task, roadmap_text=roadmap_text)

            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "taskmanager/create_task.html", {"form": form})

# @login_required
def home(request):
    return render(request, 'taskmanager/home.html')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
# @login_required

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')
    else:
        form = SignUpForm()
    return render(request, 'taskmanager/signup.html', {'form': form})
# @login_required

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'taskmanager/login.html', {'form': form})

# import requests
# import json
# from django.http import HttpResponse

# def generate_roadmap(tasks):
#     url = "https://script.google.com/macros/s/AKfycbzJzUAnhP_UOZBa5Z2OL5vCiw4Hc-csLeXQ7NOqp9pZbxM_1aR7TTWy8Bv5K8bTenQOEw/exec"
#     try:
#         resp = requests.post(url, json={"tasks": tasks})
#         print("Status code:", resp.status_code)
#         print("Response text:", resp.text)  # See what actually comes back
#         resp.raise_for_status()
#         return resp.json()  # Parse JSON
#     except Exception as e:
#         print("Error:", e)
#         return {}


from .models import Task
import requests
import json
from django.shortcuts import render
from .models import Task

API_URL ="https://script.google.com/macros/s/AKfycbxAcbfHGmXJKQge9_6KDUhc53sOsG10GRFWhkAST4TL4BcIFPetHTI83o0j4OWP4kHP9w/exec"
def tasklist_view(request):
    tasks = list(Task.objects.values('title', 'deadline'))
    
    # Convert datetime to string so JSON can handle it
    for task in tasks:
        task['deadline'] = task['deadline'].strftime("%Y-%m-%d")

    try:
        response = requests.post(API_URL, json=tasks)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        result = {"roadmap": f"Error: {e}"}

    sheet_url = result.get('sheetUrl')
    roadmap_text = result.get('roadmap', '')
    return render(request, 'taskmanager/roadmap.html', {
        'sheet_url': sheet_url,
        'roadmap_text': roadmap_text
  })
# @login_required

def task_show(request):
    tasks = Task.objects.all()  # Show newest first
    return render(request, 'taskmanager/task_show.html', {'tasks': tasks})

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Task, TaskProgress
# @login_required

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    today = timezone.now().date()

    # Get or create today's progress entry
    progress, created = TaskProgress.objects.get_or_create(task=task, date=today)

    if request.method == "POST":
        status = request.POST.get("status")
        if status == "done":
            progress.is_done = True
        elif status == "not_done":
            progress.is_done = False
        progress.save()
        return redirect("task_detail", pk=task.pk)

    # fetch progress history for this task
    history = TaskProgress.objects.filter(task=task).order_by("-date")

    return render(request, "taskmanager/task_detail.html", {
        "task": task,
        "progress": progress,
        "history": history
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .notification import send_whatsapp_reminder
from django.contrib import messages
# @login_required

def tasks(request):
    tasks = Task.objects.select_related("user").all()
    return render(request, "taskmanager/tasks.html", {"tasks": tasks})


from .models import Task
from .notification import send_whatsapp_reminder  # 👈 import correctly
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def send_whatsapp_for_task(request, task_id):
    # ✅ Only allow admins
    if not request.user.is_superuser:
        return HttpResponse("You don't have permission")  # non-admin blocked

    task = get_object_or_404(Task, id=task_id)
    days_left = task.days_left()

    if task.user:  # check if user exists
        user_name = task.user.first_name or task.user.username
        phone_number = getattr(task.user.profile, "phone_number", None)

        if phone_number:  # only send if phone number exists
            message = f"Hello {user_name},\nTask: {task.title}\nStatus: {task.status}\nDays left: {days_left}"
            send_whatsapp_reminder(phone_number, message)
            messages.success(request, f"WhatsApp reminder sent for task '{task.title}'!")
        else:
            messages.error(request, f"User '{user_name}' has no phone number linked.")
    else:
        messages.error(request, f"Task '{task.title}' has no user assigned.")
    return redirect("task_list")


from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Task, TaskRoadmap
from .utils import generate_roadmap   # 👈 import your Gemini helper
import markdown

from django.shortcuts import get_object_or_404, render
from .models import Task, TaskRoadmap
import markdown

@login_required
def roadmap(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # remove user=request.user

    # Get or create roadmap
    roadmap, created = TaskRoadmap.objects.get_or_create(task=task)

    if created or not roadmap.roadmap_text:
        # Generate roadmap (Gemini or other logic)
        prompt = f"Generate a detailed step-by-step roadmap for the task: {task.title}"
        roadmap.roadmap_text = generate_roadmap(prompt)
        roadmap.save()

    roadmap_html = markdown.markdown(roadmap.roadmap_text)

    return render(request, "taskmanager/roadmap.html", {
        "task": task,
        "roadmap": roadmap,
        "roadmap_html": roadmap_html,
    })
