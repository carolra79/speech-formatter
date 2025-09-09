#!/usr/bin/env python3
"""Setup script for Speech Formatter"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run shell command and return success status"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Setting up Speech Formatter...")
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv"):
            print("❌ Failed to create virtual environment")
            return
    
    # Activate venv and install requirements
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    print("Installing requirements...")
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        print("❌ Failed to install requirements")
        return
    
    print("Testing AWS connections...")
    if not run_command(f"{python_cmd} test_aws.py"):
        print("⚠️  AWS connection test failed - please check your configuration")
    
    print("\n✅ Setup complete!")
    print("\nTo run the app:")
    print(f"  {python_cmd} -m streamlit run app.py")
    print("\nDefault login: admin / password")

if __name__ == "__main__":
    main()
