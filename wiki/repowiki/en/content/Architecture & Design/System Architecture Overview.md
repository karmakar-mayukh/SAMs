# System Architecture Overview

<cite>
**Referenced Files in This Document**
- [main.py](file://main.py)
- [news_sentiment.py](file://news_sentiment.py)
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [templates/index.html](file://templates/index.html)
- [templates/dashboard.html](file://templates/dashboard.html)
- [templates/admin_dashboard.html](file://templates/admin_dashboard.html)
- [docs/diagrams/dfd_level0.md](file://docs/diagrams/dfd_level0.md)
- [docs/diagrams/er_diagram.md](file://docs/diagrams/er_diagram.md)
- [docs/diagrams/export_diagrams.py](file://docs/diagrams/export_diagrams.py)
- [demos/api_keys_demo.py](file://demos/api_keys_demo.py)
- [tests/test_database_models.py](file://tests/test_database_models.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the high-level architecture of the intelligent-stock-prediction system. It covers the three-tier architecture (presentation, application, and data), external entities (Users, Admins, Market Data APIs), and the end-to-end data flows using a Level 0 DFD. It also documents component interactions among frontend templates, Flask controllers, ML models, and database models, along with technology choices and deployment considerations.

## Project Structure
The repository organizes the system into:
- Presentation layer: Jinja2 templates and static assets
- Application layer: Flask routes and business logic
- Data layer: SQLAlchemy models backed by SQLite
- Supporting artifacts: documentation diagrams, tests, demos, and requirements

```mermaid
graph TB
subgraph "Presentation Layer"
T1["templates/index.html"]
T2["templates/dashboard.html"]
T3["templates/admin_dashboard.html"]
S1["static/* (CSS, JS, assets)"]
end
subgraph "Application Layer"
M["main.py<br/>Flask app, routes, controllers"]
NS["news_sentiment.py<br/>Sentiment analysis"]
end
subgraph "Data Layer"
DB["SQLite database"]
SQL["SQLAlchemy ORM models"]
end
subgraph "External Entities"
U["User"]
A["Admin"]
MD["Market Data APIs"]
end
T1 --> M
T2 --> M
T3 --> M
M --> SQL
SQL --> DB
M --> NS
M --> MD
U --> T1
A --> T3
```

**Diagram sources**
- [main.py](file://main.py#L1-L120)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [templates/index.html](file://templates/index.html#L1-L120)
- [templates/dashboard.html](file://templates/dashboard.html#L1-L120)
- [templates/admin_dashboard.html](file://templates/admin_dashboard.html#L1-L120)

**Section sources**
- [README.md](file://README.md#L73-L83)
- [main.py](file://main.py#L40-L60)
- [requirements.txt](file://requirements.txt#L1-L19)

## Core Components
- Presentation layer: HTML templates and static assets rendered by Flask and served via Jinja2.
- Application layer: Flask application with route handlers, business logic, and orchestration of ML and sentiment components.
- Data layer: SQLAlchemy models representing Users, Companies, Brokers, PortfolioItems, Transactions, and Dividends, persisted in SQLite.

Key responsibilities:
- Routes for authentication, portfolio management, prediction, and admin monitoring.
- Database models with relationships and constraints validated by tests.
- Sentiment analysis pipeline aggregating multiple sources and returning polarity scores.

**Section sources**
- [main.py](file://main.py#L120-L220)
- [tests/test_database_models.py](file://tests/test_database_models.py#L1-L120)
- [docs/diagrams/er_diagram.md](file://docs/diagrams/er_diagram.md#L1-L68)

## Architecture Overview
The system follows a three-tier architecture:
- Presentation: HTML templates and static assets.
- Application: Flask controllers and business logic.
- Data: SQLite via SQLAlchemy ORM.

External entities:
- Users: Interact with dashboards, place trades, and view predictions.
- Admins: Monitor system statistics and manage brokers/companies.
- Market Data APIs: Provide price and news data consumed by the prediction and sentiment engines.

```mermaid
graph TB
subgraph "Presentation Layer"
IDX["index.html"]
DASH["dashboard.html"]
ADM["admin_dashboard.html"]
end
subgraph "Application Layer"
APP["Flask app (main.py)"]
SENT["Sentiment Pipeline (news_sentiment.py)"]
end
subgraph "Data Layer"
ORM["SQLAlchemy Models"]
DB["SQLite"]
end
subgraph "External"
USER["User"]
ADMIN["Admin"]
MARKET["Market Data APIs"]
end
USER --> IDX
USER --> DASH
ADMIN --> ADM
IDX --> APP
DASH --> APP
ADM --> APP
APP --> ORM
ORM --> DB
APP --> SENT
APP --> MARKET
```

**Diagram sources**
- [main.py](file://main.py#L199-L224)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [docs/diagrams/er_diagram.md](file://docs/diagrams/er_diagram.md#L1-L68)

## Detailed Component Analysis

### Three-Tier Architecture Details
- Presentation layer: Templates define user-facing pages and include static assets. Controllers render templates and pass context data.
- Application layer: Flask routes implement authentication, portfolio operations, prediction orchestration, and admin monitoring. Controllers interact with the database and ML/sentiment components.
- Data layer: SQLAlchemy models encapsulate business entities and relationships. Tests validate constraints and cascades.

```mermaid
classDiagram
class User {
+int id
+string email
+string username
+string password_hash
+string role
+decimal wallet_balance
+datetime created_at
+datetime last_login_at
+bool is_active
+check_password(password) bool
}
class Company {
+int id
+string symbol
+string name
+string exchange
+string sector
+bool is_active
}
class Broker {
+int id
+string name
+string email
+decimal commission_rate
+bool is_active
}
class PortfolioItem {
+int id
+int user_id
+int company_id
+int quantity
+decimal average_buy_price
+datetime created_at
}
class Transaction {
+int id
+int user_id
+int company_id
+int broker_id
+string txn_type
+int quantity
+decimal price
+decimal total_amount
+decimal commission_amount
+datetime created_at
+string description
}
class Dividend {
+int id
+int portfolio_item_id
+decimal amount_per_share
+decimal total_amount
+date payable_date
+datetime created_at
}
User ||--o{ PortfolioItem : "owns"
Company ||--o{ PortfolioItem : "held in"
User ||--o{ Transaction : "executes"
Company ||--o{ Transaction : "traded in"
Broker ||--o{ Transaction : "charges commission on"
User ||--o{ Dividend : "receives"
Company ||--o{ Dividend : "issues"
```

**Diagram sources**
- [docs/diagrams/er_diagram.md](file://docs/diagrams/er_diagram.md#L1-L68)
- [tests/test_database_models.py](file://tests/test_database_models.py#L1-L120)

**Section sources**
- [docs/diagrams/er_diagram.md](file://docs/diagrams/er_diagram.md#L1-L68)
- [tests/test_database_models.py](file://tests/test_database_models.py#L1-L120)

### Data Flow: Level 0 DFD
The Level 0 DFD captures high-level interactions among Users, Admins, Market Data APIs, and internal processes.

```mermaid
flowchart LR
%% External Entities
User["User"]
Admin["Admin"]
MarketData["Market Data APIs"]
%% Processes
P1["P1: Authentication"]
P2["P2: Portfolio Management"]
P3["P3: Prediction Engine"]
P4["P4: Sentiment Analysis"]
P5["P5: Admin Monitoring"]
%% Data Stores
DS_User[("D1: User DB")]
DS_Company[("D2: Company DB")]
DS_Portfolio[("D3: Portfolio DB")]
DS_Txn[("D4: Transaction DB")]
DS_Dividend[("D5: Dividend DB")]
%% Flows
User --> |"Login/Logout"| P1
P1 --> |"User details"| DS_User
P1 --> |"Auth result"| User
User --> |"Trade / Dividend Requests"| P2
P2 --> |"Portfolio updates"| DS_Portfolio
P2 --> |"Transactions"| DS_Txn
P2 --> |"Dividends"| DS_Dividend
P2 --> |"Dashboard views"| User
P2 --> |"Symbol & history request"| P3
P3 --> |"Historical data & predictions"| P2
P3 --> |"Price/News requests"| MarketData
MarketData --> |"Price/News data"| P3
P3 --> |"News text"| P4
P4 --> |"Sentiment scores"| P3
Admin --> |"Monitoring requests"| P5
P5 --> |"Aggregated stats"| Admin
P5 --> DS_User
P5 --> DS_Company
P5 --> DS_Portfolio
P5 --> DS_Txn
P5 --> DS_Dividend
```

**Diagram sources**
- [docs/diagrams/dfd_level0.md](file://docs/diagrams/dfd_level0.md#L1-L50)

**Section sources**
- [docs/diagrams/dfd_level0.md](file://docs/diagrams/dfd_level0.md#L1-L50)

### Component Interactions: Prediction and Sentiment Pipeline
The prediction flow integrates market data retrieval, model inference, and sentiment aggregation.

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant Flask as "Flask Controller (main.py)"
participant ML as "Prediction Models"
participant Sent as "Sentiment Analyzer (news_sentiment.py)"
participant Market as "Market Data APIs"
participant DB as "SQLAlchemy Models"
Browser->>Flask : "POST /predict with symbol"
Flask->>Market : "Fetch historical price data"
Market-->>Flask : "Price series"
Flask->>ML : "Train/Run ARIMA/LSTM/Linear Regression"
ML-->>Flask : "Predictions, RMSE, plots"
Flask->>Sent : "Fetch news text for symbol"
Sent-->>Flask : "Sentiment scores"
Flask->>DB : "Persist predictions, plots, sentiment"
Flask-->>Browser : "Render results page with charts"
```

**Diagram sources**
- [main.py](file://main.py#L545-L780)
- [news_sentiment.py](file://news_sentiment.py#L311-L800)

**Section sources**
- [main.py](file://main.py#L545-L780)
- [news_sentiment.py](file://news_sentiment.py#L311-L800)

### Authentication and Authorization Flow
Authentication ensures secure access to dashboards and admin controls.

```mermaid
sequenceDiagram
participant Browser as "Browser"
participant Flask as "Flask App (main.py)"
participant DB as "SQLAlchemy Models"
Browser->>Flask : "GET /login"
Browser->>Flask : "POST /login with credentials"
Flask->>DB : "Lookup user by email"
DB-->>Flask : "User record"
Flask->>Flask : "Verify password hash"
alt "Valid credentials"
Flask->>DB : "Update last_login_at"
DB-->>Flask : "Success"
Flask-->>Browser : "Redirect to /dashboard"
else "Invalid credentials"
Flask-->>Browser : "Flash error and reload login"
end
Browser->>Flask : "GET /admin (role=admin)"
Flask->>DB : "Check session role"
DB-->>Flask : "Role"
alt "Admin"
Flask-->>Browser : "Admin dashboard"
else "Non-admin"
Flask-->>Browser : "403 Forbidden"
end
```

**Diagram sources**
- [main.py](file://main.py#L226-L249)
- [main.py](file://main.py#L436-L490)

**Section sources**
- [main.py](file://main.py#L226-L249)
- [main.py](file://main.py#L436-L490)

### Portfolio Management Workflow
Portfolio operations include buying/selling, dividend recording, and fund top-ups.

```mermaid
flowchart TD
Start(["User initiates operation"]) --> Choice{"Operation Type?"}
Choice --> |Buy| Buy["POST /trade/buy<br/>Validate symbol/qty<br/>Fetch price<br/>Compute commission<br/>Update holdings & wallet"]
Choice --> |Sell| Sell["POST /trade/sell<br/>Validate holdings<br/>Fetch price<br/>Compute commission<br/>Update holdings & wallet"]
Choice --> |Top Up| TopUp["POST /funds/topup<br/>Validate amount<br/>Credit wallet"]
Choice --> |Record Dividend| Dividend["POST /dividends/record<br/>Validate holdings<br/>Credit wallet & record dividend"]
Buy --> Persist["Persist Transaction & PortfolioItem"]
Sell --> Persist
TopUp --> Persist
Dividend --> Persist
Persist --> End(["Redirect to dashboard"])
```

**Diagram sources**
- [main.py](file://main.py#L268-L434)

**Section sources**
- [main.py](file://main.py#L268-L434)

### Admin Monitoring Pathways
Admins can monitor system statistics and manage entities.

```mermaid
flowchart TD
AdminStart["Admin requests /admin"] --> LoadStats["Aggregate counts & totals"]
LoadStats --> Render["Render admin dashboard with metrics"]
Render --> ManageBrokers["POST /admin/brokers<br/>Add/update broker"]
Render --> ManageCompanies["POST /admin/companies<br/>Add/update company"]
ManageBrokers --> Render
ManageCompanies --> Render
```

**Diagram sources**
- [main.py](file://main.py#L436-L541)
- [templates/admin_dashboard.html](file://templates/admin_dashboard.html#L1-L120)

**Section sources**
- [main.py](file://main.py#L436-L541)
- [templates/admin_dashboard.html](file://templates/admin_dashboard.html#L1-L120)

## Dependency Analysis
Technology stack and dependencies:
- Backend: Flask, SQLAlchemy, Werkzeug security utilities
- ML/AI: TensorFlow/Keras, Scikit-learn, Statsmodels, NLTK, TextBlob
- Data providers: yfinance, Alpha Vantage
- Frontend: Bootstrap, jQuery, static assets
- Deployment: Gunicorn

```mermaid
graph TB
Flask["Flask"]
SQL["SQLAlchemy"]
TF["TensorFlow/Keras"]
SK["Scikit-learn"]
ST["Statsmodels"]
NLTK["NLTK"]
YF["yfinance"]
AV["Alpha Vantage"]
Gunicorn["Gunicorn"]
Bootstrap["Bootstrap"]
jQuery["jQuery"]
Flask --> SQL
Flask --> TF
Flask --> SK
Flask --> ST
Flask --> NLTK
Flask --> YF
Flask --> AV
Flask --> Gunicorn
Flask --> Bootstrap
Flask --> jQuery
```

**Diagram sources**
- [requirements.txt](file://requirements.txt#L1-L19)
- [README.md](file://README.md#L51-L73)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L19)
- [README.md](file://README.md#L51-L73)

## Performance Considerations
- SQLite for development simplifies setup but limits concurrent writes and scaling compared to production-grade databases.
- ML inference (LSTM/ARIMA) can be computationally intensive; consider batching, caching, or offloading heavy tasks to background workers.
- Sentiment analysis uses multiple sources; implement timeouts and fallbacks to maintain responsiveness.
- Static asset caching and compression can improve frontend performance.
- Use production WSGI server (Gunicorn) and reverse proxy for concurrency and stability.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and remedies:
- Authentication failures: Verify credentials and ensure user is active; review session handling and CSRF protection.
- Missing API keys: The sentiment system gracefully skips unavailable sources; configure keys or environment variables.
- Database integrity errors: Foreign key violations or unique constraint conflicts indicate invalid data or missing relations.
- Prediction errors: Validate symbol availability and ensure market data retrieval succeeds before model inference.

**Section sources**
- [main.py](file://main.py#L226-L249)
- [demos/api_keys_demo.py](file://demos/api_keys_demo.py#L1-L162)
- [tests/test_database_models.py](file://tests/test_database_models.py#L331-L356)

## Conclusion
The intelligent-stock-prediction system employs a clean three-tier architecture with clear separation of concerns. The presentation layer delivers responsive dashboards, the application layer orchestrates business logic and ML/sentiment pipelines, and the data layer persists entities with strong relational constraints. While SQLite suits development, production deployments should consider scalable databases and robust infrastructure for concurrency and reliability.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Deployment Topology and Infrastructure
- Local deployment: Flask dev server with SQLite and local static assets.
- Cloud deployment: Use a WSGI server (e.g., Gunicorn) behind a reverse proxy, containerized with environment variables for secrets and database URLs. Replace SQLite with a managed database for production.

**Section sources**
- [requirements.txt](file://requirements.txt#L14-L14)
- [README.md](file://README.md#L104-L135)

### Exporting Diagrams
Mermaid diagrams can be exported to SVG/PNG using the provided export script.

**Section sources**
- [docs/diagrams/export_diagrams.py](file://docs/diagrams/export_diagrams.py#L1-L211)