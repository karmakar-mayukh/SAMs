# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 14:36:49 2019

@author: Kaushik
"""
#**************** IMPORT PACKAGES ********************
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort, Response, g
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import math, random
from datetime import datetime
import datetime as dt
import yfinance as yf
# Replaced Twitter API with free news-based sentiment analysis
# Twitter imports removed - using Finviz + FinVADER instead
import re
from sklearn.linear_model import LinearRegression
from textblob import TextBlob
from news_sentiment import retrieving_news_polarity, finviz_finvader_sentiment
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
from functools import wraps
import secrets
from collections import deque
from logging.handlers import RotatingFileHandler
import logging
import time
from pathlib import Path

# Ignore Warnings
import warnings
warnings.filterwarnings("ignore")
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#***************** FLASK *****************************
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'CHANGE_ME_IN_PRODUCTION')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sams_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
db = SQLAlchemy(app)
APP_START_TIME = datetime.utcnow()
REQUEST_METRICS = {
    'total_requests': 0,
    'total_errors': 0,
    'latency_ms': deque(maxlen=1000),
}


def configure_app_logging(flask_app):
    logs_dir = Path(flask_app.root_path) / 'logs'
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / 'app.log'
    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    if not any(isinstance(h, RotatingFileHandler) for h in flask_app.logger.handlers):
        flask_app.logger.addHandler(file_handler)
    flask_app.logger.setLevel(logging.INFO)
    flask_app.logger.propagate = False


configure_app_logging(app)
LOG_FILE_PATH = Path(app.root_path) / 'logs' / 'app.log'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    wallet_balance = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), unique=True, nullable=False)
    name = db.Column(db.String(255))
    exchange = db.Column(db.String(64))
    sector = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)


class Broker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    commission_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)


class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    average_buy_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('portfolio_items', lazy=True))
    company = db.relationship('Company')


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    txn_type = db.Column(db.String(16), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    broker_id = db.Column(db.Integer, db.ForeignKey('broker.id'))
    commission_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    company = db.relationship('Company')
    broker = db.relationship('Broker')


class Dividend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_item_id = db.Column(db.Integer, db.ForeignKey('portfolio_item.id'), nullable=False)
    amount_per_share = db.Column(db.Numeric(12, 4), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    payable_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    portfolio_item = db.relationship('PortfolioItem', backref=db.backref('dividends', lazy=True))

class NotificationPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    in_app_enabled = db.Column(db.Boolean, nullable=False, default=True)
    trade_notifications = db.Column(db.Boolean, nullable=False, default=True)
    report_notifications = db.Column(db.Boolean, nullable=False, default=True)
    invoice_notifications = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('notification_preference', uselist=False))


class UserNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(32), nullable=False, default='system')
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))


class ReportSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    period_days = db.Column(db.Integer, nullable=False, default=30)
    total_buys = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_sells = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_dividends = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_commissions = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    net_cashflow = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('report_snapshots', lazy=True))


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    transaction_type = db.Column(db.String(16), nullable=False)
    direction = db.Column(db.String(16), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    commission = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    net_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default='issued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('invoices', lazy=True))
    transaction = db.relationship('Transaction', backref=db.backref('invoice', uselist=False))


def generate_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token


def verify_csrf():
    token = session.get('csrf_token')
    form_token = request.form.get('csrf_token')
    if not token or not form_token or token != form_token:
        abort(400)


app.jinja_env.globals['csrf_token'] = generate_csrf_token


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = session.get('user_id')
            user_role = session.get('user_role')
            if not user_id:
                return redirect(url_for('login'))
            if role and user_role != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def get_latest_close_price(symbol):
    end = datetime.now()
    start = end - dt.timedelta(days=10)
    data = yf.download(symbol, start=start, end=end)
    if data.empty:
        return None
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    if len(data) >= 2:
        return float(data['Close'].iloc[-1]), float(data['Close'].iloc[-2])
    else:
        return float(data['Close'].iloc[-1]), float(data['Close'].iloc[-1])


def get_active_broker():
    return Broker.query.filter_by(is_active=True).order_by(Broker.commission_rate.asc()).first()


def calculate_commission(total_amount, broker):
    if not broker:
        return Decimal('0')
    try:
        rate = Decimal(broker.commission_rate) / Decimal('100')
    except Exception:
        return Decimal('0')
    commission = total_amount * rate
    return commission.quantize(Decimal('0.01'))

def get_notification_preferences(user_id):
    return NotificationPreference.query.filter_by(user_id=user_id).first()


def is_notification_enabled(preferences, category):
    if preferences and not preferences.in_app_enabled:
        return False
    if not preferences:
        return True
    if category == 'trade':
        return preferences.trade_notifications
    if category == 'report':
        return preferences.report_notifications
    if category == 'invoice':
        return preferences.invoice_notifications
    return True


def create_user_notification(user_id, category, title, message):
    preferences = get_notification_preferences(user_id)
    if not is_notification_enabled(preferences, category):
        return None
    notification = UserNotification(
        user_id=user_id,
        category=category,
        title=title,
        message=message,
        is_read=False
    )
    db.session.add(notification)
    return notification


def generate_invoice_number():
    while True:
        candidate = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"
        if not Invoice.query.filter_by(invoice_number=candidate).first():
            return candidate


def create_invoice_for_transaction(user_id, transaction):
    existing_invoice = Invoice.query.filter_by(transaction_id=transaction.id).first()
    if existing_invoice:
        return existing_invoice

    subtotal = Decimal(transaction.total_amount or 0).quantize(Decimal('0.01'))
    commission = Decimal(transaction.commission_amount or 0).quantize(Decimal('0.01'))
    transaction_type = transaction.txn_type

    if transaction_type == 'BUY':
        direction = 'DEBIT'
        net_amount = subtotal + commission
    elif transaction_type == 'SELL':
        direction = 'CREDIT'
        net_amount = subtotal - commission
    elif transaction_type == 'DIVIDEND':
        direction = 'CREDIT'
        net_amount = subtotal
    else:
        direction = 'INFO'
        net_amount = subtotal

    invoice = Invoice(
        invoice_number=generate_invoice_number(),
        user_id=user_id,
        transaction_id=transaction.id,
        transaction_type=transaction_type,
        direction=direction,
        subtotal=subtotal,
        commission=commission,
        net_amount=net_amount,
        status='issued'
    )
    db.session.add(invoice)
    return invoice


def build_report_snapshot(user_id, period_days):
    query = Transaction.query.filter_by(user_id=user_id)
    if period_days > 0:
        cutoff = datetime.utcnow() - dt.timedelta(days=period_days)
        query = query.filter(Transaction.created_at >= cutoff)

    transactions = query.all()
    total_buys = Decimal('0')
    total_sells = Decimal('0')
    total_dividends = Decimal('0')
    total_commissions = Decimal('0')

    for txn in transactions:
        amount = Decimal(txn.total_amount or 0)
        commission = Decimal(txn.commission_amount or 0)
        total_commissions += commission

        if txn.txn_type == 'BUY':
            total_buys += amount
        elif txn.txn_type == 'SELL':
            total_sells += amount
        elif txn.txn_type == 'DIVIDEND':
            total_dividends += amount

    net_cashflow = (total_sells + total_dividends) - total_buys - total_commissions

    return {
        'total_buys': total_buys.quantize(Decimal('0.01')),
        'total_sells': total_sells.quantize(Decimal('0.01')),
        'total_dividends': total_dividends.quantize(Decimal('0.01')),
        'total_commissions': total_commissions.quantize(Decimal('0.01')),
        'net_cashflow': net_cashflow.quantize(Decimal('0.01')),
    }


def read_recent_log_entries(limit=20):
    if not LOG_FILE_PATH.exists():
        return []
    try:
        with LOG_FILE_PATH.open('r', encoding='utf-8', errors='ignore') as file_handle:
            lines = file_handle.readlines()
        return [line.strip() for line in lines[-limit:] if line.strip()]
    except Exception:
        return []


with app.app_context():
    db.create_all()

#To control caching so as to save and retrieve plot figs on client side
@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


@app.before_request
def start_request_timer():
    g.request_started_at = time.perf_counter()


@app.after_request
def capture_request_metrics(response):
    start_time = getattr(g, 'request_started_at', None)
    if start_time is not None:
        latency_ms = (time.perf_counter() - start_time) * 1000
        REQUEST_METRICS['latency_ms'].append(latency_ms)
    else:
        latency_ms = 0

    REQUEST_METRICS['total_requests'] += 1
    if response.status_code >= 500:
        REQUEST_METRICS['total_errors'] += 1

    app.logger.info(
        'HTTP %s %s -> %s (%.2f ms)',
        request.method,
        request.path,
        response.status_code,
        latency_ms
    )
    return response


@app.route('/health')
def health():
    uptime_seconds = int((datetime.utcnow() - APP_START_TIME).total_seconds())
    latencies = list(REQUEST_METRICS['latency_ms'])
    avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0
    return {
        'status': 'ok',
        'uptime_seconds': uptime_seconds,
        'total_requests': REQUEST_METRICS['total_requests'],
        'total_errors': REQUEST_METRICS['total_errors'],
        'avg_latency_ms': round(avg_latency_ms, 2)
    }


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        verify_csrf()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not email or not username or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', email=email, username=username)
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', email=email, username=username)
        existing = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing:
            flash('Email or username already registered.', 'danger')
            return render_template('register.html', email=email, username=username)
        password_hash = generate_password_hash(password)
        user = User(email=email, username=username, password_hash=password_hash, role='user')
        db.session.add(user)
        db.session.flush()
        db.session.add(NotificationPreference(user_id=user.id))
        db.session.commit()
        app.logger.info('User registered: %s', email)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        verify_csrf()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password) or not user.is_active:
            app.logger.warning('Invalid login attempt for email: %s', email)
            flash('Invalid credentials.', 'danger')
            return render_template('login.html', email=email)
        session.clear()
        session['user_id'] = user.id
        session['user_role'] = user.role
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        app.logger.info('User logged in: %s', email)
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    app.logger.info('User logged out: %s', session.get('user_id'))
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required()
def dashboard():
    user = get_current_user()
    # Only show items with quantity > 0
    items = PortfolioItem.query.filter_by(user_id=user.id).filter(PortfolioItem.quantity > 0).all()
    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.created_at.desc()).limit(20).all()
    
    # Calculate Current Portfolio Value & Cost of Held
    current_portfolio_value = Decimal('0')
    cost_of_held = Decimal('0')
    
    for item in items:
        # Fetch live price
        price_data = get_latest_close_price(item.company.symbol)
        
        item.diff = Decimal('0')
        item.percent_change = Decimal('0')
        item.change_direction = None
        
        if price_data:
            live_price = price_data[0]
            current_price = Decimal(str(live_price))
            
            # Calculate difference vs Average Buy Price
            diff = current_price - item.average_buy_price
            item.diff = diff
            
            if item.average_buy_price > 0:
                item.percent_change = (diff / item.average_buy_price) * 100
            
            if diff > 0:
                item.change_direction = 'up'
            elif diff < 0:
                item.change_direction = 'down'
        else:
            current_price = item.average_buy_price
        
        # Attach current price to the item for the template
        item.current_price = current_price
        
        item_qty = Decimal(item.quantity)
        current_portfolio_value += current_price * item_qty
        cost_of_held += item.average_buy_price * item_qty

    # Calculate Realized Profit
    # Formula: (Total Sells + Total Dividends - Commissions) - (Total Buys - Cost of Held)
    
    # Get aggregates from DB for efficiency, or loop if volume is low. 
    # Since we need precise sums for the user, a query is better but we can iterate if we want to be safe with types.
    # Given the likely small scale, a query is cleaner.
    
    all_txns = Transaction.query.filter_by(user_id=user.id).all()
    total_buys = Decimal('0')
    total_sells = Decimal('0')
    total_dividends = Decimal('0')
    total_commissions = Decimal('0')
    
    for t in all_txns:
        amt = t.total_amount if t.total_amount is not None else Decimal('0')
        comm = t.commission_amount if t.commission_amount is not None else Decimal('0')
        
        total_commissions += comm
        
        if t.txn_type == 'BUY':
            total_buys += amt
        elif t.txn_type == 'SELL':
            total_sells += amt
        elif t.txn_type == 'DIVIDEND':
            total_dividends += amt
            
    cost_of_sold = total_buys - cost_of_held
    realized_profit = (total_sells + total_dividends) - cost_of_sold - total_commissions
    notification_preferences = get_notification_preferences(user.id)
    if not notification_preferences:
        notification_preferences = NotificationPreference(
            user_id=user.id,
            in_app_enabled=True,
            trade_notifications=True,
            report_notifications=True,
            invoice_notifications=True
        )
    recent_notifications = UserNotification.query.filter_by(user_id=user.id).order_by(UserNotification.created_at.desc()).limit(10).all()
    recent_reports = ReportSnapshot.query.filter_by(user_id=user.id).order_by(ReportSnapshot.generated_at.desc()).limit(10).all()
    latest_report = recent_reports[0] if recent_reports else None
    recent_invoices = Invoice.query.filter_by(user_id=user.id).order_by(Invoice.created_at.desc()).limit(10).all()

    return render_template('dashboard.html', user=user, items=items, transactions=transactions,
                           current_portfolio_value=current_portfolio_value,
                           realized_profit=realized_profit,
                           notification_preferences=notification_preferences,
                           recent_notifications=recent_notifications,
                           recent_reports=recent_reports,
                           latest_report=latest_report,
                           recent_invoices=recent_invoices)

@app.route('/settings/notifications', methods=['POST'])
@login_required()
def update_notification_settings():
    verify_csrf()
    user = get_current_user()
    preferences = NotificationPreference.query.filter_by(user_id=user.id).first()
    if not preferences:
        preferences = NotificationPreference(user_id=user.id)
        db.session.add(preferences)

    preferences.in_app_enabled = request.form.get('in_app_enabled') == 'on'
    preferences.trade_notifications = request.form.get('trade_notifications') == 'on'
    preferences.report_notifications = request.form.get('report_notifications') == 'on'
    preferences.invoice_notifications = request.form.get('invoice_notifications') == 'on'

    db.session.commit()
    app.logger.info('Notification settings updated for user_id=%s', user.id)
    flash('Notification settings updated.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/reports/generate', methods=['POST'])
@login_required()
def generate_report():
    verify_csrf()
    user = get_current_user()
    allowed_periods = {0, 7, 30, 90, 365}
    try:
        period_days = int(request.form.get('period_days', '30').strip())
    except Exception:
        period_days = 30

    if period_days not in allowed_periods:
        period_days = 30

    snapshot = build_report_snapshot(user.id, period_days)
    report_snapshot = ReportSnapshot(
        user_id=user.id,
        period_days=period_days,
        total_buys=snapshot['total_buys'],
        total_sells=snapshot['total_sells'],
        total_dividends=snapshot['total_dividends'],
        total_commissions=snapshot['total_commissions'],
        net_cashflow=snapshot['net_cashflow'],
    )
    db.session.add(report_snapshot)

    period_label = 'All time' if period_days == 0 else f'Last {period_days} days'
    create_user_notification(
        user.id,
        'report',
        'Portfolio report generated',
        f'Report generated for {period_label}.'
    )
    db.session.commit()
    app.logger.info('Report generated for user_id=%s period_days=%s', user.id, period_days)
    flash(f'Report generated for {period_label}.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required()
def mark_notification_read(notification_id):
    verify_csrf()
    user = get_current_user()
    notification = UserNotification.query.filter_by(id=notification_id, user_id=user.id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/invoices/<int:invoice_id>/download')
@login_required()
def download_invoice(invoice_id):
    user = get_current_user()
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user.id).first()
    if not invoice:
        abort(404)

    transaction = invoice.transaction
    company_symbol = transaction.company.symbol if transaction and transaction.company else '-'
    broker_name = transaction.broker.name if transaction and transaction.broker else 'N/A'
    created_at = invoice.created_at.strftime('%Y-%m-%d %H:%M:%S') if invoice.created_at else '-'
    transaction_time = transaction.created_at.strftime('%Y-%m-%d %H:%M:%S') if transaction and transaction.created_at else '-'

    invoice_content = '\n'.join([
        f'Invoice Number: {invoice.invoice_number}',
        f'Issued At: {created_at} UTC',
        f'User: {user.username} ({user.email})',
        f'Transaction ID: {invoice.transaction_id}',
        f'Transaction Type: {invoice.transaction_type}',
        f'Cash Direction: {invoice.direction}',
        f'Symbol: {company_symbol}',
        f'Broker: {broker_name}',
        f'Transaction Timestamp: {transaction_time} UTC',
        f'Subtotal: {invoice.subtotal}',
        f'Commission: {invoice.commission}',
        f'Net Amount: {invoice.net_amount}',
        f'Status: {invoice.status}',
    ])

    response = Response(invoice_content, mimetype='text/plain; charset=utf-8')
    response.headers['Content-Disposition'] = f'attachment; filename={invoice.invoice_number}.txt'
    return response


@app.route('/trade/buy', methods=['POST'])
@login_required()
def trade_buy():
    verify_csrf()
    user = get_current_user()
    symbol = request.form.get('symbol', '').strip().upper()
    quantity_raw = request.form.get('quantity', '0').strip()
    try:
        quantity = int(quantity_raw)
    except ValueError:
        flash('Quantity must be an integer.', 'danger')
        return redirect(url_for('dashboard'))
    if quantity <= 0:
        flash('Quantity must be greater than zero.', 'danger')
        return redirect(url_for('dashboard'))
    if not symbol:
        flash('Symbol is required.', 'danger')
        return redirect(url_for('dashboard'))
    price_data = get_latest_close_price(symbol)
    if price_data is None:
        flash('Unable to fetch latest price for symbol.', 'danger')
        return redirect(url_for('dashboard'))
    price = price_data[0]
    total = Decimal(str(price)) * Decimal(quantity)
    broker = get_active_broker()
    commission = calculate_commission(total, broker)
    if user.wallet_balance < total + commission:
        flash('Insufficient wallet balance to complete this purchase.', 'balance_error')
        return redirect(url_for('dashboard'))
    company = Company.query.filter_by(symbol=symbol).first()
    if not company:
        company = Company(symbol=symbol, name=symbol)
        db.session.add(company)
        db.session.flush()
    item = PortfolioItem.query.filter_by(user_id=user.id, company_id=company.id).first()
    if item:
        current_total = Decimal(item.average_buy_price) * Decimal(item.quantity)
        new_total = current_total + total
        new_quantity = item.quantity + quantity
        item.average_buy_price = new_total / Decimal(new_quantity)
        item.quantity = new_quantity
    else:
        item = PortfolioItem(user_id=user.id, company_id=company.id, quantity=quantity,
                             average_buy_price=total / Decimal(quantity))
        db.session.add(item)
    user.wallet_balance = user.wallet_balance - (total + commission)
    if broker and commission > 0:
        description = f'Simulated buy order via {broker.name} ({broker.commission_rate}% commission)'
    else:
        description = 'Simulated buy order'
    txn = Transaction(user_id=user.id, company_id=company.id, txn_type='BUY', quantity=quantity,
                      price=Decimal(str(price)), total_amount=total,
                      commission_amount=commission, broker_id=broker.id if broker else None,
                      description=description)
    db.session.add(txn)
    db.session.flush()
    invoice = create_invoice_for_transaction(user.id, txn)
    create_user_notification(
        user.id,
        'trade',
        'Buy order executed',
        f'Bought {quantity} share(s) of {symbol} at {Decimal(str(price)).quantize(Decimal("0.01"))}.'
    )
    if invoice:
        create_user_notification(
            user.id,
            'invoice',
            'Invoice issued',
            f'Invoice {invoice.invoice_number} was generated for your BUY transaction.'
        )
    db.session.commit()
    app.logger.info(
        'BUY executed user_id=%s symbol=%s quantity=%s total=%s commission=%s',
        user.id,
        symbol,
        quantity,
        total,
        commission
    )
    flash('Buy order executed in simulated portfolio.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/trade/sell', methods=['POST'])
@login_required()
def trade_sell():
    verify_csrf()
    user = get_current_user()
    symbol = request.form.get('symbol', '').strip().upper()
    quantity_raw = request.form.get('quantity', '0').strip()
    try:
        quantity = int(quantity_raw)
    except ValueError:
        flash('Quantity must be an integer.', 'danger')
        return redirect(url_for('dashboard'))
    if quantity <= 0:
        flash('Quantity must be greater than zero.', 'danger')
        return redirect(url_for('dashboard'))
    if not symbol:
        flash('Symbol is required.', 'danger')
        return redirect(url_for('dashboard'))
    company = Company.query.filter_by(symbol=symbol).first()
    if not company:
        flash('No holdings for this symbol.', 'danger')
        return redirect(url_for('dashboard'))
    item = PortfolioItem.query.filter_by(user_id=user.id, company_id=company.id).first()
    if not item or item.quantity < quantity:
        flash('Not enough shares to sell.', 'danger')
        return redirect(url_for('dashboard'))
    price_data = get_latest_close_price(symbol)
    if price_data is None:
        flash('Unable to fetch latest price for symbol.', 'danger')
        return redirect(url_for('dashboard'))
    price = price_data[0]
    total = Decimal(str(price)) * Decimal(quantity)
    broker = get_active_broker()
    commission = calculate_commission(total, broker)
    item.quantity = item.quantity - quantity
    # Do not delete the item even if quantity is 0, to preserve dividend history
    user.wallet_balance = user.wallet_balance + (total - commission)
    if broker and commission > 0:
        description = f'Simulated sell order via {broker.name} ({broker.commission_rate}% commission)'
    else:
        description = 'Simulated sell order'
    txn = Transaction(user_id=user.id, company_id=company.id, txn_type='SELL', quantity=quantity,
                      price=Decimal(str(price)), total_amount=total,
                      commission_amount=commission, broker_id=broker.id if broker else None,
                      description=description)
    db.session.add(txn)
    db.session.flush()
    invoice = create_invoice_for_transaction(user.id, txn)
    create_user_notification(
        user.id,
        'trade',
        'Sell order executed',
        f'Sold {quantity} share(s) of {symbol} at {Decimal(str(price)).quantize(Decimal("0.01"))}.'
    )
    if invoice:
        create_user_notification(
            user.id,
            'invoice',
            'Invoice issued',
            f'Invoice {invoice.invoice_number} was generated for your SELL transaction.'
        )
    db.session.commit()
    app.logger.info(
        'SELL executed user_id=%s symbol=%s quantity=%s total=%s commission=%s',
        user.id,
        symbol,
        quantity,
        total,
        commission
    )
    flash('Sell order executed in simulated portfolio.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/funds/topup', methods=['POST'])
@login_required()
def funds_topup():
    verify_csrf()
    user = get_current_user()
    amount_raw = request.form.get('amount', '0').strip()
    try:
        amount = Decimal(amount_raw)
    except Exception:
        flash('Invalid amount.', 'danger')
        return redirect(url_for('dashboard'))
    if amount <= 0:
        flash('Amount must be greater than zero.', 'danger')
        return redirect(url_for('dashboard'))
    user.wallet_balance = user.wallet_balance + amount
    create_user_notification(
        user.id,
        'system',
        'Wallet top-up recorded',
        f'Wallet credited by {amount.quantize(Decimal("0.01"))}.'
    )
    db.session.commit()
    app.logger.info('Wallet top-up user_id=%s amount=%s', user.id, amount)
    flash('Wallet balance updated for simulation.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dividends/record', methods=['POST'])
@login_required()
def record_dividend():
    verify_csrf()
    user = get_current_user()
    symbol = request.form.get('symbol', '').strip().upper()
    amount_per_share_raw = request.form.get('amount_per_share', '0').strip()
    try:
        amount_per_share = Decimal(amount_per_share_raw)
    except Exception:
        flash('Invalid dividend amount.', 'danger')
        return redirect(url_for('dashboard'))
    if amount_per_share <= 0:
        flash('Dividend amount must be greater than zero.', 'danger')
        return redirect(url_for('dashboard'))
    company = Company.query.filter_by(symbol=symbol).first()
    if not company:
        flash('No holdings for this symbol.', 'danger')
        return redirect(url_for('dashboard'))
    item = PortfolioItem.query.filter_by(user_id=user.id, company_id=company.id).first()
    if not item or item.quantity <= 0:
        flash('No holdings for this symbol.', 'danger')
        return redirect(url_for('dashboard'))
    total_amount = amount_per_share * Decimal(item.quantity)
    dividend = Dividend(portfolio_item_id=item.id, amount_per_share=amount_per_share,
                        total_amount=total_amount)
    user.wallet_balance = user.wallet_balance + total_amount
    txn = Transaction(user_id=user.id, company_id=company.id, txn_type='DIVIDEND', quantity=item.quantity,
                      price=amount_per_share, total_amount=total_amount,
                      commission_amount=Decimal('0'), broker_id=None,
                      description='Dividend payout recorded')
    db.session.add(dividend)
    db.session.add(txn)
    db.session.flush()
    invoice = create_invoice_for_transaction(user.id, txn)
    create_user_notification(
        user.id,
        'trade',
        'Dividend recorded',
        f'Dividend payout recorded for {symbol}: {total_amount.quantize(Decimal("0.01"))}.'
    )
    if invoice:
        create_user_notification(
            user.id,
            'invoice',
            'Invoice issued',
            f'Invoice {invoice.invoice_number} was generated for your DIVIDEND transaction.'
        )
    db.session.commit()
    app.logger.info(
        'DIVIDEND recorded user_id=%s symbol=%s quantity=%s total=%s',
        user.id,
        symbol,
        item.quantity,
        total_amount
    )
    flash('Dividend recorded and wallet credited.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    user_count = User.query.count()
    broker_count = Broker.query.count()
    transaction_count = Transaction.query.count()
    company_count = Company.query.count()
    invoice_count = Invoice.query.count()
    report_count = ReportSnapshot.query.count()
    notification_count = UserNotification.query.count()
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(25).all()
    brokers = Broker.query.order_by(Broker.name.asc()).all()
    companies = Company.query.order_by(Company.symbol.asc()).all()

    all_transactions = Transaction.query.all()
    total_commission = Decimal('0')
    total_volume = 0
    txn_type_counts = {}
    symbol_totals = {}
    for t in all_transactions:
        if t.commission_amount is not None:
            total_commission += Decimal(t.commission_amount)
        if t.txn_type in ('BUY', 'SELL'):
            total_volume += t.quantity
        txn_type_counts[t.txn_type] = txn_type_counts.get(t.txn_type, 0) + 1
        symbol = t.company.symbol if t.company else None
        if symbol:
            data = symbol_totals.setdefault(symbol, {'quantity': 0, 'value': Decimal('0')})
            data['quantity'] += t.quantity
            if t.total_amount is not None:
                data['value'] += Decimal(t.total_amount)

    txn_type_labels = list(txn_type_counts.keys())
    txn_type_values = list(txn_type_counts.values())

    top_symbols_sorted = sorted(symbol_totals.items(), key=lambda kv: kv[1]['value'], reverse=True)[:5]
    top_symbol_labels = [s for s, _ in top_symbols_sorted]
    top_symbol_values = [float(stats['value']) for _, stats in top_symbols_sorted]
    uptime_seconds = int((datetime.utcnow() - APP_START_TIME).total_seconds())
    latencies = list(REQUEST_METRICS['latency_ms'])
    avg_latency_ms = (sum(latencies) / len(latencies)) if latencies else 0
    recent_logs = read_recent_log_entries(limit=20)
    datasets = _list_datasets()

    return render_template(
        'admin_dashboard.html',
        user_count=user_count,
        broker_count=broker_count,
        transaction_count=transaction_count,
        company_count=company_count,
        invoice_count=invoice_count,
        report_count=report_count,
        notification_count=notification_count,
        total_commission=total_commission,
        total_volume=total_volume,
        recent_transactions=recent_transactions,
        brokers=brokers,
        txn_type_labels=txn_type_labels,
        txn_type_values=txn_type_values,
        top_symbol_labels=top_symbol_labels,
        top_symbol_values=top_symbol_values,
        companies=companies,
        uptime_seconds=uptime_seconds,
        total_requests=REQUEST_METRICS['total_requests'],
        total_errors=REQUEST_METRICS['total_errors'],
        avg_latency_ms=avg_latency_ms,
        recent_logs=recent_logs,
        datasets=datasets,
    )


@app.route('/admin/brokers', methods=['POST'])
@login_required(role='admin')
def admin_add_broker():
    verify_csrf()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    commission_raw = request.form.get('commission_rate', '0').strip()
    if not name:
        flash('Broker name is required.', 'danger')
        return redirect(url_for('admin_dashboard'))
    try:
        commission = Decimal(commission_raw)
    except Exception:
        flash('Invalid commission rate.', 'danger')
        return redirect(url_for('admin_dashboard'))
    if commission < 0:
        flash('Commission rate cannot be negative.', 'danger')
        return redirect(url_for('admin_dashboard'))
    broker = Broker(name=name, email=email or None, commission_rate=commission)
    db.session.add(broker)
    db.session.commit()
    app.logger.info('Broker added by admin user_id=%s broker_name=%s', session.get('user_id'), name)
    flash('Broker added.', 'success')
    return redirect(url_for('admin_dashboard'))




import glob

DATASET_DIR = Path(app.root_path)
ALLOWED_TICKER_EXTENSIONS = {'.csv'}


def _list_datasets():
    """Return a list of dicts describing each CSV dataset in the app root."""
    datasets = []
    for csv_path in sorted(DATASET_DIR.glob('*.csv')):
        stat = csv_path.stat()
        datasets.append({
            'name': csv_path.name,
            'size_kb': round(stat.st_size / 1024, 1),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
        })
    return datasets


@app.route('/admin/datasets')
@login_required(role='admin')
def admin_datasets():
    """JSON endpoint: list all CSV datasets."""
    return {'datasets': _list_datasets()}


@app.route('/admin/datasets/upload', methods=['POST'])
@login_required(role='admin')
def admin_upload_dataset():
    verify_csrf()
    if 'dataset_file' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('admin_dashboard'))
    file = request.files['dataset_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('admin_dashboard'))
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_TICKER_EXTENSIONS:
        flash('Only .csv files are allowed.', 'danger')
        return redirect(url_for('admin_dashboard'))
    # Sanitise filename: keep only alphanumeric, dots, underscores, hyphens
    safe_name = re.sub(r'[^A-Za-z0-9._\-]', '', file.filename)
    if not safe_name:
        flash('Invalid filename.', 'danger')
        return redirect(url_for('admin_dashboard'))
    dest = DATASET_DIR / safe_name
    file.save(str(dest))
    app.logger.info('Admin uploaded dataset %s (user_id=%s)', safe_name, session.get('user_id'))
    flash(f'Dataset "{safe_name}" uploaded successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/datasets/delete', methods=['POST'])
@login_required(role='admin')
def admin_delete_dataset():
    verify_csrf()
    filename = request.form.get('filename', '').strip()
    if not filename:
        flash('No filename provided.', 'danger')
        return redirect(url_for('admin_dashboard'))
    # Prevent path traversal
    safe_name = Path(filename).name
    if Path(safe_name).suffix.lower() not in ALLOWED_TICKER_EXTENSIONS:
        flash('Only .csv datasets can be deleted.', 'danger')
        return redirect(url_for('admin_dashboard'))
    target = DATASET_DIR / safe_name
    if not target.exists():
        flash(f'Dataset "{safe_name}" not found.', 'warning')
        return redirect(url_for('admin_dashboard'))
    target.unlink()
    app.logger.info('Admin deleted dataset %s (user_id=%s)', safe_name, session.get('user_id'))
    flash(f'Dataset "{safe_name}" deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/predict',methods = ['POST'])
def predict():
    nm = request.form['nm']
    prediction_mode = request.form.get('prediction_mode', 'close').strip().lower()
    if prediction_mode not in ('close', 'volume'):
        prediction_mode = 'close'

    #**************** FUNCTIONS TO FETCH DATA ***************************
    def get_historical(quote):
        import time, os
        quote = quote.upper()
        filename = f'{quote}.csv'
        
        # 1. Reuse local data if it's up-to-date (updated today)
        if os.path.exists(filename):
            try:
                df_temp = pd.read_csv(filename)
                if not df_temp.empty and 'Date' in df_temp.columns:
                    last_date = pd.to_datetime(df_temp['Date'].iloc[-1]).date()
                    if last_date >= datetime.now().date():
                        print(f"DEBUG: Reusing local up-to-date data for {quote}")
                        return
                    # If file exists but is old, we'll proceed to update it
                    print(f"DEBUG: Local data for {quote} is outdated (Last date: {last_date}). Updating...")
            except Exception as e:
                print(f"DEBUG: Local file check failed, downloading fresh: {e}")

        end = datetime.now()
        start = datetime(end.year-2, end.month, end.day)
        
        # 2. Try yfinance with multiple attempts
        data = pd.DataFrame()
        for attempt in range(3):
            try:
                # Removed custom session as it caused issues with curl_cffi in this environment
                data = yf.download(quote, start=start, end=end, progress=False)
                if not data.empty:
                    break
                time.sleep(1)
            except Exception as e:
                print(f"yfinance attempt {attempt+1} failed for {quote}: {e}")
                time.sleep(1)

        # 3. Process and Save yfinance data
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data = data.reset_index()
            df = pd.DataFrame(data=data)
            df.to_csv(filename, index=False)
            return

        # 4. Fallback to Alpha Vantage (Global symbols)
        print(f"yfinance failed for {quote}, falling back to Alpha Vantage...")
        try:
            ts = TimeSeries(key='N6A6QT6IBFJOPJ70', output_format='pandas')
            # Use get_daily instead of get_daily_adjusted as the latter is often premium
            try:
                data, meta_data = ts.get_daily(symbol=quote, outputsize='full')
            except Exception as e:
                print(f"Direct Alpha Vantage lookup failed: {e}. Trying NSE fallback...")
                data, meta_data = ts.get_daily(symbol='NSE:'+quote, outputsize='full')
            
            data = data.head(503).iloc[::-1]
            data = data.reset_index()
            df = pd.DataFrame()
            df['Date'] = data['date']
            df['Open'] = data['1. open']
            df['High'] = data['2. high']
            df['Low'] = data['3. low']
            df['Close'] = data['4. close']
            # Map Close to Adj Close for consistency since non-adjusted doesn't have it
            df['Adj Close'] = data['4. close']
            df['Volume'] = data['5. volume']
            df.to_csv(filename, index=False)
        except Exception as e:
            print(f"Global lookup failed for {quote}: {e}")
            raise Exception(f"Could not fetch data for {quote} from any source.")
        return

    #******************** ARIMA SECTION ********************
    def ARIMA_ALGO(df):
        uniqueVals = df["Code"].unique()  
        len(uniqueVals)
        df=df.set_index("Code")
        #for daily basis
        def parser(x):
            return datetime.strptime(x, '%Y-%m-%d')
        def arima_model(train, test):
            history = [x for x in train]
            predictions = list()
            for t in range(len(test)):
                model = ARIMA(history, order=(6,1 ,0))
                model_fit = model.fit()
                output = model_fit.forecast()
                yhat = output[0]
                predictions.append(yhat)
                obs = test[t]
                history.append(obs)
            return predictions
        for company in uniqueVals[:10]:
            data=(df.loc[company,:]).reset_index()
            data['Price'] = data['Close']
            Quantity_date = data[['Price','Date']]
            Quantity_date.index = Quantity_date['Date'].map(lambda x: parser(x))
            Quantity_date['Price'] = Quantity_date['Price'].map(lambda x: float(x))
            Quantity_date = Quantity_date.fillna(Quantity_date.bfill())
            Quantity_date = Quantity_date.drop(['Date'],axis =1)
            # fig = plt.figure(figsize=(7.2,4.8),dpi=75)
            # plt.plot(Quantity_date, color='#1F77B4')
            # plt.savefig('static/Trends.png')
            # plt.close(fig)
            
            quantity = Quantity_date.values
            size = int(len(quantity) * 0.80)
            train, test = quantity[0:size], quantity[size:len(quantity)]
            #fit in model
            predictions = arima_model(train, test)
            
            # Store data for D3 visualization
            arima_actual = test.flatten().tolist()
            arima_predicted = predictions
            
            #plot graph
            # fig = plt.figure(figsize=(7.2,4.8),dpi=65)
            # plt.plot(test, label='Actual Price', linestyle=':', color='#1F77B4')
            # plt.plot(predictions, label='Predicted Price', color='#4B73B1')
            # plt.legend(loc=4)
            # plt.savefig('static/ARIMA.png')
            # plt.close(fig)
            print()
            print("##############################################################################")
            arima_pred=predictions[-2]
            print("Tomorrow's",quote," Closing Price Prediction by ARIMA:",arima_pred)
            #rmse calculation
            error_arima = math.sqrt(mean_squared_error(test, predictions))
            print("ARIMA RMSE:",error_arima)
            print("##############################################################################")
            return arima_pred, error_arima, arima_actual, arima_predicted
        
        


    #************* LSTM SECTION **********************

    def LSTM_ALGO(df):
        #Split data into training set and test set
        dataset_train=df.iloc[0:int(0.8*len(df)),:]
        dataset_test=df.iloc[int(0.8*len(df)):,:]
        ############# NOTE #################
        #TO PREDICT STOCK PRICES OF NEXT N DAYS, STORE PREVIOUS N DAYS IN MEMORY WHILE TRAINING
        # HERE N=7
        ###dataset_train=pd.read_csv('Google_Stock_Price_Train.csv')
        training_set=df.iloc[:,4:5].values# 1:2, to store as numpy array else Series obj will be stored
        #select cols using above manner to select as float64 type, view in var explorer

        #Feature Scaling
        from sklearn.preprocessing import MinMaxScaler
        sc=MinMaxScaler(feature_range=(0,1))#Scaled values btween 0,1
        training_set_scaled=sc.fit_transform(training_set)
        #In scaling, fit_transform for training, transform for test
        
        #Creating data stucture with 7 timesteps and 1 output. 
        #7 timesteps meaning storing trends from 7 days before current day to predict 1 next output
        X_train=[]#memory with 7 days from day i
        y_train=[]#day i
        for i in range(7,len(training_set_scaled)):
            X_train.append(training_set_scaled[i-7:i,0])
            y_train.append(training_set_scaled[i,0])
        #Convert list to numpy arrays
        X_train=np.array(X_train)
        y_train=np.array(y_train)
        X_forecast=np.array(X_train[-1,1:])
        X_forecast=np.append(X_forecast,y_train[-1])
        #Reshaping: Adding 3rd dimension
        X_train=np.reshape(X_train, (X_train.shape[0],X_train.shape[1],1))#.shape 0=row,1=col
        X_forecast=np.reshape(X_forecast, (1,X_forecast.shape[0],1))
        #For X_train=np.reshape(no. of rows/samples, timesteps, no. of cols/features)
        
        #Building RNN
        from keras.models import Sequential
        from keras.layers import Dense
        from keras.layers import Dropout
        from keras.layers import LSTM
        
        #Initialise RNN
        regressor=Sequential()
        
        #Add first LSTM layer
        regressor.add(LSTM(units=50,return_sequences=True,input_shape=(X_train.shape[1],1)))
        #units=no. of neurons in layer
        #input_shape=(timesteps,no. of cols/features)
        #return_seq=True for sending recc memory. For last layer, retrun_seq=False since end of the line
        regressor.add(Dropout(0.1))
        
        #Add 2nd LSTM layer
        regressor.add(LSTM(units=50,return_sequences=True))
        regressor.add(Dropout(0.1))
        
        #Add 3rd LSTM layer
        regressor.add(LSTM(units=50,return_sequences=True))
        regressor.add(Dropout(0.1))
        
        #Add 4th LSTM layer
        regressor.add(LSTM(units=50))
        regressor.add(Dropout(0.1))
        
        #Add o/p layer
        regressor.add(Dense(units=1))
        
        #Compile
        regressor.compile(optimizer='adam',loss='mean_squared_error')
        
        #Training
        regressor.fit(X_train,y_train,epochs=25,batch_size=32 )
        #For lstm, batch_size=power of 2
        
        #Testing
        ###dataset_test=pd.read_csv('Google_Stock_Price_Test.csv')
        real_stock_price=dataset_test.iloc[:,4:5].values
        
        #To predict, we need stock prices of 7 days before the test set
        #So combine train and test set to get the entire data set
        dataset_total=pd.concat((dataset_train['Close'],dataset_test['Close']),axis=0) 
        testing_set=dataset_total[ len(dataset_total) -len(dataset_test) -7: ].values
        testing_set=testing_set.reshape(-1,1)
        #-1=till last row, (-1,1)=>(80,1). otherwise only (80,0)
        
        #Feature scaling
        testing_set=sc.transform(testing_set)
        
        #Create data structure
        X_test=[]
        for i in range(7,len(testing_set)):
            X_test.append(testing_set[i-7:i,0])
            #Convert list to numpy arrays
        X_test=np.array(X_test)
        
        #Reshaping: Adding 3rd dimension
        X_test=np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
        
        #Testing Prediction
        predicted_stock_price=regressor.predict(X_test)
        
        #Getting original prices back from scaled values
        predicted_stock_price=sc.inverse_transform(predicted_stock_price)
        
        # Store data for D3 visualization
        lstm_actual = real_stock_price.flatten().tolist()
        lstm_predicted = predicted_stock_price.flatten().tolist()
        
        # fig = plt.figure(figsize=(7.2,4.8),dpi=65)
        # plt.plot(real_stock_price, label='Actual Price', linestyle=':', color='#1F77B4')  
        # plt.plot(predicted_stock_price, label='Predicted Price', color='#4B73B1')
          
        # plt.legend(loc=4)
        # plt.savefig('static/LSTM.png')
        # plt.close(fig)
        
        
        error_lstm = math.sqrt(mean_squared_error(real_stock_price, predicted_stock_price))
        
        
        #Forecasting Prediction
        forecasted_stock_price=regressor.predict(X_forecast)
        
        #Getting original prices back from scaled values
        forecasted_stock_price=sc.inverse_transform(forecasted_stock_price)
        
        lstm_pred=forecasted_stock_price[0,0]
        print()
        print("##############################################################################")
        print("Tomorrow's ",quote," Closing Price Prediction by LSTM: ",lstm_pred)
        print("LSTM RMSE:",error_lstm)
        print("##############################################################################")
        return lstm_pred,error_lstm,lstm_actual,lstm_predicted
    #***************** LINEAR REGRESSION SECTION ******************       
    def LIN_REG_ALGO(df, mode='close'):
        """Linear Regression prediction.
        mode='close'  -> predict Close price from previous Close (default)
        mode='volume' -> predict Close price from Volume (volume-based catalyst)
        """
        forecast_out = int(7)

        if mode == 'volume':
            # ---- Volume-Based Catalyst ----
            # Target: Close price shifted forward by forecast_out days
            df['Close after n days'] = df['Close'].shift(-forecast_out)
            # Feature: Volume (normalised inside scaler)
            df_new = df[['Volume', 'Close after n days']].copy()
            feature_col = 'Volume'
            print(f"[LR] Running in VOLUME-based mode for {quote}")
        else:
            # ---- Close-Price Catalyst (default) ----
            df['Close after n days'] = df['Close'].shift(-forecast_out)
            df_new = df[['Close', 'Close after n days']].copy()
            feature_col = 'Close'
            print(f"[LR] Running in CLOSE-price mode for {quote}")

        # Shared structure for both modes
        y = np.array(df_new.iloc[:-forecast_out, -1])
        y = np.reshape(y, (-1, 1))
        X = np.array(df_new.iloc[:-forecast_out, 0:-1])
        X_to_be_forecasted = np.array(df_new.iloc[-forecast_out:, 0:-1])

        X_train = X[0:int(0.8 * len(df)), :]
        X_test  = X[int(0.8 * len(df)):, :]
        y_train = y[0:int(0.8 * len(df)), :]
        y_test  = y[int(0.8 * len(df)):, :]

        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test  = sc.transform(X_test)
        X_to_be_forecasted = sc.transform(X_to_be_forecasted)

        clf = LinearRegression(n_jobs=-1)
        clf.fit(X_train, y_train)

        y_test_pred = clf.predict(X_test)
        y_test_pred = y_test_pred * (1.04)

        lr_actual    = y_test.flatten().tolist()
        lr_predicted = y_test_pred.flatten().tolist()

        error_lr = math.sqrt(mean_squared_error(y_test, y_test_pred))

        forecast_set = clf.predict(X_to_be_forecasted)
        forecast_set = forecast_set * (1.04)
        mean = forecast_set.mean()
        lr_pred = forecast_set[0, 0]
        print()
        print("##############################################################################")
        print(f"Tomorrow's {quote} Closing Price Prediction by Linear Regression ({mode.upper()}): {lr_pred}")
        print("Linear Regression RMSE:", error_lr)
        print("##############################################################################")
        return df, lr_pred, forecast_set, mean, error_lr, lr_actual, lr_predicted

    def recommending(df, global_polarity, today_stock, mean):
        current_price = today_stock.iloc[-1]['Close']
        
        # Determine Idea (RISE/FALL) based on predicted mean vs current price
        if current_price < mean:
            idea = "RISE"
        else:
            idea = "FALL"
            
        # Determine Decision based on BOTH Price Action and Sentiment
        if idea == "RISE":
            if global_polarity > 0:
                decision = "STRONG BUY"
            else:
                decision = "BUY (Technical)"
        else: # idea == "FALL"
            if global_polarity > 0:
                decision = "HOLD / CAUTION"
            else:
                decision = "STRONG SELL"
                
        print()
        print("##############################################################################")
        print(f"Recommendation for {quote}: Prediction={idea}, Sentiment={'Positive' if global_polarity > 0 else 'Negative/Neutral'} => {decision}")
        print("##############################################################################")
        
        return idea, decision





    #**************GET DATA ***************************************
    quote=nm
    #Try-except to check if valid stock symbol
    try:
        get_historical(quote)
    except Exception as e:
        print(f"DEBUG: Error in get_historical for {quote}: {e}")
        import traceback
        traceback.print_exc()
        return render_template('index.html',not_found=True)
    else:
    
        #************** PREPROCESSUNG ***********************
        df = pd.read_csv(''+quote+'.csv')
        print("##############################################################################")
        print("Today's",quote,"Stock Data: ")
        # Forward fill to prevent NaN displaying when the latest fetched row is incomplete
        today_stock=df.ffill().iloc[-1:]
        print(today_stock)
        print("##############################################################################")
        df = df.dropna()
        code_list=[]
        for i in range(0,len(df)):
            code_list.append(quote)
        df2=pd.DataFrame(code_list,columns=['Code'])
        df2 = pd.concat([df2, df], axis=1)
        df=df2


        # Enable only Linear Regression model for fastest performance
        # arima_pred, error_arima, arima_actual, arima_predicted=ARIMA_ALGO(df)
        # lstm_pred, error_lstm, lstm_actual, lstm_predicted=LSTM_ALGO(df)
        
        # Set dummy values for disabled models
        arima_pred, error_arima, arima_actual, arima_predicted = 0, 0, [], []
        lstm_pred, error_lstm, lstm_actual, lstm_predicted = 0, 0, [], []
        
        # Run only Linear Regression (mode determined by user's catalyst choice)
        df, lr_pred, forecast_set, mean, error_lr, lr_actual, lr_predicted = LIN_REG_ALGO(df, mode=prediction_mode)
        
        # Use FREE news-based sentiment analysis instead of Twitter
        print()
        print("##############################################################################")
        print("Fetching news sentiment for", quote, "...")
        print("##############################################################################")
        polarity, sentiment_list, sentiment_pol, pos, neg, neutral = finviz_finvader_sentiment(quote, num_articles=7)
        
        idea, decision=recommending(df, polarity,today_stock,mean)
        print()
        print("Forecasted Prices for Next 7 days:")
        print(forecast_set)
        today_stock=today_stock.round(2)
        return render_template('results.html',quote=quote,arima_pred=round(arima_pred,2),lstm_pred=round(lstm_pred,2),
                               lr_pred=round(lr_pred,2),open_s=today_stock['Open'].to_string(index=False),
                               close_s=today_stock['Close'].to_string(index=False),
                               sentiment_list=sentiment_list,sentiment_pol=sentiment_pol,idea=idea,decision=decision,high_s=today_stock['High'].to_string(index=False),
                               low_s=today_stock['Low'].to_string(index=False),vol=today_stock['Volume'].to_string(index=False),
                               forecast_set=forecast_set,error_lr=round(error_lr,2),error_lstm=round(error_lstm,2),error_arima=round(error_arima,2),
                               arima_actual=arima_actual, arima_predicted=arima_predicted,
                               lstm_actual=lstm_actual, lstm_predicted=lstm_predicted,
                               lr_actual=lr_actual, lr_predicted=lr_predicted,
                               pos=pos, neg=neg, neutral=neutral,
                               prediction_mode=prediction_mode)
if __name__ == '__main__':
   app.run(debug=True)
   

















