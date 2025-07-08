#!/usr/bin/env python3
"""
Requirements.txt generator from pyproject.toml
"""
import sys
import subprocess
from pathlib import Path

def generate_requirements():
    """Generate requirements.txt from pyproject.toml"""
    
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    requirements_path = project_root / "requirements.txt"
    
    if not pyproject_path.exists():
        print(f"❌ pyproject.toml not found at {pyproject_path}")
        sys.exit(1)
    
    try:
        # Use pip-tools to generate requirements.txt
        print("🔧 Generating requirements.txt from pyproject.toml...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pip-tools"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("📦 Installing pip-tools...")
            print(result.stderr)
        
        # Generate requirements.txt
        result = subprocess.run([
            "pip-compile", str(pyproject_path), "--output-file", str(requirements_path)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print(f"✅ Generated {requirements_path}")
            print("📋 Contents:")
            with open(requirements_path, 'r') as f:
                print(f.read())
        else:
            print(f"❌ Failed to generate requirements.txt: {result.stderr}")
            
            # Fallback: manually extract dependencies
            print("🔄 Trying manual extraction...")
            extract_dependencies_manually(pyproject_path, requirements_path)
            
    except FileNotFoundError:
        print("❌ pip-compile not found. Trying manual extraction...")
        extract_dependencies_manually(pyproject_path, requirements_path)


def extract_dependencies_manually(pyproject_path: Path, requirements_path: Path):
    """Manually extract dependencies from pyproject.toml"""
    
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("❌ tomllib/tomli not available. Installing tomli...")
            subprocess.run([sys.executable, "-m", "pip", "install", "tomli"])
            import tomli as tomllib
    
    with open(pyproject_path, 'rb') as f:
        data = tomllib.load(f)
    
    dependencies = data.get('project', {}).get('dependencies', [])
    
    with open(requirements_path, 'w') as f:
        f.write("# Generated from pyproject.toml\n")
        f.write("# Run: python scripts/requirements_generator.py\n\n")
        
        for dep in dependencies:
            f.write(f"{dep}\n")
    
    print(f"✅ Manually generated {requirements_path}")
    print("📋 Contents:")
    with open(requirements_path, 'r') as f:
        print(f.read())


if __name__ == "__main__":
    generate_requirements()