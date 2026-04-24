from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Student
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/resources/', views.student_resources, name='student_resources'),
    path('student/mentorship/', views.student_mentorship, name='student_mentorship'),
    path('student/mentorship/request/<int:mentor_id>/', views.send_mentorship_request, name='send_mentorship_request'),
    path('student/jobs/', views.student_jobs, name='student_jobs'),
    path('student/jobs/apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('student/career/', views.student_career, name='student_career'),

    # Alumni
    path('alumni/', views.alumni_dashboard, name='alumni_dashboard'),
    path('alumni/mentorship/', views.alumni_mentorship, name='alumni_mentorship'),
    path('alumni/mentorship/<int:session_id>/<str:action>/', views.respond_mentorship, name='respond_mentorship'),
    path('alumni/jobs/', views.alumni_jobs, name='alumni_jobs'),
    path('alumni/jobs/<int:job_id>/applicants/', views.alumni_job_applicants, name='alumni_job_applicants'),
    path('alumni/applications/<int:application_id>/<str:status>/', views.alumni_update_application, name='alumni_update_application'),
    path('alumni/jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('alumni/resources/', views.alumni_resources, name='alumni_resources'),

    # Shared
    path('resource/delete/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
    path('notifications/<int:notif_id>/read/', views.mark_read, name='mark_read'),
    path('profile/', views.profile_view, name='profile'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/send/', views.send_message, name='send_message'),
    path('api/messages/<int:user_id>/', views.get_messages_api, name='get_messages_api'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/content/', views.admin_content, name='admin_content'),
    path('admin-panel/content/delete/<str:content_type>/<int:content_id>/', views.admin_delete_content, name='admin_delete_content'),
    path('admin-panel/mentorships/', views.admin_mentorships, name='admin_mentorships'),
    path('admin-panel/mentorships/delete/<int:session_id>/', views.admin_delete_session, name='admin_delete_session'),
    path('admin-panel/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin-panel/applications/', views.admin_applications, name='admin_applications'),
]
