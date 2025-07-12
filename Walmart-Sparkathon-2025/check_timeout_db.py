#!/usr/bin/env python3
"""
Script to check timeout_minutes values in the database
"""
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def check_timeout_values():
    """Check timeout_minutes values in buddy_queue table"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password='',
            database='buddycart'
        )
        
        cursor = connection.cursor()
        
        # Get all buddy_queue entries with their timeout values
        cursor.execute("""
            SELECT id, user_id, timeout_minutes, status, created_at 
            FROM buddy_queue 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        print("Recent buddy_queue entries:")
        print("ID | User ID | Timeout | Status | Created At")
        print("-" * 70)
        
        for row in results:
            print(f"{row[0][:8]}... | {row[1][:8]}... | {row[2]:7} | {row[3]:8} | {row[4]}")
            
        if not results:
            print("No entries found in buddy_queue table")
            
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_timeout_values()
