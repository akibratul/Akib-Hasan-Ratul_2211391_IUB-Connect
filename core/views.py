import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import User, StudentProfile, AlumniProfile, Resource, Job, MentorshipSession, Message, Notification, Application
from .forms import LoginForm, RegisterForm, ProfileForm, JobForm, ApplicationForm
from .decorators import role_required
from .career import get_recommendations


def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'index.html')

# ==================== AUTH ====================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            selected_role = form.cleaned_data.get('role', 'student')
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    if user.role != selected_role:
                        messages.error(request, 'Invalid login: Please select correct user role')
                    else:
                        auth_login(request, user)
                        messages.success(request, f'Welcome back, {user.full_display_name}!')
                        return redirect('dashboard_redirect')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']

            if role == 'student' and not re.match(r'^\d+@iub\.edu\.bd$', email):
                messages.error(request, 'Student email must be a valid IUB student ID (e.g., 2211391@iub.edu.bd).')
                return render(request, 'auth/register.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'auth/register.html', {'form': form})

            # Use email as username
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                role=role
            )

            if role == 'student':
                skills_str = form.cleaned_data.get('skills', '')
                skills_list = [s.strip() for s in skills_str.split(',') if s.strip()] if skills_str else []
                StudentProfile.objects.create(
                    user=user,
                    department=form.cleaned_data.get('department', 'CSE'),
                    year=int(form.cleaned_data.get('year', 1)),
                    skills=json.dumps(skills_list),
                    interests=form.cleaned_data.get('interests', '')
                )
            else:
                AlumniProfile.objects.create(
                    user=user,
                    graduation_year=form.cleaned_data.get('graduation_year') or 2020,
                    profession=form.cleaned_data.get('profession', '')
                )

            messages.success(request, '🎉 Registration successful! Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'alumni':
        return redirect('alumni_dashboard')
    else:
        return redirect('student_dashboard')


# ==================== STUDENT VIEWS ====================
@login_required
@role_required('student')
def student_dashboard(request):
    user = request.user
    resources_count = Resource.objects.filter(uploaded_by=user).count()
    mentorships_count = MentorshipSession.objects.filter(student=user).count()
    jobs_count = Job.objects.count()
    notif_count = Notification.objects.filter(user=user, read=False).count()
    recent_jobs = Job.objects.select_related('posted_by').all()[:3]

    # Career recommendations
    recommendations = []
    try:
        profile = user.student_profile
        recommendations = get_recommendations(profile)[:4]
    except StudentProfile.DoesNotExist:
        pass

    for job in recent_jobs:
        job.skills_list = job.get_skills_list()

    return render(request, 'student/dashboard.html', {
        'stats': {
            'resources': resources_count, 'mentorships': mentorships_count,
            'jobs': jobs_count, 'notifications': notif_count
        },
        'recent_jobs': recent_jobs,
        'recommendations': recommendations,
    })


@login_required
@role_required('student')
def student_resources(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        file = request.FILES.get('file')
        if title and file:
            Resource.objects.create(
                title=title, file=file, original_name=file.name, uploaded_by=request.user
            )
            messages.success(request, 'Resource uploaded!')
        else:
            messages.error(request, 'Title and file required.')
        return redirect('student_resources')

    tab = request.GET.get('tab', 'all')
    if tab == 'my':
        resources = Resource.objects.filter(uploaded_by=request.user)
    else:
        resources = Resource.objects.select_related('uploaded_by').all()
    return render(request, 'student/resources.html', {'resources': resources, 'tab': tab})


@login_required
@role_required('student')
def student_mentorship(request):
    mentors = list(User.objects.filter(role='alumni').select_related('alumni_profile'))
    my_requests = MentorshipSession.objects.filter(student=request.user).select_related('mentor', 'mentor__alumni_profile')

    # Attach request status directly to each mentor object
    request_map = {s.mentor_id: s for s in my_requests}
    for mentor in mentors:
        session = request_map.get(mentor.id)
        if session:
            mentor.request_status = session.status
        else:
            mentor.request_status = None

    tab = request.GET.get('tab', 'mentors')
    return render(request, 'student/mentorship.html', {
        'mentors': mentors, 'my_requests': my_requests,
        'tab': tab,
        'pending_count': my_requests.filter(status='pending').count(),
        'accepted_count': my_requests.filter(status='accepted').count(),
    })


@login_required
@role_required('student')
def send_mentorship_request(request, mentor_id):
    if request.method == 'POST':
        mentor = get_object_or_404(User, id=mentor_id, role='alumni')
        existing = MentorshipSession.objects.filter(
            student=request.user, mentor=mentor, status__in=['pending', 'accepted']
        ).first()
        if existing:
            messages.error(request, 'Already connected or request pending.')
        else:
            msg = request.POST.get('message', '')
            MentorshipSession.objects.create(student=request.user, mentor=mentor, message=msg)
            Notification.objects.create(user=mentor, message=f'📩 New mentorship request from {request.user.full_display_name}')
            messages.success(request, 'Mentorship request sent! 🎉')
    return redirect('student_mentorship')


@login_required
@role_required('student')
def student_jobs(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.select_related('posted_by').all()
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | Q(company__icontains=query) | Q(skills_required__icontains=query)
        )
    for job in jobs:
        job.skills_list = job.get_skills_list()
        # Check if current student has applied
        job.has_applied = Application.objects.filter(job=job, student=request.user).exists()
    
    form = ApplicationForm()
    return render(request, 'student/jobs.html', {'jobs': jobs, 'query': query, 'form': form})

@login_required
@role_required('student')
def apply_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(Job, id=job_id)
        if Application.objects.filter(job=job, student=request.user).exists():
            messages.error(request, 'You have already applied for this position.')
            return redirect('student_jobs')
            
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            Application.objects.create(
                job=job,
                student=request.user,
                cv=request.FILES['cv'],
                cover_letter=form.cleaned_data.get('cover_letter', '')
            )
            Notification.objects.create(
                user=job.posted_by, 
                message=f'📄 New application from {request.user.full_display_name} for {job.title}'
            )
            messages.success(request, 'Application submitted successfully! 🎉')
        else:
            messages.error(request, 'Failed to submit application. Please ensure CV is a valid PDF.')
    return redirect('student_jobs')


@login_required
@role_required('student')
def student_career(request):
    recommendations = []
    matched_jobs = []
    profile = None
    try:
        profile = request.user.student_profile
        recommendations = get_recommendations(profile)
        # Match jobs
        all_jobs = Job.objects.select_related('posted_by').all()
        career_titles = [r['title'].lower() for r in recommendations]
        student_skills = [s.lower() for s in profile.get_skills_list()]
        for job in all_jobs:
            job_title = job.title.lower()
            job_skills = [s.lower() for s in job.get_skills_list()]
            title_match = any(ct.split()[0] in job_title or job_title.split()[0] in ct for ct in career_titles)
            skill_match = any(js in ss or ss in js for js in job_skills for ss in student_skills)
            if title_match or skill_match:
                job.skills_list = job.get_skills_list()
                matched_jobs.append(job)
    except StudentProfile.DoesNotExist:
        pass

    return render(request, 'student/career.html', {
        'recommendations': recommendations,
        'matched_jobs': matched_jobs,
        'profile': profile,
    })


# ==================== ALUMNI VIEWS ====================
@login_required
@role_required('alumni')
def alumni_dashboard(request):
    user = request.user
    incoming = MentorshipSession.objects.filter(mentor=user).select_related('student', 'student__student_profile')
    jobs_count = Job.objects.filter(posted_by=user).count()
    notif_count = Notification.objects.filter(user=user, read=False).count()
    resources_count = Resource.objects.count()

    return render(request, 'alumni/dashboard.html', {
        'stats': {
            'incoming': incoming.count(), 'jobs': jobs_count,
            'resources': resources_count, 'notifications': notif_count
        },
        'sessions': incoming[:5],
    })


@login_required
@role_required('alumni')
def alumni_mentorship(request):
    sessions = MentorshipSession.objects.filter(mentor=request.user).select_related('student', 'student__student_profile')
    tab = request.GET.get('tab', 'all')
    if tab != 'all':
        sessions = sessions.filter(status=tab)

    return render(request, 'alumni/mentorship.html', {
        'sessions': sessions, 'tab': tab,
        'pending_count': MentorshipSession.objects.filter(mentor=request.user, status='pending').count(),
        'accepted_count': MentorshipSession.objects.filter(mentor=request.user, status='accepted').count(),
        'rejected_count': MentorshipSession.objects.filter(mentor=request.user, status='rejected').count(),
    })


@login_required
@role_required('alumni')
def respond_mentorship(request, session_id, action):
    session = get_object_or_404(MentorshipSession, id=session_id, mentor=request.user)
    if action in ['accepted', 'rejected']:
        session.status = action
        session.save()
        emoji = '✅' if action == 'accepted' else '❌'
        extra = ' — You can now chat!' if action == 'accepted' else ''
        Notification.objects.create(
            user=session.student,
            message=f'{emoji} Mentorship request {action} by {request.user.full_display_name}{extra}'
        )
        messages.success(request, f'Request {action}!')
    return redirect('alumni_mentorship')


@login_required
@role_required('alumni')
def alumni_jobs(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            skills_str = form.cleaned_data.get('skills_required', '')
            skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
            job = Job.objects.create(
                title=form.cleaned_data['title'],
                company=form.cleaned_data['company'],
                job_type=form.cleaned_data['job_type'],
                deadline=form.cleaned_data.get('deadline'),
                description=form.cleaned_data.get('description', ''),
                skills_required=json.dumps(skills_list),
                posted_by=request.user
            )
            # Notify all students
            for student in User.objects.filter(role='student'):
                Notification.objects.create(user=student, message=f'New job posted: {job.title} at {job.company}')
            messages.success(request, 'Job posted!')
            return redirect('alumni_jobs')
    else:
        form = JobForm()

    jobs = Job.objects.filter(posted_by=request.user).annotate(applicant_count=Count('applications'))
    for job in jobs:
        job.skills_list = job.get_skills_list()
    return render(request, 'alumni/jobs.html', {'jobs': jobs, 'form': form})


@login_required
@role_required('alumni')
def alumni_job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = job.applications.select_related('student', 'student__student_profile').all()
    return render(request, 'alumni/job_applicants.html', {'job': job, 'applications': applications})


@login_required
@role_required('alumni')
def alumni_update_application(request, application_id, status):
    application = get_object_or_404(Application, id=application_id, job__posted_by=request.user)
    if status in ['selected', 'rejected']:
        application.status = status
        application.save()
        
        if status == 'selected':
            Notification.objects.create(
                user=application.student,
                message=f'🎉 Congratulations! You have been selected for the {application.job.title} position at {application.job.company}.'
            )
        elif status == 'rejected':
            Notification.objects.create(
                user=application.student,
                message=f'We regret to inform you that you were not selected for the {application.job.title} position at {application.job.company}.'
            )
            
        messages.success(request, f'Application marked as {status}.')
    return redirect('alumni_job_applicants', job_id=application.job.id)


@login_required
@role_required('alumni')
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    job.delete()
    messages.success(request, 'Job deleted.')
    return redirect('alumni_jobs')


@login_required
@role_required('alumni')
def alumni_resources(request):
    resources = Resource.objects.select_related('uploaded_by').all()
    return render(request, 'alumni/resources.html', {'resources': resources})


# ==================== SHARED VIEWS ====================
@login_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, uploaded_by=request.user)
    resource.delete()
    messages.success(request, 'Resource deleted.')
    if request.user.role == 'student':
        return redirect('student_resources')
    return redirect('alumni_resources')


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user)[:50]
    unread = Notification.objects.filter(user=request.user, read=False).count()
    return render(request, 'shared/notifications.html', {'notifs': notifs, 'unread': unread})


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


@login_required
def mark_read(request, notif_id):
    return redirect('notifications')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        # Handle photo upload
        if 'photo' in request.FILES:
            user.profile_photo = request.FILES['photo']
            user.save()
            messages.success(request, 'Photo updated!')
            return redirect('profile')

        form = ProfileForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            parts = name.split()
            user.first_name = parts[0] if parts else ''
            user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            user.save()

            if user.role == 'student':
                try:
                    p = user.student_profile
                except StudentProfile.DoesNotExist:
                    p = StudentProfile.objects.create(user=user)
                p.department = form.cleaned_data.get('department', p.department)
                p.year = int(form.cleaned_data.get('year', p.year))
                skills_str = form.cleaned_data.get('skills', '')
                p.skills = json.dumps([s.strip() for s in skills_str.split(',') if s.strip()])
                p.interests = form.cleaned_data.get('interests', p.interests)
                p.save()
            elif user.role == 'alumni':
                try:
                    p = user.alumni_profile
                except AlumniProfile.DoesNotExist:
                    p = AlumniProfile.objects.create(user=user)
                if form.cleaned_data.get('graduation_year'):
                    p.graduation_year = form.cleaned_data['graduation_year']
                p.profession = form.cleaned_data.get('profession', p.profession)
                p.save()

            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        initial = {'name': user.full_display_name}
        if user.role == 'student':
            try:
                p = user.student_profile
                initial.update({
                    'department': p.department, 'year': p.year,
                    'skills': ', '.join(p.get_skills_list()),
                    'interests': p.interests,
                })
            except StudentProfile.DoesNotExist:
                pass
        elif user.role == 'alumni':
            try:
                p = user.alumni_profile
                initial.update({
                    'graduation_year': p.graduation_year,
                    'profession': p.profession,
                })
            except AlumniProfile.DoesNotExist:
                pass
        form = ProfileForm(initial=initial)

    return render(request, 'shared/profile.html', {'form': form})


# ==================== CHAT ====================
@login_required
def chat_view(request):
    user = request.user
    # Get accepted connections
    if user.role == 'student':
        sessions = MentorshipSession.objects.filter(student=user, status='accepted').select_related('mentor', 'mentor__alumni_profile')
        connections = []
        for s in sessions:
            last_msg = Message.objects.filter(
                Q(sender=user, receiver=s.mentor) | Q(sender=s.mentor, receiver=user)
            ).order_by('-created_at').first()
            connections.append({
                'user': s.mentor, 'session_id': s.id,
                'role': 'alumni',
                'info': getattr(s.mentor, 'alumni_profile', None),
                'last_message': last_msg.message if last_msg else None,
                'last_time': last_msg.created_at if last_msg else s.created_at,
            })
    elif user.role == 'alumni':
        sessions = MentorshipSession.objects.filter(mentor=user, status='accepted').select_related('student', 'student__student_profile')
        connections = []
        for s in sessions:
            last_msg = Message.objects.filter(
                Q(sender=user, receiver=s.student) | Q(sender=s.student, receiver=user)
            ).order_by('-created_at').first()
            connections.append({
                'user': s.student, 'session_id': s.id,
                'role': 'student',
                'info': getattr(s.student, 'student_profile', None),
                'last_message': last_msg.message if last_msg else None,
                'last_time': last_msg.created_at if last_msg else s.created_at,
            })
    else:
        connections = []

    connections.sort(key=lambda x: x['last_time'], reverse=True)

    selected_id = request.GET.get('user')
    selected_user = None
    chat_messages = []
    if selected_id:
        try:
            selected_user = User.objects.get(id=int(selected_id))
            # Verify connection
            has_connection = MentorshipSession.objects.filter(
                status='accepted'
            ).filter(
                Q(student=user, mentor=selected_user) | Q(student=selected_user, mentor=user)
            ).exists()
            if has_connection:
                chat_messages = Message.objects.filter(
                    Q(sender=user, receiver=selected_user) | Q(sender=selected_user, receiver=user)
                ).order_by('created_at')
            else:
                selected_user = None
        except (User.DoesNotExist, ValueError):
            pass

    return render(request, 'shared/chat.html', {
        'connections': connections,
        'selected_user': selected_user,
        'chat_messages': chat_messages,
    })


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        message_text = request.POST.get('message', '').strip()
        if receiver_id and message_text:
            receiver = get_object_or_404(User, id=int(receiver_id))
            # Verify connection
            has_connection = MentorshipSession.objects.filter(
                status='accepted'
            ).filter(
                Q(student=request.user, mentor=receiver) | Q(student=receiver, mentor=request.user)
            ).exists()
            if has_connection:
                Message.objects.create(sender=request.user, receiver=receiver, message=message_text)

        # For AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect(f'/chat/?user={receiver_id}')
    return redirect('chat')


@login_required
def get_messages_api(request, user_id):
    """API endpoint for chat polling."""
    other_user = get_object_or_404(User, id=user_id)
    has_connection = MentorshipSession.objects.filter(
        status='accepted'
    ).filter(
        Q(student=request.user, mentor=other_user) | Q(student=other_user, mentor=request.user)
    ).exists()
    if not has_connection:
        return JsonResponse({'messages': []})

    msgs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    return JsonResponse({'messages': [
        {
            'id': m.id, 'sender_id': m.sender_id, 'receiver_id': m.receiver_id,
            'message': m.message, 'sender_name': m.sender.full_display_name,
            'created_at': m.created_at.isoformat(),
            'is_mine': m.sender_id == request.user.id,
        } for m in msgs
    ]})


# ==================== ADMIN VIEWS ====================
@login_required
@role_required('admin')
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html', {
        'stats': {
            'students': User.objects.filter(role='student').count(),
            'alumni': User.objects.filter(role='alumni').count(),
            'jobs': Job.objects.count(),
            'resources': Resource.objects.count(),
            'mentorships': MentorshipSession.objects.count(),
            'pending': MentorshipSession.objects.filter(status='pending').count(),
        },
        'recent_users': User.objects.exclude(role='admin').order_by('-date_joined')[:5],
        'recent_jobs': Job.objects.select_related('posted_by').all()[:5],
        'recent_resources': Resource.objects.select_related('uploaded_by').all()[:5],
    })


