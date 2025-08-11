# JOJIAI - AI-Powered Project

[![CI Pipeline](https://github.com/gtsurkav-sudo/JOJIAI/actions/workflows/ci.yml/badge.svg)](https://github.com/gtsurkav-sudo/JOJIAI/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/gtsurkav-sudo/JOJIAI/branch/main/graph/badge.svg)](https://codecov.io/gh/gtsurkav-sudo/JOJIAI)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AI-powered project with comprehensive CI/CD pipeline, automated testing, and quality assurance.

## 🚀 Features

- **Comprehensive CI/CD Pipeline**: Automated testing, linting, and deployment
- **Multi-Python Support**: Compatible with Python 3.10, 3.11, and 3.12
- **Quality Assurance**: 80%+ code coverage requirement
- **Security Scanning**: Automated security vulnerability detection
- **Code Formatting**: Consistent code style with Black and Flake8

## 🧹 Memory Maintenance

JOJIAI includes comprehensive memory maintenance capabilities to ensure optimal performance and compliance with data retention policies.

## Features

- **Automatic TTL Cleanup**: Configurable time-to-live cleanup for old records
- **User Data Deletion**: GDPR-compliant user data deletion (right to be forgotten)  
- **Soft Delete Support**: Preserves audit trails while marking records as deleted
- **Batch Processing**: Efficient handling of large datasets
- **Automated Scheduling**: Weekly maintenance via GitHub Actions

## Quick Start

```python
from src.maintenance.memory_maintenance import CompatDbClient

# Initialize client
client = CompatDbClient()

# Clean old records (30+ days)
client.cleanup_old_records("user_sessions", days_old=30)

# Delete user data (GDPR compliance)
client.forget_user("user123")

# Health check
health = client.health_check()
```

## CI/CD Integration

Memory maintenance runs automatically every Sunday at 2 AM UTC. Manual triggers are available through GitHub Actions for immediate cleanup operations.

**Supported Operations:**
- `ttl_cleanup` - Remove old records based on age
- `forget_user` - Delete all data for a specific user
- `health_check` - Verify database connectivity
- `full_maintenance` - Comprehensive cleanup across all tables

## Configuration

Set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

## Documentation

For detailed documentation, see [`docs/memory_maintenance.md`](docs/memory_maintenance.md).

---

## 📋 Requirements

- Python 3.10 or higher
- pip (Python package installer)

## 🛠️ Installation

### Development Installation

```bash
# Clone the repository
git clone https://github.com/gtsurkav-sudo/JOJIAI.git
cd JOJIAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test]"
```

### Production Installation

```bash
pip install jojiai
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-branch --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Slow tests excluded
pytest -m "not slow"
```

## 🔍 Code Quality

### Linting and Formatting
```bash
# Format code with Black
black src/ tests/

# Check code style
black --check src/ tests/

# Run Flake8 linter
flake8 src/ tests/

# Run type checking
mypy src/
```

### Security Scanning
```bash
# Run security scan
bandit -r src/
```

## 🚀 Запуск CI локально

### Предварительные требования
- Python 3.10, 3.11, или 3.12
- Git
- Make (опционально)

### Шаги для локального запуска CI

1. **Установка зависимостей**:
   ```bash
   pip install -e ".[dev,test]"
   ```

2. **Форматирование кода**:
   ```bash
   black src/ tests/
   ```

3. **Проверка стиля кода**:
   ```bash
   black --check --diff src/ tests/
   flake8 src/ tests/
   ```

4. **Запуск тестов с покрытием**:
   ```bash
   pytest --cov=src --cov-branch --cov-report=html --cov-report=xml --cov-report=term-missing --cov-fail-under=80
   ```

5. **Проверка безопасности**:
   ```bash
   bandit -r src/ -f json -o bandit-report.json
   ```

6. **Просмотр отчета о покрытии**:
   ```bash
   # Откройте htmlcov/index.html в браузере
   open htmlcov/index.html  # macOS
   xdg-open htmlcov/index.html  # Linux
   start htmlcov/index.html  # Windows
   ```

### Автоматизация с Make (опционально)

Создайте `Makefile` для упрощения команд:

```makefile
.PHONY: install format lint test security ci

install:
	pip install -e ".[dev,test]"

format:
	black src/ tests/

lint:
	black --check --diff src/ tests/
	flake8 src/ tests/

test:
	pytest --cov=src --cov-branch --cov-report=html --cov-report=xml --cov-report=term-missing --cov-fail-under=80

security:
	bandit -r src/ -f json -o bandit-report.json

ci: format lint test security
	@echo "✅ All CI checks passed!"
```

Затем запускайте:
```bash
make ci
```

### Pre-commit хуки

Установите pre-commit хуки для автоматической проверки:

```bash
# Установка pre-commit
pip install pre-commit

# Установка хуков
pre-commit install

# Запуск на всех файлах
pre-commit run --all-files
```

## 📊 CI/CD Pipeline

Наш CI/CD pipeline включает:

### ✅ Автоматические проверки
- **Форматирование**: Black code formatter
- **Линтинг**: Flake8 с дополнительными плагинами
- **Тестирование**: pytest с покрытием ≥80%
- **Безопасность**: Bandit security scanner
- **Типизация**: MyPy type checking

### 🔄 Matrix Testing
- Python 3.10, 3.11, 3.12
- Ubuntu Latest
- Параллельное выполнение

### 📈 Отчеты
- HTML отчеты о покрытии
- XML отчеты для Codecov
- JSON отчеты безопасности
- Артефакты в GitHub Actions

### ⚡ Оптимизация
- Кеширование pip зависимостей
- Параллельное выполнение тестов
- Быстрый fail при критических ошибках

## 🏗️ Project Structure

```
JOJIAI/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
├── src/
│   └── jojiai/
│       ├── __init__.py         # Package initialization
│       ├── core.py             # Core functionality
│       └── utils.py            # Utility functions
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Pytest configuration
├── reports/                    # Project reports
├── pyproject.toml              # Project configuration
├── .flake8                     # Flake8 configuration
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Run the full CI pipeline locally (`make ci`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feat/amazing-feature`)
7. Open a Pull Request

### Contribution Guidelines

- Follow the existing code style (Black + Flake8)
- Write tests for new functionality
- Maintain or improve code coverage (≥80%)
- Update documentation as needed
- Add type hints for new functions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/gtsurkav-sudo/JOJIAI)
- [Issues](https://github.com/gtsurkav-sudo/JOJIAI/issues)
- [CI/CD Pipeline](https://github.com/gtsurkav-sudo/JOJIAI/actions)
- [Coverage Reports](https://codecov.io/gh/gtsurkav-sudo/JOJIAI)

## 📞 Support

If you have any questions or need help, please:

1. Check the [documentation](https://github.com/gtsurkav-sudo/JOJIAI/wiki)
2. Search [existing issues](https://github.com/gtsurkav-sudo/JOJIAI/issues)
3. Create a [new issue](https://github.com/gtsurkav-sudo/JOJIAI/issues/new)

---

Made with ❤️ by the JOJIAI Team
