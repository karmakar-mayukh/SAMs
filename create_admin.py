"""
Admin bootstrap script.

Credentials MUST be supplied via environment variables. Using hard-coded
defaults in source (the original ``admin@example.com`` / ``admin123`` pair) is
a critical security risk, especially since the database file is typically
committed or persisted with the application.
"""
import os
import sys

from main import app, db, User
from werkzeug.security import generate_password_hash


def create_admin():
    email = os.environ.get('ADMIN_EMAIL')
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')

    missing = [name for name, value in (
        ('ADMIN_EMAIL', email),
        ('ADMIN_USERNAME', username),
        ('ADMIN_PASSWORD', password),
    ) if not value]
    if missing:
        sys.stderr.write(
            "Refusing to create admin account. The following environment "
            f"variables must be set: {', '.join(missing)}.\n"
        )
        sys.exit(1)

    if len(password) < 12:
        sys.stderr.write(
            "ADMIN_PASSWORD must be at least 12 characters long.\n"
        )
        sys.exit(1)

    with app.app_context():
        admin = User.query.filter_by(email=email).first()
        if admin:
            print(f"Admin user already exists: {email}")
            return

        admin = User(
            email=email.strip().lower(),
            username=username.strip(),
            password_hash=generate_password_hash(password),
            role='admin',
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {email}")


if __name__ == '__main__':
    create_admin()
