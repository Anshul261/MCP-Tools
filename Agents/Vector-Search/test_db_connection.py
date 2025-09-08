#!/usr/bin/env python3
"""
Simple script to test PostgreSQL database connection
"""

import os
import psycopg2
from dotenv import load_dotenv

def test_connection():
    """Test database connection with environment variables"""
    load_dotenv()
    
    # Get connection parameters
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'rag_database'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    print("🔍 Testing database connection...")
    print(f"Host: {db_config['host']}")
    print(f"Port: {db_config['port']}")
    print(f"Database: {db_config['database']}")
    print(f"User: {db_config['user']}")
    print(f"Password: {'*' * len(db_config['password']) if db_config['password'] else 'NOT SET'}")
    print("-" * 40)
    
    if not db_config['password']:
        print("❌ DB_PASSWORD not set in environment variables")
        return False
    
    try:
        # Test connection
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0][:50]}...")
        
        # Test if database exists
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"✅ Current database: {current_db[0]}")
        
        # Test if pgvector extension exists
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');")
        has_vector = cursor.fetchone()[0]
        if has_vector:
            print("✅ pgvector extension is installed")
        else:
            print("⚠️  pgvector extension not found")
        
        # Test if our tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('documents', 'document_chunks', 'search_history');
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"✅ Found tables: {[t[0] for t in tables]}")
        else:
            print("⚠️  RAG tables not found (run setup.py to create them)")
        
        cursor.close()
        conn.close()
        print("✅ Database connection test successful!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check if PostgreSQL is running: sudo systemctl status postgresql")
        print("2. Verify your database credentials in .env file")
        print("3. Ensure the database exists: createdb -h localhost -U postgres rag_database")
        print("4. Check PostgreSQL authentication settings in pg_hba.conf")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_connection()