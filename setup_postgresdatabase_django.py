import os
import subprocess
import getpass
import re

def run(cmd, desc=None):
    """Run shell commands safely with optional description."""
    if desc:
        print(desc)
    subprocess.run(cmd, shell=True, check=True)

# --- Step 1: User Input ---
project_name = input("Enter your Django project name: ").strip()
pg_password = getpass.getpass("Enter your PostgreSQL password (hidden): ")

db_name = f"{project_name.lower()}db"
db_user = f"user{project_name.lower()}"
db_user_password = "mypassword"

print(f"\nSetting up PostgreSQL database '{db_name}' and user '{db_user}'...")

# --- Step 2: Detect PostgreSQL executable path ---
pg_path = r'"C:\Program Files\PostgreSQL\18\bin\psql.exe"'
if not os.path.exists(pg_path.replace('"', '')):
    print("PostgreSQL path not found. Please adjust pg_path variable.")
    exit(1)

# --- Step 3: Create database, user, and grant privileges ---
try:
    os.environ["PGPASSWORD"] = pg_password

    # Create database and user
    run(f'{pg_path} -U postgres -c "CREATE DATABASE {db_name};"', "Creating database...")
    run(f'{pg_path} -U postgres -c "CREATE USER {db_user} WITH PASSWORD \'{db_user_password}\';"', "Creating user...")
    run(f'{pg_path} -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"', "Granting privileges on database...")

    # --- Fix schema ownership and privileges ---
    schema_fix_sql = f"""
    \\c {db_name};
    ALTER SCHEMA public OWNER TO {db_user};
    GRANT ALL PRIVILEGES ON SCHEMA public TO {db_user};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_user};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_user};
    """
    with open("schema_fix.sql", "w") as f:
        f.write(schema_fix_sql)

    run(f'{pg_path} -U postgres -f schema_fix.sql', "Fixing schema privileges and ownership...")
    os.remove("schema_fix.sql")

except subprocess.CalledProcessError as e:
    print(f"Error running PostgreSQL commands: {e}")
    exit(1)

# --- Step 4: Update Django settings.py ---
settings_path = os.path.join(os.getcwd(), project_name, "settings.py")
if not os.path.exists(settings_path):
    print(f"settings.py not found at: {settings_path}")
    exit(1)

print("Updating Django settings.py with PostgreSQL configuration...")

with open(settings_path, "r") as f:
    settings = f.read()

new_db_settings = f"""
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{db_name}',
        'USER': '{db_user}',
        'PASSWORD': '{db_user_password}',
        'HOST': 'localhost',
        'PORT': '5432',
    }}
}}
"""

if "DATABASES" in settings:
    settings = re.sub(r"DATABASES\s*=\s*\{[\s\S]*?\}\s*\}", new_db_settings, settings)
else:
    settings += "\n" + new_db_settings

with open(settings_path, "w") as f:
    f.write(settings)

# --- Step 5: Install PostgreSQL driver and migrate ---
print("Installing psycopg2-binary...")
run("pipenv install psycopg2-binary")

print("Running makemigrations and migrate...")
run("pipenv run python manage.py makemigrations")
run("pipenv run python manage.py migrate")

print("\nPostgreSQL setup complete and connected to Django successfully.")
