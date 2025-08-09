#!/usr/bin/env python3
"""
Demonstration script showing before/after comparison of logging issues.
This script analyzes the deployment logs to show the improvement.
"""

import json
from collections import Counter
from pathlib import Path

def analyze_log_file(log_file_path):
    """Analyze a deployment log file for issues"""
    if not Path(log_file_path).exists():
        return {"file_not_found": True}
    
    message_counts = Counter()
    level_counts = Counter()
    issues = []
    
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                message = entry['message']
                level = entry['level']
                
                message_counts[message] += 1
                level_counts[level] += 1
                
                # Identify problematic patterns
                if "Logging initialized" in message:
                    if message_counts[message] > 1:
                        issues.append(f"Duplicate logging init: {message}")
                
                if "Error detected:" in message and "detected" in message:
                    # Check if this is a false positive
                    if any(fp in message for fp in ["Node.js package conflicts", "Package repository", "Permission issues", "Port conflicts"]):
                        issues.append(f"Potential false positive: {message}")
                        
            except json.JSONDecodeError:
                continue
    
    return {
        "total_entries": sum(message_counts.values()),
        "unique_messages": len(message_counts),
        "level_counts": dict(level_counts),
        "most_common_messages": message_counts.most_common(10),
        "issues": issues,
        "logging_init_count": sum(count for msg, count in message_counts.items() if "Logging initialized" in msg)
    }

def main():
    """Compare before and after logs"""
    print("🔍 Analyzing deployment logs - Before vs After Fixes\n")
    
    # Analyze original problematic log
    print("📋 BEFORE FIXES (Original Log):")
    print("=" * 50)
    before_analysis = analyze_log_file("deployment_log_before_fix.json")
    
    if before_analysis.get("file_not_found"):
        print("❌ Original log file not found")
    else:
        print(f"Total log entries: {before_analysis['total_entries']}")
        print(f"Unique messages: {before_analysis['unique_messages']}")
        print(f"Logging initialization count: {before_analysis['logging_init_count']}")
        print(f"Level distribution: {before_analysis['level_counts']}")
        print(f"Issues found: {len(before_analysis['issues'])}")
        
        if before_analysis['issues']:
            print("\n🚨 Issues detected:")
            for issue in before_analysis['issues'][:5]:  # Show first 5 issues
                print(f"  • {issue}")
            if len(before_analysis['issues']) > 5:
                print(f"  ... and {len(before_analysis['issues']) - 5} more issues")
        
        print(f"\n📊 Most frequent messages:")
        for msg, count in before_analysis['most_common_messages'][:3]:
            print(f"  • {count}x: {msg[:80]}...")
    
    # Analyze current log after fixes
    print(f"\n📋 AFTER FIXES (Current Log):")
    print("=" * 50)
    after_analysis = analyze_log_file("deployment_log.json")
    
    if after_analysis.get("file_not_found"):
        print("❌ Current log file not found")
    else:
        print(f"Total log entries: {after_analysis['total_entries']}")
        print(f"Unique messages: {after_analysis['unique_messages']}")
        print(f"Logging initialization count: {after_analysis['logging_init_count']}")
        print(f"Level distribution: {after_analysis['level_counts']}")
        print(f"Issues found: {len(after_analysis['issues'])}")
        
        if after_analysis['issues']:
            print(f"\n🚨 Issues detected:")
            for issue in after_analysis['issues'][:5]:
                print(f"  • {issue}")
        else:
            print("\n✅ No logging issues detected!")
        
        print(f"\n📊 Most frequent messages:")
        for msg, count in after_analysis['most_common_messages'][:3]:
            print(f"  • {count}x: {msg[:80]}...")
    
    # Compare improvements
    if not before_analysis.get("file_not_found") and not after_analysis.get("file_not_found"):
        print(f"\n📈 IMPROVEMENT SUMMARY:")
        print("=" * 50)
        
        logging_init_before = before_analysis['logging_init_count']
        logging_init_after = after_analysis['logging_init_count']
        
        issues_before = len(before_analysis['issues'])
        issues_after = len(after_analysis['issues'])
        
        print(f"Logging initialization spam reduction:")
        print(f"  Before: {logging_init_before} messages")
        print(f"  After:  {logging_init_after} messages")
        print(f"  Improvement: {logging_init_before - logging_init_after} fewer messages")
        
        print(f"\nOverall issues reduction:")
        print(f"  Before: {issues_before} issues")
        print(f"  After:  {issues_after} issues") 
        print(f"  Improvement: {issues_before - issues_after} fewer issues")
        
        if issues_after < issues_before:
            print(f"\n🎉 Successfully reduced deployment logging issues!")
        else:
            print(f"\n⚠️  Issues remain - may need additional fixes")
    
    print("\n✨ Analysis complete!")

if __name__ == "__main__":
    main()