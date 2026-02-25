# HRMS Portal - Human Resource Management System

A complete Leave Management Portal built with Django and vanilla JavaScript. Features role-based authentication, real-time leave application workflow, and a modern, responsive UI.

## Features

### Employee Features
- **Registration & Login**: Secure employee registration with full name, email, employee ID, and department
- **Dashboard**: Overview of leave statistics (total, pending, approved, rejected)
- **Apply Leave**: Submit leave requests with type, dates, and reason
- **Leave Status**: Track all leave requests with real-time status updates
- **Profile**: View personal information and account details

### Admin Features
- **Admin Dashboard**: Overview of all employees and leave requests
- **Leave Requests**: View and manage all leave applications
- **Approve/Reject**: One-click approval/rejection with optional remarks
- **Employees List**: View all registered employees
- **Real-time Updates**: Instant notifications for new leave requests

### Technical Features
- **Real-time Sync**: AJAX polling for instant status updates
- **Secure Authentication**: Session-based auth with CSRF protection
- **Role-based Access**: Separate dashboards for Admin and Employee
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, card-based design with subtle animations

## Project Structure

```
hrms_portal/
├── hrms_project/          # Main Django project
│   ├── __init__.py
│   ├── settings.py        # Project settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
├── accounts/              # User authentication app
│   ├── __init__.py
│   ├── models.py          # Custom User model
│   ├── views.py           # Authentication views
│   ├── forms.py           # Registration/Login forms
│   ├── urls.py            # App URLs
│   └── admin.py           # Admin configuration
├── leaves/                # Leave management app
│   ├── __init__.py
│   ├── models.py          # LeaveRequest model
│   ├── views.py           # Leave views
│   ├── forms.py           # Leave application form
│   ├── urls.py            # App URLs
│   └── admin.py           # Admin configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── accounts/          # Account templates
│   └── leaves/            # Leave templates
├── static/                # Static files
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Extract the Project

```bash
cd hrms_portal
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Create Admin User

```bash
python manage.py createsuperuser
```

Enter the following when prompted:
- Username: admin (or your preferred username)
- Email: admin@example.com
- Password: (choose a secure password)
- Confirm password

**Important**: After creating the superuser, you need to set the role to 'admin' in the database or through the Django admin panel.

### Step 6: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Usage Guide

### First Time Setup

1. **Access Django Admin**: Go to http://127.0.0.1:8000/admin/
2. **Login with superuser** credentials
3. **Update your user role**: Click on "Users" → Select your user → Set "Role" to "admin" → Save

### Employee Workflow

1. **Register**: Click "Register as Employee" on the landing page
2. **Fill details**: Full name, email, employee ID, department, password
3. **Login**: Use your email and password
4. **Apply Leave**: Go to "Apply Leave" → Fill the form → Submit
5. **Track Status**: Go to "Leave Status" to see all your requests

### Admin Workflow

1. **Login**: Click "Login as Admin" on the landing page
2. **Dashboard**: View overview statistics
3. **Review Requests**: Go to "Leave Requests" → See pending requests
4. **Approve/Reject**: Click Approve or Reject buttons with optional remarks
5. **View Employees**: Go to "Employees" to see all registered employees

## Default Admin Credentials

After running `createsuperuser`, use those credentials to log in as admin.

**Note**: Make sure to set the user's role to 'admin' in the Django admin panel for full admin access.

## Real-time Updates

The system uses AJAX polling for real-time updates:
- **Employee Dashboard**: Updates every 10 seconds
- **Admin Dashboard**: Updates every 5 seconds
- **Leave Status Page**: Updates every 8 seconds

When an employee submits a leave request, the admin sees it instantly. When an admin approves/rejects a request, the employee sees the status change immediately.

## Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **Session-based Authentication**: Secure login system
- **Role-based Access Control**: Decorators protect admin/employee routes
- **Input Validation**: Server-side form validation
- **Password Requirements**: Minimum 8 characters

## Customization

### Changing Colors

Edit `static/css/main.css` and modify the CSS variables in `:root`:

```css
:root {
    --primary-color: #4f46e5;  /* Change this */
    --success-color: #10b981;  /* And this */
    /* etc. */
}
```

### Changing Polling Interval

Edit the JavaScript in the respective templates:

```javascript
// Change the interval time (in milliseconds)
setInterval(updateDashboard, 10000);  // Default: 10 seconds
```

## Troubleshooting

### Issue: "No module named 'django'"
**Solution**: Make sure you've activated the virtual environment and installed requirements:
```bash
pip install -r requirements.txt
```

### Issue: "Access denied" for admin pages
**Solution**: Make sure your user has `role='admin'` set in the database. Check through Django admin panel.

### Issue: Static files not loading
**Solution**: Run collectstatic:
```bash
python manage.py collectstatic
```

### Issue: Database errors
**Solution**: Delete the database and recreate:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Production Deployment

For production deployment:

1. **Set DEBUG = False** in `hrms_project/settings.py`
2. **Change SECRET_KEY** to a secure random string
3. **Configure ALLOWED_HOSTS** with your domain
4. **Use a production database** (PostgreSQL recommended)
5. **Set up a web server** (Nginx + Gunicorn recommended)
6. **Enable HTTPS** for secure connections
7. **Configure static files** with a CDN or web server

Example production settings:

```python
DEBUG = False
SECRET_KEY = 'your-secure-secret-key-here'
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please refer to the Django documentation:
- https://docs.djangoproject.com/

---

**Built with Django + Vanilla JavaScript**
