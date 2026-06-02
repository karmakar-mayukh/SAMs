# Business Logic Layer

<cite>
**Referenced Files in This Document**
- [main.py](file://main.py)
- [news_sentiment.py](file://news_sentiment.py)
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py)
- [test_trading_operations.py](file://tests/test_trading_operations.py)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py)
- [conftest.py](file://tests/conftest.py)
- [templates/dashboard.html](file://templates/dashboard.html)
- [docs/diagrams/dfd_portfolio_level1.md](file://docs/diagrams/dfd_portfolio_level1.md)
- [docs/diagrams/exported/dfd_portfolio_level1.mmd](file://docs/diagrams/exported/dfd_portfolio_level1.mmd)
- [docs/diagrams/gallery.html](file://docs/diagrams/gallery.html)
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
This document focuses on the business logic layer of the intelligent stock prediction application. It explains the prediction pipeline workflow from user input to forecast visualization, including data retrieval (yfinance), preprocessing, model execution, and result aggregation. It also documents trading operations logic (buy/sell order processing, commission calculations, wallet updates, and dividend recording), portfolio valuation algorithms, and performance metric calculations. The document references the test suite to illustrate expected behavior and edge cases, and covers state management patterns for user sessions and transaction atomicity. Error handling within business workflows and data consistency requirements are addressed, along with examples of complex operations such as batch predictions and portfolio rebalancing simulations.

## Project Structure
The business logic spans several modules:
- Application entry and routing logic: [main.py](file://main.py)
- Sentiment analysis engine: [news_sentiment.py](file://news_sentiment.py)
- Tests for prediction pipeline: [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py)
- Tests for trading operations: [test_trading_operations.py](file://tests/test_trading_operations.py)
- Tests for portfolio management: [test_portfolio_management.py](file://tests/test_portfolio_management.py)
- Shared test fixtures and mocks: [conftest.py](file://tests/conftest.py)
- UI templates for dashboards and prediction views: [templates/dashboard.html](file://templates/dashboard.html)
- Portfolio DFD diagrams: [docs/diagrams/dfd_portfolio_level1.md](file://docs/diagrams/dfd_portfolio_level1.md), [docs/diagrams/exported/dfd_portfolio_level1.mmd](file://docs/diagrams/exported/dfd_portfolio_level1.mmd), [docs/diagrams/gallery.html](file://docs/diagrams/gallery.html)

```mermaid
graph TB
subgraph "Web App"
Routes["Routes and Controllers<br/>main.py"]
Templates["Templates<br/>templates/dashboard.html"]
end
subgraph "Business Logic"
Pred["Prediction Pipeline<br/>main.py"]
Trade["Trading Operations<br/>main.py"]
Portfolio["Portfolio Valuation & Metrics<br/>main.py"]
Sent["Sentiment Engine<br/>news_sentiment.py"]
end
subgraph "Data & Persistence"
DB["SQLAlchemy Models<br/>main.py"]
FS["Static Plots<br/>static/*.png"]
end
subgraph "Testing"
TP["Prediction Tests<br/>test_prediction_pipeline.py"]
TO["Trading Tests<br/>test_trading_operations.py"]
PM["Portfolio Tests<br/>test_portfolio_management.py"]
Fixtures["Fixtures & Mocks<br/>conftest.py"]
end
Routes --> Pred
Routes --> Trade
Routes --> Portfolio
Pred --> Sent
Pred --> FS
Trade --> DB
Portfolio --> DB
Templates --> Routes
TP --> Pred
TO --> Trade
PM --> Portfolio
Fixtures --> TP
Fixtures --> TO
Fixtures --> PM
```

**Diagram sources**
- [main.py](file://main.py#L1-L120)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L1-L120)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L1-L120)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L1-L120)
- [conftest.py](file://tests/conftest.py#L1-L120)
- [templates/dashboard.html](file://templates/dashboard.html#L170-L198)

**Section sources**
- [main.py](file://main.py#L1-L120)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L1-L120)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L1-L120)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L1-L120)
- [conftest.py](file://tests/conftest.py#L1-L120)
- [templates/dashboard.html](file://templates/dashboard.html#L170-L198)

## Core Components
- Prediction pipeline: Orchestrates data retrieval, preprocessing, model execution, and visualization.
- Trading operations: Buy/sell order processing, commission calculations, wallet updates, and transaction records.
- Portfolio management: Wallet operations, holdings management, valuation, and performance metrics.
- Sentiment analysis: Multi-source sentiment pipeline integrated into prediction.
- Session and CSRF management: Login-required decorators, session state, and CSRF verification.
- Testing harness: Fixtures, mocks, and integration tests validating end-to-end flows.

**Section sources**
- [main.py](file://main.py#L161-L185)
- [main.py](file://main.py#L268-L433)
- [main.py](file://main.py#L545-L980)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [conftest.py](file://tests/conftest.py#L120-L210)

## Architecture Overview
The business logic layer is centered around Flask routes that invoke business functions. The prediction pipeline integrates external data sources (yfinance, Alpha Vantage fallback), executes multiple ML models, and generates visualizations. Trading operations enforce validation, apply commission calculations, and update wallets and holdings atomically. Portfolio valuation aggregates current prices and computes performance metrics.

```mermaid
sequenceDiagram
participant U as "User"
participant R as "Flask Routes<br/>main.py"
participant YF as "yfinance<br/>main.py"
participant AV as "Alpha Vantage<br/>main.py"
participant ML as "ML Models<br/>main.py"
participant SA as "Sentiment<br/>news_sentiment.py"
participant DB as "Database<br/>main.py"
participant FS as "Static Plots<br/>static/*.png"
U->>R : "POST /predict with symbol"
R->>YF : "get_historical(symbol)"
alt "yfinance fails"
R->>AV : "fallback to Alpha Vantage"
end
R->>ML : "ARIMA/LSTM/Linear Regression"
R->>SA : "finviz_finvader_sentiment(symbol)"
ML-->>R : "predictions, RMSE, series"
SA-->>R : "polarity, sentiment list"
R->>FS : "save plots (Trends, ARIMA, LSTM, LR)"
R->>DB : "render results with predictions"
R-->>U : "results page"
```

**Diagram sources**
- [main.py](file://main.py#L545-L980)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)

**Section sources**
- [main.py](file://main.py#L545-L980)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)

## Detailed Component Analysis

### Prediction Pipeline Workflow
The prediction pipeline begins with user input, retrieves historical data (preferably via yfinance with a fallback to Alpha Vantage), preprocesses the data, runs ARIMA, LSTM, and Linear Regression models, integrates sentiment analysis, and renders results with visualizations.

Key steps:
- Data retrieval: [get_historical](file://main.py#L550-L582) downloads two years of daily adjusted data; falls back to Alpha Vantage if empty.
- Preprocessing: Drops NA values, constructs DataFrame with symbol code, and writes CSV for downstream models.
- Model execution:
  - ARIMA: [ARIMA_ALGO](file://main.py#L584-L642) trains on 80% of data, saves ARIMA.png, and returns prediction and RMSE.
  - LSTM: [LSTM_ALGO](file://main.py#L647-L779) builds and trains an LSTM model, saves LSTM.png, and returns prediction and RMSE.
  - Linear Regression: [LIN_REG_ALGO](file://main.py#L780-L846) fits a linear regression, saves LR.png, and returns prediction and RMSE.
- Sentiment integration: [finviz_finvader_sentiment](file://news_sentiment.py#L1-L120) is invoked to compute sentiment scores and lists.
- Recommendation: [recommending](file://main.py#L847-L905) derives BUY/SELL/HOLD based on model forecasts and sentiment.
- Visualization and results: Saves plots and renders [results.html](file://templates/dashboard.html#L170-L198) with predictions and today’s OHLC.

```mermaid
flowchart TD
Start(["User submits symbol"]) --> Hist["get_historical(symbol)"]
Hist --> YF["yfinance.download(...)"]
YF --> Empty{"Empty?"}
Empty --> |Yes| AV["Alpha Vantage fallback"]
Empty --> |No| Pre["Preprocess CSV<br/>dropna, add Code"]
AV --> Pre
Pre --> ARIMA["ARIMA_ALGO"]
Pre --> LSTM["LSTM_ALGO"]
Pre --> LR["LIN_REG_ALGO"]
ARIMA --> PlotA["Save ARIMA.png"]
LSTM --> PlotL["Save LSTM.png"]
LR --> PlotR["Save LR.png"]
Pre --> Sent["finviz_finvader_sentiment"]
ARIMA --> Rec["recommending()"]
LSTM --> Rec
LR --> Rec
Sent --> Rec
Rec --> Render["Render results.html"]
Render --> End(["Display predictions"])
```

**Diagram sources**
- [main.py](file://main.py#L550-L980)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)

**Section sources**
- [main.py](file://main.py#L550-L980)
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L45-L198)

### Trading Operations Logic
The trading operations enforce validation, calculate commission, update wallets and holdings, and record transactions. The system supports buy and sell operations, commission rates, and dividend recording.

Key functions:
- Buy order: [trade_buy](file://main.py#L268-L325)
  - Validates quantity and symbol, checks price availability, calculates total and commission, validates wallet balance, updates holdings (average buy price recalculation), credits/debits wallet, records transaction with commission.
- Sell order: [trade_sell](file://main.py#L327-L375)
  - Validates holdings, calculates proceeds, applies commission, updates quantity or deletes position, credits wallet, records transaction.
- Commission calculation: [calculate_commission](file://main.py#L176-L185)
  - Applies broker commission rate to total amount and quantizes to two decimals.
- Active broker: [get_active_broker](file://main.py#L172-L174)
  - Retrieves the active broker for commission calculations.
- Latest price: [get_latest_close_price](file://main.py#L161-L169)
  - Fetches latest close price via yfinance.

Validation and edge cases covered by tests:
- Insufficient funds for buy: [test_purchase_insufficient_funds](file://tests/test_trading_operations.py#L41-L52)
- Negative/zero/invalid quantity: [test_purchase_negative_quantity](file://tests/test_trading_operations.py#L83-L92), [test_purchase_zero_quantity](file://tests/test_trading_operations.py#L93-L102), [test_purchase_invalid_quantity](file://tests/test_trading_operations.py#L73-L82)
- Insufficient shares for sell: [test_sell_insufficient_shares](file://tests/test_trading_operations.py#L158-L167)
- Zero quantity handling: [test_sell_removes_portfolio_item_on_zero](file://tests/test_trading_operations.py#L168-L182)
- Commission calculation and deduction: [test_commission_calculation](file://tests/test_trading_operations.py#L209-L219), [test_commission_deducted_on_buy](file://tests/test_trading_operations.py#L233-L251), [test_commission_deducted_on_sell](file://tests/test_trading_operations.py#L252-L267)

```mermaid
sequenceDiagram
participant U as "User"
participant R as "Route /trade/buy or /trade/sell"
participant VP as "Validation & Price"
participant BR as "Broker & Commission"
participant DB as "Database"
participant TX as "Transaction Records"
U->>R : "Submit symbol & quantity"
R->>VP : "get_latest_close_price(symbol)"
R->>BR : "get_active_broker()"
R->>BR : "calculate_commission(total)"
alt "Buy"
R->>DB : "Check wallet balance"
R->>DB : "Upsert Company"
R->>DB : "Update or Insert PortfolioItem"
R->>DB : "Update User.wallet_balance"
R->>TX : "Insert BUY transaction"
else "Sell"
R->>DB : "Check holdings"
R->>DB : "Update PortfolioItem.quantity or delete"
R->>DB : "Update User.wallet_balance"
R->>TX : "Insert SELL transaction"
end
R-->>U : "Flash message & redirect"
```

**Diagram sources**
- [main.py](file://main.py#L268-L375)
- [main.py](file://main.py#L161-L185)

**Section sources**
- [main.py](file://main.py#L268-L375)
- [main.py](file://main.py#L161-L185)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L13-L204)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L206-L348)

### Portfolio Valuation and Performance Metrics
Portfolio valuation and performance metrics are computed on the dashboard and validated by tests.

Key computations:
- Total invested: Sum of average buy price × quantity for all holdings.
- Current portfolio value: Sum of current price × quantity for each holding.
- Profit/Loss: Current value minus total invested.
- Percentage return: (Profit / Total invested) × 100.
- Live price retrieval: [get_latest_close_price](file://main.py#L161-L169) used in dashboard and tests.

Validation covered by tests:
- Total invested calculation: [test_total_invested_calculation](file://tests/test_portfolio_management.py#L165-L194)
- Current portfolio value: [test_current_portfolio_value](file://tests/test_portfolio_management.py#L195-L208)
- Profit/Loss computation: [test_portfolio_profit_loss](file://tests/test_portfolio_management.py#L209-L224)
- Percentage return: [test_portfolio_percentage_return](file://tests/test_portfolio_management.py#L225-L236)

```mermaid
flowchart TD
Start(["Load Dashboard"]) --> Items["Query PortfolioItems for user"]
Items --> Invested["Sum(avg_buy_price × quantity)"]
Items --> Prices["For each item: get_latest_close_price(symbol)"]
Prices --> Current["Sum(current_price × quantity)"]
Invested --> Metrics["Compute P/L = Current - Invested"]
Current --> Metrics
Invested --> Return["Compute % Return = (P/L / Invested) * 100"]
Metrics --> Render["Render totals on dashboard"]
Return --> Render
```

**Diagram sources**
- [main.py](file://main.py#L251-L266)
- [main.py](file://main.py#L161-L169)

**Section sources**
- [main.py](file://main.py#L251-L266)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L162-L236)

### Dividend Recording
Dividend recording credits the user’s wallet and logs a transaction. The operation validates holdings and amount per share.

Key function:
- [record_dividend](file://main.py#L398-L433)
  - Validates amount per share > 0, validates company and holdings, computes total amount, credits wallet, inserts Dividend and Transaction records.

Validation covered by tests:
- Valid dividend recording: [test_record_dividend](file://tests/test_portfolio_management.py#L277-L292)
- Non-existent symbol handling: [test_dividend_invalid_symbol](file://tests/test_portfolio_management.py#L293-L306)
- Negative amount handling: [test_dividend_negative_amount](file://tests/test_portfolio_management.py#L307-L316)

```mermaid
sequenceDiagram
participant U as "User"
participant R as "Route /dividends/record"
participant DB as "Database"
participant TX as "Transaction"
U->>R : "Submit symbol & amount_per_share"
R->>DB : "Validate company & holdings"
R->>DB : "Compute total_amount = amount_per_share × quantity"
R->>DB : "Credit User.wallet_balance"
R->>DB : "Insert Dividend record"
R->>TX : "Insert DIVIDEND transaction"
R-->>U : "Flash message & redirect"
```

**Diagram sources**
- [main.py](file://main.py#L398-L433)

**Section sources**
- [main.py](file://main.py#L398-L433)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L274-L316)

### State Management and Transaction Atomicity
State management patterns:
- Session-based authentication: [login_required](file://main.py#L139-L152) decorator enforces login and role checks.
- CSRF protection: [verify_csrf](file://main.py#L129-L134) validates CSRF tokens.
- Session storage: [generate_csrf_token](file://main.py#L121-L127) stores CSRF token in session.
- User context: [get_current_user](file://main.py#L154-L159) loads current user from session.

Transaction atomicity:
- Each route performs a single commit after all database changes are staged. While explicit SELECT FOR UPDATE is not shown in the referenced code, the tests demonstrate that database state is consistent after operations (e.g., purchases, sales, dividends). For production-grade atomicity, consider wrapping critical sections in explicit database transactions and locks.

```mermaid
sequenceDiagram
participant C as "Client"
participant S as "Session"
participant A as "Auth Decorator"
participant CT as "CSRF Token"
participant R as "Route Handler"
C->>S : "Store user_id, user_role"
C->>CT : "Store CSRF token"
C->>A : "Call route with @login_required"
A->>S : "Verify user_id & user_role"
A->>CT : "Verify CSRF token"
A->>R : "Execute route"
R-->>C : "Commit changes"
```

**Diagram sources**
- [main.py](file://main.py#L121-L159)

**Section sources**
- [main.py](file://main.py#L121-L159)
- [conftest.py](file://tests/conftest.py#L128-L144)

### Error Handling and Data Consistency
Error handling patterns:
- Prediction pipeline gracefully handles invalid symbols and model failures; tests assert graceful responses and fallback behavior.
- Trading routes validate inputs and flash user-friendly messages on failures (insufficient funds, insufficient shares, invalid quantities).
- Portfolio routes rely on live price retrieval; tests validate calculations under mocked prices.

Consistency requirements:
- Wallet balance updates must be atomic with transaction insertions.
- PortfolioItem updates must preserve average buy price and quantity consistency.
- Dividend recording must credit wallet and create transaction records atomically.

Examples of complex operations:
- Batch predictions: The existing pipeline runs ARIMA, LSTM, and Linear Regression in sequence for a single symbol. Extending to batch predictions involves iterating over multiple symbols and aggregating results.
- Portfolio rebalancing simulations: The system simulates trades by updating wallet balances and holdings without real brokerage execution. A rebalancing simulation could compute target allocations, generate synthetic buy/sell orders, and aggregate transaction costs.

**Section sources**
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L152-L178)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L13-L204)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L162-L236)

## Dependency Analysis
The business logic depends on:
- Flask routes and decorators for session and CSRF management.
- SQLAlchemy models for persistence.
- External libraries for data retrieval, modeling, and plotting.
- Sentiment analysis module for news-based sentiment.

```mermaid
graph TB
M["main.py"]
NS["news_sentiment.py"]
T1["test_prediction_pipeline.py"]
T2["test_trading_operations.py"]
T3["test_portfolio_management.py"]
C["conftest.py"]
M --> NS
T1 --> M
T2 --> M
T3 --> M
C --> T1
C --> T2
C --> T3
```

**Diagram sources**
- [main.py](file://main.py#L1-L120)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L1-L120)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L1-L120)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L1-L120)
- [conftest.py](file://tests/conftest.py#L1-L120)

**Section sources**
- [main.py](file://main.py#L1-L120)
- [news_sentiment.py](file://news_sentiment.py#L1-L120)
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L1-L120)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L1-L120)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L1-L120)
- [conftest.py](file://tests/conftest.py#L1-L120)

## Performance Considerations
- Model execution: ARIMA, LSTM, and Linear Regression are computationally intensive. Consider batching predictions and caching results for frequently accessed symbols.
- Data retrieval: Prefer yfinance for live data; use Alpha Vantage fallback only when necessary to minimize latency.
- Visualization: Save plots to static files to avoid recomputing visuals on every request.
- Sentiment analysis: Use caching and rate-limiting to avoid repeated API calls.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Invalid stock symbol: The prediction pipeline returns an error page when yfinance fails to fetch data. Ensure the symbol is valid and accessible.
- Insufficient funds for buy: Route checks wallet balance including commission and prevents execution if insufficient.
- Insufficient shares for sell: Route validates holdings and rejects sell orders exceeding owned quantity.
- Invalid quantity inputs: Routes validate integer quantities and reject negative or zero values.
- Dividend recording errors: Route validates amount per share > 0 and holdings exist.

**Section sources**
- [test_prediction_pipeline.py](file://tests/test_prediction_pipeline.py#L57-L64)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L41-L52)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L158-L167)
- [test_trading_operations.py](file://tests/test_trading_operations.py#L73-L102)
- [test_portfolio_management.py](file://tests/test_portfolio_management.py#L293-L306)

## Conclusion
The business logic layer integrates data retrieval, preprocessing, multiple ML models, sentiment analysis, and trading operations into a cohesive workflow. The tests validate end-to-end behavior, error handling, and data consistency. Portfolio valuation and performance metrics are computed accurately using live price retrieval. State management relies on Flask sessions and CSRF protection. For production deployments, consider explicit transaction boundaries and database locks to guarantee atomicity and consistency.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Portfolio DFD Diagrams
The portfolio DFD diagrams illustrate the interactions among user, portfolio management functions, and data stores.

```mermaid
flowchart LR
User["User"]
subgraph P2["P2: Portfolio Management (Level 1)"]
P2_1["P2.1: Place Buy Order"]
P2_2["P2.2: Place Sell Order"]
P2_3["P2.3: Record Dividend"]
P2_4["P2.4: View Portfolio & Wallet"]
end
DS_User[(D1: User DB - Wallet)]
DS_Portfolio[(D3: Portfolio DB)]
DS_Txn[(D4: Transaction DB)]
DS_Dividend[(D5: Dividend DB)]
User --> |"Buy request: symbol & qty"| P2_1
P2_1 --> |"Update wallet & holdings"| DS_User
P2_1 --> |"Insert BUY transaction"| DS_Txn
P2_1 --> |"Updated view"| User
User --> |"Sell request: symbol & qty"| P2_2
P2_2 --> |"Update wallet & holdings"| DS_User
P2_2 --> |"Insert SELL transaction"| DS_Txn
P2_2 --> |"Updated view"| User
User --> |"Dividend info: symbol & amount"| P2_3
P2_3 --> |"Increase wallet"| DS_User
P2_3 --> |"Insert dividend record"| DS_Dividend
P2_3 --> |"Insert DIVIDEND transaction"| DS_Txn
User --> |"Dashboard request"| P2_4
P2_4 --> |"Read wallet"| DS_User
P2_4 --> |"Read holdings"| DS_Portfolio
P2_4 --> |"Read history"| DS_Txn
P2_4 --> |"Dashboard data"| User
```

**Diagram sources**
- [docs/diagrams/dfd_portfolio_level1.md](file://docs/diagrams/dfd_portfolio_level1.md#L1-L37)
- [docs/diagrams/exported/dfd_portfolio_level1.mmd](file://docs/diagrams/exported/dfd_portfolio_level1.mmd#L1-L35)
- [docs/diagrams/gallery.html](file://docs/diagrams/gallery.html#L201-L214)