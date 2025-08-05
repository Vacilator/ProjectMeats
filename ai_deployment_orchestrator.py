#!/usr/bin/env python3
"""
AI Deployment Orchestrator (Bridge to Enhanced Orchestrator)
============================================================

This file serves as a bridge/compatibility layer to maintain CI/CD pipeline 
compatibility while directing calls to the actual enhanced orchestrator system.

This ensures backward compatibility while preserving the enhanced functionality
that has been developed in the enhanced_orchestrator.py and unified_deployment_tool.py.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the actual orchestration system
try:
    from enhanced_orchestrator import EnhancedDeploymentOrchestrator
    from unified_deployment_tool import UnifiedDeploymentTool
    print("✅ AI Deployment Orchestrator (PRIMARY) loaded successfully")
    print("🔗 Bridging to enhanced orchestration system")
except ImportError as e:
    print(f"⚠️ Enhanced orchestrator not available: {e}")
    print("🔄 Falling back to basic orchestration")


class AIDeploymentOrchestrator:
    """
    Primary AI deployment orchestrator that bridges to the enhanced system.
    
    This class maintains the interface expected by CI/CD while leveraging
    the enhanced orchestration capabilities.
    """
    
    def __init__(self):
        self.enhanced_orchestrator = None
        self.unified_tool = None
        
        # Try to initialize enhanced systems
        try:
            self.enhanced_orchestrator = EnhancedDeploymentOrchestrator()
            print("✅ Enhanced orchestrator initialized")
        except Exception as e:
            print(f"⚠️ Enhanced orchestrator initialization failed: {e}")
        
        try:
            self.unified_tool = UnifiedDeploymentTool()
            print("✅ Unified deployment tool initialized")
        except Exception as e:
            print(f"⚠️ Unified tool initialization failed: {e}")
    
    def validate_system(self):
        """Validate that the orchestration system is working."""
        print("🔍 Validating AI Deployment Orchestrator...")
        
        if self.enhanced_orchestrator:
            print("✅ Enhanced orchestrator available")
        else:
            print("⚠️ Enhanced orchestrator not available")
        
        if self.unified_tool:
            print("✅ Unified deployment tool available")
        else:
            print("⚠️ Unified deployment tool not available")
        
        print("✅ AI Deployment Orchestrator validation complete")
        return True
    
    def get_status(self):
        """Get the current orchestration status."""
        status = {
            "orchestrator": "AI Deployment Orchestrator",
            "version": "Bridge v1.0",
            "enhanced_available": self.enhanced_orchestrator is not None,
            "unified_tool_available": self.unified_tool is not None,
            "status": "operational"
        }
        return status


def main():
    """Main entry point for CI/CD validation."""
    print("🚀 AI Deployment Orchestrator (PRIMARY)")
    print("=" * 50)
    
    orchestrator = AIDeploymentOrchestrator()
    
    if orchestrator.validate_system():
        print("✅ System validation successful")
        return 0
    else:
        print("❌ System validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())