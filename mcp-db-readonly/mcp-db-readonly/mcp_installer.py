#!/usr/bin/env python3
"""
MCP Server Installation and Configuration Script

This script automates the MCP server installation and configuration process:
1. Gets current working directory
2. Searches for requirements.txt file  
3. Sets proxy (http://localhost:8080) and installs dependencies
4. Searches for and reads mcp-d.json file
5. Finds .py and .jar files and gets their absolute paths
6. Updates mcp-d.json command and args with absolute paths
7. Uses virtual environment Python path for command (from MCP_VENV_PYTHON env var)
8. Detects operating system
9. On macOS: Updates ~/.cursor/mcp.json with new MCP server configurations
10. Provides success response

Usage:
    python3 mcp_installer.py
    
    Or via installer.sh (recommended):
    ./installer.sh

Environment Variables (set by installer.sh):
    MCP_VENV_PYTHON  - Absolute path to virtual environment Python executable
    MCP_INSTALL_DIR  - Directory where MCP server is installed

Requirements:
    - Python 3.10+ (for MCP package compatibility)
    - mcp-d.json file in current directory or subdirectories
    - For macOS: ~/.cursor/mcp.json file (will be created if not exists)

Expected mcp-d.json format:
{
  "server-name-1.0.0": {
    "command": "python3",
    "args": ["/path/to/script.py"],
    "env": {
      "ENV_VAR": "value"
    }
  }
}

After installation, the command will be updated to use the venv Python:
{
  "server-name-1.0.0": {
    "command": "/absolute/path/to/.venv/bin/python",
    "args": ["/absolute/path/to/script.py"],
    "env": {
      "ENV_VAR": "value"
    }
  }
}
"""

import copy
import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import traceback
import venv
from datetime import datetime
from typing import Dict, List, Optional


