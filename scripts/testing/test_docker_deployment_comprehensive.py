#!/usr/bin/env python3
"""
Comprehensive Docker Deployment Testing Suite
============================================

This script provides extensive testing for Docker deployment configurations
to prevent common deployment issues and validate security settings.

Author: ProjectMeats AI Assistant
"""

import os
import sys
import json
import subprocess
import time
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    passed: bool
    message: str
    details: Optional[str] = None

class Colors:
    """Terminal colors for output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DockerDeploymentTester:
    """Comprehensive Docker deployment testing suite"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.test_results: List[TestResult] = []
        self.docker_compose_file = self.project_root / "docker-compose.prod.yml"
        self.env_file = self.project_root / ".env.prod"
        
    def log_test(self, name: str, passed: bool, message: str, details: str = None):
        """Log test result"""
        result = TestResult(name, passed, message, details)
        self.test_results.append(result)
        
        color = Colors.GREEN if passed else Colors.RED
        status = "PASS" if passed else "FAIL"
        
        print(f"{color}[{status}]{Colors.END} {name}: {message}")
        if details:
            print(f"  Details: {details}")
        
        logger.log(logging.INFO if passed else logging.ERROR, f"{name}: {message}")
    
    def run_command(self, command: str, capture_output: bool = True, timeout: int = 30) -> Tuple[int, str, str]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)
    
    def test_docker_availability(self) -> bool:
        """Test Docker daemon availability"""
        exit_code, stdout, stderr = self.run_command("docker info")
        
        if exit_code == 0:
            self.log_test(
                "Docker Availability",
                True,
                "Docker daemon is running and accessible"
            )
            return True
        else:
            self.log_test(
                "Docker Availability",
                False,
                "Docker daemon not accessible",
                stderr
            )
            return False
    
    def test_docker_compose_availability(self) -> bool:
        """Test Docker Compose availability"""
        exit_code, stdout, stderr = self.run_command("docker compose version")
        
        if exit_code == 0:
            self.log_test(
                "Docker Compose Availability",
                True,
                f"Docker Compose available: {stdout.strip()}"
            )
            return True
        else:
            self.log_test(
                "Docker Compose Availability",
                False,
                "Docker Compose not available",
                stderr
            )
            return False
    
    def test_docker_compose_syntax(self) -> bool:
        """Test docker-compose.prod.yml syntax"""
        if not self.docker_compose_file.exists():
            self.log_test(
                "Docker Compose Syntax",
                False,
                "docker-compose.prod.yml not found"
            )
            return False
        
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config --quiet")
        
        if exit_code == 0:
            self.log_test(
                "Docker Compose Syntax",
                True,
                "docker-compose.prod.yml syntax is valid"
            )
            return True
        else:
            self.log_test(
                "Docker Compose Syntax",
                False,
                "docker-compose.prod.yml syntax error",
                stderr
            )
            return False
    
    def test_environment_variables(self) -> bool:
        """Test environment variable configuration"""
        if not self.env_file.exists():
            self.log_test(
                "Environment Variables",
                False,
                ".env.prod file not found"
            )
            return False
        
        # Read environment file
        env_vars = {}
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value.strip('"\'')
        except Exception as e:
            self.log_test(
                "Environment Variables",
                False,
                "Failed to read .env.prod file",
                str(e)
            )
            return False
        
        # Check required variables
        required_vars = [
            'POSTGRES_DB',
            'POSTGRES_USER', 
            'POSTGRES_PASSWORD',
            'REDIS_PASSWORD',
            'DJANGO_SECRET_KEY',
            'DOMAIN'
        ]
        
        missing_vars = []
        weak_passwords = []
        
        for var in required_vars:
            if var not in env_vars:
                missing_vars.append(var)
            elif 'PASSWORD' in var and len(env_vars[var]) < 12:
                weak_passwords.append(var)
        
        if missing_vars:
            self.log_test(
                "Environment Variables",
                False,
                f"Missing required variables: {', '.join(missing_vars)}"
            )
            return False
        
        if weak_passwords:
            self.log_test(
                "Environment Variables",
                False,
                f"Weak passwords detected: {', '.join(weak_passwords)}"
            )
            return False
        
        self.log_test(
            "Environment Variables",
            True,
            f"All {len(required_vars)} required environment variables are properly configured"
        )
        return True
    
    def test_security_configurations(self) -> bool:
        """Test security configurations in docker-compose file"""
        if not self.docker_compose_file.exists():
            return False
        
        try:
            with open(self.docker_compose_file, 'r') as f:
                compose_content = f.read()
        except Exception as e:
            self.log_test(
                "Security Configurations",
                False,
                "Failed to read docker-compose.prod.yml",
                str(e)
            )
            return False
        
        security_checks = {
            'no-new-privileges': 'security_opt:\n      - no-new-privileges:true' in compose_content,
            'read_only_root': 'read_only: true' in compose_content,
            'non_root_user': 'user: "1000:1000"' in compose_content,
            'no_privileged': 'privileged: true' not in compose_content,
            'resource_limits': 'limits:' in compose_content,
            'logging_config': 'logging:' in compose_content,
            'health_checks': 'healthcheck:' in compose_content
        }
        
        passed_checks = sum(security_checks.values())
        total_checks = len(security_checks)
        
        if passed_checks >= total_checks * 0.8:  # 80% threshold
            self.log_test(
                "Security Configurations",
                True,
                f"Security checks passed: {passed_checks}/{total_checks}"
            )
            return True
        else:
            failed_checks = [name for name, passed in security_checks.items() if not passed]
            self.log_test(
                "Security Configurations",
                False,
                f"Security checks failed: {total_checks - passed_checks}/{total_checks}",
                f"Failed checks: {', '.join(failed_checks)}"
            )
            return False
    
    def test_network_configuration(self) -> bool:
        """Test network configuration for proper isolation"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            self.log_test(
                "Network Configuration",
                False,
                "Cannot parse docker-compose configuration",
                stderr
            )
            return False
        
        try:
            config = yaml.safe_load(stdout)
            networks = config.get('networks', {})
            
            has_frontend = 'frontend' in networks
            has_backend = 'backend' in networks
            backend_internal = networks.get('backend', {}).get('internal', False)
            
            if has_frontend and has_backend and backend_internal:
                self.log_test(
                    "Network Configuration",
                    True,
                    "Network isolation properly configured (frontend + internal backend)"
                )
                return True
            else:
                details = []
                if not has_frontend:
                    details.append("missing frontend network")
                if not has_backend:
                    details.append("missing backend network") 
                if not backend_internal:
                    details.append("backend network not internal")
                
                self.log_test(
                    "Network Configuration",
                    False,
                    "Network isolation not properly configured",
                    ", ".join(details)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Network Configuration",
                False,
                "Failed to parse network configuration",
                str(e)
            )
            return False
    
    def test_volume_configuration(self) -> bool:
        """Test volume configuration"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            return False
        
        try:
            config = yaml.safe_load(stdout)
            volumes = config.get('volumes', {})
            
            required_volumes = ['postgres_data', 'redis_data', 'static_files', 'media_files']
            missing_volumes = [vol for vol in required_volumes if vol not in volumes]
            
            if not missing_volumes:
                self.log_test(
                    "Volume Configuration",
                    True,
                    f"All {len(required_volumes)} required volumes are configured"
                )
                return True
            else:
                self.log_test(
                    "Volume Configuration",
                    False,
                    f"Missing volumes: {', '.join(missing_volumes)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Volume Configuration",
                False,
                "Failed to parse volume configuration",
                str(e)
            )
            return False
    
    def test_build_context(self) -> bool:
        """Test build context and Dockerfile existence"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            return False
        
        try:
            config = yaml.safe_load(stdout)
            services = config.get('services', {})
            
            build_services = {}
            for service_name, service_config in services.items():
                if 'build' in service_config:
                    build_config = service_config['build']
                    if isinstance(build_config, str):
                        build_services[service_name] = build_config
                    elif isinstance(build_config, dict):
                        build_services[service_name] = build_config.get('context', '.')
            
            missing_contexts = []
            missing_dockerfiles = []
            
            for service, context in build_services.items():
                context_path = self.project_root / context
                if not context_path.exists():
                    missing_contexts.append(f"{service}: {context}")
                
                # Check for Dockerfile.prod
                dockerfile_path = context_path / "Dockerfile.prod"
                if not dockerfile_path.exists():
                    missing_dockerfiles.append(f"{service}: {context}/Dockerfile.prod")
            
            if missing_contexts or missing_dockerfiles:
                details = []
                if missing_contexts:
                    details.append(f"Missing contexts: {', '.join(missing_contexts)}")
                if missing_dockerfiles:
                    details.append(f"Missing Dockerfiles: {', '.join(missing_dockerfiles)}")
                
                self.log_test(
                    "Build Context",
                    False,
                    "Build configuration issues",
                    "; ".join(details)
                )
                return False
            else:
                self.log_test(
                    "Build Context",
                    True,
                    f"Build contexts and Dockerfiles verified for {len(build_services)} services"
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Build Context",
                False,
                "Failed to parse build configuration",
                str(e)
            )
            return False
    
    def test_health_checks(self) -> bool:
        """Test health check configuration"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            return False
        
        try:
            config = yaml.safe_load(stdout)
            services = config.get('services', {})
            
            critical_services = ['db', 'redis', 'backend', 'nginx']
            services_with_health_checks = []
            services_without_health_checks = []
            
            for service_name in critical_services:
                if service_name in services:
                    if 'healthcheck' in services[service_name]:
                        services_with_health_checks.append(service_name)
                    else:
                        services_without_health_checks.append(service_name)
            
            if not services_without_health_checks:
                self.log_test(
                    "Health Checks",
                    True,
                    f"Health checks configured for all {len(services_with_health_checks)} critical services"
                )
                return True
            else:
                self.log_test(
                    "Health Checks",
                    False,
                    f"Missing health checks for: {', '.join(services_without_health_checks)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Health Checks",
                False,
                "Failed to parse health check configuration",
                str(e)
            )
            return False
    
    def test_resource_limits(self) -> bool:
        """Test resource limits configuration"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            return False
        
        try:
            config = yaml.safe_load(stdout)
            services = config.get('services', {})
            
            services_with_limits = []
            services_without_limits = []
            
            for service_name, service_config in services.items():
                # Skip monitoring and backup services
                if service_name in ['prometheus', 'grafana', 'backup']:
                    continue
                    
                deploy_config = service_config.get('deploy', {})
                resources = deploy_config.get('resources', {})
                limits = resources.get('limits', {})
                
                if limits:
                    services_with_limits.append(service_name)
                else:
                    services_without_limits.append(service_name)
            
            if len(services_with_limits) >= len(services_without_limits):
                self.log_test(
                    "Resource Limits",
                    True,
                    f"Resource limits configured for {len(services_with_limits)} services"
                )
                return True
            else:
                self.log_test(
                    "Resource Limits",
                    False,
                    f"Missing resource limits for: {', '.join(services_without_limits)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Resource Limits",
                False,
                "Failed to parse resource limits configuration",
                str(e)
            )
            return False
    
    def test_monitoring_configuration(self) -> bool:
        """Test monitoring configuration (optional)"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            return False
        
        try:
            config = yaml.safe_load(stdout)
            services = config.get('services', {})
            
            monitoring_services = ['prometheus', 'grafana']
            available_monitoring = [svc for svc in monitoring_services if svc in services]
            
            if available_monitoring:
                # Check if monitoring services have proper profiles
                monitoring_with_profiles = []
                for svc in available_monitoring:
                    profiles = services[svc].get('profiles', [])
                    if 'monitoring' in profiles:
                        monitoring_with_profiles.append(svc)
                
                if len(monitoring_with_profiles) == len(available_monitoring):
                    self.log_test(
                        "Monitoring Configuration",
                        True,
                        f"Monitoring services properly configured with profiles: {', '.join(available_monitoring)}"
                    )
                else:
                    self.log_test(
                        "Monitoring Configuration",
                        False,
                        "Monitoring services missing profile configuration"
                    )
                    return False
            else:
                self.log_test(
                    "Monitoring Configuration",
                    True,
                    "No monitoring services configured (optional)"
                )
            
            return True
                
        except Exception as e:
            self.log_test(
                "Monitoring Configuration",
                False,
                "Failed to parse monitoring configuration",
                str(e)
            )
            return False
    
    def test_backup_configuration(self) -> bool:
        """Test backup configuration"""
        exit_code, stdout, stderr = self.run_command(f"docker compose -f {self.docker_compose_file} config")
        
        if exit_code != 0:
            return False
        
        try:
            config = yaml.safe_load(stdout)
            services = config.get('services', {})
            
            if 'backup' in services:
                backup_service = services['backup']
                
                # Check if backup service has proper configuration
                has_volumes = 'volumes' in backup_service
                has_profiles = 'backup' in backup_service.get('profiles', [])
                has_command = 'command' in backup_service
                
                if has_volumes and has_profiles and has_command:
                    self.log_test(
                        "Backup Configuration",
                        True,
                        "Backup service properly configured"
                    )
                    return True
                else:
                    missing = []
                    if not has_volumes:
                        missing.append("volumes")
                    if not has_profiles:
                        missing.append("profiles")
                    if not has_command:
                        missing.append("command")
                    
                    self.log_test(
                        "Backup Configuration",
                        False,
                        f"Backup service missing: {', '.join(missing)}"
                    )
                    return False
            else:
                self.log_test(
                    "Backup Configuration",
                    False,
                    "No backup service configured"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Backup Configuration",
                False,
                "Failed to parse backup configuration",
                str(e)
            )
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall result"""
        print(f"{Colors.CYAN}{Colors.BOLD}ProjectMeats Docker Deployment Testing Suite{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print()
        
        # Core tests (must pass)
        core_tests = [
            self.test_docker_availability,
            self.test_docker_compose_availability,
            self.test_docker_compose_syntax,
            self.test_environment_variables,
            self.test_security_configurations,
            self.test_network_configuration,
            self.test_volume_configuration,
            self.test_build_context,
            self.test_health_checks
        ]
        
        # Optional tests (warnings only)
        optional_tests = [
            self.test_resource_limits,
            self.test_monitoring_configuration,
            self.test_backup_configuration
        ]
        
        print(f"{Colors.YELLOW}Running core tests...{Colors.END}")
        core_results = []
        for test in core_tests:
            try:
                result = test()
                core_results.append(result)
            except Exception as e:
                self.log_test(test.__name__, False, f"Test failed with exception: {e}")
                core_results.append(False)
        
        print(f"\n{Colors.YELLOW}Running optional tests...{Colors.END}")
        optional_results = []
        for test in optional_tests:
            try:
                result = test()
                optional_results.append(result)
            except Exception as e:
                self.log_test(test.__name__, False, f"Test failed with exception: {e}")
                optional_results.append(False)
        
        # Calculate results
        core_passed = sum(core_results)
        core_total = len(core_results)
        optional_passed = sum(optional_results)
        optional_total = len(optional_results)
        
        print(f"\n{Colors.BOLD}Test Results Summary:{Colors.END}")
        print(f"Core tests: {core_passed}/{core_total} passed")
        print(f"Optional tests: {optional_passed}/{optional_total} passed")
        
        # Overall result
        core_success = core_passed == core_total
        overall_score = (core_passed + optional_passed) / (core_total + optional_total) * 100
        
        if core_success:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ DOCKER DEPLOYMENT TESTS PASSED{Colors.END}")
            print(f"Overall score: {overall_score:.1f}%")
            if optional_passed < optional_total:
                print(f"{Colors.YELLOW}Note: Some optional features are not configured{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ DOCKER DEPLOYMENT TESTS FAILED{Colors.END}")
            print(f"Overall score: {overall_score:.1f}%")
            print(f"{Colors.RED}Core test failures must be addressed before deployment{Colors.END}")
        
        return core_success
    
    def generate_report(self, output_file: Path = None) -> str:
        """Generate detailed test report"""
        if output_file is None:
            output_file = self.project_root / "docker_deployment_test_report.json"
        
        report = {
            "timestamp": time.time(),
            "project_root": str(self.project_root),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r.passed),
            "failed_tests": sum(1 for r in self.test_results if not r.passed),
            "tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.test_results
            ]
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n{Colors.BLUE}Test report saved to: {output_file}{Colors.END}")
            return str(output_file)
        except Exception as e:
            print(f"\n{Colors.RED}Failed to save test report: {e}{Colors.END}")
            return ""

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Docker Deployment Testing Suite")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--report", type=Path, help="Output report file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    project_root = args.project_root or Path.cwd()
    
    tester = DockerDeploymentTester(project_root)
    success = tester.run_all_tests()
    
    # Generate report
    if args.report:
        tester.generate_report(args.report)
    else:
        tester.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()