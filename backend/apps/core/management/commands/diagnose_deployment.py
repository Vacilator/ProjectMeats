"""
Django management command to diagnose deployment issues.

This command helps identify and fix common deployment problems including:
- Django settings configuration
- Database connectivity
- Secret key validation
- Environment variable issues
- Static files configuration
"""

import os
import secrets
import string
import sys
from pathlib import Path

from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Diagnose and fix common Django deployment issues"

    def add_arguments(self, parser):
        parser.add_argument(
            "--generate-secret-key",
            action="store_true",
            help="Generate a safe secret key for deployment",
        )
        parser.add_argument(
            "--validate-secret-key",
            type=str,
            help="Validate a secret key for deployment safety",
        )
        parser.add_argument(
            "--test-database",
            action="store_true",
            help="Test database connectivity",
        )
        parser.add_argument(
            "--check-environment",
            action="store_true",
            help="Check environment configuration",
        )
        parser.add_argument(
            "--fix-permissions",
            action="store_true",
            help="Check and suggest file permission fixes",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔍 Django Deployment Diagnostics\n"))

        # Execute requested operations
        if options["generate_secret_key"]:
            self.generate_secret_key()

        if options["validate_secret_key"]:
            self.validate_secret_key(options["validate_secret_key"])

        if options["test_database"]:
            self.test_database()

        if options["check_environment"]:
            self.check_environment()

        if options["fix_permissions"]:
            self.check_permissions()

        # If no specific options, run all diagnostics
        if not any(
            [
                options["generate_secret_key"],
                options["validate_secret_key"],
                options["test_database"],
                options["check_environment"],
                options["fix_permissions"],
            ]
        ):
            self.run_full_diagnostics()

    def generate_secret_key(self):
        """Generate a deployment-safe secret key."""
        self.stdout.write("🔑 Generating safe Django secret key...\n")

        # Use characters safe for shell environments
        safe_chars = string.ascii_letters + string.digits + "-_@#$%^&*+=<>?"
        key = "".join(secrets.choice(safe_chars) for _ in range(50))

        self.stdout.write(f"Generated key: {key}\n")
        self.stdout.write(
            self.style.WARNING(
                "⚠️  Please update your .env file or environment variables with this key\n"
            )
        )

    def validate_secret_key(self, key):
        """Validate secret key safety."""
        self.stdout.write("🔐 Validating secret key...\n")

        problematic_chars = [
            "(",
            ")",
            "'",
            '"',
            "`",
            "\\",
            "|",
            ";",
            "&",
            " ",
            "\t",
            "\n",
        ]
        issues = []

        for char in problematic_chars:
            if char in key:
                issues.append(f"Contains shell special character: '{char}'")

        if len(key) < 50:
            issues.append(f"Too short: {len(key)} characters (minimum 50)")

        if key.startswith("django-insecure-"):
            issues.append("Development key detected")

        if issues:
            self.stdout.write(self.style.ERROR("❌ Secret key validation failed:"))
            for issue in issues:
                self.stdout.write(f"  • {issue}")
            self.stdout.write("")
            self.generate_secret_key()
        else:
            self.stdout.write(self.style.SUCCESS("✅ Secret key is deployment-safe\n"))

    def test_database(self):
        """Test database connectivity."""
        self.stdout.write("🗄️  Testing database connectivity...\n")

        try:
            # Test basic connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            if result:
                self.stdout.write(
                    self.style.SUCCESS("✅ Database connection successful\n")
                )

            # Test migrations
            from io import StringIO

            from django.core.management import call_command

            out = StringIO()
            call_command("showmigrations", "--verbosity=0", stdout=out)
            migrations_output = out.getvalue()

            if "[ ]" in migrations_output:
                self.stdout.write(
                    self.style.WARNING("⚠️  Unapplied migrations detected")
                )
                self.stdout.write("   Run: python manage.py migrate\n")
            else:
                self.stdout.write(self.style.SUCCESS("✅ All migrations are applied\n"))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Database connection failed: {str(e)}\n")
            )

    def check_environment(self):
        """Check environment configuration."""
        self.stdout.write("🌍 Checking environment configuration...\n")

        # Critical settings to check
        checks = [
            ("DEBUG", "Should be False in production"),
            ("SECRET_KEY", "Must be set and secure"),
            ("ALLOWED_HOSTS", "Must include your domain"),
            ("DATABASE_URL", "Database connection string"),
        ]

        for setting_name, description in checks:
            try:
                value = getattr(settings, setting_name, None)
                if setting_name == "SECRET_KEY" and value:
                    # Don't display the actual key
                    display_value = f"Set (length: {len(value)})"
                    self.validate_secret_key(value)
                else:
                    display_value = str(value)

                if value:
                    self.stdout.write(f"✅ {setting_name}: {display_value}")
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  {setting_name}: Not set - {description}"
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {setting_name}: Error - {str(e)}")
                )

        self.stdout.write("")

    def check_permissions(self):
        """Check file and directory permissions."""
        self.stdout.write("📁 Checking file permissions...\n")

        # Check critical paths
        base_dir = Path(settings.BASE_DIR)
        paths_to_check = [
            (base_dir, "Base directory"),
            (Path(settings.STATIC_ROOT), "Static files directory"),
            (Path(settings.MEDIA_ROOT), "Media files directory"),
        ]

        for path, description in paths_to_check:
            if path.exists():
                if os.access(path, os.R_OK | os.W_OK):
                    self.stdout.write(f"✅ {description}: Readable and writable")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {description}: Permission issues")
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  {description}: Does not exist - {path}")
                )

        self.stdout.write("")

    def run_full_diagnostics(self):
        """Run all diagnostic checks."""
        self.stdout.write("🔍 Running full deployment diagnostics...\n")

        self.check_environment()
        self.test_database()
        self.check_permissions()

        # Final summary
        self.stdout.write(self.style.SUCCESS("📋 Diagnostics complete!"))
        self.stdout.write("\n💡 For specific fixes, run with individual flags:")
        self.stdout.write("   --generate-secret-key    Generate safe secret key")
        self.stdout.write("   --test-database          Test database connectivity")
        self.stdout.write("   --check-environment      Check configuration")
        self.stdout.write("   --fix-permissions        Check file permissions\n")
