"""Create an initial admin account.

Credentials are read from environment variables so that weak defaults are
never baked into the repository. Example:

    ADMIN_EMAIL=admin@example.com \\
    ADMIN_USERNAME=admin \\
    ADMIN_PASSWORD='<strong password>' \\
    python create_admin.py
"""
import os
import sys

from main import app, db, User
from werkzeug.security import generate_password_hash


def create_admin():
    email = os.environ.get('ADMIN_EMAIL')
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')

    if not email or not username or not password:
        sys.stderr.write(
            'ERROR: ADMIN_EMAIL, ADMIN_USERNAME and ADMIN_PASSWORD must be set '
            'in the environment. Refusing to create an admin with default '
            'credentials.\n'
        )
        sys.exit(1)

    if len(password) < 12:
        sys.stderr.write(
            'ERROR: ADMIN_PASSWORD must be at least 12 characters.\n'
        )
        sys.exit(1)

    with app.app_context():
        admin = User.query.filter_by(email=email).first()
        if not admin:
            admin = User(
                email=email,
                username=username,
                password_hash=generate_password_hash(password),
                role='admin',
            )
            db.session.add(admin)
            db.session.commit()
            print(f'Admin user created: {email}')
        else:
            print('Admin user already exists.')


if __name__ == '__main__':
    create_admin()
