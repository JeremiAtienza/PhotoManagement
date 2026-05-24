# PhotoFlow

PhotoFlow is a polished Django photo album management system built for secure uploads, organized albums, and streamlined administration.

## Highlights

- Clean Bootstrap-based UI with a modern dark theme
- Album and photo CRUD workflows for authenticated users
- Public/private visibility controls
- Cloudinary-backed media uploads
- Admin dashboard for moderation and operational oversight
- Render-ready deployment configuration

## Project structure

- `photoalbum/` – Django settings, routing, and production configuration
- `albums/` – models, forms, views, tests, and migrations
- `templates/` – HTML templates for the web interface
- `static/` – CSS and static assets
- `requirements.txt` – Python dependencies
- `Procfile` and `render.yaml` – deployment configuration

## Local development

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `python` is not available, use the Windows launcher:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file and set the values below:

```env
DJANGO_ENV=development
DEBUG=true
SECRET_KEY=replace-with-a-secure-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
DATABASE_URL=
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

### 3. Apply migrations

```powershell
python manage.py migrate
```

### 4. Create an admin account

```powershell
python manage.py createsuperuser
```

### 5. Run the development server

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Cloudinary setup

1. Create a Cloudinary account.
2. Retrieve your `Cloud Name`, `API Key`, and `API Secret`.
3. Add them to `CLOUDINARY_URL` in your `.env` file.
4. Restart the Django server after changing `.env`.
5. Confirm the value is loaded with:

```powershell
.\.venv\Scripts\python.exe -c "import os; print(os.getenv('CLOUDINARY_URL'))"
```

If `CLOUDINARY_URL` is empty, uploads will still work locally because the app falls back to local media storage, but Cloudinary will not be used.

### Example `.env` values

```env
CLOUDINARY_URL=cloudinary://123456789012345:your-api-secret@your-cloud-name
```

You can also use separate variables instead of `CLOUDINARY_URL`:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## Production deployment

### Render environment variables

```env
DJANGO_ENV=production
DEBUG=false
SECRET_KEY=your-strong-secret
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
DATABASE_URL=your-render-postgres-url
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

### Deployment checklist

1. Create a Render web service and connect the GitHub repository.
2. Add a Render PostgreSQL database.
3. Set the environment variables above.
4. Deploy the service.
5. Run migrations in the Render shell:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Testing

```powershell
python manage.py test albums
```

## Notes

- Production static files are served with WhiteNoise.
- Cloudinary is configured as the media storage backend.
- The admin dashboard is limited to users in the `Album Administrator` role.
