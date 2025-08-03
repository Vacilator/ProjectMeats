#!/usr/bin/env python3
"""
ProjectMeats Repository Cleanup Script
=====================================

This script identifies and cleans redundancies, duplicates, unused items, and backups
in the ProjectMeats repository. It can be used by AI deployment orchestrator to
maintain a clean production-ready codebase.

Usage:
    python cleanup_redundancies.py --analyze    # Analyze redundancies (dry run)
    python cleanup_redundancies.py --clean      # Clean redundant files
    python cleanup_redundancies.py --help       # Show help

Features:
- Identifies duplicate deployment scripts
- Finds redundant documentation files
- Detects unused test files
- Locates backup and temporary files
- Preserves core application files
- Generates cleanup report
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class RedundancyAnalyzer:
    """Analyzes and cleans repository redundancies"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'redundant_files': {},
            'duplicate_files': {},
            'backup_files': [],
            'unused_files': [],
            'preserved_files': [],
            'cleanup_summary': {}
        }
        
        # Core files that should never be removed
        self.core_files = {
            'setup.py',
            'Makefile', 
            'README.md',
            '.gitignore',
            'ai_deployment_orchestrator.py',  # Being enhanced in PR 93
            'ProjectMeats.code-workspace',
        }
        
        # Core directories that should be preserved
        self.core_directories = {
            'backend',
            'frontend', 
            'docs',
            'powerapps_export',
            '.git',
            '.github',
            '.vscode'
        }
        
        # Patterns for redundant files
        self.redundant_patterns = {
            'deployment_scripts': [
                'deploy_*.py', 'deploy_*.sh', '*_deploy.*', 
                'one_click_deploy.*', 'quick_deploy.*', 'complete_deployment.*',
                'enhanced_deployment.*', 'master_deploy.*'
            ],
            'test_files': [
                'test_*.py', 'test_*.sh', '*_test.*',
                'validate_*.py', 'validate_*.sh',
                'verify_*.py', 'verify_*.sh'
            ],
            'documentation': [
                '*_SUMMARY.md', '*_FIX*.md', '*_INSTRUCTIONS.md', 
                '*_GUIDE.md', '*_README.md', 'DEPRECATED_*.md'
            ],
            'configuration': [
                'ai_deployment_config.*.json', '*_config.json',
                'deployment_*.json', '*_state.json'
            ],
            'setup_scripts': [
                'setup_*.py', 'setup_*.bat', '*_setup.*'
            ]
        }
        
        # Essential files to keep in each category
        self.essential_files = {
            'deployment_scripts': ['ai_deployment_orchestrator.py'],
            'test_files': [],  # Keep tests that are in backend/frontend dirs
            'documentation': ['README.md', 'PRODUCTION_DEPLOYMENT.md'],
            'configuration': ['ai_deployment_config.json'],
            'setup_scripts': ['setup.py']
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def find_duplicate_files(self) -> Dict[str, List[Path]]:
        """Find files with identical content"""
        hash_map = {}
        duplicates = {}
        
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file() and not self.is_in_core_directory(file_path):
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    if file_hash in hash_map:
                        if file_hash not in duplicates:
                            duplicates[file_hash] = [hash_map[file_hash]]
                        duplicates[file_hash].append(file_path)
                    else:
                        hash_map[file_hash] = file_path
        
        return duplicates

    def is_in_core_directory(self, file_path: Path) -> bool:
        """Check if file is in a core directory that should be preserved"""
        relative_path = file_path.relative_to(self.repo_root)
        return any(str(relative_path).startswith(core_dir) for core_dir in self.core_directories)

    def categorize_redundant_files(self) -> Dict[str, List[Path]]:
        """Categorize files by redundancy type"""
        redundant_files = {category: [] for category in self.redundant_patterns}
        
        for file_path in self.repo_root.glob('*'):
            if file_path.is_file() and file_path.name not in self.core_files:
                for category, patterns in self.redundant_patterns.items():
                    for pattern in patterns:
                        if file_path.match(pattern):
                            redundant_files[category].append(file_path)
                            break
        
        return redundant_files

    def find_backup_files(self) -> List[Path]:
        """Find backup and temporary files"""
        backup_patterns = ['*.bak', '*.backup', '*.old', '*.tmp', '*~', '*.orig']
        backup_files = []
        
        for pattern in backup_patterns:
            backup_files.extend(self.repo_root.rglob(pattern))
        
        return backup_files

    def analyze_redundancies(self) -> Dict:
        """Perform complete redundancy analysis"""
        print(f"{Colors.BLUE}🔍 Analyzing repository redundancies...{Colors.END}")
        
        # Find duplicate files
        duplicates = self.find_duplicate_files()
        self.analysis_report['duplicate_files'] = {
            hash_val: [str(p) for p in paths] for hash_val, paths in duplicates.items()
        }
        
        # Categorize redundant files
        redundant_files = self.categorize_redundant_files()
        self.analysis_report['redundant_files'] = {
            category: [str(p) for p in paths] for category, paths in redundant_files.items()
        }
        
        # Find backup files
        backup_files = self.find_backup_files()
        self.analysis_report['backup_files'] = [str(p) for p in backup_files]
        
        # Calculate totals
        total_redundant = sum(len(paths) for paths in redundant_files.values())
        total_duplicates = sum(len(paths) - 1 for paths in duplicates.values())  # -1 because we keep one copy
        total_backups = len(backup_files)
        
        self.analysis_report['cleanup_summary'] = {
            'total_redundant_files': total_redundant,
            'total_duplicate_files': total_duplicates,
            'total_backup_files': total_backups,
            'total_cleanable_files': total_redundant + total_duplicates + total_backups
        }
        
        return self.analysis_report

    def print_analysis_report(self):
        """Print detailed analysis report"""
        print(f"\n{Colors.BOLD}📊 Repository Redundancy Analysis Report{Colors.END}")
        print("=" * 60)
        
        summary = self.analysis_report['cleanup_summary']
        print(f"\n{Colors.CYAN}Summary:{Colors.END}")
        print(f"  📁 Total redundant files: {summary['total_redundant_files']}")
        print(f"  🔄 Total duplicate files: {summary['total_duplicate_files']}")
        print(f"  🗃️  Total backup files: {summary['total_backup_files']}")
        print(f"  🧹 Total cleanable files: {summary['total_cleanable_files']}")
        
        # Redundant files by category
        print(f"\n{Colors.YELLOW}Redundant Files by Category:{Colors.END}")
        for category, files in self.analysis_report['redundant_files'].items():
            if files:
                print(f"  {category}: {len(files)} files")
                essential = self.essential_files.get(category, [])
                for file_path in files[:5]:  # Show first 5
                    file_name = Path(file_path).name
                    status = "KEEP" if file_name in essential else "REMOVE"
                    color = Colors.GREEN if status == "KEEP" else Colors.RED
                    print(f"    {color}[{status}]{Colors.END} {file_name}")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more")
        
        # Duplicate files
        if self.analysis_report['duplicate_files']:
            print(f"\n{Colors.YELLOW}Duplicate Files:{Colors.END}")
            for hash_val, paths in list(self.analysis_report['duplicate_files'].items())[:3]:
                print(f"  Duplicate set (hash: {hash_val[:8]}...):")
                for i, path in enumerate(paths):
                    status = "KEEP" if i == 0 else "REMOVE"
                    color = Colors.GREEN if status == "KEEP" else Colors.RED
                    print(f"    {color}[{status}]{Colors.END} {Path(path).name}")
        
        # Backup files
        if self.analysis_report['backup_files']:
            print(f"\n{Colors.YELLOW}Backup Files:{Colors.END}")
            for backup_file in self.analysis_report['backup_files'][:10]:
                print(f"  {Colors.RED}[REMOVE]{Colors.END} {Path(backup_file).name}")
            if len(self.analysis_report['backup_files']) > 10:
                print(f"  ... and {len(self.analysis_report['backup_files']) - 10} more")

    def generate_cleanup_plan(self) -> List[Dict]:
        """Generate a structured cleanup plan"""
        cleanup_plan = []
        
        # Add redundant files to cleanup plan
        for category, files in self.analysis_report['redundant_files'].items():
            essential = self.essential_files.get(category, [])
            for file_path in files:
                file_name = Path(file_path).name
                if file_name not in essential:
                    cleanup_plan.append({
                        'action': 'remove',
                        'file': file_path,
                        'reason': f'Redundant {category}',
                        'category': category
                    })
        
        # Add duplicate files to cleanup plan (keep first, remove others)
        for hash_val, paths in self.analysis_report['duplicate_files'].items():
            for path in paths[1:]:  # Skip first file (keep it)
                cleanup_plan.append({
                    'action': 'remove',
                    'file': path,
                    'reason': 'Duplicate file',
                    'category': 'duplicates'
                })
        
        # Add backup files to cleanup plan
        for backup_file in self.analysis_report['backup_files']:
            cleanup_plan.append({
                'action': 'remove',
                'file': backup_file,
                'reason': 'Backup/temporary file',
                'category': 'backups'
            })
        
        return cleanup_plan

    def save_report(self, output_file: Path):
        """Save analysis report to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.analysis_report, f, indent=2)
        print(f"\n{Colors.GREEN}📄 Analysis report saved to: {output_file}{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description='Clean ProjectMeats repository redundancies')
    parser.add_argument('--analyze', action='store_true', 
                       help='Analyze redundancies (dry run)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean redundant files')
    parser.add_argument('--report', type=str, default='cleanup_analysis.json',
                       help='Output file for analysis report')
    
    args = parser.parse_args()
    
    if not args.analyze and not args.clean:
        parser.print_help()
        return
    
    repo_root = Path(__file__).parent
    analyzer = RedundancyAnalyzer(repo_root)
    
    if args.analyze:
        # Perform analysis
        analyzer.analyze_redundancies()
        analyzer.print_analysis_report()
        analyzer.save_report(Path(args.report))
        
        print(f"\n{Colors.CYAN}💡 Next steps:{Colors.END}")
        print(f"  1. Review the analysis report: {args.report}")
        print(f"  2. Run cleanup: python cleanup_redundancies.py --clean")
        print(f"  3. Verify with: git status")
    
    elif args.clean:
        # Load existing analysis or create new one
        try:
            if Path(args.report).exists():
                with open(args.report) as f:
                    analyzer.analysis_report = json.load(f)
                print(f"{Colors.GREEN}📄 Loaded analysis from: {args.report}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  No analysis found, performing analysis first...{Colors.END}")
                analyzer.analyze_redundancies()
        except Exception as e:
            print(f"{Colors.RED}❌ Error loading analysis: {e}{Colors.END}")
            return
        
        # Generate and execute cleanup plan
        cleanup_plan = analyzer.generate_cleanup_plan()
        
        if not cleanup_plan:
            print(f"{Colors.GREEN}✅ No files to clean - repository is already clean!{Colors.END}")
            return
        
        print(f"\n{Colors.YELLOW}🧹 Cleanup Plan: {len(cleanup_plan)} files to remove{Colors.END}")
        
        # Ask for confirmation
        response = input(f"\n{Colors.BOLD}Proceed with cleanup? (y/N): {Colors.END}")
        if response.lower() != 'y':
            print(f"{Colors.YELLOW}⚠️  Cleanup cancelled{Colors.END}")
            return
        
        # Execute cleanup
        removed_count = 0
        for item in cleanup_plan:
            try:
                file_path = Path(item['file'])
                if file_path.exists():
                    file_path.unlink()
                    removed_count += 1
                    print(f"  {Colors.RED}🗑️  Removed:{Colors.END} {file_path.name}")
            except Exception as e:
                print(f"  {Colors.RED}❌ Error removing {file_path.name}: {e}{Colors.END}")
        
        print(f"\n{Colors.GREEN}✅ Cleanup completed: {removed_count} files removed{Colors.END}")
        print(f"{Colors.CYAN}💡 Run 'git status' to see changes{Colors.END}")

if __name__ == '__main__':
    main()