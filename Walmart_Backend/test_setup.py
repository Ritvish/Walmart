#!/usr/bin/env python3
"""
BuddyCart FastAPI Server Test and Setup Script
Run this script to test your FastAPI server setup
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating default .env file...")
        create_default_env()
        print("📝 Please update .env file with your database credentials")
        return False
    
    print("✅ .env file found")
    return True

def create_default_env():
    """Create a default .env file"""
    default_env = """DATABASE_URL=mysql+mysqlconnector://ritvish:bitblt.23@localhost:3306/buddycart
SECRET_KEY=your-secret-key-here-change-in-production-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CLUB_WAIT_TIME_MINUTES=5
MAX_DELIVERY_WEIGHT_KG=5.0
LOCATION_CLUSTER_RADIUS_KM=2.0"""
    
    with open(".env", "w") as f:
        f.write(default_env)

def test_server():
    """Test if the server starts and responds"""
    print("🚀 Testing server startup...")
    
    # Start server in background
    try:
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and responding")
                print("🌐 API Documentation: http://localhost:8000/docs")
                print("📊 Health Check: http://localhost:8000/health")
                
                # Terminate the test server
                process.terminate()
                process.wait()
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Server not responding: {e}")
        
        # Cleanup
        process.terminate()
        process.wait()
        return False
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def run_sample_data_setup():
    """Run the sample data setup script"""
    print("🛍️  Setting up sample data...")
    try:
        subprocess.check_call([sys.executable, "setup_sample_data.py"])
        print("✅ Sample data setup completed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Sample data setup failed")
        return False

def main():
    """Main test function"""
    print("🧪 BuddyCart FastAPI Server Test Suite")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check environment file
    env_exists = check_env_file()
    
    # Test server startup
    if env_exists and test_server():
        print("\n🎉 All tests passed!")
        print("\nNext steps:")
        print("1. Update your .env file with actual database credentials")
        print("2. Start server: python main.py")
        print("3. Visit API docs: http://localhost:8000/docs")
        print("4. Load sample data: python setup_sample_data.py")
        print("5. Test API: python api_tester.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        if not env_exists:
            print("💡 Make sure to update your .env file with proper database credentials")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
