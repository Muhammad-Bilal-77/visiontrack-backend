import os
import re
import subprocess

def run(cmd, desc=None):
    """Run a shell command with optional description."""
    if desc:
        print(f"\n🔹 {desc}")
    subprocess.run(cmd, shell=True, check=True)

def add_app_to_installed_apps(settings_path, app_name):
    """Add the new app to INSTALLED_APPS in settings.py"""
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add app at end of INSTALLED_APPS if not already present
    if app_name not in content:
        new_content = re.sub(
            r"INSTALLED_APPS\s*=\s*\[[^\]]*\]",
            lambda match: match.group(0)[:-1] + f"    '{app_name}',\n]",
            content
        )
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Added '{app_name}' to INSTALLED_APPS in settings.py")
    else:
        print(f"⚠️ '{app_name}' already in INSTALLED_APPS")

def create_app_urls(app_path, app_name):
    """Create urls.py inside the new app with an example endpoint"""
    urls_path = os.path.join(app_path, "urls.py")
    if not os.path.exists(urls_path):
        with open(urls_path, "w", encoding="utf-8") as f:
            f.write(f"""from django.urls import path
from django.http import JsonResponse

def {app_name}_index(request):
    return JsonResponse({{"message": "Hello from {app_name} API!"}})

urlpatterns = [
    path('', {app_name}_index, name='{app_name}_index'),
]
""")
        print(f"✅ Created urls.py with a test endpoint for '{app_name}' app")
    else:
        print(f"⚠️ urls.py already exists in '{app_name}' app")

def connect_app_urls_to_project(project_urls_path, app_name):
    """Include app-level urls.py in project-level urls.py with a unique API prefix"""
    with open(project_urls_path, "r", encoding="utf-8") as f:
        content = f.read()

    include_import = "from django.urls import include, path"
    if "include" not in content:
        content = re.sub(r"from django\.urls import path", include_import, content)

    # Create a unique path prefix for the app
    api_prefix = f"api_{app_name}"

    pattern = rf"path\('{api_prefix}/', include\('{app_name}\.urls'\)\)"
    if re.search(pattern, content):
        print(f"⚠️ API route for '{app_name}' already exists.")
    else:
        content = re.sub(
            r"urlpatterns\s*=\s*\[",
            f"urlpatterns = [\n    path('{api_prefix}/', include('{app_name}.urls')),\n",
            content
        )
        with open(project_urls_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Connected '{app_name}' urls to project with path: /{api_prefix}/")

def create_django_app():
    """Main automation: create app, configure settings, and connect URLs"""
    app_name = input("🧱 Enter your Django app name: ").strip()
    if not app_name:
        print("❌ App name cannot be empty.")
        return

    # Detect project structure
    base_dir = os.getcwd()
    settings_path = None
    project_urls_path = None

    # Find settings.py automatically
    for root, dirs, files in os.walk(base_dir):
        if "settings.py" in files:
            settings_path = os.path.join(root, "settings.py")
            project_folder = os.path.basename(root)
            project_urls_path = os.path.join(root, "urls.py")
            break

    if not settings_path:
        print("❌ Could not find Django settings.py in this folder.")
        return

    # Step 1: Create app
    run(f"pipenv run python manage.py startapp {app_name}", f"Creating Django app '{app_name}'")

    # Step 2: Add to INSTALLED_APPS
    add_app_to_installed_apps(settings_path, app_name)

    # Step 3: Create urls.py with default endpoint
    app_path = os.path.join(base_dir, app_name)
    create_app_urls(app_path, app_name)

    # Step 4: Include app’s urls in project urls.py
    connect_app_urls_to_project(project_urls_path, app_name)

    print(f"\n🎉 App '{app_name}' created and configured successfully!")

if __name__ == "__main__":
    create_django_app()
