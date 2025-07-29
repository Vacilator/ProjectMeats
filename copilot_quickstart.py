#!/usr/bin/env python3
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
            print("\n📂 Opening optimized workspace...")
            subprocess.run(['code', 'ProjectMeats.code-workspace'])
            
        else:
            print("❌ VS Code not found in PATH")
            
    except Exception as e:
        print(f"❌ Could not launch VS Code: {e}")
    
    # Show key features
    print("\n🎯 Key Copilot Features Available:")
    print("  • Custom instructions for Django/React patterns")
    print("  • MCP servers for enhanced AI context")  
    print("  • Optimized VS Code workspace")
    print("  • Smart code suggestions and completions")
    print("  • PowerApps migration assistance")
    
    # Open documentation
    print("\n📚 Opening Copilot documentation...")
    docs_path = Path(__file__).parent / "docs" / "copilot_usage_guide.md"
    if docs_path.exists():
        try:
            webbrowser.open(f"file://{docs_path.absolute()}")
        except:
            print(f"📖 Manual link: {docs_path}")
    
    print("\n🎉 Setup complete! Happy coding with AI assistance!")


if __name__ == "__main__":
    main()
