#!/usr/bin/env python3
"""
ProjectMeats Deployment Issues Management Console
===============================================

Master control system for managing deployment issues, agent assignments,
and automated remediation. This console provides unified access to all
deployment issue management capabilities.

Features:
- Centralized issue creation and tracking
- Automated agent assignment and workload management
- SLA monitoring and breach escalation
- Progress reporting and metrics
- Integration with GitHub for issue management

Usage:
    python deployment_issues_console.py [COMMAND] [OPTIONS]

Commands:
    analyze      - Analyze deployment system and identify issues
    create       - Create GitHub Issues for identified problems  
    assign       - Assign issues to appropriate agents
    monitor      - Monitor issue status and SLA compliance
    report       - Generate comprehensive status reports
    escalate     - Handle SLA breaches and escalations
    dashboard    - Launch interactive dashboard
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional


class DeploymentIssuesConsole:
    """Master console for deployment issues management"""
    
    def __init__(self, repo_name: str = "Vacilator/ProjectMeats", github_token: str = None):
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        
        # Available commands and their descriptions
        self.commands = {
            'analyze': {
                'description': 'Analyze deployment system and identify critical issues',
                'script': None,  # Built-in function
                'args': ['--full', '--security-only', '--output']
            },
            'create': {
                'description': 'Create GitHub Issues for identified deployment problems',
                'script': 'create_deployment_issues.py',
                'args': ['--dry-run', '--repo', '--token']
            },
            'assign': {
                'description': 'Assign issues to appropriate agents automatically',
                'script': 'agent_assignment_system.py',
                'args': ['--assign-all', '--rebalance', '--dry-run', '--repo', '--token']
            },
            'monitor': {
                'description': 'Monitor issue status, SLA compliance, and escalations',
                'script': 'monitor_deployment_issues.py', 
                'args': ['--report', '--escalate', '--update-backlog', '--repo', '--token']
            },
            'report': {
                'description': 'Generate comprehensive status and progress reports',
                'script': None,  # Built-in function
                'args': ['--format', '--output', '--include-metrics']
            },
            'dashboard': {
                'description': 'Launch interactive web dashboard for issue management',
                'script': None,  # Built-in function
                'args': ['--port', '--host', '--debug']
            }
        }
    
    def print_banner(self):
        """Print console banner"""
        print("\\n" + "="*80)
        print("🚀 PROJECTMEATS DEPLOYMENT ISSUES MANAGEMENT CONSOLE")
        print("="*80)
        print("Centralized command center for deployment system remediation")
        print(f"Repository: {self.repo_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("="*80)
    
    def print_usage(self):
        """Print usage information"""
        print("\\n📚 USAGE:")
        print(f"   python {os.path.basename(__file__)} [COMMAND] [OPTIONS]")
        
        print("\\n🎯 AVAILABLE COMMANDS:")
        for cmd, info in self.commands.items():
            print(f"   {cmd:12} - {info['description']}")
        
        print("\\n🔧 GLOBAL OPTIONS:")
        print("   --repo REPO        GitHub repository (default: Vacilator/ProjectMeats)")
        print("   --token TOKEN      GitHub personal access token") 
        print("   --help             Show this help message")
        print("   --verbose          Enable verbose output")
        print("   --dry-run          Show what would be done without executing")
        
        print("\\n📋 EXAMPLE WORKFLOWS:")
        print("   # Complete deployment cleanup workflow")
        print(f"   python {os.path.basename(__file__)} analyze --full")
        print(f"   python {os.path.basename(__file__)} create --dry-run")
        print(f"   python {os.path.basename(__file__)} create")
        print(f"   python {os.path.basename(__file__)} assign --assign-all")
        print(f"   python {os.path.basename(__file__)} monitor --report")
        print("")
        print("   # Daily monitoring workflow")
        print(f"   python {os.path.basename(__file__)} monitor --escalate --update-backlog")
        print(f"   python {os.path.basename(__file__)} report --include-metrics")
        print("")
        print("   # Emergency response workflow")
        print(f"   python {os.path.basename(__file__)} analyze --security-only")
        print(f"   python {os.path.basename(__file__)} create")
        print(f"   python {os.path.basename(__file__)} assign --assign-all")
        print(f"   python {os.path.basename(__file__)} monitor --escalate")
    
    def analyze_deployment_system(self, args) -> Dict[str, Any]:
        """Analyze deployment system and identify issues"""
        print("\\n🔍 ANALYZING DEPLOYMENT SYSTEM")
        print("-" * 50)
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'issues_identified': [],
            'summary': {},
            'recommendations': []
        }
        
        print("📊 Scanning deployment files...")
        
        # Count deployment files
        deployment_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(keyword in file.lower() for keyword in ['deploy', 'orchestrator']):
                    deployment_files.append(os.path.join(root, file))
        
        print(f"   Found {len(deployment_files)} deployment-related files")
        
        # Check for specific issues
        issues = []
        
        # Issue 1: Script proliferation
        if len(deployment_files) > 20:
            issues.append({
                'id': 'DEPLOY-001',
                'title': 'Script Proliferation Crisis',
                'severity': 'CRITICAL',
                'count': len(deployment_files),
                'description': f'Found {len(deployment_files)} deployment files - severe proliferation'
            })
        
        # Issue 2: Large files (potential monoliths)
        large_files = []
        for file_path in deployment_files:
            try:
                if os.path.getsize(file_path) > 100000:  # >100KB
                    large_files.append((file_path, os.path.getsize(file_path)))
            except:
                pass
        
        if large_files:
            issues.append({
                'id': 'DEPLOY-002', 
                'title': 'Monolithic Deployment Scripts',
                'severity': 'HIGH',
                'files': large_files,
                'description': f'Found {len(large_files)} oversized deployment files'
            })
        
        # Issue 3: Configuration files
        config_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.startswith('.env') or 'config' in file.lower():
                    config_files.append(os.path.join(root, file))
        
        if len(config_files) > 10:
            issues.append({
                'id': 'CONFIG-001',
                'title': 'Configuration Management Chaos',
                'severity': 'CRITICAL',
                'count': len(config_files),
                'description': f'Found {len(config_files)} configuration files'
            })
        
        # Issue 4: Test files proliferation
        test_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.startswith('test_') and ('deploy' in file or 'test' in root):
                    test_files.append(os.path.join(root, file))
        
        if len(test_files) > 15:
            issues.append({
                'id': 'TEST-001',
                'title': 'Testing Infrastructure Chaos',
                'severity': 'HIGH', 
                'count': len(test_files),
                'description': f'Found {len(test_files)} deployment test files'
            })
        
        analysis_results['issues_identified'] = issues
        analysis_results['summary'] = {
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i['severity'] == 'CRITICAL']),
            'high_issues': len([i for i in issues if i['severity'] == 'HIGH']),
            'deployment_files': len(deployment_files),
            'config_files': len(config_files),
            'test_files': len(test_files)
        }
        
        # Generate recommendations
        recommendations = []
        if len(deployment_files) > 20:
            recommendations.append("URGENT: Consolidate deployment scripts immediately")
        if len(config_files) > 10:
            recommendations.append("CRITICAL: Implement configuration hierarchy")
        if len(test_files) > 15:
            recommendations.append("HIGH: Consolidate test infrastructure")
        
        analysis_results['recommendations'] = recommendations
        
        # Print results
        print("\\n📋 ANALYSIS RESULTS:")
        print(f"   Total Issues: {analysis_results['summary']['total_issues']}")
        print(f"   Critical Issues: {analysis_results['summary']['critical_issues']}")
        print(f"   High Priority Issues: {analysis_results['summary']['high_issues']}")
        
        print("\\n🚨 CRITICAL ISSUES FOUND:")
        for issue in issues:
            severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟡", "MEDIUM": "🟢"}[issue['severity']]
            print(f"   {severity_emoji} {issue['id']}: {issue['title']}")
            print(f"      {issue['description']}")
        
        if recommendations:
            print("\\n💡 IMMEDIATE RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        # Save analysis results
        if hasattr(args, 'output') and args.output:
            with open(args.output, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            print(f"\\n💾 Analysis results saved to: {args.output}")
        
        return analysis_results
    
    def generate_comprehensive_report(self, args) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        print("\\n📊 GENERATING COMPREHENSIVE REPORT")
        print("-" * 50)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'comprehensive_status',
            'sections': {}
        }
        
        # System overview
        print("📋 Gathering system overview...")
        report['sections']['system_overview'] = {
            'repository': self.repo_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'console_version': '1.0.0'
        }
        
        # File statistics
        print("📁 Analyzing file statistics...")
        deployment_files = 0
        config_files = 0
        test_files = 0
        doc_files = 0
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(keyword in file.lower() for keyword in ['deploy', 'orchestrator']):
                    deployment_files += 1
                elif file.startswith('.env') or 'config' in file.lower():
                    config_files += 1
                elif file.startswith('test_'):
                    test_files += 1
                elif file.endswith('.md'):
                    doc_files += 1
        
        report['sections']['file_statistics'] = {
            'deployment_files': deployment_files,
            'configuration_files': config_files,
            'test_files': test_files,
            'documentation_files': doc_files,
            'total_files': deployment_files + config_files + test_files + doc_files
        }
        
        # Issue tracking status
        print("📋 Checking issue tracking status...")
        # This would integrate with GitHub API to get actual issue data
        report['sections']['issue_tracking'] = {
            'total_issues': 0,  # Would be populated from GitHub
            'open_issues': 0,
            'assigned_issues': 0,
            'sla_breaches': 0,
            'note': 'GitHub integration required for live data'
        }
        
        # Recommendations
        recommendations = []
        if deployment_files > 20:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Consolidate deployment scripts',
                'impact': 'Reduce operational complexity'
            })
        if config_files > 10:
            recommendations.append({
                'priority': 'CRITICAL', 
                'action': 'Implement configuration hierarchy',
                'impact': 'Improve security and consistency'
            })
        if test_files > 15:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Consolidate test infrastructure', 
                'impact': 'Improve test efficiency and reliability'
            })
        
        report['sections']['recommendations'] = recommendations
        
        # Print report summary
        print("\\n📊 REPORT SUMMARY:")
        stats = report['sections']['file_statistics']
        print(f"   Deployment Files: {stats['deployment_files']}")
        print(f"   Configuration Files: {stats['configuration_files']}")
        print(f"   Test Files: {stats['test_files']}")
        print(f"   Documentation Files: {stats['documentation_files']}")
        
        if recommendations:
            print("\\n🎯 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. [{rec['priority']}] {rec['action']}")
                print(f"      Impact: {rec['impact']}")
        
        # Save report
        if hasattr(args, 'output') and args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\\n💾 Report saved to: {args.output}")
        
        return report
    
    def execute_script_command(self, script_name: str, args_list: List[str]) -> bool:
        """Execute external script command"""
        try:
            cmd = ['python', script_name] + args_list
            print(f"\\n🚀 Executing: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                print("📤 OUTPUT:")
                print(result.stdout)
            
            if result.stderr:
                print("⚠️ ERRORS:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error executing {script_name}: {e}")
            return False
    
    def run_command(self, command: str, args) -> bool:
        """Run specified command"""
        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            return False
        
        cmd_info = self.commands[command]
        
        # Handle built-in commands
        if cmd_info['script'] is None:
            if command == 'analyze':
                self.analyze_deployment_system(args)
                return True
            elif command == 'report':
                self.generate_comprehensive_report(args)
                return True
            elif command == 'dashboard':
                print("🌐 Dashboard functionality would be implemented here")
                print("   Features: Interactive web interface for issue management")
                return True
        else:
            # Handle external script commands
            script_args = []
            
            # Add repo and token if available
            if self.repo_name and '--repo' in cmd_info['args']:
                script_args.extend(['--repo', self.repo_name])
            if self.github_token and '--token' in cmd_info['args']:
                script_args.extend(['--token', self.github_token])
            
            # Add dry-run if specified
            if hasattr(args, 'dry_run') and args.dry_run and '--dry-run' in cmd_info['args']:
                script_args.append('--dry-run')
            
            # Add command-specific arguments
            if command == 'create' and '--dry-run' not in script_args:
                pass  # Create issues for real
            elif command == 'assign':
                script_args.append('--assign-all')
            elif command == 'monitor':
                script_args.extend(['--report', '--escalate', '--update-backlog'])
            
            return self.execute_script_command(cmd_info['script'], script_args)
        
        return False


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="ProjectMeats Deployment Issues Management Console",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Global options
    parser.add_argument('--repo', default='Vacilator/ProjectMeats', help='GitHub repository')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze deployment system')
    analyze_parser.add_argument('--full', action='store_true', help='Full system analysis')
    analyze_parser.add_argument('--security-only', action='store_true', help='Security-focused analysis')
    analyze_parser.add_argument('--output', help='Save analysis to file')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create GitHub Issues')
    
    # Assign command
    assign_parser = subparsers.add_parser('assign', help='Assign issues to agents')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor issue status')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='Report format')
    report_parser.add_argument('--output', help='Save report to file')
    report_parser.add_argument('--include-metrics', action='store_true', help='Include detailed metrics')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch web dashboard')
    dashboard_parser.add_argument('--port', type=int, default=8080, help='Dashboard port')
    dashboard_parser.add_argument('--host', default='localhost', help='Dashboard host')
    
    args = parser.parse_args()
    
    # Initialize console
    console = DeploymentIssuesConsole(args.repo, args.token)
    console.print_banner()
    
    # Handle no command
    if not args.command:
        console.print_usage()
        return
    
    # Verbose mode
    if args.verbose:
        print(f"🔧 Running in verbose mode")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🔑 GitHub token: {'Present' if console.github_token else 'Not provided'}")
    
    # Execute command
    print(f"\\n⚡ Executing command: {args.command}")
    success = console.run_command(args.command, args)
    
    if success:
        print(f"\\n✅ Command '{args.command}' completed successfully!")
        
        # Suggest next steps
        if args.command == 'analyze':
            print("\\n🎯 SUGGESTED NEXT STEPS:")
            print("   1. Create GitHub Issues: python deployment_issues_console.py create")
            print("   2. Assign to agents: python deployment_issues_console.py assign") 
            print("   3. Monitor progress: python deployment_issues_console.py monitor")
        elif args.command == 'create':
            print("\\n🎯 SUGGESTED NEXT STEPS:")
            print("   1. Assign to agents: python deployment_issues_console.py assign")
            print("   2. Monitor progress: python deployment_issues_console.py monitor")
        elif args.command == 'assign':
            print("\\n🎯 SUGGESTED NEXT STEPS:")
            print("   1. Monitor progress: python deployment_issues_console.py monitor")
            print("   2. Generate report: python deployment_issues_console.py report")
    else:
        print(f"\\n❌ Command '{args.command}' failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()