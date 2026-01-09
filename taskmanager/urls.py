# Create your views here.
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('viewmytasks', views.task_list, name='task_list'),
    path('task/new/', views.create_task, name='create_task'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('tasklist_view/', views.tasklist_view, name='tasklist_view'),
     path('task_show/', views.task_show, name='task_show'),
     path('task_list/',views.task_list,name='task_list'),
     path("task/<int:pk>/", views.task_detail, name="task_detail"),
path("send_whatsapp_reminder/<int:task_id>/", views.send_whatsapp_for_task, name="send_whatsapp_reminder"),
    path('tasks', views.tasks, name='tasks'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('task/<int:task_id>/roadmap/', views.roadmap, name='roadmap'),




]

