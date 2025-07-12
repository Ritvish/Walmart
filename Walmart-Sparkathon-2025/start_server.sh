#!/bin/bash

# # BuddyCart Server Startup Script

# echo "🚀 Starting BuddyCart FastAPI Server..."

# # Check if virtual environment exists
if [ ! -d "myenv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv myenv
fi

# # Activate virtual environment
echo "🔧 Activating virtual environment..."
source myenv/bin/activate

# # Install dependencies
# echo "📚 Installing dependencies..."
# pip install -r requirements.txt

# # Check if .env file exists
# if [ ! -f ".env" ]; then
#     echo "⚠️  .env file not found. Please create one with your database credentials."
#     echo "Example .env file:"
#     cat .env
#     exit 1
# fi

# # Start the server
# echo "🌟 Starting FastAPI server..."
# python main.py
