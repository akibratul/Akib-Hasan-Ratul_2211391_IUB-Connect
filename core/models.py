from django.db import models
from django.contrib.auth.models import AbstractUser
import json


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def display_initial(self):
        return (self.first_name or self.username or '?')[0].upper()

    @property
    def full_display_name(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.CharField(max_length=50, blank=True, default='CSE')
    year = models.IntegerField(default=1)
    skills = models.TextField(default='[]', help_text='JSON array of skills')
    interests = models.TextField(blank=True, default='')

    def get_skills_list(self):
        try:
            return json.loads(self.skills)
        except:
            return []

    def set_skills_list(self, skills_list):
        self.skills = json.dumps(skills_list)

    def __str__(self):
        return f"Student: {self.user.full_display_name} ({self.department})"


class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni_profile')
    graduation_year = models.IntegerField(default=2020)
    profession = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return f"Alumni: {self.user.full_display_name} ({self.profession})"


class Resource(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return self.title


class Job(models.Model):
    JOB_TYPES = [
        ('job', 'Job'),
        ('internship', 'Internship'),
    ]
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    skills_required = models.TextField(default='[]', help_text='JSON array')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='job')
    deadline = models.DateTimeField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_skills_list(self):
        try:
            return json.loads(self.skills_required)
        except:
            return []

    def set_skills_list(self, skills_list):
        self.skills_required = json.dumps(skills_list)

    def __str__(self):
        return f"{self.title} at {self.company}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cv = models.FileField(upload_to='cvs/')
    cover_letter = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.full_display_name} for {self.job.title} ({self.status})"


class MentorshipSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_as_student')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_as_mentor')
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_display_name} → {self.mentor.full_display_name} ({self.status})"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.full_display_name} → {self.receiver.full_display_name}: {self.message[:50]}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{'📬' if not self.read else '📭'} {self.user.full_display_name}: {self.message[:50]}"
