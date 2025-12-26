"""
TaskFlow Models

These models define the data structure for your task management system.

Key Insight: You only define the structure here. Everything else
(forms, tables, API endpoints) generates automatically via
Adaptive Convergence.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Project(models.Model):
    """
    A project contains multiple tasks.
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Project name"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed project description"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        help_text="Current project status"
    )
    
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project start date"
    )
    
    deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Project deadline"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Deadline must be after start date
        if self.start_date and self.deadline:
            if self.deadline < self.start_date:
                raise ValidationError({
                    'deadline': 'Deadline must be after start date'
                })


class TeamMember(models.Model):
    """
    Team members who can be assigned to tasks.
    """
    ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('manager', 'Project Manager'),
        ('qa', 'QA Tester'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Full name"
    )
    
    email = models.EmailField(
        unique=True,
        help_text="Email address"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='developer',
        help_text="Team member role"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this member currently active?"
    )
    
    joined_at = models.DateField(
        default=timezone.now,
        help_text="Date joined the team"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.role})"


class Tag(models.Model):
    """
    Tags for categorizing tasks.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Tag name"
    )
    
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color code (e.g., #3B82F6)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Individual tasks within projects.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Brief task description"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed task description"
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Project this task belongs to"
    )
    
    assigned_to = models.ForeignKey(
        TeamMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="Team member assigned to this task"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Task priority level"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        help_text="Current task status"
    )
    
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='tasks',
        help_text="Tags for categorization"
    )
    
    estimated_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated hours to complete"
    )
    
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Task due date"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When task was completed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['project', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Due date validation
        if self.due_date and self.due_date < timezone.now().date():
            raise ValidationError({
                'due_date': 'Due date cannot be in the past'
            })
        
        # Can't assign tasks to archived projects
        if self.project and self.project.status == 'archived':
            raise ValidationError({
                'project': 'Cannot create tasks for archived projects'
            })
    
    def save(self, *args, **kwargs):
        """Auto-set completed_at when status changes to done"""
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
        
        super().save(*args, **kwargs)