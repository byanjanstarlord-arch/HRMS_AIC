#!/usr/bin/env python
"""
HRMS Portal - Setup Script
Automates the initial setup process
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}...")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"ERROR: {description} failed!")
        sys.exit(1)
    print(f"✓ {description} completed successfully!")


def main():
    """Main setup function"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              HRMS Portal - Setup Script                      ║
    ║                                                              ║
    ║     Human Resource Management System - Leave Portal          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version}")
    
    # Install requirements
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    # Run migrations
    run_command("python manage.py migrate", "Running database migrations")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              Setup Completed Successfully!                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Next steps:
    
    1. Create an admin user:
       python manage.py createsuperuser
       
    2. Run the development server:
       python manage.py runserver
       
    3. Open your browser and go to:
       http://127.0.0.1:8000/
       
    4. To access the admin panel:
       http://127.0.0.1:8000/admin/
       
    5. IMPORTANT: After creating the superuser, log in to the admin
       panel and set your user's "role" to "admin" for full access.
    
    For more information, see README.md
    """)


if __name__ == '__main__':
    main()
