#!/usr/bin/env python3
"""
ProjectMeats Environment Migration Tool

This script helps migrate existing environment files to the new unified system.
It can read existing .env files and generate equivalent configurations using
the new EnvironmentConfigManager.

Usage:
    python migrate_environment.py --from=backend/.env
    python migrate_environment.py --from=.env.prod --to=new_production.env
    python migrate_environment.py --analyze-all
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


def parse_env_file(file_path: str) -> Dict[str, str]:
    """Parse an environment file and return key-value pairs"""
    env_vars = {}
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return env_vars
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                else:
                    print(f"⚠️  Skipping malformed line {line_num} in {file_path}: {line}")
    
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
    
    return env_vars


def map_legacy_vars_to_config(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Map legacy environment variables to new configuration format"""
    config = {}
    
    # Direct mappings
    mappings = {
        'DEBUG': ('debug', lambda x: x.lower() in ('true', '1', 'yes')),
        'SECRET_KEY': ('secret_key', str),
        'ALLOWED_HOSTS': ('allowed_hosts', str),
        'DATABASE_URL': ('database_url', str),
        'CORS_ALLOWED_ORIGINS': ('cors_origins', str),
        'CSRF_TRUSTED_ORIGINS': ('csrf_trusted_origins', str),
        'COMPANY_NAME': ('company_name', str),
        'COMPANY_EMAIL': ('company_email', str),
        'COMPANY_PHONE': ('company_phone', str),
        'COMPANY_ADDRESS': ('company_address', str),
        'EMAIL_HOST': ('email_host', str),
        'EMAIL_PORT': ('email_port', str),
        'EMAIL_HOST_USER': ('email_user', str),
        'EMAIL_HOST_PASSWORD': ('email_password', str),
        'EMAIL_USE_TLS': ('email_use_tls', lambda x: x.lower() in ('true', '1', 'yes')),
        'STATIC_ROOT': ('static_root', str),
        'MEDIA_ROOT': ('media_root', str),
        'LOG_DIR': ('log_dir', str),
        'BACKUP_DIR': ('backup_dir', str),
        'SECURE_SSL_REDIRECT': ('enable_ssl', lambda x: x.lower() in ('true', '1', 'yes')),
    }
    
    for env_key, (config_key, converter) in mappings.items():
        if env_key in env_vars:
            try:
                config[config_key] = converter(env_vars[env_key])
            except Exception as e:
                print(f"⚠️  Error converting {env_key}: {e}")
                config[config_key] = env_vars[env_key]
    
    # Extract database info from DATABASE_URL if present
    if 'database_url' in config:
        db_url = config['database_url']
        if db_url.startswith('postgresql://'):
            try:
                # Parse postgresql://user:password@host:port/database
                url_parts = db_url.replace('postgresql://', '').split('/')
                db_name = url_parts[1] if len(url_parts) > 1 else 'projectmeats'
                
                user_host = url_parts[0]
                if '@' in user_host:
                    user_pass, host_port = user_host.split('@')
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                        config['db_user'] = user
                        config['db_password'] = password
                    
                    if ':' in host_port:
                        host, port = host_port.split(':')
                        config['db_host'] = host
                        config['db_port'] = port
                    else:
                        config['db_host'] = host_port
                        config['db_port'] = '5432'
                
                config['db_name'] = db_name
            except Exception as e:
                print(f"⚠️  Error parsing DATABASE_URL: {e}")
    
    # Extract domain from ALLOWED_HOSTS or CORS_ALLOWED_ORIGINS
    if not config.get('domain'):
        for source in ['allowed_hosts', 'cors_origins']:
            if source in config:
                hosts = config[source].split(',')
                for host in hosts:
                    host = host.strip()
                    if host and not host.startswith('localhost') and not host.startswith('127.0.0.1'):
                        # Remove protocol if present
                        if '://' in host:
                            host = host.split('://', 1)[1]
                        # Remove www. if present
                        if host.startswith('www.'):
                            host = host[4:]
                        config['domain'] = host
                        break
                if config.get('domain'):
                    break
    
    # Set defaults for missing values
    defaults = {
        'debug': False,
        'db_host': 'localhost',
        'db_port': '5432',
        'enable_ssl': True,
        'company_name': 'ProjectMeats',
        'static_root': '/opt/projectmeats/backend/staticfiles',
        'media_root': '/opt/projectmeats/media',
        'log_dir': '/opt/projectmeats/logs',
        'backup_dir': '/opt/projectmeats/backups'
    }
    
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value
    
    return config


def analyze_environment_file(file_path: str) -> None:
    """Analyze an environment file and show what would be migrated"""
    print(f"\n📊 Analyzing {file_path}")
    print("=" * 60)
    
    env_vars = parse_env_file(file_path)
    if not env_vars:
        print("❌ No environment variables found")
        return
    
    print(f"Found {len(env_vars)} environment variables:")
    for key, value in env_vars.items():
        # Mask sensitive values
        display_value = value
        if key in ['SECRET_KEY', 'DATABASE_URL', 'EMAIL_HOST_PASSWORD']:
            if len(value) > 10:
                display_value = value[:5] + '*' * (len(value) - 10) + value[-5:]
            else:
                display_value = '*' * len(value)
        print(f"  {key}={display_value}")
    
    # Show mapped configuration
    config = map_legacy_vars_to_config(env_vars)
    print(f"\nMapped configuration ({len(config)} settings):")
    for key, value in config.items():
        display_value = str(value)
        if key in ['secret_key', 'db_password', 'email_password']:
            if len(display_value) > 10:
                display_value = display_value[:5] + '*' * (len(display_value) - 10) + display_value[-5:]
            else:
                display_value = '*' * len(display_value)
        print(f"  {key}: {display_value}")
    
    # Check for missing critical values
    critical_fields = ['secret_key', 'db_name', 'db_user', 'db_password']
    missing_fields = [field for field in critical_fields if not config.get(field)]
    
    if missing_fields:
        print(f"\n⚠️  Missing critical fields: {', '.join(missing_fields)}")
        print("   These would need to be generated automatically during migration")
    else:
        print("\n✅ All critical fields present")


def migrate_environment_file(from_path: str, to_path: str = None) -> bool:
    """Migrate an existing environment file to the new format"""
    print(f"\n🔄 Migrating {from_path}")
    
    # Parse existing file
    env_vars = parse_env_file(from_path)
    if not env_vars:
        return False
    
    # Map to new configuration
    config = map_legacy_vars_to_config(env_vars)
    
    # Import the environment manager
    try:
        from deployment.environment_config import EnvironmentConfigManager
    except ImportError:
        print("❌ Cannot import EnvironmentConfigManager. Ensure deployment/environment_config.py exists.")
        return False
    
    mgr = EnvironmentConfigManager()
    
    # Generate missing credentials if needed
    missing_fields = []
    critical_fields = ['secret_key', 'db_name', 'db_user', 'db_password']
    
    for field in critical_fields:
        if not config.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        print(f"⚠️  Generating missing credentials: {', '.join(missing_fields)}")
        credentials = mgr.generate_secure_credentials()
        
        if 'secret_key' in missing_fields:
            config['secret_key'] = credentials['secret_key']
        if 'db_name' in missing_fields:
            config['db_name'] = credentials['db_name']
        if 'db_user' in missing_fields:
            config['db_user'] = credentials['db_user']
        if 'db_password' in missing_fields:
            config['db_password'] = credentials['db_password']
    
    # Check if existing secret key needs replacement
    if config.get('secret_key'):
        secret_key = config['secret_key']
        if (len(secret_key) < 50 or 
            'change-this' in secret_key.lower() or 
            'your-' in secret_key.lower() or
            'replace' in secret_key.lower() or
            secret_key == 'django-insecure-dev-key-change-in-production'):
            print(f"⚠️  Replacing insecure secret key")
            credentials = mgr.generate_secure_credentials()
            config['secret_key'] = credentials['secret_key']
    
    # Validate configuration
    is_valid, issues = mgr.validate_configuration(config)
    if not is_valid:
        print("❌ Configuration validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    # Generate new environment file
    try:
        env_content = mgr.create_environment_file(config)
    except Exception as e:
        print(f"❌ Error generating environment file: {e}")
        return False
    
    # Determine output path
    if not to_path:
        to_path = from_path + '.migrated'
    
    # Write the new file
    try:
        with open(to_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Migrated environment file saved to: {to_path}")
        print(f"   Generated {len(env_content)} characters")
        return True
    except Exception as e:
        print(f"❌ Error writing migrated file: {e}")
        return False


def find_environment_files() -> List[str]:
    """Find all potential environment files in the project"""
    env_files = []
    
    # Common environment file patterns
    patterns = [
        '.env',
        '.env.prod',
        '.env.production',
        '.env.example',
        'backend/.env',
        'backend/.env.production',
        'deployment/config/projectmeats.env.template'
    ]
    
    for pattern in patterns:
        if os.path.exists(pattern):
            env_files.append(pattern)
    
    # Also check for any .env* files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.startswith('.env') and file not in ['.env.example', '.env.test']:
                full_path = os.path.join(root, file)
                if full_path not in env_files:
                    env_files.append(full_path)
    
    return sorted(env_files)


def main():
    parser = argparse.ArgumentParser(description='Migrate ProjectMeats environment files')
    parser.add_argument('--from', dest='from_file', help='Source environment file to migrate')
    parser.add_argument('--to', help='Destination file for migrated environment (optional)')
    parser.add_argument('--analyze-all', action='store_true', 
                       help='Analyze all found environment files')
    args = parser.parse_args()
    
    print("🔄 ProjectMeats Environment Migration Tool")
    print("=" * 50)
    
    if args.analyze_all:
        env_files = find_environment_files()
        if not env_files:
            print("❌ No environment files found")
            return 1
        
        print(f"Found {len(env_files)} environment files:")
        for i, file_path in enumerate(env_files, 1):
            print(f"{i}. {file_path}")
        
        for file_path in env_files:
            analyze_environment_file(file_path)
        
        print("\n💡 To migrate a file, use:")
        print("   python migrate_environment.py --from=path/to/file.env")
        
    elif args.from_file:
        if migrate_environment_file(args.from_file, args.to):
            print("\n✅ Migration completed successfully!")
            print("\n💡 Next steps:")
            print("1. Review the migrated file for accuracy")
            print("2. Test with: python validate_environment.py --test-deployment")
            print("3. Use the migrated file in your deployment")
            return 0
        else:
            print("\n❌ Migration failed")
            return 1
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python migrate_environment.py --analyze-all")
        print("   python migrate_environment.py --from=backend/.env")
        print("   python migrate_environment.py --from=.env.prod --to=production.env")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())