@login_required
@role_required('admin')
def admin_users(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    users = User.objects.exclude(role='admin')
    if query:
        users = users.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'admin_panel/users.html', {'users': users, 'query': query, 'role_filter': role_filter})


@login_required
@role_required('admin')
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.role != 'admin':
        user.delete()
        messages.success(request, 'User deleted.')
    return redirect('admin_users')


@login_required
@role_required('admin')
def admin_content(request):
    tab = request.GET.get('tab', 'jobs')
    query = request.GET.get('q', '')
    jobs = Job.objects.select_related('posted_by').all()
    resources = Resource.objects.select_related('uploaded_by').all()
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company__icontains=query))
        resources = resources.filter(Q(title__icontains=query))
    for j in jobs:
        j.skills_list = j.get_skills_list()
    return render(request, 'admin_panel/content.html', {'jobs': jobs, 'resources': resources, 'tab': tab, 'query': query})


@login_required
@role_required('admin')
def admin_delete_content(request, content_type, content_id):
    if content_type == 'job':
        get_object_or_404(Job, id=content_id).delete()
    elif content_type == 'resource':
        get_object_or_404(Resource, id=content_id).delete()
    messages.success(request, 'Content deleted.')
    return redirect('admin_content')


@login_required
@role_required('admin')
def admin_mentorships(request):
    tab = request.GET.get('tab', 'all')
    sessions = MentorshipSession.objects.select_related('student', 'mentor').all()
    if tab != 'all':
        sessions = sessions.filter(status=tab)
    return render(request, 'admin_panel/mentorships.html', {
        'sessions': sessions, 'tab': tab,
        'pending_count': MentorshipSession.objects.filter(status='pending').count(),
        'accepted_count': MentorshipSession.objects.filter(status='accepted').count(),
        'rejected_count': MentorshipSession.objects.filter(status='rejected').count(),
    })


@login_required
@role_required('admin')
def admin_delete_session(request, session_id):
    get_object_or_404(MentorshipSession, id=session_id).delete()
    messages.success(request, 'Session deleted.')
    return redirect('admin_mentorships')


@login_required
@role_required('admin')
def admin_announcements(request):
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        target_role = request.POST.get('target_role', '')
        if message_text:
            users = User.objects.exclude(role='admin')
            if target_role:
                users = users.filter(role=target_role)
            for u in users:
                Notification.objects.create(user=u, message=f'📢 {message_text}')
            messages.success(request, f'Announcement sent to {users.count()} users!')
        return redirect('admin_announcements')
    return render(request, 'admin_panel/announcements.html')


@login_required
@role_required('admin')
def admin_applications(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    applications = Application.objects.select_related('student', 'job').all()
    
    if query:
        applications = applications.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(job__title__icontains=query) |
            Q(job__company__icontains=query)
        )
    if status_filter:
        applications = applications.filter(status=status_filter)
        
    return render(request, 'admin_panel/applications.html', {
        'applications': applications.order_by('-applied_at'),
        'query': query,
        'status_filter': status_filter
    })
