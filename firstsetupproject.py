import os
import subprocess

def run(cmd, desc=None):
    """Run a shell command with optional description."""
    if desc:
        print(f"\n🔹 {desc}")
    subprocess.run(cmd, shell=True, check=True)

def setup_django_project():
    """Set up a Django backend project automatically."""
    print("🚀 Starting Django project setup...")

    # Use current directory as backend folder
    backend_dir = os.getcwd()

    # --- Step 1: Ask user for project name ---
    project_name = ""
    while not project_name.strip():
        project_name = input("🧱 Enter your Django project name: ").strip()

    # --- Step 2: Ensure Pipenv installed and environment ready ---
    print("\n🔹 Checking for Pipenv environment...")
    pipenv_check = subprocess.run("pipenv --venv", shell=True, capture_output=True)
    if pipenv_check.returncode != 0:
        run("pip install pipenv", "Installing Pipenv (first-time only)")
        run("pipenv install", "Creating new Pipenv environment")
    else:
        print("✅ Pipenv environment already exists.")

    # --- Step 3: Install Django ---
    run("pipenv install django", "Installing Django inside Pipenv")

    # --- Step 4: Start project in current folder ---
    run(f"pipenv run django-admin startproject {project_name} .", f"Creating Django project '{project_name}' in current folder")

    print(f"\n✅ Django project '{project_name}' created successfully in: {backend_dir}")
    print("👉 Next: run `pipenv shell` then `python manage.py runserver` to verify.")

if __name__ == "__main__":
    setup_django_project()
