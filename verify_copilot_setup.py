#!/usr/bin/env python3
"""
GitHub Copilot Setup Verification Script for ProjectMeats

This script verifies that all Copilot configurations are properly set up
and provides a summary of the available features.
"""
import os
import json
import sys
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists and print status."""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False


def check_json_file(path: str, description: str) -> bool:
    """Check if a JSON file exists and is valid."""
    if not os.path.exists(path):
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False
    
    try:
        with open(path, 'r') as f:
            json.load(f)
        print(f"✅ {description}: {path} (Valid JSON)")
        return True
    except json.JSONDecodeError:
        print(f"❌ {description}: {path} (INVALID JSON)")
        return False


def main():
    """Main verification function."""
    print("🔍 ProjectMeats GitHub Copilot Setup Verification")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    all_good = True
    
    # Check GitHub Copilot instructions
    copilot_instructions = project_root / ".github" / "copilot-instructions.md"
    all_good &= check_file_exists(str(copilot_instructions), "Copilot Instructions")
    
    # Check VS Code configurations
    print("\n📁 VS Code Configuration:")
    vscode_settings = project_root / ".vscode" / "settings.json"
    vscode_tasks = project_root / ".vscode" / "tasks.json"
    vscode_launch = project_root / ".vscode" / "launch.json"
    vscode_extensions = project_root / ".vscode" / "extensions.json"
    
    all_good &= check_json_file(str(vscode_settings), "VS Code Settings")
    all_good &= check_json_file(str(vscode_tasks), "VS Code Tasks")
    all_good &= check_json_file(str(vscode_launch), "VS Code Launch Config")
    all_good &= check_json_file(str(vscode_extensions), "VS Code Extensions")
    
    # Check workspace file
    workspace_file = project_root / "ProjectMeats.code-workspace"
    all_good &= check_json_file(str(workspace_file), "VS Code Workspace")
    
    # Check MCP configuration
    print("\n🔗 MCP Configuration:")
    mcp_config = project_root / ".mcp-config.json"
    all_good &= check_json_file(str(mcp_config), "MCP Configuration")
    
    # Check documentation
    print("\n📚 Documentation:")
    copilot_guide = project_root / "docs" / "copilot_usage_guide.md"
    developer_guidelines = project_root / "docs" / "copilot_developer_guidelines.md"
    
    all_good &= check_file_exists(str(copilot_guide), "Copilot Usage Guide")
    all_good &= check_file_exists(str(developer_guidelines), "Developer Guidelines")
    
    # Check project structure
    print("\n🏗️ Project Structure:")
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"
    docs_dir = project_root / "docs"
    
    all_good &= check_file_exists(str(backend_dir), "Backend Directory")
    all_good &= check_file_exists(str(frontend_dir), "Frontend Directory")
    all_good &= check_file_exists(str(docs_dir), "Documentation Directory")
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All GitHub Copilot configurations are set up correctly!")
        print("\n📋 Next Steps:")
        print("1. Open VS Code with: code ProjectMeats.code-workspace")
        print("2. Install recommended extensions when prompted")
        print("3. Read docs/copilot_usage_guide.md for usage instructions")
        print("4. Start developing with enhanced Copilot assistance!")
        sys.exit(0)
    else:
        print("⚠️  Some configurations are missing or invalid.")
        print("Please check the errors above and fix them before continuing.")
        sys.exit(1)


if __name__ == "__main__":
    main()