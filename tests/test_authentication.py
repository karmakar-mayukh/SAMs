"""
Phase 2: Unit Tests for Authentication & Authorization

Tests for user registration, login, logout, and role-based access control.
"""

import pytest
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from main import db, User


class TestUserRegistration:
    """Test cases for user registration."""
    
    def test_registration_GET_request(self, client):
        """Test GET request to registration page."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'sign up' in response.data.lower()
    
    def test_successful_registration(self, client, test_db):
        """Test successful user registration."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!'
        }
        response = client.post('/register', data=data, follow_redirects=True)
        
        assert response.status_code == 200
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.role == 'user'
        assert check_password_hash(user.password_hash, 'SecurePass123!')
    
    def test_registration_password_mismatch(self, client, test_db):
        """Test registration with mismatched passwords."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Pass123!',
            'confirm_password': 'DifferentPass123!'
        }
        response = client.post('/register', data=data, follow_redirects=True)
        
        assert b'do not match' in response.data.lower() or b'passwords must match' in response.data.lower()
        user = User.query.filter_by(email='test@example.com').first()
        assert user is None
    
    def test_registration_duplicate_email(self, client, test_db, sample_user):
        """Test registration with duplicate email."""
        data = {
            'email': sample_user.email,
            'username': 'differentuser',
            'password': 'Pass123!',
            'confirm_password': 'Pass123!'
        }
        response = client.post('/register', data=data, follow_redirects=True)
        
        assert b'already' in response.data.lower()
        users = User.query.filter_by(email=sample_user.email).all()
        assert len(users) == 1
    
    def test_registration_duplicate_username(self, client, test_db, sample_user):
        """Test registration with duplicate username."""
        data = {
            'email': 'different@example.com',
            'username': sample_user.username,
            'password': 'Pass123!',
            'confirm_password': 'Pass123!'
        }
        response = client.post('/register', data=data, follow_redirects=True)
        
        assert b'already' in response.data.lower()
        users = User.query.filter_by(username=sample_user.username).all()
        assert len(users) == 1
    
    def test_registration_missing_fields(self, client, test_db):
        """Test registration with missing required fields."""
        data = {
            'email': '',
            'username': 'testuser',
            'password': 'Pass123!',
            'confirm_password': 'Pass123!'
        }
        response = client.post('/register', data=data, follow_redirects=True)
        
        assert b'required' in response.data.lower() or b'field' in response.data.lower()
        user = User.query.filter_by(username='testuser').first()
        assert user is None


class TestUserLogin:
    """Test cases for user login."""
    
    def test_login_GET_request(self, client):
        """Test GET request to login page."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'sign in' in response.data.lower()
    
    def test_successful_login(self, client, test_db, sample_user):
        """Test successful login with valid credentials."""
        data = {
            'email': sample_user.email,
            'password': 'TestPass123!'
        }
        response = client.post('/login', data=data, follow_redirects=True)
        
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get('user_id') == sample_user.id
            assert sess.get('user_role') == sample_user.role
    
    def test_login_invalid_password(self, client, test_db, sample_user):
        """Test login with invalid password."""
        data = {
            'email': sample_user.email,
            'password': 'WrongPassword123!'
        }
        response = client.post('/login', data=data, follow_redirects=True)
        
        assert b'invalid' in response.data.lower() or b'incorrect' in response.data.lower()
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
    
    def test_login_nonexistent_user(self, client, test_db):
        """Test login with non-existent email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePass123!'
        }
        response = client.post('/login', data=data, follow_redirects=True)
        
        assert b'invalid' in response.data.lower() or b'not found' in response.data.lower()
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
    
    def test_login_inactive_user(self, client, test_db, sample_user):
        """Test login with inactive user account."""
        sample_user.is_active = False
        test_db.session.commit()
        
        data = {
            'email': sample_user.email,
            'password': 'TestPass123!'
        }
        response = client.post('/login', data=data, follow_redirects=True)
        
        assert b'invalid' in response.data.lower() or b'inactive' in response.data.lower()
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
    
    def test_login_updates_last_login(self, client, test_db, sample_user):
        """Test that login updates last_login_at timestamp."""
        original_last_login = sample_user.last_login_at
        
        data = {
            'email': sample_user.email,
            'password': 'TestPass123!'
        }
        client.post('/login', data=data, follow_redirects=True)
        
        test_db.session.refresh(sample_user)
        assert sample_user.last_login_at is not None
        assert sample_user.last_login_at != original_last_login


class TestUserLogout:
    """Test cases for user logout."""
    
    def test_logout_clears_session(self, authenticated_client, sample_user):
        """Test that logout clears the session."""
        # Verify user is logged in
        with authenticated_client.session_transaction() as sess:
            assert sess.get('user_id') == sample_user.id
        
        # Logout
        response = authenticated_client.get('/logout', follow_redirects=True)
        
        # Verify session is cleared
        with authenticated_client.session_transaction() as sess:
            assert sess.get('user_id') is None
            assert sess.get('user_role') is None
    
    def test_logout_redirects_to_index(self, authenticated_client):
        """Test that logout redirects to index page."""
        response = authenticated_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302  # Redirect
        assert '/' in response.location or 'index' in response.location


class TestCSRFProtection:
    """Test cases for CSRF token validation."""
    
    def test_csrf_token_generation(self, client):
        """Test that CSRF token is generated."""
        with client.session_transaction() as sess:
            from main import generate_csrf_token
            token = generate_csrf_token()
            assert token is not None
            assert len(token) > 0
    
    def test_csrf_token_in_session(self, client):
        """Test CSRF token is stored in session."""
        with client.session_transaction() as sess:
            from main import generate_csrf_token
            token = generate_csrf_token()
            assert sess.get('csrf_token') == token


class TestRoleBasedAccessControl:
    """Test cases for role-based access control."""
    
    def test_user_cannot_access_admin_dashboard(self, authenticated_client, sample_user):
        """Test that regular users cannot access admin dashboard."""
        response = authenticated_client.get('/admin')
        assert response.status_code in [302, 403]  # Redirect or Forbidden
    
    def test_admin_can_access_admin_dashboard(self, admin_client, sample_admin):
        """Test that admin users can access admin dashboard."""
        response = admin_client.get('/admin')
        assert response.status_code == 200
    
    def test_unauthenticated_user_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location.lower()
    
    def test_login_required_decorator(self, client):
        """Test that login_required decorator works."""
        # Try to access protected routes without authentication
        protected_routes = ['/dashboard', '/trade/buy', '/trade/sell', '/funds/topup']
        
        for route in protected_routes:
            response = client.get(route, follow_redirects=False)
            assert response.status_code in [302, 401, 405]  # Redirect, Unauthorized, or Method Not Allowed
    
    def test_admin_only_routes(self, authenticated_client, sample_user):
        """Test that admin-only routes are protected."""
        admin_routes = ['/admin', '/admin/brokers', '/admin/companies']
        
        for route in admin_routes:
            response = authenticated_client.get(route, follow_redirects=False)
            # Should be redirected or forbidden for non-admin users
            assert response.status_code in [302, 403]


class TestSessionManagement:
    """Test cases for session management."""
    
    def test_session_created_on_login(self, client, test_db, sample_user):
        """Test that session is created on successful login."""
        data = {
            'email': sample_user.email,
            'password': 'TestPass123!'
        }
        client.post('/login', data=data, follow_redirects=True)
        
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'user_role' in sess
    
    def test_session_persists_across_requests(self, authenticated_client, sample_user):
        """Test that session persists across multiple requests."""
        # First request
        response1 = authenticated_client.get('/dashboard')
        with authenticated_client.session_transaction() as sess:
            user_id_1 = sess.get('user_id')
        
        # Second request
        response2 = authenticated_client.get('/dashboard')
        with authenticated_client.session_transaction() as sess:
            user_id_2 = sess.get('user_id')
        
        assert user_id_1 == user_id_2 == sample_user.id
    
    def test_session_cleared_on_logout(self, authenticated_client):
        """Test that all session data is cleared on logout."""
        authenticated_client.get('/logout')
        
        with authenticated_client.session_transaction() as sess:
            assert len(sess.keys()) == 0 or 'user_id' not in sess


class TestPasswordSecurity:
    """Test cases for password security."""
    
    def test_password_is_hashed(self, test_db):
        """Test that passwords are stored as hashes, not plain text."""
        password = 'SecurePassword123!'
        user = User(
            email='test@example.com',
            username='testuser',
            password_hash=generate_password_hash(password),
            role='user'
        )
        test_db.session.add(user)
        test_db.session.commit()
        
        # Password hash should not equal plain text password
        assert user.password_hash != password
        # Hash should be long (bcrypt hashes are 60 characters)
        assert len(user.password_hash) >= 50
    
    def test_same_password_different_hashes(self, test_db):
        """Test that same password generates different hashes (salt)."""
        password = 'SamePassword123!'
        
        user1 = User(
            email='user1@example.com',
            username='user1',
            password_hash=generate_password_hash(password),
            role='user'
        )
        user2 = User(
            email='user2@example.com',
            username='user2',
            password_hash=generate_password_hash(password),
            role='user'
        )
        
        test_db.session.add_all([user1, user2])
        test_db.session.commit()
        
        # Different hashes due to salting
        assert user1.password_hash != user2.password_hash
        # But both should verify correctly
        assert user1.check_password(password)
        assert user2.check_password(password)
