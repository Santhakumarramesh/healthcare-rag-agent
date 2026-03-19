# 🤝 Contributing to Healthcare AI Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

---

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/healthcare-rag-agent.git
   cd healthcare-rag-agent
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements-local.txt
   ```
5. **Make your changes**
6. **Test your changes**
   ```bash
   pytest tests/
   ```
7. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

---

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **Formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for linting
- **Type hints**: Use type hints where possible
- **Docstrings**: Use Google-style docstrings

### Commit Messages

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add multimodal image analysis
fix: resolve timeout in report analyzer
docs: update API documentation
```

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_intelligence.py

# With coverage
pytest --cov=. tests/
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Include docstrings

Example:
```python
def test_query_routing():
    """Test that router correctly classifies query types."""
    router = RouterAgent()
    result = router.route("What are diabetes symptoms?")
    assert result["type"] == "symptom_check"
```

---

## 🏗️ Architecture Guidelines

### Adding New Features

1. **Services** (`services/`) - Business logic
2. **Agents** (`agents/`) - AI agents
3. **API** (`api/`) - REST endpoints
4. **UI** (`streamlit_app/`) - Frontend

### File Organization

- Keep files focused and single-purpose
- Use clear, descriptive names
- Add docstrings to all modules
- Import from `utils/config.py` for configuration

---

## 🔐 Security

### Important Rules

- **Never commit API keys** - Use environment variables
- **Never commit `.env` files** - Use `.env.example` as template
- **Hash passwords** - Use bcrypt
- **Validate inputs** - Sanitize all user inputs
- **Log security events** - Use audit service

### Pre-commit Hooks

The project uses pre-commit hooks to prevent secrets from being committed:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📚 Documentation

### When to Update Docs

- **New features** - Update README and feature docs
- **API changes** - Update API documentation
- **Breaking changes** - Update CHANGELOG
- **Configuration** - Update `.env.example`

### Documentation Files

- `README.md` - Main project documentation
- `USER_GUIDE.md` - User manual
- `ARCHITECTURE.md` - System design
- `docs/features/` - Feature-specific docs

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try latest version
3. Reproduce the bug
4. Gather logs and error messages

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 14]
- Python: [e.g., 3.11]
- Version: [e.g., 1.0.0]

**Logs**
```
Paste relevant logs here
```
```

---

## 💡 Feature Requests

### Suggesting Features

1. Check existing issues and roadmap
2. Describe the problem it solves
3. Explain the proposed solution
4. Consider alternatives

### Feature Request Template

```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives**
What other approaches did you consider?

**Additional Context**
Any other information
```

---

## 🎯 Areas for Contribution

### High Priority

- [ ] Additional medical knowledge sources
- [ ] More comprehensive tests
- [ ] Performance optimizations
- [ ] UI/UX improvements
- [ ] Documentation improvements

### Medium Priority

- [ ] Additional language support
- [ ] Mobile-friendly UI
- [ ] Export functionality
- [ ] Advanced visualizations

### Advanced

- [ ] Real-time monitoring dashboard
- [ ] A/B testing framework
- [ ] Advanced analytics
- [ ] Integration with EHR systems

---

## 🔄 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG** if applicable
5. **Request review** from maintainers

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No secrets in code
- [ ] Branch is up to date with main

---

## 🤔 Questions?

- **GitHub Issues**: [Open an issue](https://github.com/Santhakumarramesh/healthcare-rag-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Santhakumarramesh/healthcare-rag-agent/discussions)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to better healthcare AI!** 🙏
