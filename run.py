"""
RiskGuard Pro — Enterprise Business Risk Assessment Dashboard Launcher
Runs the Flask backend server from the server/ package.
"""

import os
import sys

# Ensure UTF-8 stdout on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
sys.path.insert(0, server_dir)

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*65)
    print("  RiskGuard Pro — Enterprise Business Risk Assessment Dashboard")
    print("  Client Folder: ./client")
    print("  Server Folder: ./server")
    print("  Database: Supabase (PostgreSQL Cloud) / Local SQLite Fallback")
    print(f"  Dashboard URL: http://localhost:{port}")
    print("="*65 + "\n")
    app.run(debug=False, port=port, host="0.0.0.0")
