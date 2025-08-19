#!/usr/bin/env python3
"""
Test database connection with actual Render PostgreSQL credentials.
This script verifies connectivity to the deployed database.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import psycopg2

# Database connection details from Render
INTERNAL_URL = "postgresql://waardhaven_db_5t62_user:tJGnwSw4vLwNVAN7JWzi3BhP6yniOnS4@dpg-d2dpibbe5dus7390qqcg-a/waardhaven_db_5t62"
EXTERNAL_URL = "postgresql://waardhaven_db_5t62_user:tJGnwSw4vLwNVAN7JWzi3BhP6yniOnS4@dpg-d2dpibbe5dus7390qqcg-a.oregon-postgres.render.com/waardhaven_db_5t62"

def test_connection(url, connection_type):
    """Test database connection and print diagnostics."""
    print(f"\n{'='*60}")
    print(f"Testing {connection_type} Connection")
    print(f"{'='*60}")
    
    try:
        # Create engine with minimal pool for testing
        engine = create_engine(
            url,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            connect_args={"sslmode": "require"}
        )
        
        # Test basic connection
        with engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Check current database
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"📁 Connected to database: {db_name}")
            
            # Check tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"📋 Found {len(tables)} tables:")
                for table in tables:
                    # Get row count for each table
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"   - {table}: {count} rows")
            else:
                print("⚠️  No tables found in public schema")
            
            # Check connection pool status
            pool = engine.pool
            print(f"\n🔗 Connection Pool Status:")
            print(f"   - Size: {pool.size()}")
            print(f"   - Checked in: {pool.checkedin()}")
            print(f"   - Checked out: {pool.checkedout()}")
            
            return True
            
    except OperationalError as e:
        print(f"❌ Connection failed!")
        print(f"Error: {str(e)}")
        
        # Additional diagnostics
        if "could not translate host name" in str(e):
            print("\n💡 This error suggests:")
            print("   - The hostname might be internal-only (use from within Render)")
            print("   - Try the external URL for local testing")
        elif "password authentication failed" in str(e):
            print("\n💡 This error suggests:")
            print("   - Invalid credentials")
            print("   - Database user might have been recreated")
        elif "SSL" in str(e):
            print("\n💡 This error suggests:")
            print("   - SSL/TLS connection required")
            print("   - Already configured with sslmode=require")
            
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

def check_environment():
    """Check current environment configuration."""
    print("\n📍 Environment Check:")
    print(f"   - Current DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    print(f"   - Running on Render: {os.getenv('RENDER', 'No')}")
    print(f"   - Python version: {sys.version}")

if __name__ == "__main__":
    print("🚀 Waardhaven Database Connection Test")
    print("="*60)
    
    check_environment()
    
    # Test external connection (should work from local)
    external_success = test_connection(EXTERNAL_URL, "External (for local testing)")
    
    # Test internal connection (only works within Render)
    print("\n" + "="*60)
    print("ℹ️  Note: Internal URL only works from within Render's network")
    print("    Attempting connection anyway for completeness...")
    internal_success = test_connection(INTERNAL_URL, "Internal (Render-only)")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Connection Test Summary")
    print("="*60)
    print(f"External URL: {'✅ Success' if external_success else '❌ Failed'}")
    print(f"Internal URL: {'✅ Success' if internal_success else '❌ Failed (expected from local)'}")
    
    if external_success:
        print("\n✅ Database is accessible and configured correctly!")
        print("   Use the external URL for local development")
        print("   Render will automatically use the internal URL in production")
    else:
        print("\n⚠️  Could not connect to database")
        print("   Please verify credentials and network access")