#!/bin/bash
#
# MCP Server Installer Script
# Created by: Digital COE Gen AI Team (Amdocs)
#
# Supported Platforms:
#   - macOS (native)
#   - Linux (native)
#   - Windows (via Git Bash, WSL, or Cygwin)
#
# This script:
# 1. Checks if Python 3.10+ is installed on the system
# 2. Detects and relocates from restricted directories (Downloads, Desktop, etc.)
# 3. Creates a virtual environment to avoid PEP 668 restrictions
# 4. Sets up proxy for package downloads
# 5. Executes mcp_installer.py in the virtual environment
# 6. Configures Cursor with correct absolute paths
#
# Windows Users:
#   Run this script using Git Bash or WSL:
#   $ ./installer.sh
#

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Minimum required Python version for MCP package
MIN_PYTHON_VERSION="3.10"

# Proxy configuration (can be overridden via environment variable)
# Set PROXY_URL environment variable before running to override default
DEFAULT_PROXY="http://genproxy:8080"
PROXY_URL="${PROXY_URL:-$DEFAULT_PROXY}"

# Set to "true" to skip proxy setup (for environments without proxy)
SKIP_PROXY="${SKIP_PROXY:-false}"

# Virtual environment directory name
VENV_DIR=".venv"

# Safe installation directory (where MCP servers will be copied to)
SAFE_INSTALL_DIR="${MCP_INSTALL_DIR:-$HOME/.mcp-servers}"

# Global variable to store venv Python path (absolute)
VENV_PYTHON=""

# Global variable to track if we relocated
RELOCATED="false"
ORIGINAL_DIR=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    local python_cmd="$1"
    if command_exists "$python_cmd"; then
        # Use sed for better portability than grep -oE
        version=$("$python_cmd" --version 2>&1 | sed -n 's/.*Python \([0-9]*\.[0-9]*\).*/\1/p' | head -1)
        echo "$version"
    else
        echo ""
    fi
}

