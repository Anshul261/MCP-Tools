#!/usr/bin/env python3
"""
Database initialization script
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import init_db, close_db, engine
from db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize the database with all tables"""
    try:
        logger.info("🚀 Initializing database...")
        
        # Create all tables
        await init_db()
        
        logger.info("✅ Database initialized successfully")
        logger.info("📊 Created tables:")
        
        # List all tables
        async with engine.begin() as conn:
            def get_table_names(connection):
                from sqlalchemy import inspect
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            table_names = await conn.run_sync(get_table_names)
            for table_name in table_names:
                logger.info(f"  - {table_name}")
        
        logger.info("🎉 Database setup complete!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await close_db()


async def reset_database():
    """Reset the database by dropping and recreating all tables"""
    try:
        logger.info("⚠️  Resetting database (this will delete all data)...")
        
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("🗑️  All tables dropped")
        
        # Create all tables
        await init_db()
        
        logger.info("✅ Database reset complete!")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise
    finally:
        await close_db()


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset the database (WARNING: This will delete all data)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        confirm = input("Are you sure you want to reset the database? This will delete all data. (y/N): ")
        if confirm.lower() != 'y':
            logger.info("Database reset cancelled")
            return
        
        await reset_database()
    else:
        await initialize_database()


if __name__ == "__main__":
    asyncio.run(main())