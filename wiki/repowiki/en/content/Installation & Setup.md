# Installation & Setup

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [main.py](file://main.py)
- [news_sentiment.py](file://news_sentiment.py)
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md)
</cite>

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Repository Cloning](#repository-cloning)
3. [Virtual Environment Setup](#virtual-environment-setup)
4. [Dependency Installation](#dependency-installation)
5. [API Key Configuration](#api-key-configuration)
6. [Database Initialization](#database-initialization)
7. [Running the Application](#running-the-application)
8. [Verification Steps](#verification-steps)
9. [Development vs Production Setup](#development-vs-production-setup)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)

## Prerequisites

Before installing the intelligent-stock-prediction application, ensure your system meets the following requirements:

- **Python 3.7+**: The application requires Python version 3.7 or higher. Verify your Python version by running:
  ```bash
  python --version
  ```
  or
  ```bash
  python3 --version
  ```

- **pip package manager**: Ensure pip is installed and updated to the latest version:
  ```bash
  pip install --upgrade pip
  ```

These prerequisites are essential for the proper functioning of the application and its dependencies.

**Section sources**
- [README.md](file://README.md#L106-L108)

## Repository Cloning

To begin the installation process, clone the repository from GitHub to your local machine:

```bash
git clone https://github.com/cultmt616god-ship-it/intelligent-stock-prediction.git
cd intelligent-stock-prediction
```

This will create a local copy of the repository in a directory named `intelligent-stock-prediction`. All subsequent setup steps should be performed within this directory.

**Section sources**
- [README.md](file://README.md#L112-L116)

## Virtual Environment Setup

It is recommended to use a virtual environment to isolate the application's dependencies from your system's Python environment. Create and activate a virtual environment using the following commands:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

The virtual environment prevents package conflicts and makes it easier to manage dependencies. You should see `(venv)` in your command prompt, indicating that the virtual environment is active.

**Section sources**
- [README.md](file://README.md#L118-L122)

## Dependency Installation

With the virtual environment activated, install the required Python packages using pip and the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command installs all the necessary packages listed in the requirements file, including:
- TensorFlow and Keras for deep learning
- Flask for web framework functionality
- SQLAlchemy for database operations
- YFinance for stock market data retrieval
- Alpha Vantage for financial data API access
- NLTK and TextBlob for natural language processing
- Pandas and NumPy for data manipulation

The installation may take several minutes depending on your internet connection speed.

**Section sources**
- [README.md](file://README.md#L124-L127)
- [requirements.txt](file://requirements.txt)

## API Key Configuration

The application uses several external APIs for financial data and sentiment analysis. Some of these services require API keys for access.

### Required API Keys

The following services require API keys:
- **Alpha Vantage**: Required for financial data API access
- **EODHD API**: Required for premium features
- **Finnhub Social Sentiment API**: Required for social sentiment data
- **StockGeist.ai**: Required for premium features

### Optional API Sources

The following sources do not require API keys and can be used without configuration:
- Finviz + FinVADER (scraping-based sentiment analysis)
- Tradestie WallStreetBets API (Reddit sentiment)
- Google News RSS (news sentiment)

### Setting Up API Keys

API keys should be configured using environment variables for security. Create a `.env` file in the project root directory with the following content:

```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
EODHD_API_KEY=your_eodhd_key
FINNHUB_API_KEY=your_finnhub_key
STOCKGEIST_API_KEY=your_stockgeist_key
SECRET_KEY=your_secret_key
```

Alternatively, you can set environment variables directly in your shell:

```bash
export ALPHA_VANTAGE_API_KEY="your_api_key_here"
export SECRET_KEY="your_secure_secret_key"
```

If API keys are not provided, the system will gracefully skip those sources and continue with available ones, as documented in the API_KEYS_GUIDE.md.

**Section sources**
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md#L7-L103)
- [news_sentiment.py](file://news_sentiment.py#L313-L316)
- [main.py](file://main.py#L42)

## Database Initialization

The application uses SQLite as its database backend with SQLAlchemy as the ORM. Database initialization occurs automatically when the application starts.

When you run the application for the first time, the following occurs:
1. The SQLite database file (`sams_database.db`) is created in the project root directory
2. All database tables are created based on the model definitions in `main.py`
3. The database schema is initialized with the necessary tables for users, companies, brokers, portfolio items, transactions, and dividends

The database initialization is handled by the following code in `main.py`:
```python
with app.app_context():
    db.create_all()
```

No manual database setup is required. The database will be created automatically when the application starts.

**Section sources**
- [main.py](file://main.py#L187)
- [main.py](file://main.py#L44)

## Running the Application

After completing the setup steps, you can start the application:

```bash
python main.py
```

By default, the application runs on port 5000. You can access it by navigating to `http://localhost:5000` in your web browser.

To run the application on a different port, you can modify the `app.run()` call in `main.py` or use environment variables to configure the port.

**Section sources**
- [README.md](file://README.md#L129-L132)
- [main.py](file://main.py#L960)

## Verification Steps

To verify that the installation was successful, follow these steps:

1. **Access the application**: Open your web browser and navigate to `http://localhost:5000`. You should see the application's home page.

2. **Log in with default credentials**: Use the admin credentials provided in the README:
   - **Username**: admin
   - **Email**: stockpredictorapp@gmail.com
   - **Password**: Samplepass@123

3. **Test prediction functionality**: Enter a stock symbol (e.g., "AAPL" for Apple) in the prediction form and submit. The application should display prediction results using LSTM, ARIMA, and Linear Regression models.

4. **Verify sentiment analysis**: The results page should include sentiment analysis from financial news sources, confirming that the sentiment analysis module is working.

5. **Check database creation**: Verify that the `sams_database.db` file has been created in the project root directory.

If all these steps work correctly, your installation is successful and the application is ready for use.

**Section sources**
- [README.md](file://README.md#L134-L141)

## Development vs Production Setup

### Development Setup

For development purposes, the default configuration is sufficient:
- Uses SQLite database stored as a file
- Runs on localhost with default port 5000
- Uses development secret key
- Debug mode can be enabled for easier troubleshooting

To enable debug mode, modify the `app.run()` call in `main.py`:
```python
if __name__ == '__main__':
   app.run(debug=True)
```

### Production Setup

For production deployment, additional configuration is recommended:
- **Database**: Consider using a more robust database like PostgreSQL or MySQL instead of SQLite
- **Environment variables**: Set proper environment variables for `SECRET_KEY` and `DATABASE_URL`
- **Web server**: Use a production-grade WSGI server like Gunicorn instead of the Flask development server
- **Reverse proxy**: Use Nginx or Apache as a reverse proxy for better performance and security
- **HTTPS**: Enable HTTPS for secure communication

The application already includes Gunicorn in the requirements, making it ready for production deployment.

**Section sources**
- [main.py](file://main.py#L42-L45)
- [requirements.txt](file://requirements.txt#L15)

## Troubleshooting Common Issues

### Port Conflicts

If you encounter a port conflict (e.g., "Address already in use"), you can:
1. Stop the process using the port:
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```
2. Or run the application on a different port:
   ```bash
   python main.py
   ```
   Then modify the `app.run()` call to specify a different port:
   ```python
   app.run(port=5001)
   ```

### Missing Dependencies

If you encounter import errors or missing package errors:
1. Ensure your virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For specific packages, install them individually:
   ```bash
   pip install package_name
   ```

### API Key Errors

If you encounter API key errors:
1. Verify that your API keys are correctly set in environment variables
2. Check that you're using the correct environment variable names as expected by the code
3. Ensure there are no typos in the API key values
4. If issues persist, the system will gracefully fall back to sources that don't require API keys

### Database Initialization Problems

If the database fails to initialize:
1. Check file permissions in the project directory
2. Verify that you have write permissions to create files
3. Check if there's already a `sams_database.db` file with incorrect permissions
4. Delete the database file and restart the application to recreate it

### General Debugging Tips

- Check the terminal output for error messages when starting the application
- Ensure all required packages are installed by comparing your installed packages with `requirements.txt`
- Verify Python version compatibility
- Check that the virtual environment is properly activated
- Review the API_KEYS_GUIDE.md for proper API key configuration

**Section sources**
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md#L233-L246)
- [main.py](file://main.py#L39)
- [main.py](file://main.py#L187)