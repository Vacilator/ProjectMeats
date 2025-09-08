#!/usr/bin/env python3
"""
DigitalOcean App Platform Specification Validator
Checks for common issues in app.yaml files including the certificate_id error
"""

import yaml
import sys
import os
from typing import Dict, List, Any

class AppSpecValidator:
    """Validates DigitalOcean App Platform specifications"""
    
    VALID_SERVICE_FIELDS = {
        'name', 'source_dir', 'dockerfile_path', 'github', 'http_port', 
        'instance_count', 'instance_size_slug', 'environment_slug', 'envs',
        'health_check', 'routes', 'run_command', 'build_command'
    }
    
    VALID_STATIC_SITE_FIELDS = {
        'name', 'source_dir', 'github', 'build_command', 'output_dir',
        'index_document', 'error_document', 'environment_slug', 'envs',
        'routes', 'node_version'
    }
    
    INVALID_FIELDS = {'certificate_id', 'ssl_certificate', 'tls_certificate'}
    
    def __init__(self, spec_file: str = 'app.yaml'):
        self.spec_file = spec_file
        self.errors = []
        self.warnings = []
        
    def validate(self) -> bool:
        """Validate the app specification file"""
        if not os.path.exists(self.spec_file):
            self.errors.append(f"Spec file not found: {self.spec_file}")
            return False
            
        try:
            with open(self.spec_file, 'r') as f:
                self.spec = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
            
        self._validate_structure()
        self._check_invalid_fields()
        self._validate_services()
        self._validate_static_sites()
        self._validate_jobs()
        
        return len(self.errors) == 0
        
    def _validate_structure(self):
        """Validate basic structure"""
        required_fields = {'name'}
        for field in required_fields:
            if field not in self.spec:
                self.errors.append(f"Missing required field: {field}")
                
        # Check for reasonable app name
        if 'name' in self.spec:
            name = self.spec['name']
            if not isinstance(name, str) or not name.strip():
                self.errors.append("App name must be a non-empty string")
            elif not name.replace('-', '').replace('_', '').isalnum():
                self.warnings.append("App name should only contain alphanumeric characters, hyphens, and underscores")
                
    def _check_invalid_fields(self):
        """Check for invalid/deprecated fields"""
        def check_dict_for_invalid(obj: Dict[str, Any], path: str = ""):
            for key, value in obj.items():
                if key in self.INVALID_FIELDS:
                    self.errors.append(f"Invalid field '{key}' found at {path}. This field is not supported by DigitalOcean App Platform.")
                if isinstance(value, dict):
                    check_dict_for_invalid(value, f"{path}.{key}")
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            check_dict_for_invalid(item, f"{path}.{key}[{i}]")
                            
        check_dict_for_invalid(self.spec, "root")
        
    def _validate_services(self):
        """Validate services configuration"""
        if 'services' not in self.spec:
            return
            
        services = self.spec['services']
        if not isinstance(services, list):
            self.errors.append("Services must be a list")
            return
            
        for i, service in enumerate(services):
            if not isinstance(service, dict):
                self.errors.append(f"Service {i} must be an object")
                continue
                
            if 'name' not in service:
                self.errors.append(f"Service {i} missing required 'name' field")
                
            # Check for unknown fields
            for field in service.keys():
                if field not in self.VALID_SERVICE_FIELDS:
                    self.warnings.append(f"Service '{service.get('name', i)}' has unknown field: {field}")
                    
    def _validate_static_sites(self):
        """Validate static sites configuration"""
        if 'static_sites' not in self.spec:
            return
            
        static_sites = self.spec['static_sites']
        if not isinstance(static_sites, list):
            self.errors.append("Static sites must be a list")
            return
            
        for i, site in enumerate(static_sites):
            if not isinstance(site, dict):
                self.errors.append(f"Static site {i} must be an object")
                continue
                
            if 'name' not in site:
                self.errors.append(f"Static site {i} missing required 'name' field")
                
            # Check for unknown fields
            for field in site.keys():
                if field not in self.VALID_STATIC_SITE_FIELDS:
                    self.warnings.append(f"Static site '{site.get('name', i)}' has unknown field: {field}")
                    
    def _validate_jobs(self):
        """Validate jobs configuration"""
        if 'jobs' not in self.spec:
            return
            
        jobs = self.spec['jobs']
        if not isinstance(jobs, list):
            self.errors.append("Jobs must be a list")
            return
            
        for i, job in enumerate(jobs):
            if not isinstance(job, dict):
                self.errors.append(f"Job {i} must be an object")
                continue
                
            if 'name' not in job:
                self.errors.append(f"Job {i} missing required 'name' field")
            if 'run_command' not in job:
                self.errors.append(f"Job {i} missing required 'run_command' field")
                
    def print_results(self):
        """Print validation results"""
        print(f"🔍 Validating DigitalOcean App Platform spec: {self.spec_file}")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        if not self.errors and not self.warnings:
            print("\n✅ Validation passed! No issues found.")
        elif not self.errors:
            print(f"\n✅ Validation passed with {len(self.warnings)} warnings.")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors.")
            
        print()
        return len(self.errors) == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate DigitalOcean App Platform specification')
    parser.add_argument('spec_file', nargs='?', default='app.yaml', help='App spec file to validate (default: app.yaml)')
    parser.add_argument('--minimal', action='store_true', help='Also validate app.minimal.yaml')
    
    args = parser.parse_args()
    
    success = True
    
    # Validate main spec file
    validator = AppSpecValidator(args.spec_file)
    if not validator.validate():
        success = False
    validator.print_results()
    
    # Validate minimal spec if requested
    if args.minimal and os.path.exists('app.minimal.yaml'):
        print("\n" + "="*60)
        validator_minimal = AppSpecValidator('app.minimal.yaml')
        if not validator_minimal.validate():
            success = False
        validator_minimal.print_results()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()