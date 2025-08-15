#!/usr/bin/env python3
"""
ProjectMeats Cross-Platform Setup Script
======================================

This script provides a unified setup experience across Windows, macOS, and Linux.
It handles environment setup, dependency installation, initial configuration, and test data creation.

Usage:
    python setup.py              # Full setup (backend + frontend)
    python setup.py --backend    # Backend only
    python setup.py --frontend   # Frontend only
    python setup.py --help       # Show help

Features:
- Cross-platform compatibility (Windows, macOS, Linux)
- Automatic platform detection
- Error handling and validation
- Progress reporting
- Dependency checking
- Admin user creation (admin/WATERMELON1219)
- Comprehensive test data creation
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path


class Colors:
    """ANSI color codes for cross-platform terminal output"""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported"""
        if platform.system() == "Windows" and not os.environ.get("TERM"):
            for attr in dir(cls):
                if not attr.startswith("_") and attr != "disable_on_windows":
                    setattr(cls, attr, "")


class ProjectMeatsSetup:
    """Main setup class for ProjectMeats"""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"

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
        }

        if color is None:
            color = color_map.get(level, Colors.WHITE)

        timestamp = ""  # Keep simple for now
        print(f"{color}[{level}]{Colors.END} {message}")

    def run_command(self, command, cwd=None, shell=None, check=True):
        """Run a command with proper error handling"""
        if cwd is None:
            cwd = self.project_root

        if shell is None:
            shell = self.is_windows

        try:
            self.log(f"Running: {command}", "INFO", Colors.CYAN)

            # Handle different command formats
            if isinstance(command, str):
                if shell:
                    result = subprocess.run(
                        command, shell=True, cwd=cwd, capture_output=False, check=check
                    )
                else:
                    result = subprocess.run(
                        command.split(), cwd=cwd, capture_output=False, check=check
                    )
            else:
                result = subprocess.run(
                    command, cwd=cwd, capture_output=False, check=check
                )

            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.log(
                f"Command failed with exit code {e.returncode}: {command}", "ERROR"
            )
            return False
        except FileNotFoundError:
            self.log(f"Command not found: {command}", "ERROR")
            return False

    def check_dependency(self, command, version_flag="--version", min_version=None):
        """Check if a dependency is installed"""
        try:
            # Use shutil.which to properly resolve command path (handles .cmd/.bat on Windows)
            command_path = shutil.which(command)
            if command_path is None:
                self.log(f"✗ {command} not found", "ERROR")
                return False

            result = subprocess.run(
                [command_path, version_flag], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version_output = result.stdout.strip()
                self.log(
                    f"✓ {command} found: {version_output.split()[0] if version_output else 'installed'}",
                    "SUCCESS",
                )
                return True
            else:
                self.log(f"✗ {command} not found or not working", "ERROR")
                return False
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            self.log(f"✗ {command} not found", "ERROR")
            return False

    def _try_install_without_postgres(self, pip_cmd):
        """Try to install requirements without PostgreSQL adapter as fallback"""
        try:
            self.log(
                "Creating temporary requirements file without PostgreSQL adapter...",
                "INFO",
            )

            # Read original requirements
            requirements_file = self.backend_dir / "requirements.txt"
            with open(requirements_file, "r") as f:
                lines = f.readlines()

            # Filter out PostgreSQL-related packages
            filtered_lines = []
            for line in lines:
                line_lower = line.lower().strip()
                if not any(pkg in line_lower for pkg in ["psycopg", "postgres"]):
                    filtered_lines.append(line)

            # Create temporary requirements file
            temp_requirements = self.backend_dir / "requirements_temp.txt"
            with open(temp_requirements, "w") as f:
                f.writelines(filtered_lines)

            # Try installing without PostgreSQL adapter
            install_cmd = f"{pip_cmd} install --timeout 60 -r requirements_temp.txt"
            success = self.run_command(install_cmd, cwd=self.backend_dir)

            # Clean up temp file
            if temp_requirements.exists():
                temp_requirements.unlink()

            return success

        except Exception as e:
            self.log(f"Failed to install without PostgreSQL adapter: {e}", "ERROR")
            return False

    def _create_admin_user(self, python_cmd):
        """Create admin superuser with specified credentials"""
        try:
            self.log("Creating admin superuser (admin/WATERMELON1219)...", "INFO")

            # Use Django's createsuperuser command with environment variables
            create_user_cmd = (
                f'echo "from django.contrib.auth import get_user_model; '
                f"User = get_user_model(); "
                f"User.objects.filter(username='admin').exists() or "
                f"User.objects.create_superuser('admin', 'admin@projectmeats.com', 'WATERMELON1219')\" | "
                f"{python_cmd} manage.py shell"
            )

            if self.run_command(create_user_cmd, cwd=self.backend_dir, shell=True):
                self.log("✓ Admin superuser created successfully", "SUCCESS")
                self.log("  Username: admin", "INFO")
                self.log("  Password: WATERMELON1219", "INFO")
                self.log("  Email: admin@projectmeats.com", "INFO")
            else:
                self.log(
                    "Failed to create admin user, trying alternative method...",
                    "WARNING",
                )
                # Alternative method using manage.py directly
                alt_cmd = (
                    f'{python_cmd} manage.py shell -c "'
                    f"from django.contrib.auth import get_user_model; "
                    f"User = get_user_model(); "
                    f"User.objects.filter(username='admin').exists() or "
                    f"User.objects.create_superuser('admin', 'admin@projectmeats.com', 'WATERMELON1219')\""
                )
                if self.run_command(alt_cmd, cwd=self.backend_dir):
                    self.log(
                        "✓ Admin superuser created with alternative method", "SUCCESS"
                    )
                else:
                    self.log("Failed to create admin user", "WARNING")
                    self.log(
                        "You can create it manually: python manage.py createsuperuser",
                        "INFO",
                    )

        except Exception as e:
            self.log(f"Error creating admin user: {e}", "WARNING")
            self.log(
                "You can create it manually: python manage.py createsuperuser", "INFO"
            )

    def _create_test_data(self, python_cmd):
        """Create comprehensive test data for the application"""
        try:
            self.log("Creating comprehensive test data for all entities...", "INFO")

            # Check if the test data script exists
            test_data_script = self.backend_dir / "create_test_data.py"
            if not test_data_script.exists():
                self.log(
                    "Test data script not found, skipping test data creation", "WARNING"
                )
                return

            # Execute the test data creation script
            create_data_cmd = f"{python_cmd} create_test_data.py"
            if self.run_command(create_data_cmd, cwd=self.backend_dir):
                self.log("✓ Test data created successfully", "SUCCESS")
                self.log("  The application now has sample data for testing", "INFO")
                self.log(
                    "  This includes suppliers, customers, purchase orders, and more",
                    "INFO",
                )
            else:
                self.log("Failed to create test data", "WARNING")
                self.log(
                    "You can create it manually: cd backend && python create_test_data.py",
                    "INFO",
                )

        except Exception as e:
            self.log(f"Error creating test data: {e}", "WARNING")
            self.log(
                "You can create it manually: cd backend && python create_test_data.py",
                "INFO",
            )

    def copy_env_file(self, source, destination):
        """Copy environment file if it doesn't exist"""
        source_path = Path(source)
        dest_path = Path(destination)

        if dest_path.exists():
            self.log(f"ℹ️  {dest_path.name} already exists", "WARNING")
            return True

        if not source_path.exists():
            self.log(f"Source file not found: {source_path}", "ERROR")
            return False

        try:
            shutil.copy2(source_path, dest_path)
            self.log(f"✓ Created {dest_path.name}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to copy {source_path} to {dest_path}: {e}", "ERROR")
            return False

    def check_prerequisites(self):
        """Check system prerequisites"""
        self.log("🔍 Checking system prerequisites...", "STEP")

        prerequisites = []

        # Check Python
        if self.check_dependency("python", "--version"):
            prerequisites.append("python")
        elif self.check_dependency("python3", "--version"):
            prerequisites.append("python3")
        else:
            self.log("Python 3.9+ is required. Please install Python.", "ERROR")
            return False

        # Check Node.js and npm
        if not self.check_dependency("node", "--version"):
            self.log(
                "Node.js 16+ is required. Please install Node.js from https://nodejs.org/",
                "ERROR",
            )
            return False

        if not self.check_dependency("npm", "--version"):
            self.log("npm is required and should come with Node.js", "ERROR")
            return False

        # Check pip
        pip_cmd = "pip3" if "python3" in prerequisites else "pip"
        if not self.check_dependency(pip_cmd, "--version"):
            self.log("pip is required for Python package installation", "ERROR")
            return False

        # Optional: Check git
        if self.check_dependency("git", "--version"):
            self.log("✓ Git available for version control", "SUCCESS")
        else:
            self.log("ℹ️  Git not found - version control won't be available", "WARNING")

        self.log("✅ Prerequisites check completed", "SUCCESS")
        return True

    def _try_install_without_postgres(self, pip_cmd):
        """Try to install requirements without PostgreSQL adapter as fallback"""
        try:
            self.log(
                "Creating temporary requirements file without PostgreSQL adapter...",
                "INFO",
            )

            # Read original requirements
            requirements_file = self.backend_dir / "requirements.txt"
            with open(requirements_file, "r") as f:
                lines = f.readlines()

            # Filter out PostgreSQL-related packages
            filtered_lines = []
            for line in lines:
                line_lower = line.lower().strip()
                if not any(pkg in line_lower for pkg in ["psycopg", "postgres"]):
                    filtered_lines.append(line)

            # Create temporary requirements file
            temp_requirements = self.backend_dir / "requirements_temp.txt"
            with open(temp_requirements, "w") as f:
                f.writelines(filtered_lines)

            # Try installing without PostgreSQL adapter
            install_cmd = f"{pip_cmd} install --timeout 60 -r requirements_temp.txt"
            success = self.run_command(install_cmd, cwd=self.backend_dir)

            # Clean up temp file
            if temp_requirements.exists():
                temp_requirements.unlink()

            return success

        except Exception as e:
            self.log(f"Failed to install without PostgreSQL adapter: {e}", "ERROR")
            return False

    def _create_admin_user(self, python_cmd):
        """Create admin superuser with specified credentials"""
        try:
            self.log("Creating admin superuser (admin/WATERMELON1219)...", "INFO")

            # Use Django's createsuperuser command with environment variables
            create_user_cmd = (
                f'echo "from django.contrib.auth import get_user_model; '
                f"User = get_user_model(); "
                f"User.objects.filter(username='admin').exists() or "
                f"User.objects.create_superuser('admin', 'admin@projectmeats.com', 'WATERMELON1219')\" | "
                f"{python_cmd} manage.py shell"
            )

            if self.run_command(create_user_cmd, cwd=self.backend_dir, shell=True):
                self.log("✓ Admin superuser created successfully", "SUCCESS")
                self.log("  Username: admin", "INFO")
                self.log("  Password: WATERMELON1219", "INFO")
                self.log("  Email: admin@projectmeats.com", "INFO")
            else:
                self.log(
                    "Failed to create admin user, trying alternative method...",
                    "WARNING",
                )
                # Alternative method using manage.py directly
                alt_cmd = (
                    f'{python_cmd} manage.py shell -c "'
                    f"from django.contrib.auth import get_user_model; "
                    f"User = get_user_model(); "
                    f"User.objects.filter(username='admin').exists() or "
                    f"User.objects.create_superuser('admin', 'admin@projectmeats.com', 'WATERMELON1219')\""
                )
                if self.run_command(alt_cmd, cwd=self.backend_dir):
                    self.log(
                        "✓ Admin superuser created with alternative method", "SUCCESS"
                    )
                else:
                    self.log("Failed to create admin user", "WARNING")
                    self.log(
                        "You can create it manually: python manage.py createsuperuser",
                        "INFO",
                    )

        except Exception as e:
            self.log(f"Error creating admin user: {e}", "WARNING")
            self.log(
                "You can create it manually: python manage.py createsuperuser", "INFO"
            )

    def _create_test_data(self, python_cmd):
        """Create comprehensive test data for the application"""
        try:
            self.log("Creating comprehensive test data for all entities...", "INFO")

            # Check if the test data script exists
            test_data_script = self.backend_dir / "create_test_data.py"
            if not test_data_script.exists():
                self.log(
                    "Test data script not found, skipping test data creation", "WARNING"
                )
                return

            # Execute the test data creation script
            create_data_cmd = f"{python_cmd} create_test_data.py"
            if self.run_command(create_data_cmd, cwd=self.backend_dir):
                self.log("✓ Test data created successfully", "SUCCESS")
                self.log("  The application now has sample data for testing", "INFO")
                self.log(
                    "  This includes suppliers, customers, purchase orders, and more",
                    "INFO",
                )
            else:
                self.log("Failed to create test data", "WARNING")
                self.log(
                    "You can create it manually: cd backend && python create_test_data.py",
                    "INFO",
                )

        except Exception as e:
            self.log(f"Error creating test data: {e}", "WARNING")
            self.log(
                "You can create it manually: cd backend && python create_test_data.py",
                "INFO",
            )

    def setup_backend(self):
        """Setup Django backend"""
        self.log("🔧 Setting up Django backend...", "STEP")

        if not self.backend_dir.exists():
            self.log(f"Backend directory not found: {self.backend_dir}", "ERROR")
            return False

        # Copy environment file
        env_source = self.backend_dir / ".env.example"
        env_dest = self.backend_dir / ".env"
        if not self.copy_env_file(env_source, env_dest):
            return False

        # Install Python dependencies
        self.log("📦 Installing Python dependencies...", "INFO")

        # Determine Python and pip commands
        python_cmd = "python3" if shutil.which("python3") else "python"
        pip_cmd = "pip3" if shutil.which("pip3") else "pip"

        # Check if we should use development requirements for better compatibility
        requirements_file = self.backend_dir / "requirements.txt"
        requirements_dev_file = self.backend_dir / "requirements-dev.txt"

        # For Python 3.13+, prefer development requirements without PostgreSQL issues
        use_dev_requirements = (
            sys.version_info >= (3, 13)
            and requirements_dev_file.exists()
            and self.is_windows
        )

        if use_dev_requirements:
            self.log(
                "Python 3.13+ detected on Windows - using development requirements",
                "INFO",
            )
            target_requirements = "requirements-dev.txt"
        else:
            target_requirements = "requirements.txt"

        if not (self.backend_dir / target_requirements).exists():
            self.log(
                f"Requirements file not found: {self.backend_dir / target_requirements}",
                "ERROR",
            )
            return False

        # Try to install with timeout and retry
        install_cmd = f"{pip_cmd} install --timeout 30 -r {target_requirements}"
        if not self.run_command(install_cmd, cwd=self.backend_dir):
            self.log(
                "First attempt failed, trying with increased timeout...", "WARNING"
            )
            # Retry with longer timeout for slow networks
            install_cmd_retry = (
                f"{pip_cmd} install --timeout 60 --retries 2 -r {target_requirements}"
            )
            if not self.run_command(install_cmd_retry, cwd=self.backend_dir):
                self.log("Failed to install Python dependencies", "ERROR")
                self.log("This may be due to one of the following issues:", "ERROR")

                # Check for common Python 3.13+ psycopg issues
                if sys.version_info >= (3, 13):
                    self.log(
                        "• Python 3.13+ detected: PostgreSQL adapter compatibility issue",
                        "ERROR",
                    )
                    self.log(
                        "  Solution: Install Visual C++ Build Tools or use SQLite for development",
                        "ERROR",
                    )
                    self.log(
                        "  Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/",
                        "ERROR",
                    )
                    self.log(
                        "  Alternative: The project uses SQLite by default, so PostgreSQL is optional",
                        "ERROR",
                    )

                self.log("• Network issues or package index problems", "ERROR")
                self.log("• Missing system dependencies (like build tools)", "ERROR")
                self.log("", "ERROR")
                self.log("Try these solutions:", "ERROR")
                self.log(
                    "1. Run 'pip install -r backend/requirements.txt' manually for detailed error info",
                    "ERROR",
                )
                self.log(
                    "2. For PostgreSQL issues: Install Visual C++ Build Tools (Windows)",
                    "ERROR",
                )
                self.log(
                    "3. Skip PostgreSQL: Remove 'psycopg[binary]' line from requirements.txt",
                    "ERROR",
                )
                self.log(
                    "4. Use development mode: The app works with SQLite (default database)",
                    "ERROR",
                )

                # Try to continue setup without PostgreSQL adapter
                self.log("", "INFO")
                self.log(
                    "Attempting to continue setup without PostgreSQL adapter...",
                    "WARNING",
                )
                if self._try_install_without_postgres(pip_cmd):
                    self.log(
                        "✓ Successfully installed other dependencies (PostgreSQL adapter skipped)",
                        "SUCCESS",
                    )
                    self.log(
                        "ℹ️  The application will use SQLite database (recommended for development)",
                        "INFO",
                    )
                else:
                    return False

        # Run migrations
        self.log("🗃️  Running database migrations...", "INFO")
        migrate_cmd = f"{python_cmd} manage.py migrate"
        if not self.run_command(migrate_cmd, cwd=self.backend_dir):
            self.log("Failed to run migrations", "ERROR")
            return False

        # Create admin superuser
        self.log("👤 Creating admin superuser...", "INFO")
        self._create_admin_user(python_cmd)

        # Create test data
        self.log("📊 Creating test data...", "INFO")
        self._create_test_data(python_cmd)

        self.log("✅ Backend setup complete!", "SUCCESS")
        return True

    def setup_frontend(self):
        """Setup React frontend"""
        self.log("🔧 Setting up React frontend...", "STEP")

        if not self.frontend_dir.exists():
            self.log(f"Frontend directory not found: {self.frontend_dir}", "ERROR")
            return False

        # Check package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            self.log(f"package.json not found: {package_json}", "ERROR")
            return False

        # Install Node.js dependencies
        self.log("📦 Installing Node.js dependencies...", "INFO")

        if not self.run_command("npm install", cwd=self.frontend_dir):
            self.log(
                "First attempt failed, trying npm install with cache clean...",
                "WARNING",
            )
            # Retry with cache clear for reliability
            if not self.run_command(
                "npm cache clean --force && npm install",
                cwd=self.frontend_dir,
                shell=True,
            ):
                self.log("Failed to install Node.js dependencies", "ERROR")
                self.log(
                    "This may be due to network issues. Try running 'npm install' in the frontend directory manually.",
                    "ERROR",
                )
                return False

        # Copy environment file if it exists
        env_source = self.frontend_dir / ".env.example"
        env_dest = self.frontend_dir / ".env.local"

        if env_source.exists():
            self.copy_env_file(env_source, env_dest)
        else:
            # Create a basic environment file
            try:
                with open(env_dest, "w", encoding="utf-8") as f:
                    f.write("# React Environment Variables\n")
                    f.write("REACT_APP_API_BASE_URL=http://localhost:8000/api/v1\n")
                    f.write("REACT_APP_ENVIRONMENT=development\n")
                self.log(f"✓ Created basic {env_dest.name}", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to create {env_dest}: {e}", "WARNING")

        self.log("✅ Frontend setup complete!", "SUCCESS")
        return True

    def setup_ai_assistant_only(self):
        """Setup AI assistant configuration only"""
        self.log("🤖 Setting up AI Assistant configuration...", "STEP")

        # Check if the comprehensive setup script exists
        ai_setup_script = self.project_root / "setup_ai_assistant.py"
        if ai_setup_script.exists():
            self.log("Running comprehensive AI assistant setup...", "INFO")
            try:
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(ai_setup_script)], cwd=self.project_root
                )
                return result.returncode == 0
            except Exception as e:
                self.log(f"Failed to run AI assistant setup: {e}", "ERROR")
                return False
        else:
            self.log("AI assistant setup script not found", "ERROR")
            return False

    def setup_ai_assistant_integration(self):
        """Integrate AI assistant setup into main setup"""
        self.log("🤖 AI Assistant Configuration", "STEP")

        # Ask if user wants to configure AI assistant
        try:
            response = (
                input(
                    f"{Colors.CYAN}[INPUT]{Colors.END} Configure AI Assistant now? (y/N): "
                )
                .strip()
                .lower()
            )
            if response in ["y", "yes"]:
                return self.setup_ai_assistant_only()
            else:
                self.log("AI Assistant configuration skipped", "WARNING")
                self.log(
                    "Run 'python setup_ai_assistant.py' later to configure AI features",
                    "INFO",
                )
                return True
        except KeyboardInterrupt:
            self.log("\nAI Assistant configuration skipped", "WARNING")
            return True

    def print_next_steps(self):
        """Print helpful next steps"""
        self.log("\n🎉 Setup completed successfully!", "SUCCESS", Colors.BOLD)

        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        print(f"{Colors.GREEN}1.{Colors.END} Start the backend server:")
        if self.is_windows:
            print(f"   {Colors.CYAN}cd backend; python manage.py runserver{Colors.END}")
            print(f"   {Colors.CYAN}# Or in two commands: cd backend{Colors.END}")
            print(
                f"   {Colors.CYAN}#                     python manage.py runserver{Colors.END}"
            )
        else:
            print(
                f"   {Colors.CYAN}make backend{Colors.END} or {Colors.CYAN}cd backend && python manage.py runserver{Colors.END}"
            )

        print(f"\n{Colors.GREEN}2.{Colors.END} Start the frontend server:")
        if self.is_windows:
            print(f"   {Colors.CYAN}cd frontend; npm start{Colors.END}")
            print(f"   {Colors.CYAN}# Or in two commands: cd frontend{Colors.END}")
            print(f"   {Colors.CYAN}#                     npm start{Colors.END}")
        else:
            print(
                f"   {Colors.CYAN}make frontend{Colors.END} or {Colors.CYAN}cd frontend && npm start{Colors.END}"
            )

        print(f"\n{Colors.GREEN}3.{Colors.END} Access the application:")
        print(f"   {Colors.CYAN}Backend API: http://localhost:8000{Colors.END}")
        print(f"   {Colors.CYAN}Frontend:    http://localhost:3000{Colors.END}")
        print(
            f"   {Colors.CYAN}API Docs:    http://localhost:8000/api/docs/{Colors.END}"
        )
        print(f"   {Colors.CYAN}Admin Panel: http://localhost:8000/admin/{Colors.END}")

        # Check if AI assistant is configured
        env_file = self.backend_dir / ".env"
        ai_configured = False
        if env_file.exists():
            with open(env_file, "r") as f:
                content = f.read()
                ai_configured = any(
                    key in content
                    for key in [
                        "OPENAI_API_KEY",
                        "ANTHROPIC_API_KEY",
                        "AZURE_OPENAI_API_KEY",
                    ]
                )

        if ai_configured:
            print(f"\n{Colors.GREEN}4.{Colors.END} AI Assistant Features:")
            print(
                f"   {Colors.CYAN}Chat Interface: Access via frontend navigation{Colors.END}"
            )
            print(
                f"   {Colors.CYAN}Document Processing: Upload documents for AI analysis{Colors.END}"
            )
            print(
                f"   {Colors.CYAN}Business Intelligence: Ask questions about your data{Colors.END}"
            )
        else:
            print(f"\n{Colors.YELLOW}🤖 AI Assistant Setup:{Colors.END}")
            print(
                f"   {Colors.YELLOW}Run 'python setup_ai_assistant.py' to configure AI features{Colors.END}"
            )
            print(
                f"   {Colors.YELLOW}Includes document processing, chat interface, and business intelligence{Colors.END}"
            )

        if not self.is_windows:
            print(f"\n{Colors.BOLD}Available Make Commands:{Colors.END}")
            print(f"   {Colors.CYAN}make dev{Colors.END}      - Start both servers")
            print(f"   {Colors.CYAN}make test{Colors.END}     - Run all tests")
            print(
                f"   {Colors.CYAN}make docs{Colors.END}     - Generate API documentation"
            )
            print(f"   {Colors.CYAN}make clean{Colors.END}    - Clean build artifacts")

        print(f"\n{Colors.BOLD}Documentation:{Colors.END}")
        print(
            f"   {Colors.CYAN}README.md{Colors.END}                    - Project overview"
        )
        print(
            f"   {Colors.CYAN}docs/setup-and-development.md{Colors.END} - Development guide"
        )
        print(
            f"   {Colors.CYAN}docs/ai_assistant_setup.md{Colors.END}    - AI assistant configuration"
        )
        print(
            f"   {Colors.CYAN}docs/{Colors.END}                        - Complete documentation"
        )

        print(f"\n{Colors.BOLD}Getting Started with AI Assistant:{Colors.END}")
        print(
            f"   {Colors.GREEN}1.{Colors.END} Configure: {Colors.CYAN}python setup_ai_assistant.py{Colors.END}"
        )
        print(
            f"   {Colors.GREEN}2.{Colors.END} Test: Upload a document or send a chat message"
        )
        print(
            f"   {Colors.GREEN}3.{Colors.END} Explore: Try business intelligence queries"
        )

    def main(self):
        """Main setup function"""
        parser = argparse.ArgumentParser(
            description="ProjectMeats Cross-Platform Setup Script with AI Assistant Support",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python setup.py              # Full setup with AI assistant configuration
  python setup.py --backend    # Backend only  
  python setup.py --frontend   # Frontend only
  python setup.py --ai-only    # AI assistant setup only
  
For comprehensive AI assistant setup, use:
  python setup_ai_assistant.py
  
For more information, see docs/ai_assistant_setup.md
            """,
        )

        parser.add_argument("--backend", action="store_true", help="Setup backend only")
        parser.add_argument(
            "--frontend", action="store_true", help="Setup frontend only"
        )
        parser.add_argument(
            "--ai-only", action="store_true", help="Setup AI assistant only"
        )
        parser.add_argument(
            "--skip-prereqs", action="store_true", help="Skip prerequisite checks"
        )
        parser.add_argument(
            "--skip-ai", action="store_true", help="Skip AI assistant configuration"
        )

        args = parser.parse_args()

        # Welcome message
        self.log("🚀 ProjectMeats Setup Script", "STEP", Colors.BOLD)
        self.log(f"Platform: {platform.system()} {platform.release()}", "INFO")
        self.log(f"Python: {sys.version.split()[0]}", "INFO")
        self.log(f"Working directory: {self.project_root}", "INFO")

        # Check prerequisites
        if not args.skip_prereqs and not self.check_prerequisites():
            self.log(
                "Prerequisites not met. Please install required dependencies.", "ERROR"
            )
            return 1

        # AI-only setup
        if args.ai_only:
            return self.setup_ai_assistant_only()

        # Determine what to setup
        setup_backend = args.backend or not args.frontend
        setup_frontend = args.frontend or not args.backend

        success = True

        # Setup backend
        if setup_backend:
            if not self.setup_backend():
                success = False

        # Setup frontend
        if setup_frontend:
            if not self.setup_frontend():
                success = False

        # Setup AI assistant if not skipped
        if success and not args.skip_ai and (setup_backend or args.ai_only):
            success = self.setup_ai_assistant_integration()

        if success:
            self.print_next_steps()
            return 0
        else:
            self.log(
                "Setup completed with errors. Please check the messages above.", "ERROR"
            )
            return 1


if __name__ == "__main__":
    setup = ProjectMeatsSetup()
    sys.exit(setup.main())
