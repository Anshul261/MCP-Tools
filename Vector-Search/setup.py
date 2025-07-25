"""
Setup script for RAG Agent with Agno
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_postgresql():
    """Check if PostgreSQL is running"""
    print("🔍 Checking PostgreSQL...")
    try:
        result = subprocess.run("pg_isready", capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is running")
            return True
        else:
            print("❌ PostgreSQL is not running")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed")
        return False

def setup_database():
    """Setup the database and pgvector extension"""
    print("🔄 Setting up database...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    db_name = os.getenv('DB_NAME', 'rag_database')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    if not db_password:
        print("❌ DB_PASSWORD not set in environment variables")
        return False
    
    # Set PGPASSWORD environment variable for authentication
    env_vars = os.environ.copy()
    env_vars['PGPASSWORD'] = db_password
    
    # Create database if it doesn't exist
    create_db_cmd = f'createdb -h {db_host} -p {db_port} -U {db_user} {db_name}'
    print(f"🔄 Creating database {db_name} if it doesn't exist...")
    try:
        result = subprocess.run(create_db_cmd, shell=True, env=env_vars, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Database {db_name} created successfully")
        else:
            # Database might already exist, which is okay
            if "already exists" in result.stderr:
                print(f"✅ Database {db_name} already exists")
            else:
                print(f"⚠️  Database creation result: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Database creation error: {e}")
    
    # Run initialization script
    init_script = Path("database/init_db.sql")
    if init_script.exists():
        init_cmd = f'psql -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f {init_script}'
        print("🔄 Initializing database schema...")
        try:
            result = subprocess.run(init_cmd, shell=True, env=env_vars, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Database schema initialized successfully")
                return True
            else:
                print(f"❌ Database initialization failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return False
    else:
        print("❌ Database initialization script not found")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if Path("requirements.txt").exists():
        return run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements")
    else:
        print("❌ requirements.txt not found")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "documents",      # Source documents
        "converted_docs", # Converted markdown files
        "logs",          # Log files
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def check_env_file():
    """Check if .env file exists and is configured"""
    print("🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found. Copying from .env.example...")
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from example")
            print("📝 Please edit .env file with your actual configuration")
            return False
        else:
            print("❌ Neither .env nor .env.example found")
            return False
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "DB_HOST",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  The following environment variables need to be configured:")
        for var in missing_vars:
            print(f"   - {var}")
        print("Please edit your .env file with actual values")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    test_imports = [
        ("agno", "Agno framework"),
        ("docling", "Docling document processor"),
        ("psycopg2", "PostgreSQL adapter"),
        ("openai", "OpenAI client"),
        ("requests", "HTTP requests"),
        ("transformers", "HuggingFace transformers"),
        ("sentence_transformers", "Sentence transformers for local embeddings"),
    ]
    
    all_good = True
    for package, description in test_imports:
        try:
            __import__(package)
            print(f"✅ {description} imported successfully")
        except ImportError as e:
            print(f"❌ {description} import failed: {e}")
            all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("🚀 RAG Agent Setup")
    print("=" * 40)
    
    steps = [
        ("Check environment file", check_env_file),
        ("Install dependencies", install_dependencies),
        ("Test imports", test_imports),
        ("Create directories", create_directories),
        ("Check PostgreSQL", check_postgresql),
        ("Setup database", setup_database),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 40)
    print("🏁 Setup Summary")
    
    if failed_steps:
        print(f"❌ {len(failed_steps)} step(s) failed:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix the issues above and run setup again.")
        return False
    else:
        print("✅ All setup steps completed successfully!")
        print("\nYou can now run:")
        print("   python agno_rag_example.py")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)