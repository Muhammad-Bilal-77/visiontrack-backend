# Koyeb Deployment Instructions for VisionTrack

## Prerequisites
- Koyeb account (https://app.koyeb.com)
- GitHub account with your repository
- PostgreSQL database (Koyeb provides managed databases)

## Step 1: Create a PostgreSQL Database on Koyeb

1. Go to **Koyeb Dashboard** → **Databases**
2. Click **Create Database**
3. Select **PostgreSQL 16**
4. Configuration:
   - Name: `visiontrack-db`
   - Region: Choose closest to you (Singapore recommended for Pakistan)
   - Plan: **Starter** (suitable for testing)
5. Click **Create**
6. Wait for the database to be ready
7. Copy the connection string (you'll need it later)

## Step 2: Create a Service on Koyeb

### Option A: Using Docker (Recommended - Solves Memory Issues)

1. Go to **Koyeb Dashboard** → **Services**
2. Click **Create Service**
3. Choose deployment method: **Docker**
4. Select **GitHub** as source
5. Repository: `Muhammad-Bilal-77/visiontrack-backend`
6. Select branch: `master`
7. Docker settings:
   - **Dockerfile path**: `./Dockerfile`
   - **Build command**: Leave empty (uses Dockerfile)
   - **Run command**: Leave empty (uses Dockerfile CMD)
8. Instance settings:
   - **Instance type**: **Micro** (512MB RAM - sufficient with Docker optimization)
   - **Region**: Singapore
9. Environment variables (click **Add environment variable**):

```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-service-name.koyeb.app
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DOMAIN=your-service-name.koyeb.app
SITE_NAME=VisionTrack
```

10. Click **Create Service**

### Option B: Using buildpacks (Without Docker)

1. Go to **Koyeb Dashboard** → **Services**
2. Click **Create Service**
3. Choose: **Git**
4. GitHub: `Muhammad-Bilal-77/visiontrack-backend`
5. Branch: `master`
6. Buildpack: **Python**
7. Build settings:
   - **Build command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
   - **Run command**: `gunicorn visiontrack.wsgi:application --bind 0.0.0.0:8000`
8. Same environment variables as above
9. **Note**: This might still have memory issues; Docker is safer

## Step 3: Set Environment Variables

After creating the service:

1. Go to **Services** → Your service name
2. Click **Settings** → **Environment variables**
3. Add all the variables listed above
4. Get your actual `DATABASE_URL` from your PostgreSQL database connection details
5. Click **Save**

## Step 4: Configure Database Connection String

Your `DATABASE_URL` should look like:
```
postgresql://username:password@host:port/dbname
```

Example:
```
postgresql://user123:pass456@visiontrack-db-abcd.koyeb.app:5432/visiontrack_db
```

## Step 5: Deploy

1. Koyeb automatically starts deploying when you create the service
2. Monitor the deployment in **Activity** tab
3. Wait for status to show **RUNNING** (green)
4. Your app will be available at: `https://your-service-name.koyeb.app`

## Step 6: Create Superuser & Run Migrations

Once deployed:

1. Go to **Services** → Your service → **Logs** tab
2. Check if migrations ran automatically from `build.sh`
3. If not, create a one-off task:
   - Click **Run task**
   - Command: `python manage.py migrate`
   - Click **Run**

4. Create admin user:
   - Click **Run task**
   - Command: `python manage.py createsuperuser`
   - Fill in email/password
   - Click **Run**

## Step 7: Test Your Deployment

1. Visit: `https://your-service-name.koyeb.app/admin/`
2. Login with superuser credentials
3. Test API endpoints:
   - `https://your-service-name.koyeb.app/api/auth/users/`
   - `https://your-service-name.koyeb.app/api/auth/jwt/create/`

## Troubleshooting

### Out of Memory Error
- **Solution**: Docker reduces memory usage. If still an issue:
  - Reduce workers in Dockerfile: `--workers 1`
  - Use **Standard** instance instead of Micro
  - Upgrade database separately

### Database Connection Failed
- Check `DATABASE_URL` format is correct
- Verify database is in same region
- Check firewall allows connections

### Migrations Not Running
- Run manually via **Run task**
- Or add to Dockerfile entrypoint

### Static Files Not Loading
- Ensure `collectstatic` ran (check logs)
- Verify `STATIC_ROOT` in settings.py
- WhiteNoise should serve them automatically

## Docker Deployment Advantages

✅ Smaller memory footprint (uses slim Python image)
✅ Pre-built dependencies (faster builds)
✅ Consistent environment (local = production)
✅ Faster cold starts
✅ Better control over system packages

## Cost Estimation (Koyeb Free Tier)

- **Service**: 2 free services, 512MB RAM
- **Database**: Free tier with limits
- **Bandwidth**: 100GB/month free

Perfect for development and small projects!

## Next Steps

1. Push code with Dockerfile to GitHub
2. Create service on Koyeb
3. Monitor logs and test endpoints
4. Configure custom domain (optional)
5. Set up error monitoring (Sentry recommended)

## Support

- Koyeb Docs: https://docs.koyeb.com
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

---

**Your app will be live at:**
`https://<your-service-name>.koyeb.app`

🚀 Good luck with Koyeb!
