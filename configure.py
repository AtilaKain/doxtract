#!/usr/bin/env python3
"""
Configuration script for DoxTract deployment
Usage: python configure.py --backend-url https://your-backend.run.app --frontend-url https://your-app.vercel.app
"""

import argparse
import re
import sys
from pathlib import Path

def update_frontend_config(backend_url):
    """Update frontend configuration with backend URL"""
    frontend_file = Path("frontend/index.html")
    
    if not frontend_file.exists():
        print("❌ frontend/index.html not found")
        return False
    
    content = frontend_file.read_text()
    
    # Update the backend URL
    pattern = r"return 'https://your-backend-url\.run\.app';"
    replacement = f"return '{backend_url}';"
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        frontend_file.write_text(content)
        print(f"✅ Updated frontend to use backend: {backend_url}")
        return True
    else:
        print("❌ Could not find backend URL pattern in frontend")
        return False

def update_backend_cors(frontend_url):
    """Update backend CORS configuration with frontend URL"""
    backend_file = Path("backend/app.py")
    
    if not backend_file.exists():
        print("❌ backend/app.py not found")
        return False
    
    content = backend_file.read_text()
    
    # Update CORS origins
    pattern = r'"https://your-app-name\.vercel\.app"'
    replacement = f'"{frontend_url}"'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        backend_file.write_text(content)
        print(f"✅ Updated backend CORS to allow: {frontend_url}")
        return True
    else:
        print("❌ Could not find CORS pattern in backend")
        return False

def main():
    parser = argparse.ArgumentParser(description="Configure DoxTract for deployment")
    parser.add_argument("--backend-url", help="Backend URL (Cloud Run)")
    parser.add_argument("--frontend-url", help="Frontend URL (Vercel)")
    
    args = parser.parse_args()
    
    if not args.backend_url and not args.frontend_url:
        print("Usage: python configure.py --backend-url https://your-backend.run.app --frontend-url https://your-app.vercel.app")
        sys.exit(1)
    
    success = True
    
    if args.backend_url:
        if not update_frontend_config(args.backend_url):
            success = False
    
    if args.frontend_url:
        if not update_backend_cors(args.frontend_url):
            success = False
    
    if success:
        print("\n🎉 Configuration updated successfully!")
        print("\nNext steps:")
        print("1. Deploy backend: cd backend && gcloud run deploy")
        print("2. Deploy frontend: cd frontend && vercel --prod")
    else:
        print("\n❌ Configuration failed. Please check the files manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()