# Function to get absolute path of Python command
get_python_absolute_path() {
    local python_cmd="$1"
    if command_exists "$python_cmd"; then
        # For Windows 'py' launcher, get the actual Python path it uses
        if [[ "$python_cmd" == "py" ]]; then
            # py -c prints the actual Python executable path
            "$python_cmd" -c "import sys; print(sys.executable)" 2>/dev/null || echo "$python_cmd"
        else
            # Get the absolute path using command -v
            local cmd_path
            cmd_path=$(command -v "$python_cmd")
            # If it's a relative path, get absolute
            if [[ "$cmd_path" != /* ]]; then
                cmd_path=$(which "$python_cmd" 2>/dev/null || echo "$python_cmd")
            fi
            echo "$cmd_path"
        fi
    else
        echo ""
    fi
}

# Function to compare version numbers (portable, works on macOS and Linux)
# Returns 0 (true) if $1 >= $2, 1 (false) otherwise
version_ge() {
    local ver1="$1"
    local ver2="$2"
    
    # Extract major and minor versions
    local major1="${ver1%%.*}"
    local minor1="${ver1#*.}"
    minor1="${minor1%%.*}"
    
    local major2="${ver2%%.*}"
    local minor2="${ver2#*.}"
    minor2="${minor2%%.*}"
    
    # Compare major versions
    if [ "$major1" -gt "$major2" ]; then
        return 0
    elif [ "$major1" -lt "$major2" ]; then
        return 1
    fi
    
    # Major versions equal, compare minor versions
    if [ "$minor1" -ge "$minor2" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if current directory is in a restricted location
is_restricted_directory() {
    local current_dir="$1"
    
    # List of restricted directories (macOS and Windows sandboxed locations)
    local restricted_patterns=(
        "$HOME/Downloads"
        "$HOME/Desktop"
        "/tmp"
        "/var/folders"
        "$HOME/Library/Mobile Documents"  # iCloud (macOS)
    )
    
    # Add Windows-specific paths if running in Git Bash/WSL/Cygwin
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        # Get Windows username for path patterns
        local win_user="${USERNAME:-${USER:-}}"
        
        # Git Bash uses /c/Users/... format
        if [ -n "$win_user" ]; then
            restricted_patterns+=(
                "/c/Users/$win_user/Downloads"
                "/c/Users/$win_user/Desktop"
                "/d/Users/$win_user/Downloads"
                "/d/Users/$win_user/Desktop"
            )
        fi
        
        # Also check USERPROFILE if set (native Windows path converted)
        if [ -n "${USERPROFILE:-}" ]; then
            # Convert Windows path to Git Bash format: C:\Users\x -> /c/Users/x
            local userprofile_unix
            userprofile_unix=$(echo "$USERPROFILE" | sed 's|\\|/|g' | sed 's|^\([A-Za-z]\):|/\L\1|')
            restricted_patterns+=(
                "$userprofile_unix/Downloads"
                "$userprofile_unix/Desktop"
            )
        fi
    fi
    
    for pattern in "${restricted_patterns[@]}"; do
        if [[ "$current_dir" == "$pattern"* ]]; then
            return 0  # true - is restricted
        fi
    done
    
    return 1  # false - not restricted
}

# Function to copy package to safe location
relocate_to_safe_directory() {
    local source_dir="$1"
    local package_name
    package_name=$(basename "$source_dir")
    local target_dir="$SAFE_INSTALL_DIR/$package_name"
    
    log_warning "Current directory is in a restricted location!"
    log_warning "The OS may prevent executing scripts from: $source_dir"
    log ""
    log "Relocating to safe directory: $target_dir"
    
    # Create safe install directory if it doesn't exist
    if ! mkdir -p "$SAFE_INSTALL_DIR"; then
        log_error "Failed to create directory: $SAFE_INSTALL_DIR"
        return 1
    fi
    
    # Remove existing installation if present
    if [ -d "$target_dir" ]; then
        log_warning "Existing installation found at: $target_dir"
        log "Removing previous installation..."
        rm -rf "$target_dir"
    fi
    
    # Copy all files to safe location
    log "Copying files to: $target_dir"
    if ! cp -R "$source_dir" "$target_dir"; then
        log_error "Failed to copy files to: $target_dir"
        return 1
    fi
    
    # Change to new directory
    if ! cd "$target_dir"; then
        log_error "Failed to change to directory: $target_dir"
        return 1
    fi
    
    log_success "Successfully relocated to: $(pwd)"
    RELOCATED="true"
    
    return 0
}

# Function to find mcp_installer.py
find_mcp_installer() {
    local script_path=""
    
    # Check current directory first
    if [ -f "./mcp_installer.py" ]; then
        script_path="./mcp_installer.py"
    # Check src/main/resources/scripts/
    elif [ -f "./src/main/resources/scripts/mcp_installer.py" ]; then
        script_path="./src/main/resources/scripts/mcp_installer.py"
    # Check scripts directory
    elif [ -f "./scripts/mcp_installer.py" ]; then
        script_path="./scripts/mcp_installer.py"
    # Search recursively with depth limit for security
    else
        script_path=$(find . -maxdepth 5 -name "mcp_installer.py" -type f 2>/dev/null | head -1)
    fi
    
    echo "$script_path"
}

# Function to set up proxy environment variables
setup_proxy() {
    if [ "$SKIP_PROXY" = "true" ]; then
        log_warning "Skipping proxy setup (SKIP_PROXY=true)"
        return 0
    fi
    
    log "Setting up proxy: $PROXY_URL"
    
    export http_proxy="$PROXY_URL"
    export https_proxy="$PROXY_URL"
    export HTTP_PROXY="$PROXY_URL"
    export HTTPS_PROXY="$PROXY_URL"
    export ftp_proxy="$PROXY_URL"
    export FTP_PROXY="$PROXY_URL"
    
    # Set no_proxy for localhost
    export no_proxy="localhost,127.0.0.1,::1"
    export NO_PROXY="localhost,127.0.0.1,::1"
    
    log_success "Proxy environment variables configured"
}

# Function to remove proxy environment variables
remove_proxy() {
    log "Removing proxy environment variables..."
    
    unset http_proxy 2>/dev/null || true
    unset https_proxy 2>/dev/null || true
    unset HTTP_PROXY 2>/dev/null || true
    unset HTTPS_PROXY 2>/dev/null || true
    unset ftp_proxy 2>/dev/null || true
    unset FTP_PROXY 2>/dev/null || true
    unset no_proxy 2>/dev/null || true
    unset NO_PROXY 2>/dev/null || true
    
    log_success "Proxy environment variables removed"
}

# Function to create and setup virtual environment
setup_venv() {
    local python_cmd="$1"
    local venv_path
    venv_path="$(pwd)/$VENV_DIR"  # Use absolute path
    
    log_info "=============================================="
    log_info "  Creating Virtual Environment"
    log_info "=============================================="
    log "System Python: $python_cmd"
    log "Venv location: $venv_path"
    
    # Check if venv already exists and is valid
    if [ -d "$venv_path" ]; then
        local existing_python=""
        if [ -f "$venv_path/bin/python" ]; then
            existing_python="$venv_path/bin/python"
        elif [ -f "$venv_path/Scripts/python.exe" ]; then
            existing_python="$venv_path/Scripts/python.exe"
        fi
        
        # Check if existing venv is functional
        if [ -n "$existing_python" ] && "$existing_python" --version >/dev/null 2>&1; then
            log_success "Found existing valid virtual environment"
            VENV_PYTHON="$existing_python"
            log "Virtual environment Python: $VENV_PYTHON"
            log_info "=============================================="
            return 0
        else
            log_warning "Existing virtual environment is broken, recreating..."
            rm -rf "$venv_path"
        fi
    fi
    
    log "Creating new virtual environment..."
    
    # Create virtual environment with --clear flag to ensure clean state
    if ! "$python_cmd" -m venv "$venv_path" --clear 2>&1; then
        log_error "Failed to create virtual environment!"
        log_error "Command: $python_cmd -m venv $venv_path --clear"
        log_error ""
        log_error "Possible fixes:"
        log_error "  1. Install venv module: sudo apt install python3-venv (Linux)"
        log_error "  2. Reinstall Python with venv support"
        log_error "  3. Try: $python_cmd -m ensurepip --upgrade"
        return 1
    fi
    
    # Determine the path to Python in the venv (use absolute path)
    if [ -f "$venv_path/bin/python" ]; then
        # Unix-like systems (macOS, Linux)
        VENV_PYTHON="$venv_path/bin/python"
    elif [ -f "$venv_path/Scripts/python.exe" ]; then
        # Windows
        VENV_PYTHON="$venv_path/Scripts/python.exe"
    else
        log_error "Could not find Python executable in virtual environment!"
        log_error "Expected at: $venv_path/bin/python or $venv_path/Scripts/python.exe"
        log_error "Venv contents:"
        ls -la "$venv_path/" 2>/dev/null || echo "  (directory not accessible)"
        return 1
    fi
    
    # Verify venv Python actually works
    if ! "$VENV_PYTHON" --version >/dev/null 2>&1; then
        log_error "Virtual environment Python is not functional!"
        log_error "Path: $VENV_PYTHON"
        return 1
    fi
    
    local venv_version
    venv_version=$("$VENV_PYTHON" --version 2>&1)
    log_success "Virtual environment created successfully"
    log "Venv Python: $VENV_PYTHON"
    log "Venv Python version: $venv_version"
    
    # Upgrade pip in the venv
    log "Upgrading pip in virtual environment..."
    if "$VENV_PYTHON" -m pip install --upgrade pip --quiet 2>/dev/null; then
        log_success "pip upgraded successfully"
    else
        log_warning "Could not upgrade pip (continuing anyway)"
    fi
    
    log_info "=============================================="
    
    return 0
}

# Function to cleanup on exit
cleanup() {
    local exit_code=$?
    log "Performing cleanup..."
    
    # Remove proxy settings
    remove_proxy
    
    if [ $exit_code -eq 0 ]; then
        log_success "Installation completed successfully!"
        echo ""
        log_info "=============================================="
        log_info "  MCP Server is ready to use!"
        log_info "=============================================="
        if [ "$RELOCATED" = "true" ]; then
            log_info "  Installation location: $(pwd)"
            log_info "  (Moved from restricted Downloads folder)"
        fi
        log_info "  Virtual environment: $(pwd)/$VENV_DIR"
        log_info ""
        log_info "  Please restart Cursor to activate the MCP server."
        log_info ""
        log_info "  Cursor config location:"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
            log_info "    Windows: %USERPROFILE%\\.cursor\\mcp.json"
            log_info "         or: %APPDATA%\\Cursor\\mcp.json"
        else
            log_info "    ~/.cursor/mcp.json"
        fi
        log_info "=============================================="
    else
        log_error "Installation failed with exit code: $exit_code"
    fi
    
    exit $exit_code
}

# Set trap for cleanup
trap cleanup EXIT

# Main installation function
main() {
    log "=== MCP Server Installer Started ==="
    log "Created by: Digital"
    echo ""
    
    # Detect and log OS type for debugging
    log "Operating System: $OSTYPE"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        log_info "Detected Windows environment (Git Bash/Cygwin)"
        log "  HOME=$HOME"
        log "  USERPROFILE=${USERPROFILE:-<not set>}"
        log "  USERNAME=${USERNAME:-${USER:-<not set>}}"
    fi
    echo ""
    
    # Store original directory
    ORIGINAL_DIR="$(pwd)"
    
    # Step 1: Check if Python is installed
    log "Step 1: Checking Python installation (requires Python ${MIN_PYTHON_VERSION}+)..."
    
    local python_cmd=""
    local python_version=""
    local python_absolute_path=""
    local found_version=""
    
    # List of Python commands to check (in order of preference - newest first)
    # Includes 'py' for Windows Python Launcher
    local python_commands="python3.13 python3.12 python3.11 python3.10 python3 python py"
    
    for cmd in $python_commands; do
        if command_exists "$cmd"; then
            found_version=$(get_python_version "$cmd")
            if [ -n "$found_version" ]; then
                log "Found $cmd version: $found_version"
                if version_ge "$found_version" "$MIN_PYTHON_VERSION"; then
                    python_cmd="$cmd"
                    python_version="$found_version"
                    python_absolute_path=$(get_python_absolute_path "$cmd")
                    log_success "$cmd version $found_version meets requirement (>= ${MIN_PYTHON_VERSION})"
                    log "Python path: $python_absolute_path"
                    break
                else
                    log_warning "$cmd version $found_version is below required ${MIN_PYTHON_VERSION}"
                fi
            fi
        fi
    done
    
    # Final check
    if [ -z "$python_cmd" ]; then
        log_error "No suitable Python installation found!"
        log_error "The MCP package requires Python ${MIN_PYTHON_VERSION} or higher."
        log_error ""
        log_error "Please install Python ${MIN_PYTHON_VERSION}+ and try again."
        log_error "  - macOS:   brew install python@3.11"
        log_error "  - Ubuntu:  sudo apt install python3.11"
        log_error "  - Windows: Download from https://www.python.org/downloads/"
        log_error "             (Check 'Add Python to PATH' during installation)"
        exit 1
    fi
    
    # Step 2: Check if in restricted directory and relocate if needed
    log "Step 2: Checking directory permissions..."
    
    local current_dir
    current_dir="$(pwd)"
    
    if is_restricted_directory "$current_dir"; then
        log_warning "Detected restricted directory: $current_dir"
        
        if ! relocate_to_safe_directory "$current_dir"; then
            log_error "Failed to relocate to safe directory!"
            log_error "Please manually move the package to a non-Downloads location and try again."
            exit 1
        fi
    else
        log_success "Directory is accessible: $current_dir"
    fi
    
    # Step 3: Find mcp_installer.py
    log "Step 3: Locating mcp_installer.py..."
    
    local mcp_installer_path=""
    mcp_installer_path=$(find_mcp_installer)
    
    if [ -z "$mcp_installer_path" ]; then
        log_error "mcp_installer.py not found!"
        log_error "Please ensure mcp_installer.py is in the current directory or subdirectories."
        exit 1
    fi
    
    # Convert to absolute path
    mcp_installer_path="$(cd "$(dirname "$mcp_installer_path")" && pwd)/$(basename "$mcp_installer_path")"
    log_success "Found mcp_installer.py at: $mcp_installer_path"
    
    # Step 4: Set up proxy (before venv creation for pip upgrade)
    log "Step 4: Configuring proxy for package downloads..."
    setup_proxy
    
    # Step 5: Create virtual environment
    log "Step 5: Creating virtual environment (avoids PEP 668 restrictions)..."
    
    if ! setup_venv "$python_cmd"; then
        log_error "Failed to setup virtual environment!"
        exit 1
    fi
    
    log_success "Using virtual environment Python: $VENV_PYTHON"
    
    # Step 6: Export environment variables for mcp_installer.py
    log "Step 6: Setting up environment for mcp_installer.py..."
    
    # Export the venv Python path for mcp_installer.py to use
    export MCP_VENV_PYTHON="$VENV_PYTHON"
    export MCP_INSTALL_DIR="$(pwd)"
    export MCP_PYTHON_VERSION="$python_version"
    
    log_success "Environment variables exported:"
    log "  MCP_VENV_PYTHON=$MCP_VENV_PYTHON"
    log "  MCP_INSTALL_DIR=$MCP_INSTALL_DIR"
    
    # Step 7: Execute mcp_installer.py using venv Python
    log "Step 7: Executing mcp_installer.py in virtual environment..."
    echo ""
    
    if ! "$VENV_PYTHON" "$mcp_installer_path"; then
        log_error "mcp_installer.py execution failed!"
        exit 1
    fi
    
    echo ""
    log_success "mcp_installer.py completed successfully!"
    
    # Step 8: Done
    log "Step 8: Finalizing..."
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi