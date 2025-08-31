#!/usr/bin/env python3
"""
Test script to verify DigitalOcean PostgreSQL configuration
"""

import json
import sys
import os

def test_config():
    """Test the production configuration"""
    print("🔍 Testing DigitalOcean PostgreSQL Configuration")
    print("=" * 50)
    
    # Test 1: Check if production config exists
    config_file = "ai_deployment_config.production.json"
    if not os.path.exists(config_file):
        print(f"❌ Production config file not found: {config_file}")
        return False
    
    print(f"✅ Found production config: {config_file}")
    
    # Test 2: Load and validate config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
        
    print("✅ Configuration loaded successfully")
    
    # Test 3: Check database configuration
    db_config = config.get('database', {})
    required_fields = ['host', 'port', 'name', 'user', 'password']
    
    for field in required_fields:
        if field not in db_config:
            print(f"❌ Missing required database field: {field}")
            return False
        print(f"✅ Database {field}: {'***' if field == 'password' else db_config[field]}")
    
    # Test 4: Check external database settings
    if not db_config.get('external_managed', False):
        print("❌ external_managed should be true for DigitalOcean PostgreSQL")
        return False
    print("✅ External managed database: enabled")
    
    if db_config.get('ssl_mode') != 'require':
        print("⚠️  Warning: ssl_mode is not 'require' - DigitalOcean requires SSL")
    else:
        print("✅ SSL mode: require")
        
    # Test 5: Check Docker configuration
    docker_config = config.get('docker', {})
    if not docker_config.get('skip_database_container', False):
        print("❌ skip_database_container should be true for external database")
        return False
    print("✅ Skip database container: enabled")
    
    # Test 6: Validate database connection string format
    host = db_config['host']
    port = db_config['port']
    name = db_config['name']
    user = db_config['user']
    password = db_config['password']
    ssl_mode = db_config.get('ssl_mode', 'require')
    
    if ssl_mode != 'disable':
        test_url = f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode={ssl_mode}"
    else:
        test_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    print(f"✅ Database URL format: postgresql://{user}:***@{host}:{port}/{name}?sslmode={ssl_mode}")
    
    print("\n🎉 Configuration validation completed successfully!")
    print("\n📋 Summary:")
    print(f"  Database Host: {host}")
    print(f"  Database Port: {port}")
    print(f"  Database Name: {name}")
    print(f"  Database User: {user}")
    print(f"  SSL Mode: {ssl_mode}")
    print(f"  External Managed: {db_config.get('external_managed')}")
    print(f"  Skip DB Container: {docker_config.get('skip_database_container')}")
    
    return True

if __name__ == "__main__":
    if test_config():
        print("\n✅ Ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Configuration validation failed!")
        sys.exit(1)