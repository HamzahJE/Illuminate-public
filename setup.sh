#!/bin/bash
# Illuminate Setup Script
# Automatically installs dependencies for Linux/macOS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "========================================="
    echo "  $1"
    echo "========================================="
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[→]${NC} $1"
}

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_header "Illuminate Setup - $MACHINE"

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found! Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION detected"

# Check if version is 3.8+
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    print_success "Python version is compatible"
else
    print_error "Python 3.8 or higher is required"
    exit 1
fi

# Install system dependencies based on OS
if [ "$MACHINE" = "Linux" ]; then
    print_header "Installing Linux System Dependencies"
    
    # Check if apt-get is available (Debian/Ubuntu/Raspberry Pi)
    if command -v apt-get &> /dev/null; then
        print_info "Updating package list..."
        sudo apt-get update -qq
        
        print_info "Installing system packages..."
        sudo apt-get install -y \
            espeak \
            alsa-utils \
            portaudio19-dev \
            libespeak1 \
            python3-dev \
            python3-pip
        
        print_success "System dependencies installed"
    else
        print_error "apt-get not found. Please install dependencies manually:"
        echo "  - espeak"
        echo "  - alsa-utils"
        echo "  - portaudio19-dev"
        echo "  - libespeak1"
    fi

elif [ "$MACHINE" = "Mac" ]; then
    print_header "Installing macOS System Dependencies"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_info "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    print_info "Installing portaudio..."
    brew install portaudio 2>/dev/null || print_info "portaudio may already be installed"
    
    print_success "macOS dependencies ready"
fi

# Upgrade pip
print_header "Setting up Python Environment"
print_info "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    exit 1
fi

# Install Python packages
print_info "Installing Python packages..."
if python3 -m pip install -r requirements.txt --quiet; then
    print_success "Python packages installed"
else
    print_error "Failed to install some Python packages"
    echo "Try running: python3 -m pip install -r requirements.txt"
    exit 1
fi

# Verify key modules
print_header "Verifying Installation"

check_module() {
    if python3 -c "import $1" 2>/dev/null; then
        print_success "$2"
        return 0
    else
        print_error "$2 - failed to import"
        return 1
    fi
}

FAILED=0
check_module "cv2" "opencv-python" || FAILED=1
check_module "dotenv" "python-dotenv" || FAILED=1
check_module "openai" "openai" || FAILED=1
check_module "speech_recognition" "SpeechRecognition" || FAILED=1
check_module "pyaudio" "pyaudio" || FAILED=1

if [ "$MACHINE" = "Linux" ]; then
    if command -v espeak &> /dev/null; then
        print_success "espeak"
    else
        print_error "espeak not found"
        FAILED=1
    fi
fi

if [ "$MACHINE" = "Mac" ]; then
    check_module "pyttsx3" "pyttsx3" || FAILED=1
fi

# Check .env file
print_header "Environment Configuration"
if [ -f ".env" ]; then
    print_success ".env file exists"
elif [ -f ".env.example" ]; then
    print_info ".env file not found"
    echo "  Create it by copying: cp .env.example .env"
    echo "  Then add your OpenAI API credentials"
else
    print_info "No .env or .env.example file found"
    echo "  Create a .env file with your OpenAI API credentials"
fi

# Summary
print_header "Setup Complete!"
if [ $FAILED -eq 0 ]; then
    print_success "All dependencies installed successfully!"
else
    print_error "Some dependencies failed to install"
    echo "  Try installing them manually or check the error messages above"
fi

echo ""
echo "Next steps:"
echo "  1. Configure your .env file with API keys"
echo "  2. Test TTS: python3 modules/tts.py"
echo "  3. Run the program: python3 main.py"
echo ""
echo "========================================="
