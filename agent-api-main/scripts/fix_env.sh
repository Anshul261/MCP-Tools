#!/bin/bash
# scripts/fix_env.sh - Fix common .env file issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

print_header "Environment File Fixer"

if [ ! -f ".env" ]; then
    print_error ".env file not found"
    exit 1
fi

# Backup original file
cp .env .env.backup
print_info "Created backup: .env.backup"

# Create a temporary fixed file
temp_file=$(mktemp)

print_info "Fixing common .env file issues..."

python3 << 'EOF' > "$temp_file"
import re
import sys

def fix_env_line(line):
    """Fix common issues in environment variable lines"""
    # Skip comments and empty lines
    if not line.strip() or line.strip().startswith('#'):
        return line
    
    # Check if it's a valid key=value pair
    if '=' not in line:
        return line
    
    key, value = line.split('=', 1)
    key = key.strip()
    value = value.strip()
    
    # If value contains special characters and isn't quoted, quote it
    special_chars = [';', '&', '|', '(', ')', '$', '`', '"', "'", ' ', '\t']
    needs_quotes = any(char in value for char in special_chars)
    
    # Remove existing quotes first
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    
    # Add quotes if needed
    if needs_quotes and value:
        # Escape double quotes inside the value
        value = value.replace('"', '\\"')
        value = f'"{value}"'
    
    return f"{key}={value}\n"

try:
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line_num, line in enumerate(lines, 1):
        try:
            fixed_line = fix_env_line(line)
            fixed_lines.append(fixed_line)
        except Exception as e:
            print(f"Warning: Could not fix line {line_num}: {line.strip()}", file=sys.stderr)
            fixed_lines.append(line)
    
    # Write fixed content
    for line in fixed_lines:
        print(line, end='')
        
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

# Check if the fix was successful
if [ $? -eq 0 ]; then
    mv "$temp_file" .env
    print_success "Fixed .env file successfully"
    
    print_info "Changes made:"
    print_info "  - Added quotes around values with special characters"
    print_info "  - Escaped problematic characters"
    print_info "  - Preserved comments and formatting"
    
    # Test the fixed file
    print_step "Testing fixed .env file..."
    if load_env_vars >/dev/null 2>&1; then
        print_success "✓ .env file loads correctly now"
    else
        print_warning "⚠ .env file still has issues, restoring backup"
        mv .env.backup .env
        exit 1
    fi
else
    rm -f "$temp_file"
    print_error "Failed to fix .env file"
    exit 1
fi

print_header "Environment File Status"
print_info "Original file backed up as: .env.backup"
print_info "Fixed file ready for use"
print_success "You can now run: ./scripts/start.sh --dev"