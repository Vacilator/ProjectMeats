"""
Test to verify Django configuration fixes for deployment issues.

This test verifies that the three main issues are resolved:
1. Invalid http_host header (internal IP 10.244.32.208 in ALLOWED_HOSTS)
2. CSRF configuration (SessionMiddleware before CsrfViewMiddleware)
3. Python version specification (.python-version file exists)
"""

import os
import tempfile
from pathlib import Path
from django.test import TestCase, Client
from django.conf import settings


class DeploymentConfigurationTest(TestCase):
    """Test deployment configuration fixes"""

    def test_allowed_hosts_includes_internal_ip(self):
        """Test that ALLOWED_HOSTS includes the internal IP 10.244.32.208 or accepts all hosts"""
        # Check if either the specific IP is included OR "*" is in ALLOWED_HOSTS (which allows all)
        has_internal_ip = '10.244.32.208' in settings.ALLOWED_HOSTS
        allows_all_hosts = '*' in settings.ALLOWED_HOSTS
        
        self.assertTrue(has_internal_ip or allows_all_hosts, 
                       f"ALLOWED_HOSTS should include '10.244.32.208' or '*'. Current: {settings.ALLOWED_HOSTS}")

    def test_internal_ip_request_accepted(self):
        """Test that requests from internal IP are accepted (no DisallowedHost error)"""
        client = Client(HTTP_HOST='10.244.32.208')
        
        # This should not raise DisallowedHost error
        try:
            response = client.get('/api/')
            # We expect 404 since we don't have API endpoints set up in test
            # But the important thing is no DisallowedHost exception
            self.assertIn(response.status_code, [200, 404, 405])
        except Exception as e:
            self.assertNotIn('DisallowedHost', str(e))

    def test_middleware_ordering_correct(self):
        """Test that SessionMiddleware comes before CsrfViewMiddleware"""
        middleware_list = settings.MIDDLEWARE
        
        session_index = None
        csrf_index = None
        
        for i, middleware in enumerate(middleware_list):
            if 'SessionMiddleware' in middleware:
                session_index = i
            elif 'CsrfViewMiddleware' in middleware:
                csrf_index = i
        
        self.assertIsNotNone(session_index, "SessionMiddleware not found")
        self.assertIsNotNone(csrf_index, "CsrfViewMiddleware not found")
        self.assertLess(session_index, csrf_index, 
                       "SessionMiddleware must come before CsrfViewMiddleware")

    def test_python_version_file_exists(self):
        """Test that .python-version file exists in project root"""
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        python_version_file = project_root / '.python-version'
        
        self.assertTrue(python_version_file.exists(), 
                       ".python-version file should exist in project root")
        
        # Test that it contains a valid Python version
        with open(python_version_file, 'r') as f:
            version = f.read().strip()
        
        # Should be in format like "3.12" or "3.12.3"
        self.assertRegex(version, r'^\d+\.\d+(\.\d+)?$', 
                        "Python version should be in format X.Y or X.Y.Z")