class McpInstaller:
    """Main class for MCP server installation and configuration."""
    
    # Default venv directory name
    VENV_DIR_NAME = ".venv"
    
    def __init__(self):
        self.current_dir = os.getcwd()
        self.os_type = self._detect_os_type()
        # Configurable proxy URL via environment variable
        self.proxy_url = os.environ.get('MCP_PROXY_URL', "http://localhost:8080")
        self._windows_secondary_path = None  # For writing to multiple locations on Windows
        
        # Get venv Python path from installer.sh environment variable
        self.install_dir = os.environ.get('MCP_INSTALL_DIR', self.current_dir)
        
        # Flag to track if we're using venv from installer
        self.using_venv_from_installer = bool(os.environ.get('MCP_VENV_PYTHON'))
        
        # Setup virtual environment - create if needed
        self.venv_python = self._setup_virtual_environment()
    
    def _get_venv_python_path(self, venv_dir: str) -> str:
        """Get the Python executable path inside a venv directory."""
        if self.os_type == "windows":
            return os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            return os.path.join(venv_dir, "bin", "python")
    
    def _setup_virtual_environment(self) -> str:
        """Setup virtual environment - use existing or create new one."""
        # Priority 1: Use venv from environment variable (set by installer.sh)
        env_venv = os.environ.get('MCP_VENV_PYTHON')
        if env_venv and os.path.isfile(env_venv):
            print(f"[INFO] Using venv Python from environment: {env_venv}")
            return env_venv
        
        # Priority 2: Check if .venv already exists in current directory
        venv_dir = os.path.join(self.current_dir, self.VENV_DIR_NAME)
        venv_python = self._get_venv_python_path(venv_dir)
        
        if os.path.isfile(venv_python):
            print(f"[INFO] Found existing virtual environment: {venv_dir}")
            return venv_python
        
        # Priority 3: Create a new virtual environment
        print(f"[INFO] No virtual environment found. Creating one at: {venv_dir}")
        try:
            # Create venv with pip included
            venv.create(venv_dir, with_pip=True, clear=False)
            
            if os.path.isfile(venv_python):
                print(f"[SUCCESS] Created virtual environment at: {venv_dir}")
                
                # Upgrade pip in the new venv
                self._upgrade_pip(venv_python)
                
                return venv_python
            else:
                print(f"[ERROR] Failed to create virtual environment", file=sys.stderr)
                sys.exit(1)
                
        except Exception as e:
            print(f"[ERROR] Failed to create virtual environment: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _upgrade_pip(self, python_path: str) -> None:
        """Upgrade pip in the virtual environment."""
        try:
            subprocess.run(
                [python_path, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                timeout=120
            )
        except Exception:
            pass  # Ignore pip upgrade failures
    
    def _detect_os_type(self) -> str:
        """Detect OS type, handling Git Bash/MSYS/Cygwin on Windows."""
        raw_os = platform.system()
        os_name = raw_os.lower()
        
        # Handle Git Bash / MSYS / Cygwin on Windows
        if 'msys' in os_name or 'cygwin' in os_name or 'mingw' in os_name:
            return 'windows'
        return os_name
    
    def _is_venv(self, python_path: str) -> bool:
        """Check if the given Python path is inside a virtual environment."""
        # Check for common venv directory indicators
        venv_indicators = ['.venv', 'venv', 'env', '.env', 'virtualenv']
        path_parts = python_path.lower().replace('\\', '/').split('/')
        return any(indicator in path_parts for indicator in venv_indicators)
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log messages with timestamp and level."""
        print(f"[{level}] {message}")
        
    def get_current_directory(self) -> str:
        """Get and return current working directory."""
        self.log(f"Current working directory: {self.current_dir}")
        return self.current_dir
        
    def find_requirements_txt(self) -> Optional[str]:
        """Search for requirements.txt file in current directory."""
        requirements_path = os.path.join(self.current_dir, "requirements.txt")
        
        if os.path.exists(requirements_path):
            self.log(f"Found requirements.txt at: {requirements_path}")
            return requirements_path
        else:
            # Search recursively in subdirectories
            for root, dirs, files in os.walk(self.current_dir):
                if "requirements.txt" in files:
                    found_path = os.path.join(root, "requirements.txt")
                    self.log(f"Found requirements.txt at: {found_path}")
                    return found_path
                    
        self.log("requirements.txt not found", "WARNING")
        return None
        
    def set_proxy_and_install_requirements(self, requirements_path: str) -> bool:
        """Set proxy environment and install requirements."""
        try:
            # Set proxy environment variables
            env = os.environ.copy()
            env['https_proxy'] = self.proxy_url
            env['http_proxy'] = self.proxy_url
            env['HTTPS_PROXY'] = self.proxy_url
            env['HTTP_PROXY'] = self.proxy_url
            
            self.log(f"Setting proxy: {self.proxy_url}")
            
            # Run pip install command with additional options for proxy/SSL issues
            # Dependencies are ONLY installed in the virtual environment (never system Python)
            cmd = [
                self.venv_python, "-m", "pip", "install", 
                "-r", requirements_path,
                "--trusted-host", "pypi.org",
                "--trusted-host", "pypi.python.org", 
                "--trusted-host", "files.pythonhosted.org",
                "--proxy", self.proxy_url,
            ]
            self.log(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.log("Requirements installed successfully")
                return True
            else:
                self.log(f"Error installing requirements: {result.stderr}", "ERROR")
                # Try without proxy if first attempt fails
                self.log("Retrying installation without proxy...")
                cmd_no_proxy = [self.venv_python, "-m", "pip", "install", "-r", requirements_path]
                # Use clean environment without proxy settings
                clean_env = {k: v for k, v in os.environ.items() 
                            if k.lower() not in ['http_proxy', 'https_proxy', 'no_proxy']}
                result_no_proxy = subprocess.run(
                    cmd_no_proxy,
                    env=clean_env,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result_no_proxy.returncode == 0:
                    self.log("Requirements installed successfully (without proxy)")
                    return True
                else:
                    self.log(f"Error installing requirements (no proxy): {result_no_proxy.stderr}", "ERROR")
                    return False
                
        except subprocess.TimeoutExpired:
            self.log("Installation timeout after 5 minutes", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error during installation: {str(e)}", "ERROR")
            return False
            
    def find_mcp_d_json(self) -> Optional[str]:
        """Search for mcp-d.json file."""
        # First check current directory
        mcp_json_path = os.path.join(self.current_dir, "mcp-d.json")
        if os.path.exists(mcp_json_path):
            self.log(f"Found mcp-d.json at: {mcp_json_path}")
            return mcp_json_path
            
        # Search recursively
        for root, dirs, files in os.walk(self.current_dir):
            if "mcp-d.json" in files:
                found_path = os.path.join(root, "mcp-d.json")
                self.log(f"Found mcp-d.json at: {found_path}")
                return found_path
                
        self.log("mcp-d.json not found", "ERROR")
        return None
        
    def read_mcp_json(self, mcp_json_path: str) -> Optional[Dict]:
        """Read and parse mcp-d.json file."""
        try:
            with open(mcp_json_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.log(f"Read mcp-d.json content: {len(content)} characters")
                
                # Handle empty file
                if not content or not content.strip():
                    self.log("mcp-d.json file is empty", "ERROR")
                    return None
                    
                return json.loads(content)
        except json.JSONDecodeError as e:
            self.log(f"Error parsing JSON: {str(e)}", "ERROR")
            return None
        except Exception as e:
            self.log(f"Error reading file: {str(e)}", "ERROR")
            return None
            
    def find_python_and_jar_files(self) -> List[str]:
        """Search for .py and .jar files and return their absolute paths, excluding mcp_installer.py."""
        found_files = []
        excluded_files = []
        
        # Get the absolute path of this script to exclude it
        current_script_path = os.path.abspath(__file__)
        
        # Search for Python files
        python_patterns = ["**/*.py"]
        for pattern in python_patterns:
            for file_path in glob.glob(os.path.join(self.current_dir, pattern), recursive=True):
                if os.path.isfile(file_path):
                    abs_path = os.path.abspath(file_path)
                    
                    # Exclude files inside virtual environment and cache directories
                    path_lower = abs_path.lower().replace('\\', '/')
                    if any(exclude_dir in path_lower for exclude_dir in ['/.venv/', '/venv/', '/.env/', '/env/', '/virtualenv/', '/site-packages/', '/__pycache__/', '/node_modules/']):
                        continue
                    
                    # Exclude mcp_installer.py and any installer scripts
                    filename = os.path.basename(abs_path)
                    if (abs_path == current_script_path or 
                        filename == 'mcp_installer.py' or
                        filename.startswith('install') or
                        filename.endswith('_installer.py')):
                        excluded_files.append(abs_path)
                        continue
                        
                    found_files.append(abs_path)
                    
        # Search for JAR files
        jar_patterns = ["**/*.jar"]
        for pattern in jar_patterns:
            for file_path in glob.glob(os.path.join(self.current_dir, pattern), recursive=True):
                if os.path.isfile(file_path):
                    abs_path = os.path.abspath(file_path)
                    found_files.append(abs_path)
                    
        self.log(f"Found {len(found_files)} .py and .jar files (excluded {len(excluded_files)} installer files)")
        
        # Log excluded files for transparency
        if excluded_files:
            self.log("Excluded installer files:")
            for file_path in excluded_files[:3]:  # Log first 3 excluded files
                self.log(f"  - EXCLUDED: {file_path}")
            if len(excluded_files) > 3:
                self.log(f"  ... and {len(excluded_files) - 3} more excluded files")
        
        # Log found files
        for file_path in found_files[:5]:  # Log first 5 files
            self.log(f"  - {file_path}")
        if len(found_files) > 5:
            self.log(f"  ... and {len(found_files) - 5} more files")
            
        return found_files
        
    def _normalize_path(self, path: str) -> str:
        """Normalize path to use consistent separators for the current OS."""
        if not path:
            return path
        # On Windows, convert forward slashes to backslashes for consistency
        # This ensures paths work correctly when Cursor reads the config
        if self.os_type == "windows":
            # First normalize the path (handles mixed separators)
            normalized = os.path.normpath(path)
            return normalized
        return path
    
    def update_mcp_json_args(self, mcp_data: Dict, executable_files: List[str]) -> Dict:
        """Update args and command in mcp-d.json with absolute paths."""
        updated_data = {}
        
        for server_name, server_config in mcp_data.items():
            if not isinstance(server_config, dict):
                updated_data[server_name] = server_config
                continue
                
            # Create a deep copy of the server config to avoid modifying original
            updated_config = copy.deepcopy(server_config)
            
            # Determine if this is a Python or Java server
            original_command = updated_config.get("command", "")
            is_python_server = "python" in original_command.lower()
            is_java_server = "java" in original_command.lower()
            
            # Find the most relevant executable file
            python_files = [f for f in executable_files if f.endswith('.py')]
            jar_files = [f for f in executable_files if f.endswith('.jar')]
            
            if is_python_server and python_files:
                # Use venv Python as the command (absolute path, normalized)
                normalized_venv = self._normalize_path(self.venv_python)
                updated_config["command"] = normalized_venv
                self.log(f"Updated {server_name} command to venv Python: {normalized_venv}")
                
                # Smart selection of Python file based on server name
                selected_file = self._select_best_python_file(server_name, python_files)
                normalized_file = self._normalize_path(selected_file)
                updated_config["args"] = [normalized_file]
                self.log(f"Updated {server_name} args to: {normalized_file}")
                
            elif is_java_server and jar_files:
                # For JAR files, keep java command but update jar path
                selected_file = self._select_best_jar_file(jar_files)
                normalized_file = self._normalize_path(selected_file)
                # Update args to include the jar file with absolute path
                current_args = updated_config.get("args", [])
                # Replace any .jar references with absolute path
                new_args = []
                for arg in current_args:
                    if arg.endswith('.jar') or '${' in arg:
                        new_args.append(normalized_file)
                    else:
                        new_args.append(self._normalize_path(arg))
                if not any(arg.endswith('.jar') for arg in new_args):
                    new_args.append(normalized_file)
                updated_config["args"] = new_args
                self.log(f"Updated {server_name} args to: {new_args}")
                
            elif python_files:
                # Default to Python if we have Python files
                normalized_venv = self._normalize_path(self.venv_python)
                updated_config["command"] = normalized_venv
                selected_file = self._select_best_python_file(server_name, python_files)
                normalized_file = self._normalize_path(selected_file)
                updated_config["args"] = [normalized_file]
                self.log(f"Updated {server_name} to use venv Python with: {normalized_file}")
            
            updated_data[server_name] = updated_config
                        
        return updated_data
        
    def _select_best_python_file(self, server_name: str, python_files: List[str]) -> str:
        """Select the most appropriate Python file based on server name and patterns."""
        # Extract server type from server name (e.g., "confluence-1.0.0" -> "confluence")
        server_type = server_name.split('-')[0].lower() if '-' in server_name else server_name.lower()
        
        # Priority patterns for Python file selection
        priority_patterns = [
            f"*{server_type}*server*.py",      # e.g., confluence_server.py, fastmcp_confluence_server.py
            f"*{server_type}*.py",             # e.g., confluence.py
            "*server*.py",                     # Any server file
            "*mcp*.py",                        # Any MCP-related file
            "*.py"                             # Any Python file
        ]
        
        for pattern in priority_patterns:
            matching_files = [f for f in python_files if self._matches_pattern(os.path.basename(f).lower(), pattern.lower())]
            if matching_files:
                # Sort by preference: shorter names first, then alphabetically
                matching_files.sort(key=lambda x: (len(os.path.basename(x)), os.path.basename(x)))
                selected = matching_files[0]
                self.log(f"Selected Python file for {server_name} using pattern '{pattern}': {os.path.basename(selected)}")
                return selected
        
        # Fallback to first available Python file
        selected = python_files[0]
        self.log(f"Selected Python file for {server_name} (fallback): {os.path.basename(selected)}")
        return selected
        
    def _select_best_jar_file(self, jar_files: List[str]) -> str:
        """Select the most appropriate JAR file, preferring main application JARs."""
        # Priority patterns for JAR file selection
        priority_patterns = [
            "*mcp*.jar",                       # MCP-related JARs
            "*server*.jar",                    # Server JARs
            "*application*.jar",               # Application JARs
            "*main*.jar",                      # Main JARs
            "*.jar"                           # Any JAR file
        ]
        
        for pattern in priority_patterns:
            matching_files = [f for f in jar_files if self._matches_pattern(os.path.basename(f).lower(), pattern.lower())]
            if matching_files:
                # Prefer files not in target/lib or similar directories (check both path separators)
                non_lib_files = [f for f in matching_files if '/lib/' not in f.lower() and '\\lib\\' not in f.lower()]
                if non_lib_files:
                    matching_files = non_lib_files
                
                # Sort by preference: shorter names first, then alphabetically
                matching_files.sort(key=lambda x: (len(os.path.basename(x)), os.path.basename(x)))
                selected = matching_files[0]
                self.log(f"Selected JAR file using pattern '{pattern}': {os.path.basename(selected)}")
                return selected
        
        # Fallback to first available JAR file
        selected = jar_files[0]
        self.log(f"Selected JAR file (fallback): {os.path.basename(selected)}")
        return selected
        
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the given pattern (supports * wildcards)."""
        # Convert shell-style wildcards to regex, escaping special chars first
        # Escape all regex special characters except *
        escaped_pattern = re.escape(pattern)
        # Now convert escaped \* back to .* for wildcard matching
        regex_pattern = escaped_pattern.replace(r'\*', '.*')
        return re.match(f"^{regex_pattern}$", filename) is not None
        
    def detect_operating_system(self) -> str:
        """Detect and return the operating system."""
        os_name = platform.system().lower()
        
        # Handle Git Bash / MSYS / Cygwin on Windows
        if 'msys' in os_name or 'cygwin' in os_name or 'mingw' in os_name:
            os_name = 'windows'
            self.log(f"Detected Git Bash/MSYS/Cygwin environment, treating as Windows")
        
        self.log(f"Detected operating system: {os_name}")
        return os_name
        
    def _log_final_configuration(self, mcp_data: Dict) -> None:
        """Log the final MCP server configuration for verification."""
        self.log("=" * 60)
        self.log("Final MCP Server Configuration:")
        self.log("=" * 60)
        for server_name, server_config in mcp_data.items():
            if isinstance(server_config, dict):
                self.log(f"  Server: {server_name}")
                self.log(f"    Command: {server_config.get('command', 'N/A')}")
                args = server_config.get('args', [])
                if args:
                    self.log(f"    Args: {args[0] if len(args) == 1 else args}")
                env = server_config.get('env', {})
                if env:
                    self.log(f"    Env vars: {len(env)} configured")
        self.log("=" * 60)
        
    def get_cursor_mcp_path(self) -> Optional[str]:
        """Get the path to Cursor's mcp.json file based on OS."""
        self.log(f"Detecting Cursor config path for OS: {self.os_type}")
        
        if self.os_type == "darwin":  # macOS
            cursor_path = os.path.expanduser("~/.cursor/mcp.json")
        elif self.os_type == "windows":
            # Windows: Try multiple possible locations (order matters)
            # Use fallbacks if environment variables are not set
            appdata = os.environ.get('APPDATA') or os.path.join(os.path.expanduser("~"), 'AppData', 'Roaming')
            localappdata = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser("~"), 'AppData', 'Local')
            userprofile = os.environ.get('USERPROFILE') or os.path.expanduser("~")
            home = os.path.expanduser("~")
            
            self.log("=" * 50)
            self.log("WINDOWS PATH DETECTION - DEBUG INFO")
            self.log("=" * 50)
            self.log(f"  APPDATA      = {appdata}")
            self.log(f"  LOCALAPPDATA = {localappdata}")
            self.log(f"  USERPROFILE  = {userprofile}")
            self.log(f"  ~ (HOME)     = {home}")
            self.log("=" * 50)
            
            # All possible Cursor mcp.json locations on Windows
            possible_paths = [
                # User's home .cursor folder (like macOS/Linux)
                os.path.join(userprofile, '.cursor', 'mcp.json'),
                os.path.join(home, '.cursor', 'mcp.json'),
                # AppData locations
                os.path.join(appdata, 'Cursor', 'User', 'mcp.json'),
                os.path.join(appdata, 'Cursor', 'mcp.json'),
                os.path.join(localappdata, 'Cursor', 'User', 'mcp.json'),
                os.path.join(localappdata, 'Cursor', 'mcp.json'),
                # Expanded home path
                os.path.expanduser("~/.cursor/mcp.json")
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_paths = []
            for path in possible_paths:
                normalized = os.path.normpath(path) if path else ''
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    unique_paths.append(path)
            possible_paths = unique_paths
            
            self.log("Checking possible mcp.json locations:")
            for i, path in enumerate(possible_paths, 1):
                exists = os.path.exists(path) if path else False
                parent_exists = os.path.exists(os.path.dirname(path)) if path else False
                status = "[OK] EXISTS" if exists else ("[DIR] Parent exists" if parent_exists else "[X] Not found")
                self.log(f"  [{i}] {path}")
                self.log(f"      Status: {status}")
            
            # PRIORITY 1: Check if any mcp.json already exists (use that one!)
            cursor_path = None
            self.log("")
            self.log("Step 1: Searching for EXISTING mcp.json files...")
            existing_paths = []
            for path in possible_paths:
                if path and os.path.exists(path):
                    existing_paths.append(path)
                    self.log(f"  [OK] FOUND: {path}")
            
            if existing_paths:
                # If multiple exist, prefer .cursor folder, then AppData
                for path in existing_paths:
                    if '.cursor' in path:
                        cursor_path = path
                        self.log(f"  -> Using .cursor path: {path}")
                        break
                if not cursor_path:
                    cursor_path = existing_paths[0]
                    self.log(f"  -> Using first found: {cursor_path}")
            
            # PRIORITY 2: If no existing file, check where .cursor folder exists
            if not cursor_path:
                self.log("")
                self.log("Step 2: No existing mcp.json. Checking for .cursor directories...")
                cursor_dirs = [
                    os.path.join(userprofile, '.cursor'),
                    os.path.join(home, '.cursor'),
                    os.path.join(appdata, 'Cursor'),
                    os.path.join(localappdata, 'Cursor'),
                ]
                for cursor_dir in cursor_dirs:
                    if os.path.isdir(cursor_dir):
                        cursor_path = os.path.join(cursor_dir, 'mcp.json')
                        self.log(f"  [OK] Found Cursor directory: {cursor_dir}")
                        self.log(f"  -> Will create mcp.json at: {cursor_path}")
                        break
            
            # PRIORITY 3: Check if Cursor application is installed (look for Cursor directories)
            if not cursor_path:
                self.log("")
                self.log("Step 3: Looking for Cursor installation...")
                
                # Check common Cursor installation indicators
                program_files = os.environ.get('ProgramFiles') or 'C:\\Program Files'
                program_files_x86 = os.environ.get('ProgramFiles(x86)') or 'C:\\Program Files (x86)'
                cursor_indicators = [
                    os.path.join(localappdata, 'Programs', 'cursor'),
                    os.path.join(localappdata, 'cursor'),
                    os.path.join(appdata, 'Cursor'),
                    os.path.join(program_files, 'Cursor'),
                    os.path.join(program_files_x86, 'Cursor'),
                ]
                
                cursor_installed_appdata = False
                for indicator in cursor_indicators:
                    if indicator and os.path.exists(indicator):
                        self.log(f"  Found Cursor at: {indicator}")
                        if 'AppData' in indicator or 'Roaming' in indicator:
                            cursor_installed_appdata = True
                        break
                
                # If Cursor seems to use AppData, create config there
                if cursor_installed_appdata or os.path.exists(os.path.join(appdata, 'Cursor')):
                    cursor_path = os.path.join(appdata, 'Cursor', 'mcp.json')
                    self.log(f"  -> Cursor uses AppData. Will create at: {cursor_path}")
                else:
                    # Default to USERPROFILE/.cursor/ (like macOS/Linux)
                    cursor_path = os.path.join(userprofile, '.cursor', 'mcp.json')
                    self.log(f"  -> Will create at: {cursor_path}")
                
                # Also write to both locations for safety
                self._windows_secondary_path = None
                alt_path = os.path.join(userprofile, '.cursor', 'mcp.json')
                if cursor_path != alt_path:
                    self._windows_secondary_path = alt_path
                    self.log(f"  -> Will ALSO create at: {alt_path} (for compatibility)")
            
            self.log("=" * 50)
                
        elif self.os_type == "linux":
            cursor_path = os.path.expanduser("~/.cursor/mcp.json")
        else:
            self.log(f"Unsupported OS: {self.os_type}", "ERROR")
            return None
            
        self.log(f"Cursor MCP config path: {cursor_path}")
        return cursor_path
        
    def read_cursor_mcp_config(self, cursor_path: str) -> Optional[Dict]:
        """Read Cursor's mcp.json configuration."""
        try:
            if not os.path.exists(cursor_path):
                self.log("Cursor mcp.json not found, creating new configuration")
                return {"mcpServers": {}}
                
            with open(cursor_path, 'r', encoding='utf-8') as f:
                content = f.read()
                config = json.loads(content)
                self.log("Successfully read Cursor MCP configuration")
                return config
        except Exception as e:
            self.log(f"Error reading Cursor config: {str(e)}", "ERROR")
            return None
            
    def _backup_config(self, config_path: str) -> Optional[str]:
        """Create a backup of the config file before modifying."""
        if not os.path.exists(config_path):
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{config_path}.backup_{timestamp}"
            shutil.copy2(config_path, backup_path)
            self.log(f"Created backup: {backup_path}")
            return backup_path
        except OSError as e:
            self.log(f"Could not create backup: {e}", "WARNING")
            return None
    
    def update_cursor_mcp_config(self, cursor_path: str, cursor_config: Dict, mcp_data: Dict) -> bool:
        """Update Cursor's mcp.json with new MCP server configurations."""
        try:
            self.log("=" * 50)
            self.log("UPDATING CURSOR CONFIG")
            self.log("=" * 50)
            self.log(f"Target file: {cursor_path}")
            self.log(f"Target file exists before write: {os.path.exists(cursor_path)}")
            
            # Create backup of existing config
            self._backup_config(cursor_path)
            
            # Ensure mcpServers exists
            if "mcpServers" not in cursor_config:
                cursor_config["mcpServers"] = {}
                self.log("Created new mcpServers section")
            else:
                self.log(f"Existing mcpServers count: {len(cursor_config['mcpServers'])}")
                
            # Add new MCP server configurations
            self.log("")
            self.log("Adding/Updating servers:")
            for server_name, server_config in mcp_data.items():
                cursor_config["mcpServers"][server_name] = server_config
                self.log(f"  [+] Server: '{server_name}'")
                self.log(f"     Command: {server_config.get('command', 'N/A')}")
                self.log(f"     Args: {server_config.get('args', [])}")
                
            # Ensure directory exists
            parent_dir = os.path.dirname(cursor_path)
            self.log("")
            self.log(f"Parent directory: {parent_dir}")
            self.log(f"Parent exists before mkdir: {os.path.exists(parent_dir)}")
            os.makedirs(parent_dir, exist_ok=True)
            self.log(f"Parent exists after mkdir: {os.path.exists(parent_dir)}")
            
            # Write back to file
            self.log("")
            self.log(f"Writing config to: {cursor_path}")
            json_content = json.dumps(cursor_config, indent=2, ensure_ascii=False)
            self.log(f"JSON content length: {len(json_content)} characters")
            
            with open(cursor_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
                
            # Verify the file was written
            self.log("")
            if os.path.exists(cursor_path):
                file_size = os.path.getsize(cursor_path)
                self.log(f"[OK] SUCCESS: Config written to: {cursor_path}")
                self.log(f"   File size: {file_size} bytes")
                
                # Read back and verify
                with open(cursor_path, 'r', encoding='utf-8') as f:
                    verification = f.read()
                self.log(f"   Verification read: {len(verification)} characters")
                
                # Show the actual content written
                self.log("")
                self.log("[FILE] CONFIG FILE CONTENT:")
                self.log("-" * 40)
                for line in json_content.split('\n')[:30]:  # First 30 lines
                    self.log(f"   {line}")
                if len(json_content.split('\n')) > 30:
                    self.log("   ... (truncated)")
                self.log("-" * 40)
            else:
                self.log(f"[FAILED] File not found after write: {cursor_path}", "WARNING")
            
            # On Windows, also write to secondary path for compatibility
            if self.os_type == "windows" and hasattr(self, '_windows_secondary_path') and self._windows_secondary_path:
                secondary_path = self._windows_secondary_path
                if secondary_path != cursor_path:
                    self.log("")
                    self.log(f"[WRITE] Also writing to secondary location: {secondary_path}")
                    try:
                        secondary_parent = os.path.dirname(secondary_path)
                        os.makedirs(secondary_parent, exist_ok=True)
                        with open(secondary_path, 'w', encoding='utf-8') as f:
                            f.write(json_content)
                        if os.path.exists(secondary_path):
                            self.log(f"   [OK] Secondary config written: {secondary_path}")
                        else:
                            self.log(f"   [WARN] Secondary write may have failed")
                    except Exception as e:
                        self.log(f"   [WARN] Could not write secondary: {str(e)}")
            
            self.log("=" * 50)
                
            return True
            
        except PermissionError as e:
            self.log(f"Permission denied writing to {cursor_path}: {str(e)}", "ERROR")
            self.log("Try running as Administrator or check file permissions", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error updating Cursor config: {str(e)}", "ERROR")
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
            
    def run(self) -> bool:
        """Main execution method."""
        self.log("=== MCP Server Installation and Configuration Started ===")
        
        # Log venv configuration if set by installer.sh
        if self.using_venv_from_installer:
            self.log(f"Using venv Python from installer: {self.venv_python}")
            self.log(f"Installation directory: {self.install_dir}")
        
        try:
            # Step 1: Get current working directory
            current_dir = self.get_current_directory()
            
            # Step 2: Search for requirements.txt
            requirements_path = self.find_requirements_txt()
            
            # Step 3: Install requirements if found
            if requirements_path:
                if not self.set_proxy_and_install_requirements(requirements_path):
                    self.log("Failed to install requirements", "ERROR")
                    return False
            else:
                self.log("Skipping requirements installation - no requirements.txt found")
                
            # Step 4: Search for mcp-d.json
            mcp_json_path = self.find_mcp_d_json()
            if not mcp_json_path:
                self.log("mcp-d.json not found - cannot proceed", "ERROR")
                return False
                
            # Step 5: Read mcp-d.json
            mcp_data = self.read_mcp_json(mcp_json_path)
            if not mcp_data:
                self.log("Failed to read mcp-d.json", "ERROR")
                return False
                
            # Step 6: Find .py and .jar files
            executable_files = self.find_python_and_jar_files()
            
            # Step 7: Update mcp-d.json with absolute paths
            updated_mcp_data = self.update_mcp_json_args(mcp_data, executable_files)
            
            # Step 8: Detect OS and update Cursor config (sync to self.os_type)
            self.os_type = self.detect_operating_system()
            
            self.log("=" * 50)
            self.log(f"OS DETECTION RESULT: '{self.os_type}'")
            self.log("=" * 50)
            
            if self.os_type == "darwin":  # macOS
                self.log("[macOS] Executing macOS configuration path...")
                cursor_path = self.get_cursor_mcp_path()
                if cursor_path:
                    cursor_config = self.read_cursor_mcp_config(cursor_path)
                    if cursor_config is not None:
                        if self.update_cursor_mcp_config(cursor_path, cursor_config, updated_mcp_data):
                            self.log("=== SUCCESS: MCP Server Installation and Configuration Completed ===")
                            self._log_final_configuration(updated_mcp_data)
                            return True
                        else:
                            self.log("Failed to update Cursor configuration", "ERROR")
                            return False
                    else:
                        self.log("Failed to read Cursor configuration", "ERROR")
                        return False
                else:
                    self.log("Failed to get Cursor config path", "ERROR")
                    return False
            elif self.os_type == "linux":
                self.log("[Linux] Executing Linux configuration path...")
                self.log("[INFO] Note: Primary support is for Windows and macOS. Linux support is experimental.")
                cursor_path = self.get_cursor_mcp_path()
                if cursor_path:
                    cursor_config = self.read_cursor_mcp_config(cursor_path)
                    if cursor_config is not None:
                        if self.update_cursor_mcp_config(cursor_path, cursor_config, updated_mcp_data):
                            self.log("=== SUCCESS: MCP Server Installation and Configuration Completed ===")
                            self._log_final_configuration(updated_mcp_data)
                            return True
                        else:
                            self.log("Failed to update Cursor configuration", "ERROR")
                            return False
                    else:
                        self.log("Failed to read Cursor configuration", "ERROR")
                        return False
                else:
                    self.log("Failed to get Cursor config path", "ERROR")
                    return False
            elif self.os_type == "windows":
                self.log("[Windows] Executing Windows configuration path...")
                cursor_path = self.get_cursor_mcp_path()
                if cursor_path:
                    cursor_config = self.read_cursor_mcp_config(cursor_path)
                    if cursor_config is not None:
                        if self.update_cursor_mcp_config(cursor_path, cursor_config, updated_mcp_data):
                            self.log("=== SUCCESS: MCP Server Installation and Configuration Completed ===")
                            self._log_final_configuration(updated_mcp_data)
                            return True
                        else:
                            self.log("Failed to update Cursor configuration", "ERROR")
                            return False
                    else:
                        self.log("Failed to read Cursor configuration", "ERROR")
                        return False
                else:
                    self.log("Failed to get Cursor config path", "ERROR")
                    return False
            else:
                self.log("=" * 50)
                self.log(f"[?] UNKNOWN OS: '{self.os_type}'", "WARNING")
                self.log("   This OS is not explicitly supported!")
                self.log("   Supported: darwin (macOS), linux, windows")
                self.log("=" * 50)
                self.log(f"OS '{self.os_type}' detected - Cursor config update not implemented for this OS", "WARNING")
                self.log("=== PARTIAL SUCCESS: MCP data processed but Cursor config not updated ===")
                return True
                
        except Exception as e:
            self.log(f"Unexpected error: {str(e)}", "ERROR")
            return False


def main():
    """Main entry point."""
    installer = McpInstaller()
    success = installer.run()
    
    if success:
        print("\n[SUCCESS] MCP Server installation and configuration completed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILED] MCP Server installation and configuration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
