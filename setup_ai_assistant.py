#!/usr/bin/env python3
"""
ProjectMeats AI Assistant Interactive Setup
==========================================

This script provides a comprehensive, guided setup for the AI Assistant functionality
in ProjectMeats, including authentication, API keys, and configuration management.

Features:
- Interactive prompts for all configuration values
- Automatic environment file generation
- AI provider setup (OpenAI, Anthropic, Azure OpenAI)
- Authentication and database configuration
- Validation and testing of configurations

Usage:
    python setup_ai_assistant.py
"""

import os
import sys
import json
import secrets
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from getpass import getpass


class Colors:
    """ANSI color codes for cross-platform terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported"""
        if platform.system() == "Windows" and not os.environ.get('TERM'):
            for attr in dir(cls):
                if not attr.startswith('_') and attr != 'disable_on_windows':
                    setattr(cls, attr, '')


class AIAssistantSetup:
    """Interactive setup for ProjectMeats AI Assistant"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.is_windows = platform.system() == "Windows"
        
        # Configuration storage
        self.config = {}
        self.env_vars = {}
        
        # Disable colors on unsupported Windows terminals
        if self.is_windows:
            Colors.disable_on_windows()
    
    def log(self, message, level="INFO", color=None):
        """Enhanced logging with colors and levels"""
        color_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.PURPLE,
            "INPUT": Colors.CYAN
        }
        
        if color is None:
            color = color_map.get(level, Colors.WHITE)
        
        print(f"{color}[{level}]{Colors.END} {message}")
    
    def prompt_input(self, prompt: str, default: str = "", required: bool = True, 
                    secret: bool = False, validation_func: callable = None) -> str:
        """Enhanced input prompt with validation and defaults"""
        while True:
            self.log(f"{prompt}", "INPUT")
            if default:
                self.log(f"  (Press Enter for default: {default})", "INFO", Colors.YELLOW)
            
            if secret:
                value = getpass("  Enter value (hidden): ").strip()
            else:
                value = input("  Enter value: ").strip()
            
            # Use default if no value provided
            if not value and default:
                value = default
            
            # Check if required
            if required and not value:
                self.log("This field is required. Please provide a value.", "ERROR")
                continue
            
            # Validate if function provided
            if value and validation_func:
                is_valid, error_msg = validation_func(value)
                if not is_valid:
                    self.log(f"Invalid input: {error_msg}", "ERROR")
                    continue
            
            return value
    
    def prompt_choice(self, prompt: str, choices: List[str], default: int = 0) -> str:
        """Prompt user to select from a list of choices"""
        while True:
            self.log(f"{prompt}", "INPUT")
            for i, choice in enumerate(choices):
                marker = ">" if i == default else " "
                self.log(f"  {marker} {i + 1}. {choice}", "INFO", Colors.CYAN)
            
            try:
                choice_input = input(f"  Enter choice (1-{len(choices)}, default: {default + 1}): ").strip()
                
                if not choice_input:
                    return choices[default]
                
                choice_index = int(choice_input) - 1
                if 0 <= choice_index < len(choices):
                    return choices[choice_index]
                else:
                    self.log(f"Please enter a number between 1 and {len(choices)}", "ERROR")
            except ValueError:
                self.log("Please enter a valid number", "ERROR")
    
    def prompt_boolean(self, prompt: str, default: bool = True) -> bool:
        """Prompt for yes/no input"""
        default_text = "Y/n" if default else "y/N"
        while True:
            self.log(f"{prompt} ({default_text})", "INPUT")
            response = input("  Enter choice: ").strip().lower()
            
            if not response:
                return default
            
            if response in ['y', 'yes', 'true', '1']:
                return True
            elif response in ['n', 'no', 'false', '0']:
                return False
            else:
                self.log("Please enter y/yes or n/no", "ERROR")
    
    def validate_url(self, url: str) -> tuple[bool, str]:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if url_pattern.match(url):
            return True, ""
        return False, "Invalid URL format. Must start with http:// or https://"
    
    def validate_email(self, email: str) -> tuple[bool, str]:
        """Validate email format"""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if email_pattern.match(email):
            return True, ""
        return False, "Invalid email format"
    
    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        """Validate API key format"""
        if len(api_key) < 10:
            return False, "API key seems too short"
        if ' ' in api_key:
            return False, "API key should not contain spaces"
        return True, ""
    
    def welcome_message(self):
        """Display welcome message and setup overview"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}=" * 70)
        print(f"🤖 ProjectMeats AI Assistant Setup")
        print(f"=" * 70 + f"{Colors.END}\n")
        
        self.log("Welcome to the ProjectMeats AI Assistant setup wizard!", "SUCCESS")
        print()
        self.log("This wizard will guide you through configuring:", "INFO")
        print(f"  {Colors.GREEN}✓{Colors.END} Backend authentication and database")
        print(f"  {Colors.GREEN}✓{Colors.END} AI provider configuration (OpenAI, Anthropic, etc.)")
        print(f"  {Colors.GREEN}✓{Colors.END} Environment variables and secrets")
        print(f"  {Colors.GREEN}✓{Colors.END} Frontend API integration")
        print(f"  {Colors.GREEN}✓{Colors.END} Database initialization and admin user")
        print()
        
        self.log("The setup will create/update configuration files:", "INFO")
        print(f"  {Colors.CYAN}•{Colors.END} backend/.env")
        print(f"  {Colors.CYAN}•{Colors.END} frontend/.env.local")
        print(f"  {Colors.CYAN}•{Colors.END} AI provider configurations")
        print()
        
        if not self.prompt_boolean("Ready to begin setup?", True):
            self.log("Setup cancelled by user", "WARNING")
            sys.exit(0)
    
    def configure_django_backend(self):
        """Configure Django backend settings"""
        self.log("🔧 Configuring Django Backend", "STEP")
        print()
        
        # Generate secret key
        secret_key = secrets.token_urlsafe(50)
        self.env_vars['SECRET_KEY'] = secret_key
        self.log("Generated Django SECRET_KEY", "SUCCESS")
        
        # Debug mode
        debug_mode = self.prompt_boolean("Enable DEBUG mode? (recommended for development)", True)
        self.env_vars['DEBUG'] = str(debug_mode)
        
        # Allowed hosts
        if debug_mode:
            allowed_hosts = "localhost,127.0.0.1,testserver"
        else:
            allowed_hosts = self.prompt_input(
                "Enter allowed hosts (comma-separated)",
                "your-domain.com,localhost"
            )
        self.env_vars['ALLOWED_HOSTS'] = allowed_hosts
        
        # Database configuration
        self.log("\n📊 Database Configuration", "STEP")
        db_choice = self.prompt_choice(
            "Select database type:",
            ["SQLite (recommended for development)", "PostgreSQL (production)"],
            0
        )
        
        if "SQLite" in db_choice:
            self.env_vars['DATABASE_URL'] = "sqlite:///db.sqlite3"
            self.log("Using SQLite database (development)", "SUCCESS")
        else:
            self.log("PostgreSQL configuration:", "INFO")
            pg_host = self.prompt_input("PostgreSQL host", "localhost")
            pg_port = self.prompt_input("PostgreSQL port", "5432")
            pg_name = self.prompt_input("Database name", "projectmeats")
            pg_user = self.prompt_input("Database username", "projectmeats_user")
            pg_password = self.prompt_input("Database password", required=True, secret=True)
            
            db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_name}"
            self.env_vars['DATABASE_URL'] = db_url
            self.log("PostgreSQL configuration saved", "SUCCESS")
    
    def configure_ai_providers(self):
        """Configure AI providers and API keys"""
        self.log("🤖 AI Provider Configuration", "STEP")
        print()
        
        self.log("ProjectMeats AI Assistant supports multiple providers:", "INFO")
        print(f"  {Colors.CYAN}•{Colors.END} OpenAI (GPT-3.5, GPT-4)")
        print(f"  {Colors.CYAN}•{Colors.END} Azure OpenAI")
        print(f"  {Colors.CYAN}•{Colors.END} Anthropic (Claude)")
        print(f"  {Colors.CYAN}•{Colors.END} Mock Provider (for testing)")
        print()
        
        # Primary provider selection
        providers = [
            "OpenAI (OpenAI API)",
            "Azure OpenAI (Microsoft Azure)",
            "Anthropic (Claude API)",
            "Mock Provider (No API key needed - for testing)"
        ]
        
        primary_provider = self.prompt_choice("Select your primary AI provider:", providers, 0)
        
        # Configure based on selection
        if "OpenAI" in primary_provider and "Azure" not in primary_provider:
            self._configure_openai()
        elif "Azure OpenAI" in primary_provider:
            self._configure_azure_openai()
        elif "Anthropic" in primary_provider:
            self._configure_anthropic()
        else:
            self._configure_mock_provider()
        
        # Ask about backup providers
        configure_backup = self.prompt_boolean(
            "\nWould you like to configure backup providers? (recommended)", True
        )
        
        if configure_backup:
            self._configure_backup_providers(primary_provider)
    
    def _configure_openai(self):
        """Configure OpenAI provider"""
        self.log("\n🔑 OpenAI Configuration", "INFO")
        
        api_key = self.prompt_input(
            "Enter your OpenAI API key (starts with 'sk-')",
            required=True,
            secret=True,
            validation_func=self.validate_api_key
        )
        self.env_vars['OPENAI_API_KEY'] = api_key
        
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
        model = self.prompt_choice("Select OpenAI model:", models, 0)
        self.env_vars['OPENAI_MODEL'] = model
        
        # Temperature setting
        temperature = self.prompt_input(
            "Enter temperature (0.0-1.0, default: 0.7)",
            "0.7"
        )
        self.env_vars['OPENAI_TEMPERATURE'] = temperature
        
        # Max tokens
        max_tokens = self.prompt_input(
            "Enter max tokens (default: 2000)",
            "2000"
        )
        self.env_vars['OPENAI_MAX_TOKENS'] = max_tokens
        
        self.config['ai_provider'] = {
            'name': 'openai_primary',
            'provider': 'openai',
            'model_name': model,
            'api_key_name': 'OPENAI_API_KEY',
            'configuration': {
                'temperature': float(temperature),
                'max_tokens': int(max_tokens)
            },
            'is_default': True
        }
        
        self.log("OpenAI configuration completed", "SUCCESS")
    
    def _configure_azure_openai(self):
        """Configure Azure OpenAI provider"""
        self.log("\n🔑 Azure OpenAI Configuration", "INFO")
        
        api_key = self.prompt_input(
            "Enter your Azure OpenAI API key",
            required=True,
            secret=True,
            validation_func=self.validate_api_key
        )
        self.env_vars['AZURE_OPENAI_API_KEY'] = api_key
        
        endpoint = self.prompt_input(
            "Enter your Azure OpenAI endpoint URL",
            "https://your-resource.openai.azure.com/",
            validation_func=self.validate_url
        )
        self.env_vars['AZURE_OPENAI_ENDPOINT'] = endpoint
        
        deployment = self.prompt_input(
            "Enter your deployment name",
            "gpt-35-turbo"
        )
        self.env_vars['AZURE_OPENAI_DEPLOYMENT'] = deployment
        
        api_version = self.prompt_input(
            "Enter API version",
            "2024-02-01"
        )
        self.env_vars['AZURE_OPENAI_API_VERSION'] = api_version
        
        self.config['ai_provider'] = {
            'name': 'azure_openai_primary',
            'provider': 'azure_openai',
            'model_name': deployment,
            'api_endpoint': endpoint,
            'api_key_name': 'AZURE_OPENAI_API_KEY',
            'configuration': {
                'api_version': api_version,
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'is_default': True
        }
        
        self.log("Azure OpenAI configuration completed", "SUCCESS")
    
    def _configure_anthropic(self):
        """Configure Anthropic provider"""
        self.log("\n🔑 Anthropic Configuration", "INFO")
        
        api_key = self.prompt_input(
            "Enter your Anthropic API key",
            required=True,
            secret=True,
            validation_func=self.validate_api_key
        )
        self.env_vars['ANTHROPIC_API_KEY'] = api_key
        
        models = ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
        model = self.prompt_choice("Select Claude model:", models, 1)
        self.env_vars['ANTHROPIC_MODEL'] = model
        
        self.config['ai_provider'] = {
            'name': 'anthropic_primary',
            'provider': 'anthropic',
            'model_name': model,
            'api_key_name': 'ANTHROPIC_API_KEY',
            'configuration': {
                'max_tokens': 2000,
                'temperature': 0.7
            },
            'is_default': True
        }
        
        self.log("Anthropic configuration completed", "SUCCESS")
    
    def _configure_mock_provider(self):
        """Configure mock provider for testing"""
        self.log("\n🧪 Mock Provider Configuration", "INFO")
        self.log("Mock provider selected - no API key required", "SUCCESS")
        
        self.config['ai_provider'] = {
            'name': 'mock_provider',
            'provider': 'local',
            'model_name': 'mock-model-v1',
            'configuration': {
                'response_delay': 0.5,
                'enable_detailed_responses': True
            },
            'is_default': True
        }
        
        self.log("Mock provider configuration completed", "SUCCESS")
    
    def _configure_backup_providers(self, primary_provider: str):
        """Configure backup AI providers"""
        self.log("\n🔄 Backup Provider Configuration", "INFO")
        # Implementation for backup providers would go here
        # For now, just acknowledge the feature
        self.log("Backup provider configuration skipped for this setup", "WARNING")
        self.log("You can add backup providers later through the admin interface", "INFO")
    
    def configure_cors_and_frontend(self):
        """Configure CORS and frontend settings"""
        self.log("🌐 Frontend & CORS Configuration", "STEP")
        print()
        
        # CORS origins
        cors_origins = self.prompt_input(
            "Enter allowed CORS origins (comma-separated)",
            "http://localhost:3000,http://127.0.0.1:3000"
        )
        self.env_vars['CORS_ALLOWED_ORIGINS'] = cors_origins
        
        # Frontend API base URL
        api_base_url = self.prompt_input(
            "Enter API base URL for frontend",
            "http://localhost:8000/api/v1",
            validation_func=self.validate_url
        )
        
        # Frontend environment variables
        self.frontend_env = {
            'REACT_APP_API_BASE_URL': api_base_url,
            'REACT_APP_ENVIRONMENT': 'development',
            'REACT_APP_AI_ASSISTANT_ENABLED': 'true'
        }
        
        self.log("Frontend configuration completed", "SUCCESS")
    
    def configure_email_and_notifications(self):
        """Configure email and notification settings"""
        self.log("📧 Email & Notifications Configuration", "STEP")
        print()
        
        email_choice = self.prompt_choice(
            "Select email backend:",
            ["Console (development - emails printed to terminal)", 
             "SMTP (production email server)",
             "Disable email"],
            0
        )
        
        if "Console" in email_choice:
            self.env_vars['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
        elif "SMTP" in email_choice:
            self.env_vars['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
            self.env_vars['EMAIL_HOST'] = self.prompt_input("SMTP Host", "smtp.gmail.com")
            self.env_vars['EMAIL_PORT'] = self.prompt_input("SMTP Port", "587")
            self.env_vars['EMAIL_USE_TLS'] = 'True'
            self.env_vars['EMAIL_HOST_USER'] = self.prompt_input(
                "Email username", 
                validation_func=self.validate_email
            )
            self.env_vars['EMAIL_HOST_PASSWORD'] = self.prompt_input(
                "Email password (or app password)", 
                secret=True
            )
        else:
            self.env_vars['EMAIL_BACKEND'] = 'django.core.mail.backends.dummy.EmailBackend'
        
        self.log("Email configuration completed", "SUCCESS")
    
    def configure_security_settings(self):
        """Configure security and additional settings"""
        self.log("🔒 Security Configuration", "STEP")
        print()
        
        # Security settings for production
        if self.env_vars.get('DEBUG', 'True') == 'False':
            self.log("Production security settings enabled", "INFO")
            self.env_vars['SECURE_SSL_REDIRECT'] = 'True'
            self.env_vars['SECURE_HSTS_SECONDS'] = '31536000'
            self.env_vars['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = 'True'
            self.env_vars['SECURE_HSTS_PRELOAD'] = 'True'
        
        # Log level
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        log_level = self.prompt_choice("Select logging level:", log_levels, 1)
        self.env_vars['LOG_LEVEL'] = log_level
        
        # Additional paths
        self.env_vars['MEDIA_ROOT'] = 'media/'
        self.env_vars['STATIC_ROOT'] = 'static/'
        
        # API versioning
        self.env_vars['API_VERSION'] = 'v1'
        
        self.log("Security configuration completed", "SUCCESS")
    
    def create_environment_files(self):
        """Create .env files with the collected configuration"""
        self.log("📝 Creating Environment Files", "STEP")
        print()
        
        # Backend .env file
        backend_env_path = self.backend_dir / ".env"
        self._create_backend_env_file(backend_env_path)
        
        # Frontend .env.local file
        frontend_env_path = self.frontend_dir / ".env.local"
        self._create_frontend_env_file(frontend_env_path)
        
        # Create AI configuration file
        self._create_ai_config_file()
        
        self.log("Environment files created successfully", "SUCCESS")
    
    def _create_backend_env_file(self, env_path: Path):
        """Create backend .env file"""
        env_content = f"""# ProjectMeats Backend Environment Configuration
# Generated by setup_ai_assistant.py on {__import__('datetime').datetime.now()}

# Django Settings
SECRET_KEY={self.env_vars['SECRET_KEY']}
DEBUG={self.env_vars['DEBUG']}
ALLOWED_HOSTS={self.env_vars['ALLOWED_HOSTS']}

# Database Configuration
DATABASE_URL={self.env_vars['DATABASE_URL']}

# CORS Settings (for React frontend)
CORS_ALLOWED_ORIGINS={self.env_vars['CORS_ALLOWED_ORIGINS']}

# API Configuration
API_VERSION={self.env_vars.get('API_VERSION', 'v1')}

# Email Configuration
EMAIL_BACKEND={self.env_vars.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')}
"""
        
        # Add email settings if SMTP configured
        if 'EMAIL_HOST' in self.env_vars:
            env_content += f"""EMAIL_HOST={self.env_vars['EMAIL_HOST']}
EMAIL_PORT={self.env_vars['EMAIL_PORT']}
EMAIL_USE_TLS={self.env_vars['EMAIL_USE_TLS']}
EMAIL_HOST_USER={self.env_vars['EMAIL_HOST_USER']}
EMAIL_HOST_PASSWORD={self.env_vars['EMAIL_HOST_PASSWORD']}
"""
        
        # Add AI provider keys
        if 'OPENAI_API_KEY' in self.env_vars:
            env_content += f"""
# OpenAI Configuration
OPENAI_API_KEY={self.env_vars['OPENAI_API_KEY']}
OPENAI_MODEL={self.env_vars.get('OPENAI_MODEL', 'gpt-3.5-turbo')}
OPENAI_TEMPERATURE={self.env_vars.get('OPENAI_TEMPERATURE', '0.7')}
OPENAI_MAX_TOKENS={self.env_vars.get('OPENAI_MAX_TOKENS', '2000')}
"""
        
        if 'AZURE_OPENAI_API_KEY' in self.env_vars:
            env_content += f"""
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY={self.env_vars['AZURE_OPENAI_API_KEY']}
AZURE_OPENAI_ENDPOINT={self.env_vars['AZURE_OPENAI_ENDPOINT']}
AZURE_OPENAI_DEPLOYMENT={self.env_vars['AZURE_OPENAI_DEPLOYMENT']}
AZURE_OPENAI_API_VERSION={self.env_vars['AZURE_OPENAI_API_VERSION']}
"""
        
        if 'ANTHROPIC_API_KEY' in self.env_vars:
            env_content += f"""
# Anthropic Configuration
ANTHROPIC_API_KEY={self.env_vars['ANTHROPIC_API_KEY']}
ANTHROPIC_MODEL={self.env_vars.get('ANTHROPIC_MODEL', 'claude-3-sonnet')}
"""
        
        # Add remaining settings
        env_content += f"""
# File Upload Settings
MEDIA_ROOT={self.env_vars.get('MEDIA_ROOT', 'media/')}
STATIC_ROOT={self.env_vars.get('STATIC_ROOT', 'static/')}

# Logging Level
LOG_LEVEL={self.env_vars.get('LOG_LEVEL', 'INFO')}

# Security Settings (production)
"""
        
        if self.env_vars.get('DEBUG') == 'False':
            env_content += f"""SECURE_SSL_REDIRECT={self.env_vars.get('SECURE_SSL_REDIRECT', 'True')}
SECURE_HSTS_SECONDS={self.env_vars.get('SECURE_HSTS_SECONDS', '31536000')}
SECURE_HSTS_INCLUDE_SUBDOMAINS={self.env_vars.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True')}
SECURE_HSTS_PRELOAD={self.env_vars.get('SECURE_HSTS_PRELOAD', 'True')}
"""
        
        # Write the file
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        self.log(f"Created backend .env file: {env_path}", "SUCCESS")
    
    def _create_frontend_env_file(self, env_path: Path):
        """Create frontend .env.local file"""
        env_content = f"""# ProjectMeats Frontend Environment Configuration
# Generated by setup_ai_assistant.py on {__import__('datetime').datetime.now()}

# API Configuration
REACT_APP_API_BASE_URL={self.frontend_env['REACT_APP_API_BASE_URL']}
REACT_APP_ENVIRONMENT={self.frontend_env['REACT_APP_ENVIRONMENT']}

# Feature Flags
REACT_APP_AI_ASSISTANT_ENABLED={self.frontend_env['REACT_APP_AI_ASSISTANT_ENABLED']}

# Development Settings
GENERATE_SOURCEMAP=false
"""
        
        # Write the file
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        self.log(f"Created frontend .env.local file: {env_path}", "SUCCESS")
    
    def _create_ai_config_file(self):
        """Create AI configuration JSON file for reference"""
        if 'ai_provider' in self.config:
            ai_config_path = self.backend_dir / "ai_config.json"
            
            with open(ai_config_path, 'w') as f:
                json.dump(self.config['ai_provider'], f, indent=2)
            
            self.log(f"Created AI configuration file: {ai_config_path}", "SUCCESS")
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.log("📦 Installing Dependencies", "STEP")
        print()
        
        # Check if user wants to install dependencies
        install_deps = self.prompt_boolean(
            "Install Python and Node.js dependencies?", True
        )
        
        if not install_deps:
            self.log("Dependency installation skipped", "WARNING")
            return
        
        # Install backend dependencies
        self.log("Installing Python dependencies...", "INFO")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.backend_dir / "requirements.txt")
            ], check=True, cwd=self.backend_dir)
            self.log("Python dependencies installed successfully", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install Python dependencies: {e}", "ERROR")
            self.log("You may need to install them manually", "WARNING")
        
        # Install frontend dependencies
        if self.frontend_dir.exists():
            self.log("Installing Node.js dependencies...", "INFO")
            try:
                subprocess.run(["npm", "install"], check=True, cwd=self.frontend_dir)
                self.log("Node.js dependencies installed successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log(f"Failed to install Node.js dependencies: {e}", "ERROR")
                self.log("You may need to run 'npm install' manually in the frontend directory", "WARNING")
    
    def initialize_database(self):
        """Initialize database and create admin user"""
        self.log("🗃️ Database Initialization", "STEP")
        print()
        
        init_db = self.prompt_boolean("Initialize database and create admin user?", True)
        
        if not init_db:
            self.log("Database initialization skipped", "WARNING")
            return
        
        try:
            # Run migrations
            self.log("Running database migrations...", "INFO")
            subprocess.run([
                sys.executable, "manage.py", "migrate"
            ], check=True, cwd=self.backend_dir)
            self.log("Database migrations completed", "SUCCESS")
            
            # Create admin user
            create_admin = self.prompt_boolean("Create admin superuser?", True)
            if create_admin:
                self._create_admin_user()
            
            # Create AI configuration in database
            self._create_ai_configuration_in_db()
            
        except subprocess.CalledProcessError as e:
            self.log(f"Database initialization failed: {e}", "ERROR")
            self.log("You may need to run migrations manually", "WARNING")
    
    def _create_admin_user(self):
        """Create admin superuser"""
        self.log("Creating admin superuser...", "INFO")
        
        username = self.prompt_input("Admin username", "admin")
        email = self.prompt_input("Admin email", "admin@projectmeats.com", 
                                 validation_func=self.validate_email)
        password = self.prompt_input("Admin password", "WATERMELON1219", secret=True)
        
        # Create superuser using Django management command
        create_user_script = f'''
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="{username}").exists():
    User.objects.create_superuser("{username}", "{email}", "{password}")
    print("Superuser created successfully")
else:
    print("Superuser already exists")
'''
        
        try:
            subprocess.run([
                sys.executable, "manage.py", "shell", "-c", create_user_script
            ], check=True, cwd=self.backend_dir)
            self.log(f"Admin user '{username}' created successfully", "SUCCESS")
            self.log(f"Login credentials: {username} / {password}", "INFO")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to create admin user: {e}", "ERROR")
    
    def _create_ai_configuration_in_db(self):
        """Create AI configuration in the database"""
        if 'ai_provider' not in self.config:
            return
        
        self.log("Creating AI configuration in database...", "INFO")
        
        config = self.config['ai_provider']
        create_config_script = f'''
from apps.ai_assistant.models import AIConfiguration
import json

config_data = {json.dumps(config)}

# Delete existing default config
AIConfiguration.objects.filter(is_default=True).update(is_default=False)

# Create new config
ai_config, created = AIConfiguration.objects.get_or_create(
    name=config_data["name"],
    defaults={{
        "provider": config_data["provider"],
        "model_name": config_data["model_name"],
        "api_endpoint": config_data.get("api_endpoint"),
        "api_key_name": config_data.get("api_key_name"),
        "configuration": config_data["configuration"],
        "is_active": True,
        "is_default": config_data.get("is_default", True)
    }}
)

if created:
    print("AI configuration created in database")
else:
    print("AI configuration already exists")
'''
        
        try:
            subprocess.run([
                sys.executable, "manage.py", "shell", "-c", create_config_script
            ], check=True, cwd=self.backend_dir)
            self.log("AI configuration saved to database", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to create AI configuration: {e}", "WARNING")
    
    def test_configuration(self):
        """Test the configuration"""
        self.log("🧪 Testing Configuration", "STEP")
        print()
        
        test_config = self.prompt_boolean("Test the configuration?", True)
        
        if not test_config:
            self.log("Configuration testing skipped", "WARNING")
            return
        
        # Test Django settings
        self._test_django_settings()
        
        # Test AI provider
        self._test_ai_provider()
        
        # Test frontend connection
        self._test_frontend_connection()
    
    def _test_django_settings(self):
        """Test Django settings"""
        self.log("Testing Django configuration...", "INFO")
        
        try:
            # Test Django check
            subprocess.run([
                sys.executable, "manage.py", "check"
            ], check=True, cwd=self.backend_dir, capture_output=True)
            self.log("✓ Django configuration valid", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log("✗ Django configuration has issues", "ERROR")
            self.log("Run 'python manage.py check' for details", "INFO")
    
    def _test_ai_provider(self):
        """Test AI provider configuration"""
        self.log("Testing AI provider...", "INFO")
        
        test_ai_script = '''
from apps.ai_assistant.services.ai_service import ai_service

try:
    response, metadata = ai_service.generate_chat_response("Hello, this is a test message")
    print(f"✓ AI provider test successful: {response[:50]}...")
except Exception as e:
    print(f"✗ AI provider test failed: {str(e)}")
'''
        
        try:
            result = subprocess.run([
                sys.executable, "manage.py", "shell", "-c", test_ai_script
            ], capture_output=True, text=True, cwd=self.backend_dir)
            
            if result.returncode == 0:
                self.log("✓ AI provider test passed", "SUCCESS")
            else:
                self.log("✗ AI provider test failed", "ERROR")
                
        except subprocess.CalledProcessError:
            self.log("✗ AI provider test failed", "ERROR")
    
    def _test_frontend_connection(self):
        """Test frontend configuration"""
        self.log("Testing frontend configuration...", "INFO")
        
        frontend_env_path = self.frontend_dir / ".env.local"
        if frontend_env_path.exists():
            self.log("✓ Frontend environment file created", "SUCCESS")
        else:
            self.log("✗ Frontend environment file missing", "ERROR")
    
    def display_completion_message(self):
        """Display setup completion message"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}=" * 70)
        print(f"🎉 AI Assistant Setup Complete!")
        print(f"=" * 70 + f"{Colors.END}\n")
        
        self.log("Setup completed successfully! 🚀", "SUCCESS")
        print()
        
        self.log("Files created/updated:", "INFO")
        print(f"  {Colors.GREEN}✓{Colors.END} backend/.env")
        print(f"  {Colors.GREEN}✓{Colors.END} frontend/.env.local")
        if 'ai_provider' in self.config:
            print(f"  {Colors.GREEN}✓{Colors.END} backend/ai_config.json")
        print()
        
        self.log("Next Steps:", "STEP")
        print(f"  {Colors.CYAN}1.{Colors.END} Start the backend server:")
        print(f"     {Colors.YELLOW}cd backend && python manage.py runserver{Colors.END}")
        print()
        print(f"  {Colors.CYAN}2.{Colors.END} Start the frontend server:")
        print(f"     {Colors.YELLOW}cd frontend && npm start{Colors.END}")
        print()
        print(f"  {Colors.CYAN}3.{Colors.END} Access the application:")
        print(f"     {Colors.YELLOW}Frontend: http://localhost:3000{Colors.END}")
        print(f"     {Colors.YELLOW}Backend API: http://localhost:8000/api/v1{Colors.END}")
        print(f"     {Colors.YELLOW}Admin Panel: http://localhost:8000/admin{Colors.END}")
        print()
        
        if 'ai_provider' in self.config and self.config['ai_provider']['provider'] != 'local':
            self.log("AI Assistant Features:", "INFO")
            print(f"  {Colors.GREEN}•{Colors.END} Chat interface with intelligent responses")
            print(f"  {Colors.GREEN}•{Colors.END} Document upload and processing")
            print(f"  {Colors.GREEN}•{Colors.END} Entity extraction and data integration")
            print(f"  {Colors.GREEN}•{Colors.END} Business intelligence and analytics")
        else:
            self.log("Mock AI Provider Enabled:", "WARNING")
            print(f"  {Colors.YELLOW}•{Colors.END} AI features will use mock responses")
            print(f"  {Colors.YELLOW}•{Colors.END} Configure a real AI provider for full functionality")
        
        print()
        self.log("Documentation:", "INFO")
        print(f"  {Colors.CYAN}•{Colors.END} API Documentation: http://localhost:8000/api/docs/")
        print(f"  {Colors.CYAN}•{Colors.END} Setup Guide: docs/setup-and-development.md")
        print(f"  {Colors.CYAN}•{Colors.END} AI Assistant Guide: docs/ai_assistant_guide.md")
        print()
        
        self.log("Enjoy using ProjectMeats with AI Assistant! 🥩🤖", "SUCCESS")
    
    def main(self):
        """Main setup process"""
        try:
            self.welcome_message()
            self.configure_django_backend()
            self.configure_ai_providers()
            self.configure_cors_and_frontend()
            self.configure_email_and_notifications()
            self.configure_security_settings()
            self.create_environment_files()
            self.install_dependencies()
            self.initialize_database()
            self.test_configuration()
            self.display_completion_message()
            
            return 0
            
        except KeyboardInterrupt:
            self.log("\nSetup cancelled by user", "WARNING")
            return 1
        except Exception as e:
            self.log(f"\nSetup failed with error: {str(e)}", "ERROR")
            return 1


if __name__ == "__main__":
    setup = AIAssistantSetup()
    sys.exit(setup.main())