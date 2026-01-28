#!/usr/bin/env python3
"""
Illuminate Setup Script
Automatically installs dependencies based on the current platform.
Run with: python3 setup.py
"""

import sys
import os
import platform
import subprocess
import shutil

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_command(command, description, check=True, shell=False):
    """Run a shell command with error handling."""
    print(f"\n[→] {description}...")
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"[✗] Error: {e}")
        if e.stderr:
            print(e.stderr.strip())
        return False
    except FileNotFoundError:
        print(f"[✗] Command not found: {command[0] if isinstance(command, list) else command}")
        return False

def check_python_version():
    """Verify Python version is 3.8 or higher."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[✗] Python 3.8 or higher is required!")
        sys.exit(1)
    print("[✓] Python version is compatible")

def install_linux_dependencies():
    """Install system dependencies for Linux/Raspberry Pi."""
    print_header("Installing Linux System Dependencies")
    
    # Check if running as root or can sudo
    if os.geteuid() != 0:
        print("Note: You may be prompted for your password (sudo)")
    
    packages = [
        'espeak',
        'alsa-utils',
        'portaudio19-dev',
        'libespeak1',
        'python3-dev',
    ]
    
    # Update package list
    run_command(['sudo', 'apt-get', 'update', '-qq'], 
                "Updating package list")
    
    # Install packages
    cmd = ['sudo', 'apt-get', 'install', '-y'] + packages
    run_command(cmd, f"Installing {', '.join(packages)}")
    
    print("[✓] Linux system dependencies installed")

def install_macos_dependencies():
    """Install system dependencies for macOS."""
    print_header("Installing macOS System Dependencies")
    
    # Check if Homebrew is installed
    if not shutil.which('brew'):
        print("[!] Homebrew not found. Installing Homebrew...")
        install_brew = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        run_command(install_brew, "Installing Homebrew", shell=True)
    
    # Install portaudio for pyaudio
    run_command(['brew', 'install', 'portaudio'], 
                "Installing portaudio", check=False)
    
    print("[✓] macOS system dependencies ready")

def install_python_packages():
    """Install Python packages from requirements.txt."""
    print_header("Installing Python Packages")
    
    # Upgrade pip first
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                "Upgrading pip")
    
    # Check if requirements.txt exists
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if not os.path.exists(req_file):
        print("[✗] requirements.txt not found!")
        return False
    
    # Install requirements
    success = run_command([sys.executable, '-m', 'pip', 'install', '-r', req_file],
                         "Installing Python packages from requirements.txt")
    
    if success:
        print("[✓] Python packages installed")
    return success

def verify_installation():
    """Verify that key modules can be imported."""
    print_header("Verifying Installation")
    
    modules = {
        'cv2': 'opencv-python',
        'dotenv': 'python-dotenv',
        'openai': 'openai',
        'speech_recognition': 'SpeechRecognition',
        'pyaudio': 'pyaudio',
    }
    
    failed = []
    for module, package in modules.items():
        try:
            __import__(module)
            print(f"[✓] {package}")
        except ImportError:
            print(f"[✗] {package} - failed to import")
            failed.append(package)
    
    # Check platform-specific
    system = platform.system()
    if system == "Linux":
        # Check espeak
        if shutil.which('espeak'):
            print("[✓] espeak")
        else:
            print("[✗] espeak not found")
            failed.append("espeak")
    
    if system in ["Darwin", "Windows"]:
        try:
            import pyttsx3
            print("[✓] pyttsx3")
        except ImportError:
            print("[✗] pyttsx3 - failed to import")
            failed.append("pyttsx3")
    
    if failed:
        print(f"\n[!] Some packages failed to install: {', '.join(failed)}")
        print("    Try installing them manually.")
        return False
    
    print("\n[✓] All required packages are installed!")
    return True

def setup_env_file():
    """Check for .env file and guide user."""
    print_header("Environment Configuration")
    
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    env_example = os.path.join(os.path.dirname(__file__), '.env.example')
    
    if os.path.exists(env_file):
        print("[✓] .env file exists")
    elif os.path.exists(env_example):
        print("[!] .env file not found")
        print(f"    Copy {env_example} to .env and add your API keys:")
        print(f"    cp .env.example .env")
    else:
        print("[!] No .env or .env.example file found")
        print("    Create a .env file with your OpenAI API credentials")

def main():
    """Main setup routine."""
    print_header("Illuminate Setup")
    print(f"Platform: {platform.system()} ({platform.machine()})")
    
    # Check Python version
    check_python_version()
    
    # Install system dependencies based on platform
    system = platform.system()
    
    if system == "Linux":
        install_linux_dependencies()
    elif system == "Darwin":  # macOS
        install_macos_dependencies()
    elif system == "Windows":
        print_header("Windows System Dependencies")
        print("[!] On Windows, most dependencies are handled by pip")
        print("    Make sure you have a working microphone and camera")
    
    # Install Python packages
    if not install_python_packages():
        print("\n[✗] Setup failed!")
        sys.exit(1)
    
    # Verify installation
    verify_installation()
    
    # Check .env configuration
    setup_env_file()
    
    # Final instructions
    print_header("Setup Complete!")
    print("\nNext steps:")
    print("  1. Configure your .env file with API keys")
    print("  2. Test the modules:")
    print("     python3 modules/tts.py")
    print("  3. Run the main program:")
    print("     python3 main.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[✗] Unexpected error: {e}")
        sys.exit(1)
