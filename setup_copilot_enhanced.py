#!/usr/bin/env python3
"""
Enhanced GitHub Copilot and MCP Setup Script for ProjectMeats

This script automatically configures and validates an enhanced GitHub Copilot
development environment with Model Context Protocol (MCP) servers for smarter
AI assistance.
"""
import os
import json
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional


class CopilotEnhancer:
    """Enhanced GitHub Copilot setup with MCP servers and optimization."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def print_banner(self):
        """Print setup banner."""
        print("🚀 ProjectMeats Enhanced GitHub Copilot Setup")
        print("=" * 50)
        print("Setting up smarter AI assistance with:")
        print("  • GitHub Copilot custom instructions")
        print("  • Optimized VS Code development environment")
        print("  • Model Context Protocol (MCP) servers")
        print("  • Advanced AI context and memory")
        print("")

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed."""
        print("🔍 Checking prerequisites...")
        
        prerequisites = {
            'node': ['node', '--version'],
            'npm': ['npm', '--version'],
            'python': [sys.executable, '--version'],
        }
        
        missing = []
        for name, cmd in prerequisites.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"  ✅ {name}: {version}")
                else:
                    missing.append(name)
            except FileNotFoundError:
                missing.append(name)
        
        if missing:
            print(f"  ❌ Missing prerequisites: {', '.join(missing)}")
            return False
        
        return True

    def install_mcp_servers(self) -> bool:
        """Install and configure MCP servers."""
        print("\n🔧 Installing MCP servers...")
        
        # Standard MCP servers
        standard_servers = [
            '@modelcontextprotocol/server-filesystem',
            '@modelcontextprotocol/server-git', 
            '@modelcontextprotocol/server-sqlite'
        ]
        
        # Enhanced MCP servers for better context
        enhanced_servers = [
            '@modelcontextprotocol/server-memory',  # Context persistence
            '@modelcontextprotocol/server-slack',   # Communication context
        ]
        
        all_servers = standard_servers + enhanced_servers
        
        for server in all_servers:
            print(f"  📦 Installing {server}...")
            try:
                result = subprocess.run(
                    ['npm', 'install', '-g', server],
                    capture_output=True, 
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"    ✅ {server} installed successfully")
                else:
                    # Try with npx for servers that work better this way
                    print(f"    ℹ️  {server} will be installed on-demand via npx")
            except subprocess.TimeoutExpired:
                print(f"    ⚠️  {server} installation timed out, will use npx")
            except Exception as e:
                print(f"    ⚠️  {server} installation failed: {e}")
                
        return True

    def create_enhanced_mcp_config(self) -> bool:
        """Create enhanced MCP configuration."""
        print("\n⚙️  Creating enhanced MCP configuration...")
        
        config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-filesystem", 
                        str(self.project_root)
                    ],
                    "env": {
                        "FILESYSTEM_MAX_FILE_SIZE": "1048576",  # 1MB limit
                        "FILESYSTEM_ALLOWED_EXTENSIONS": ".py,.js,.ts,.tsx,.md,.json,.yml,.yaml,.sql"
                    }
                },
                "sqlite": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-sqlite", 
                        str(self.project_root / "backend" / "db.sqlite3")
                    ],
                    "env": {
                        "SQLITE_MAX_ROWS": "1000"
                    }
                },
                "git": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-git", 
                        "--repository", str(self.project_root)
                    ],
                    "env": {
                        "GIT_MAX_COMMITS": "100"
                    }
                },
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "env": {
                        "MEMORY_STORE_PATH": str(self.project_root / ".mcp-memory")
                    }
                },
                "documentation": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-filesystem",
                        str(self.project_root / "docs")
                    ],
                    "env": {
                        "FILESYSTEM_MAX_FILE_SIZE": "2097152",  # 2MB for docs
                        "FILESYSTEM_ALLOWED_EXTENSIONS": ".md,.txt,.rst"
                    }
                }
            }
        }
        
        config_path = self.project_root / ".mcp-config.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"  ✅ Enhanced MCP config created: {config_path}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to create MCP config: {e}")
            return False

    def enhance_vscode_settings(self) -> bool:
        """Enhance VS Code settings for better Copilot integration."""
        print("\n🎛️  Enhancing VS Code settings...")
        
        settings_path = self.project_root / ".vscode" / "settings.json"
        
        if not settings_path.exists():
            print("  ❌ VS Code settings not found")
            return False
            
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                
            # Enhanced Copilot settings
            copilot_enhancements = {
                "github.copilot.enable": {
                    "*": True,
                    "yaml": True,
                    "plaintext": True,  # Enable for documentation
                    "markdown": True,
                    "javascript": True,
                    "typescript": True,
                    "python": True,
                    "sql": True,
                    "dockerfile": True
                },
                "github.copilot.advanced": {
                    "secret_key": "github.copilot",
                    "length": 1000,  # Longer suggestions
                    "temperature": 0.1,
                    "top_p": 1,
                    "stop": ["\n\n", "# TODO", "# FIXME"]
                },
                "github.copilot.chat.welcomeMessage": "never",
                "github.copilot.suggestions.count": 5,  # More suggestions
                "github.copilot.experimental.chat.codeGeneration": True,
                
                # Enhanced context for AI
                "editor.suggest.showSnippets": True,
                "editor.suggest.localityBonus": True,
                "editor.suggest.shareSuggestSelections": True,
                "editor.inlineSuggest.enabled": True,
                "editor.inlineSuggest.showToolbar": "onHover",
                
                # Performance optimizations
                "search.smartCase": True,
                "search.useIgnoreFiles": True,
                "files.watcherExclude": {
                    "**/.git/objects/**": True,
                    "**/node_modules/**": True,
                    "**/venv/**": True,
                    "**/__pycache__/**": True,
                    "**/dist/**": True,
                    "**/build/**": True,
                    "**/.mcp-memory/**": True
                }
            }
            
            # Merge enhancements with existing settings
            settings.update(copilot_enhancements)
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
                
            print("  ✅ VS Code settings enhanced")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to enhance VS Code settings: {e}")
            return False

    def create_copilot_workspace_settings(self) -> bool:
        """Create Copilot-optimized workspace settings."""
        print("\n💼 Creating Copilot workspace configuration...")
        
        workspace_path = self.project_root / "ProjectMeats.code-workspace"
        
        if not workspace_path.exists():
            print("  ❌ VS Code workspace not found")
            return False
            
        try:
            with open(workspace_path, 'r') as f:
                workspace = json.load(f)
            
            # Add Copilot-specific workspace settings
            if "settings" not in workspace:
                workspace["settings"] = {}
                
            copilot_workspace_settings = {
                "github.copilot.enableAutoCompletions": True,
                "github.copilot.autocomplete.enable": True,
                "github.copilot.chat.followUps": "on",
                "github.copilot.renameSuggestions.triggerAutomatically": True,
                
                # Project-specific context
                "files.associations": {
                    "*.md": "markdown",
                    "Makefile": "makefile",
                    "*.env*": "dotenv",
                    "*.sql": "sql"
                },
                
                # Enhanced search for better context
                "search.exclude": {
                    "**/node_modules": True,
                    "**/venv": True,
                    "**/__pycache__": True,
                    "**/dist": True,
                    "**/build": True,
                    "**/.git": True,
                    "**/.mcp-memory": True
                },
                
                # Intelligent file watching
                "files.watcherExclude": {
                    "**/.git/objects/**": True,
                    "**/node_modules/**": True,
                    "**/venv/**": True,
                    "**/__pycache__/**": True,
                    "**/dist/**": True,
                    "**/build/**": True,
                    "**/.mcp-memory/**": True
                }
            }
            
            workspace["settings"].update(copilot_workspace_settings)
            
            with open(workspace_path, 'w') as f:
                json.dump(workspace, f, indent=2)
                
            print("  ✅ Workspace configuration enhanced")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to enhance workspace: {e}")
            return False

    def create_quick_start_script(self) -> bool:
        """Create a quick start script for Copilot features."""
        print("\n📝 Creating Copilot quick-start script...")
        
        script_content = '''#!/usr/bin/env python3
"""
Quick Start Script for GitHub Copilot in ProjectMeats

This script demonstrates key Copilot features and provides interactive setup.
"""
import os
import json
import webbrowser
from pathlib import Path


def main():
    print("🚀 ProjectMeats GitHub Copilot Quick Start")
    print("=" * 45)
    
    # Check if VS Code is available
    try:
        import subprocess
        result = subprocess.run(['code', '--version'], capture_output=True)
        if result.returncode == 0:
            print("✅ VS Code detected")
            
            # Open workspace
            print("\\n📂 Opening optimized workspace...")
            subprocess.run(['code', 'ProjectMeats.code-workspace'])
            
        else:
            print("❌ VS Code not found in PATH")
            
    except Exception as e:
        print(f"❌ Could not launch VS Code: {e}")
    
    # Show key features
    print("\\n🎯 Key Copilot Features Available:")
    print("  • Custom instructions for Django/React patterns")
    print("  • MCP servers for enhanced AI context")  
    print("  • Optimized VS Code workspace")
    print("  • Smart code suggestions and completions")
    print("  • PowerApps migration assistance")
    
    # Open documentation
    print("\\n📚 Opening Copilot documentation...")
    docs_path = Path(__file__).parent / "docs" / "copilot_usage_guide.md"
    if docs_path.exists():
        try:
            webbrowser.open(f"file://{docs_path.absolute()}")
        except:
            print(f"📖 Manual link: {docs_path}")
    
    print("\\n🎉 Setup complete! Happy coding with AI assistance!")


if __name__ == "__main__":
    main()
'''
        
        script_path = self.project_root / "copilot_quickstart.py"
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable on Unix systems
            if platform.system() != 'Windows':
                os.chmod(script_path, 0o755)
                
            print(f"  ✅ Quick-start script created: {script_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to create quick-start script: {e}")
            return False

    def validate_setup(self) -> bool:
        """Validate the enhanced Copilot setup."""
        print("\n🔍 Validating enhanced setup...")
        
        checks = [
            (".github/copilot-instructions.md", "Custom instructions"),
            (".mcp-config.json", "MCP configuration"),
            (".vscode/settings.json", "VS Code settings"),
            ("ProjectMeats.code-workspace", "VS Code workspace"),
            ("copilot_quickstart.py", "Quick-start script"),
        ]
        
        all_valid = True
        for file_path, description in checks:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} missing")
                all_valid = False
                
        return all_valid

    def run_setup(self):
        """Run the complete enhanced setup."""
        self.print_banner()
        
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed. Please install missing dependencies.")
            return False
            
        steps = [
            ("Installing MCP servers", self.install_mcp_servers),
            ("Creating enhanced MCP config", self.create_enhanced_mcp_config),
            ("Enhancing VS Code settings", self.enhance_vscode_settings),
            ("Updating workspace configuration", self.create_copilot_workspace_settings),
            ("Creating quick-start script", self.create_quick_start_script),
            ("Validating setup", self.validate_setup),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Failed: {step_name}")
                return False
                
        print("\n" + "=" * 50)
        print("🎉 Enhanced GitHub Copilot setup complete!")
        print("\n📋 Next Steps:")
        print("1. Run: python copilot_quickstart.py")
        print("2. Open VS Code: code ProjectMeats.code-workspace")
        print("3. Install recommended extensions when prompted")
        print("4. Read: docs/copilot_usage_guide.md")
        print("5. Start coding with enhanced AI assistance!")
        
        return True


def main():
    """Main entry point."""
    enhancer = CopilotEnhancer()
    success = enhancer.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()