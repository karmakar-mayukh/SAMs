# Developer Guide

<cite>
**Referenced Files in This Document**   
- [CONTRIBUTING.md](file://docs/CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](file://docs/CODE_OF_CONDUCT.md)
- [main.py](file://main.py)
- [news_sentiment.py](file://news_sentiment.py)
- [pytest.ini](file://pytest.ini)
- [requirements.txt](file://requirements.txt)
- [requirements_test.txt](file://requirements_test.txt)
- [conftest.py](file://tests/conftest.py)
- [test_comprehensive_framework.py](file://tests/test_comprehensive_framework.py)
- [advanced_features_demo.py](file://demos/advanced_features_demo.py)
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md)
- [ADVANCED_FEATURES.md](file://docs/ADVANCED_FEATURES.md)
- [COMPREHENSIVE_TESTING_FRAMEWORK.md](file://docs/COMPREHENSIVE_TESTING_FRAMEWORK.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Contribution Guidelines](#contribution-guidelines)
3. [Code of Conduct](#code-of-conduct)
4. [Development Environment Setup](#development-environment-setup)
5. [Testing Workflows](#testing-workflows)
6. [Coding Standards](#coding-standards)
7. [Working with ML Components](#working-with-ml-components)
8. [Frontend Assets Management](#frontend-assets-management)
9. [Database Migrations](#database-migrations)
10. [Common Development Challenges](#common-development-challenges)
11. [Extending Features](#extending-features)
12. [Onboarding for New Contributors](#onboarding-for-new-contributors)

## Introduction
This Developer Guide provides comprehensive information for contributors to the intelligent-stock-prediction project. It covers contribution guidelines, development practices, testing workflows, and best practices for extending the system's functionality. The guide is designed to help both new and experienced developers understand the project's architecture, coding standards, and development processes.

## Contribution Guidelines
The intelligent-stock-prediction project welcomes contributions from the community. The contribution process follows a structured workflow to ensure code quality and maintainability.

### Branching Strategy
The project uses a feature-branch workflow with the following conventions:
- Create feature branches from the `dev` branch for new functionality
- Create bug branches from the `dev` branch for issue resolution
- Follow specific naming conventions:
  - Feature branches: `feature/--implementation-name--`
  - Bug branches: `bug/--fix-name--`

The `main` branch is protected and only receives updates through merges from the `dev` branch, ensuring a stable production-ready codebase.

### Pull Request Workflow
The pull request process includes the following steps:
1. Fork the repository and create a feature/bug branch from `dev`
2. Implement changes with appropriate unit tests and code coverage
3. Commit changes with descriptive messages
4. Push the branch to your fork
5. Create a pull request from your feature branch to the `dev` branch
6. Request review from repository maintainers

All pull requests require two mandatory reviews before merging. Contributors should address all feedback and ensure that style checkers and validation steps pass before requesting a merge.

### Code Review Process
The code review process emphasizes clean code practices and thorough validation:
- Reviewers examine code for adherence to coding standards
- All changes must be appropriately commented for documentation generation
- New methods and classes require comprehensive documentation
- Automated tasks run on pull requests, and any failures must be addressed
- Maintainers provide feedback, and contributors must resolve all comments before merging

**Section sources**
- [CONTRIBUTING.md](file://docs/CONTRIBUTING.md#L45-L60)

## Code of Conduct
The intelligent-stock-prediction project adheres to the Contributor Covenant Code of Conduct to ensure a welcoming and inclusive community.

### Our Pledge
All members, contributors, and leaders pledge to make participation in the community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity, experience level, education, socio-economic status, nationality, appearance, race, religion, or sexual identity.

### Community Standards
Positive behaviors that contribute to a healthy community include:
- Demonstrating empathy and kindness toward others
- Respecting differing opinions, viewpoints, and experiences
- Giving and gracefully accepting constructive feedback
- Accepting responsibility for mistakes and learning from them
- Focusing on what is best for the overall community

Unacceptable behaviors include:
- Use of sexualized language or imagery
- Trolling, insults, derogatory comments, or personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Any conduct that could be considered inappropriate in a professional setting

### Enforcement
Community leaders are responsible for clarifying and enforcing the code of conduct. They have the right to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that violate these standards.

Instances of abusive or harassing behavior can be reported to the community leaders at cultmt616god-ship-it@github.com. All complaints are reviewed and investigated promptly and fairly, with privacy and security of reporters respected.

**Section sources**
- [CODE_OF_CONDUCT.md](file://docs/CODE_OF_CONDUCT.md#L1-L129)

## Development Environment Setup
Setting up a proper development environment is essential for contributing to the intelligent-stock-prediction project.

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Git for version control

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/cultmt616god-ship-it/intelligent-stock-prediction.git
cd intelligent-stock-prediction
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install production dependencies:
```bash
pip install -r requirements.txt
```

4. Install testing dependencies:
```bash
pip install -r requirements_test.txt
```

### IDE Configuration
For optimal development experience, configure your IDE with the following:
- Python interpreter set to the virtual environment
- Code formatting tools (autopep8, black) for consistent style
- Linting tools (pylint, flake8) for code quality checks
- Debugging configuration for Flask applications
- Environment variables management for API keys

### Debugging Tools
The project includes comprehensive logging and monitoring capabilities:
- Configure logging levels in the application settings
- Use Flask's debug mode during development
- Implement breakpoints and step-through debugging
- Monitor application logs for error tracking
- Utilize the error handling and monitoring demo scripts for testing

**Section sources**
- [README.md](file://README.md#L104-L135)
- [requirements.txt](file://requirements.txt#L1-L19)
- [requirements_test.txt](file://requirements_test.txt#L1-L36)

## Testing Workflows
The intelligent-stock-prediction project has a comprehensive testing framework to ensure code reliability and robustness.

### Test Structure
The testing framework is organized into multiple suites covering different aspects:
- **Unit tests**: Fast, isolated tests for individual components
- **Integration tests**: Tests for component interactions
- **ML tests**: Tests for machine learning model functionality
- **Security tests**: Security and vulnerability assessments
- **Slow tests**: Time-consuming tests that can be excluded from regular runs

### Running Tests
To execute the test suite:
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_comprehensive_framework.py

# Run tests with coverage
python -m pytest --cov=.
```

The pytest configuration in `pytest.ini` defines test discovery patterns, markers, and coverage options. Test paths are configured to discover tests in the `tests` directory.

### Test Fixtures
The project uses pytest fixtures for test setup and teardown:
- `test_app`: Creates a test Flask application instance
- `client`: Provides a test client for the Flask application
- `test_db`: Creates a fresh in-memory database for each test
- Various sample data fixtures (users, companies, transactions) for testing

These fixtures ensure consistent test environments and proper resource cleanup.

### Continuous Integration
The testing framework is designed for CI/CD integration with GitHub Actions. The workflow includes:
- Automatic test execution on push and pull requests
- Test coverage reporting
- Performance monitoring
- Detailed reporting and diagnostics

**Section sources**
- [pytest.ini](file://pytest.ini#L1-L56)
- [conftest.py](file://tests/conftest.py#L1-L273)
- [test_comprehensive_framework.py](file://tests/test_comprehensive_framework.py#L1-L425)
- [COMPREHENSIVE_TESTING_FRAMEWORK.md](file://docs/COMPREHENSIVE_TESTING_FRAMEWORK.md#L1-L261)

## Coding Standards
Maintaining consistent coding standards is crucial for code readability and maintainability.

### Naming Conventions
- Use descriptive variable and function names
- Follow PEP 8 naming conventions:
  - Variables and functions: snake_case
  - Classes: PascalCase
  - Constants: UPPER_CASE
- Use meaningful names that reflect the purpose of the code
- Avoid abbreviations unless they are widely understood

### Code Documentation
All code should be properly documented:
- Use docstrings for modules, classes, and functions
- Include type hints for function parameters and return values
- Add comments for complex logic or algorithms
- Ensure documentation is updated when code changes
- Use the `generateDocsForDebug` or `generateDocsForRelease` tasks to generate updated documentation

### Code Quality
The project emphasizes clean code practices:
- Keep functions focused and small
- Avoid code duplication through proper abstraction
- Write self-documenting code
- Handle errors gracefully with appropriate logging
- Follow the principle of least surprise

**Section sources**
- [CONTRIBUTING.md](file://docs/CONTRIBUTING.md#L37-L39)
- [ADVANCED_FEATURES.md](file://docs/ADVANCED_FEATURES.md#L1-L298)

## Working with ML Components
The intelligent-stock-prediction project includes several machine learning components that require specific development practices.

### Prediction Models
The system implements three predictive models:
- **LSTM Neural Network**: Deep learning model for complex pattern recognition
- **ARIMA**: Classical statistical model for time series forecasting
- **Linear Regression**: Simple baseline model for comparison

When working with ML components:
- Ensure proper data preprocessing and normalization
- Validate model inputs and outputs
- Monitor model performance metrics
- Implement proper error handling for model failures
- Consider computational efficiency and memory usage

### Sentiment Analysis
The sentiment analysis system supports multiple sources:
- Finviz + FinVADER (no API key required)
- EODHD API (API key required)
- Alpha Vantage News & Sentiments API (API key required)
- Tradestie WallStreetBets API (no API key required)
- Finnhub Social Sentiment API (API key required)
- StockGeist.ai (API key required)
- Google News/Yahoo Finance RSS (no API key required)

The system implements a fallback mechanism that prioritizes sources:
1. Finviz (Primary Source - Fast & Reliable)
2. Investing.com (Secondary Source - Selenium scraping)
3. EODHD API (API Fallback)
4. Alpha Vantage News API (Enhanced API Source)
5. Tradestie Reddit API (Social Sentiment Source)
6. Finnhub Social Sentiment API (Multi-Source Social)
7. Google News RSS (Last Resort)

### Advanced ML Features
The project includes several advanced ML features:
- **Batch Processing**: Multi-symbol sentiment analysis with queue processing
- **Hybrid Scoring**: Combining FinVADER with API signals for improved accuracy
- **Custom Lexicons**: Domain-specific sentiment terms for context-aware analysis
- **Performance Optimizations**: Caching and efficiency features

These features are demonstrated in the `advanced_features_demo.py` script and documented in `ADVANCED_FEATURES.md`.

**Section sources**
- [news_sentiment.py](file://news_sentiment.py)
- [ADVANCED_FEATURES.md](file://docs/ADVANCED_FEATURES.md#L1-L298)
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md#L1-L246)
- [advanced_features_demo.py](file://demos/advanced_features_demo.py#L1-L154)

## Frontend Assets Management
The project's frontend assets are managed to ensure a responsive and user-friendly interface.

### Asset Structure
Frontend assets are organized in the `static/` directory:
- CSS files for styling (Bootstrap, custom styles)
- JavaScript files for interactivity (D3.js, jQuery)
- Font files and icons
- Custom scripts for specific components

### Responsive Design
The interface uses Bootstrap for responsive design:
- Mobile-first approach
- Grid system for layout
- Responsive components and utilities
- Cross-browser compatibility

### Data Visualization
The project uses D3.js for interactive data visualization:
- Stock price charts
- Prediction accuracy visualizations
- Portfolio performance metrics
- Interactive summary widgets

### Asset Optimization
Best practices for frontend asset management include:
- Minifying CSS and JavaScript files
- Using appropriate image formats and compression
- Implementing lazy loading for non-critical assets
- Caching static assets for improved performance

**Section sources**
- [static/](file://static/)
- [templates/](file://templates/)
- [README.md](file://README.md#L66-L72)

## Database Migrations
The project uses SQLAlchemy ORM for database operations with SQLite as the database management system.

### Database Schema
The system uses a relational database with the following key entities:
- **User**: Authentication and profile information
- **Company**: Stock information and metadata
- **Broker**: Commission configuration
- **PortfolioItem**: User holdings tracking
- **Transaction**: Buy/sell records with commission tracking
- **Dividend**: Dividend payout records

### Migration Strategy
Database changes are managed through the following process:
- Create migration scripts for schema changes
- Test migrations in a development environment
- Document migration steps and potential issues
- Implement rollback procedures for failed migrations
- Update database documentation after migrations

### Data Integrity
The system ensures data integrity through:
- Proper foreign key constraints
- Validation rules for data entry
- Transaction management for critical operations
- Regular data backups
- Data consistency checks

**Section sources**
- [main.py](file://main.py)
- [README.md](file://README.md#L83-L90)

## Common Development Challenges
Developers may encounter several common challenges when working on the intelligent-stock-prediction project.

### API Key Management
Several sentiment sources require API keys:
- Store API keys in environment variables, not in code
- Use the `.env` file for local development (add to `.gitignore`)
- Implement graceful degradation when API keys are not provided
- Be aware of rate limits for each API service

### Rate Limiting
External APIs have rate limits that must be respected:
- Alpha Vantage: 5 calls/minute (free), 1200 calls/minute (premium)
- Finnhub: 60 calls/minute (free)
- EODHD: Varies by plan
- StockGeist: 10,000 credits/month (free tier)

Implement caching and request batching to minimize API calls.

### Data Consistency
Ensure data consistency across different components:
- Synchronize stock data with sentiment analysis
- Maintain accurate portfolio calculations
- Handle time zone differences in data timestamps
- Validate data before processing

### Performance Optimization
Optimize performance for resource-intensive operations:
- Use caching for frequently accessed data
- Implement efficient algorithms for data processing
- Optimize database queries with proper indexing
- Monitor memory usage and prevent leaks

**Section sources**
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md#L1-L246)
- [ADVANCED_FEATURES.md](file://docs/ADVANCED_FEATURES.md#L1-L298)

## Extending Features
The project is designed to be extensible, allowing contributors to add new features and functionality.

### Adding New Prediction Models
To add a new prediction model:
1. Create a new module in the appropriate directory
2. Implement the model class with required methods
3. Add configuration options for the model
4. Create unit tests for the model
5. Update documentation with usage instructions
6. Integrate the model with the existing prediction pipeline

### Integrating Additional Data Sources
To integrate a new data source:
1. Create a new module for the data source
2. Implement data retrieval and parsing functions
3. Add error handling for connectivity issues
4. Implement caching if appropriate
5. Create unit tests for the integration
6. Update the fallback mechanism to include the new source
7. Document the new source and its configuration

### Maintaining Code Quality
When extending features, maintain code quality by:
- Following existing coding standards
- Writing comprehensive unit tests
- Ensuring proper documentation
- Performing thorough code reviews
- Testing for performance impact
- Validating backward compatibility

**Section sources**
- [CONTRIBUTING.md](file://docs/CONTRIBUTING.md#L15-L20)
- [ADVANCED_FEATURES.md](file://docs/ADVANCED_FEATURES.md#L1-L298)

## Onboarding for New Contributors
New contributors should follow these steps to get started with the intelligent-stock-prediction project.

### Getting Started
1. Read the README.md for project overview and installation instructions
2. Review the CONTRIBUTING.md for contribution guidelines
3. Study the CODE_OF_CONDUCT.md for community standards
4. Explore the documentation in the docs/ directory
5. Set up the development environment

### Understanding the Codebase
To understand the codebase:
- Start with the main.py file as the application entry point
- Study the news_sentiment.py module for sentiment analysis implementation
- Review the database models in the main.py file
- Examine the templates in the templates/ directory
- Look at the test files to understand expected behavior

### First Contribution
For your first contribution:
- Start with minor issues like typos or basic layout changes
- Fix issues that have been raised in the issue tracker
- Add or modify existing features with proper unit testing
- Ensure code coverage is maintained or improved
- Follow the pull request workflow and code review process

### Resources
Additional resources for new contributors:
- [API_KEYS_GUIDE.md](file://docs/API_KEYS_GUIDE.md) for API key information
- [ADVANCED_FEATURES.md](file://docs/ADVANCED_FEATURES.md) for advanced functionality
- [COMPREHENSIVE_TESTING_FRAMEWORK.md](file://docs/COMPREHENSIVE_TESTING_FRAMEWORK.md) for testing details
- Demo scripts in the demos/ directory for usage examples

**Section sources**
- [CONTRIBUTING.md](file://docs/CONTRIBUTING.md#L21-L43)
- [README.md](file://README.md#L1-L202)
- [docs/](file://docs/)