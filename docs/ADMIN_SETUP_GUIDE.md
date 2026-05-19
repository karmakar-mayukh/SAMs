# Admin Setup and Management Guide

This document provides comprehensive information about setting up and managing administrative access for the Stock Analysis & Market Sentiment System.

## Table of Contents
- [Admin User Creation](#admin-user-creation)
- [Default Admin Credentials](#default-admin-credentials)
- [Admin Dashboard Features](#admin-dashboard-features)
- [User Management](#user-management)
- [System Configuration](#system-configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Admin User Creation

### Automatic Setup
The system includes an automated admin user creation script:

```bash
# On Windows:
.\venv\Scripts\python create_admin.py

# On Mac/Linux:
python3 create_admin.py
```

This script will:
- Check if an admin user already exists
- Create a default admin account if none exists
- Display confirmation messages

### Manual Admin Creation
If you need to create additional admin users or modify existing ones, you can do so programmatically:

```python
from main import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        email='your-admin@example.com',
        username='admin_username',
        password_hash=generate_password_hash('secure_password'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
```

## Default Admin Credentials

After running the setup script, use these credentials to log in:

- **Email**: `admin@example.com`
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

> ⚠️ **Security Warning**: Change the default password immediately after first login for security purposes.

## Admin Dashboard Features

The admin dashboard (`/admin`) provides comprehensive system management capabilities:

### System Statistics
- Total user count
- Active broker count
- Transaction volume
- Company listings count
- Invoice and report counts
- System uptime and performance metrics

### User Management
- View all registered users
- Monitor user activity
- Access user account details

### Broker Management
- Add new brokers with commission rates
- Configure commission percentages
- Enable/disable broker accounts
- View broker performance statistics

### Transaction Monitoring
- Real-time transaction feed
- Transaction type analysis
- Commission tracking
- Volume statistics by symbol

### Data Management
- Upload CSV datasets for analysis
- Delete outdated datasets
- Monitor dataset storage

## User Management

### Role-Based Access Control
The system implements role-based permissions:

- **user**: Standard user with portfolio management access
- **admin**: Full system administration privileges

### Admin Permissions
Admin users have access to:
- User account management
- System configuration
- Broker setup and management
- Transaction monitoring
- Dataset management
- System statistics and analytics

## System Configuration

### Environment Variables
Configure the following environment variables for production:

```bash
export SECRET_KEY='your-secret-key-here'
export DATABASE_URL='sqlite:///production.db'
export FLASK_ENV='production'
```

### Database Configuration
The system uses SQLite by default. For production deployments, consider PostgreSQL:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
```

### Logging Configuration
Admin actions are logged to `logs/app.log` with the following levels:
- INFO: General operations
- WARNING: Security events
- ERROR: System errors

## Security Considerations

### Password Policy
- Enforce strong passwords for admin accounts
- Implement password expiration policies
- Enable two-factor authentication (if implemented)

### Session Security
- Admin sessions timeout appropriately
- CSRF protection enabled on all forms
- Secure cookie settings configured

### Access Control
- Admin routes protected with `@login_required(role='admin')`
- Role verification on all admin operations
- Audit logging for sensitive actions

## Troubleshooting

### Admin Login Issues
- Verify admin user exists in database
- Check password hash integrity
- Review application logs for authentication errors

### Permission Errors
- Confirm user has 'admin' role assigned
- Check session variables after login
- Verify route decorators are properly applied

### Database Issues
- Ensure database file exists and is writable
- Check SQLAlchemy connection string
- Verify table schema matches model definitions

### Performance Issues
- Monitor request latency in admin dashboard
- Check log files for performance bottlenecks
- Review database query efficiency

## API Endpoints

Admin functionality is accessible via these endpoints:

- `/admin` - Main admin dashboard
- `/admin/brokers` - Broker management (POST)
- `/admin/datasets` - Dataset listing (JSON)
- `/admin/datasets/upload` - Dataset upload (POST)
- `/admin/datasets/delete` - Dataset deletion (POST)

## Best Practices

1. **Regular Backups**: Backup the database regularly
2. **Monitor Logs**: Review application logs for security events
3. **Update Credentials**: Change default admin password immediately
4. **Limit Admin Access**: Only grant admin privileges to trusted users
5. **Secure Configuration**: Use environment variables for sensitive data
6. **Monitor Performance**: Regularly check system metrics

## Support

For additional assistance with admin setup or configuration, refer to:
- Main README.md for general setup instructions
- System logs for troubleshooting
- Database schema documentation for advanced configuration</content>
<parameter name="filePath">C:\docs\intelligent-stock-prediction-forked\docs\ADMIN_SETUP_GUIDE.md