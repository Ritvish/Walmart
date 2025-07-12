#!/usr/bin/env python3
"""
Test MySQL connection for BuddyCart
"""

import mysql.connector
import os
from urllib.parse import urlparse

def test_mysql_connection():
    """Test direct MySQL connection"""
    try:
        # Parse DATABASE_URL
        db_url = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:@localhost:3306/buddycart")
        parsed = urlparse(db_url.replace("mysql+mysqlconnector://", "mysql://"))
        
        # Extract connection details
        host = parsed.hostname or "localhost"
        port = parsed.port or 3306
        user = parsed.username or "root"
        password = parsed.password or ""
        database = parsed.path.lstrip("/") or "buddycart"
        
        print(f"🔌 Testing MySQL connection...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   User: {user}")
        print(f"   Database: {database}")
        
        # Test connection
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL connection successful!")
            print(f"   MySQL version: {version[0]}")
            
            # Test if tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"   Tables found: {len(tables)}")
            
            if tables:
                print("   Table list:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table[0]}: {count} records")
            
            cursor.close()
            connection.close()
            return True
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n💡 Common solutions:")
        print("   1. Make sure XAMPP/WAMP/MAMP is running")
        print("   2. Check if MySQL service is started")
        print("   3. Verify the database 'buddycart' exists")
        print("   4. Check your .env file credentials")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_fastapi_connection():
    """Test FastAPI database connection"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        print(f"\n🚀 Testing FastAPI database connection...")
        
        # Test SQLAlchemy connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ FastAPI SQLAlchemy connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ FastAPI connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 BuddyCart MySQL Connection Test")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test direct MySQL connection
    mysql_ok = test_mysql_connection()
    
    # Test FastAPI connection
    if mysql_ok:
        fastapi_ok = test_fastapi_connection()
        
        if fastapi_ok:
            print(f"\n🎉 All connections successful!")
            print("✅ Your FastAPI is ready to connect to MySQL")
            print("✅ You can now start your server with: python main.py")
        else:
            print(f"\n⚠️  FastAPI connection issues detected")
    else:
        print(f"\n❌ MySQL connection failed - fix this first")
