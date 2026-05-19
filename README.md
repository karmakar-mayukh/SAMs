# Stock Analysis & Market Sentiment System

A comprehensive, full-stack web application that integrates machine-learning forecasting, news-driven sentiment analysis, and a risk-free simulated brokerage into a unified platform. Designed for students, researchers, and investors, this system bridges the gap between standalone prediction tools and functional portfolio management environments.

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [System Components](#system-components)
- [Quick Start](#quick-start-for-new-users)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [License](#license)

## Project Overview

This project delivers an end-to-end decision-support platform that combines quantitative equity models with qualitative market signals. By embedding short-horizon forecasting and sentiment scoring into a complete paper-trading workflow, the application provides a practical resource for learning and experimentation in equity markets.

The system features a **dual-mode forecasting engine** and a **multi-source sentiment aggregator**, all managed through intuitive user and administrator dashboards.

## Key Features

### Dual-Mode Prediction Engine
- **Linear Regression Core**: Projects closing prices 7 days ahead with calculated RMSE accuracy scores.
- **Close-Price Mode**: Forecasts based on historical pricing patterns.
- **Volume-Based Mode**: Uses trading activity as the primary predictive signal.
- **Catalyst Badges**: Visual indicators on the results page showing which model mode is active.
- **Interactive Visualizations**: D3.js-based charts for comparing actual vs. predicted performance.

### Portfolio & Simulation Module
- **Risk-Free Trading**: Full support for buy/sell order execution with a virtual cash wallet.
- **Integrated Portfolio Oversight**: Real-time valuation, dividend logging, and searchable transaction history.
- **Automated Invoicing**: Every trade automatically generates a downloadable plain-text invoice.
- **Notification Layer**: In-app alerts for trades, reports, and billing, with customizable user preferences.
- **Portfolio Snapshots**: On-demand performance reports for multiple time horizons (7, 30, 90, 365 days, or all-time).

### Advanced Administration
- **Live Traffic Metrics**: Monitoring of per-request latency, error counts, and system uptime.
- **Dataset Management**: Administrative interface for uploading, inspecting, and removing CSV files used for model training.
- **Brokerage Governance**: Configuration of active brokers and adjustable commission rates.
- **System Integrity**: `/health` endpoint for external monitoring and size-based rotating logs (`logs/app.log`).

## Technology Stack

- **Backend**: Python, Flask
- **Database / ORM**: SQLite, SQLAlchemy
- **ML & Analytics**: scikit-learn (Linear Regression), pandas, NumPy
- **Sentiment / NLP**: NLTK VADER, TextBlob, BeautifulSoup, requests, newspaper3k, aiohttp, tenacity
- **Frontend**: HTML/CSS, Bootstrap, JavaScript, D3.js

## Architecture

The system follows a classic **three-tier architecture**:
1. **Presentation Layer**: Responsive web interface and interactive D3.js dashboards.
2. **Application Layer**: Flask-based backend handling business logic, prediction orchestration, and security.
3. **Data Layer**: SQLite relational database for persistence of user data, transactions, and system settings.

## Quick Start for New Users

### 1. Prerequisites
- Python 3.7+ installed.
- Access to a terminal/command prompt.

### 2. Environment Setup
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Installation
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Admin
```bash
# Creates the default admin: admin@example.com / admin123
python create_admin.py
```

### 5. Run & Explore
```bash
python main.py
# Access at http://localhost:5000
```

## Documentation

Detailed project documentation can be found in the `docs/` and `documents/` directories:
- **Project Report**: Comprehensive breakdown of methodology, literature review, and results.
- **Advanced Features**: Detailed guides on the sentiment engine and notification system.
- **API Keys**: Instructions for configuring optional Alpha Vantage or NewsAPI integrations.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details.
