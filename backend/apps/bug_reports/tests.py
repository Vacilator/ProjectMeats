"""
Bug Reports tests.

Tests for the bug reporting feature including GitHub integration.
"""
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import BugReport, BugReportPriority, BugReportStatus
from .github_service import GitHubIssueService


class BugReportModelTest(TestCase):
    """Test the BugReport model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_bug_report_creation(self):
        """Test creating a bug report."""
        bug_report = BugReport.objects.create(
            reporter=self.user,
            reporter_email=self.user.email,
            title='Test Bug',
            description='This is a test bug description.',
            priority=BugReportPriority.HIGH,
            current_url='http://localhost:3000/dashboard',
            page_title='Dashboard',
            browser_info={'userAgent': 'Test Browser'},
            application_state={'test': 'data'}
        )
        
        self.assertEqual(bug_report.title, 'Test Bug')
        self.assertEqual(bug_report.reporter, self.user)
        self.assertEqual(bug_report.priority, BugReportPriority.HIGH)
        self.assertEqual(bug_report.status, BugReportStatus.PENDING)
        self.assertFalse(bug_report.is_submitted_to_github)
        self.assertEqual(str(bug_report), 'Bug Report #1: Test Bug')
    
    def test_bug_report_properties(self):
        """Test bug report computed properties."""
        bug_report = BugReport.objects.create(
            reporter=self.user,
            reporter_email=self.user.email,
            title='Test Bug',
            description='Test description',
            priority=BugReportPriority.CRITICAL,
            status=BugReportStatus.SUBMITTED,
            github_issue_number=123
        )
        
        self.assertTrue(bug_report.is_submitted_to_github)
        self.assertEqual(bug_report.priority_display_color, '#dc3545')  # Critical = red


class BugReportAPITest(APITestCase):
    """Test the Bug Reports API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.bug_report = BugReport.objects.create(
            reporter=self.user,
            reporter_email=self.user.email,
            title='Existing Bug',
            description='This is an existing bug.',
            priority=BugReportPriority.MEDIUM
        )
    
    def test_list_bug_reports_requires_auth(self):
        """Test that listing bug reports requires authentication."""
        url = reverse('bug-reports-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_user_bug_reports(self):
        """Test that users can see their own bug reports."""
        self.client.force_authenticate(user=self.user)
        url = reverse('bug-reports-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Existing Bug')
    
    def test_staff_can_see_all_bug_reports(self):
        """Test that staff users can see all bug reports."""
        # Create a bug report from another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        BugReport.objects.create(
            reporter=other_user,
            reporter_email=other_user.email,
            title='Other User Bug',
            description='Bug from another user.',
            priority=BugReportPriority.LOW
        )
        
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('bug-reports-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Should see both bug reports
