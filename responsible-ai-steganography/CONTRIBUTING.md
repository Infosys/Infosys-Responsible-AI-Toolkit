# Contributing to Responsible AI Steganography Detection

🎉 Thank you for your interest in contributing to the **Responsible AI Steganography Detection** module!

We appreciate all contributions, whether it's fixing bugs, improving documentation, adding features, or suggesting enhancements.

## 📋 How to Contribute

There are several ways you can contribute:

✅ **Report Issues**: Found a bug? Create an issue with the [Bug] template  
✅ **Suggest Features**: Have a great idea? Open a feature request  
✅ **Improve Documentation**: Spotted a typo? Help improve our documentation  
✅ **Fix Bugs**: Help us squash bugs by submitting patches  
✅ **Add Features**: Implement new detection techniques or capabilities  

## 🔥 Development Setup

### Prerequisites
- Python 3.11+
- pip package manager
- Virtual environment (recommended)
- Git

### Local Setup
```bash
# Clone the repository
git clone <repository-url>
cd responsible-ai-steganography

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements/requirements.txt

# Run tests
python -m pytest tests/ -v

# Run demo
python demo.py
```

## 🚦 Development Guidelines

### Branching Strategy
- All development happens on feature branches off `dev`
- Use branch naming: `feature/STEGO-XXX-description`
- Never commit directly to `main` or `dev`

### Code Quality Standards
```bash
# Run linting
flake8 src/ --max-line-length=120

# Auto-format code
black src/ --line-length=120

# Type checking
mypy src/

# Run tests
python -m pytest tests/ -v --cov=src
```

### Commit Message Format
Follow conventional commit format:
```
feat: add new detection algorithm for Unicode steganography
fix: resolve false positive in whitespace detection
docs: update API documentation with examples
test: add comprehensive tests for zero-width detection
refactor: optimize frequency analysis algorithm
```

### Code Standards
- Use meaningful variable and function names
- Keep functions small and focused (<50 lines preferred)
- Add type hints to all functions
- Write docstrings for all public methods
- Follow PEP 8 style guidelines
- Maintain test coverage >80%

## 🧪 Testing Requirements

### Test Types
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and workflows
- **Security Tests**: Validate input handling and security features
- **Performance Tests**: Ensure acceptable response times

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_steganography_api.py -v
```

### Test Guidelines
- Write tests for all new features
- Ensure tests are deterministic and isolated
- Use descriptive test names
- Include edge cases and error conditions
- Mock external dependencies

## 🔒 Security Requirements

### Security Checks
All contributions must pass:
- ✅ Static code analysis (flake8, mypy)
- ✅ Dependency vulnerability scanning
- ✅ Input validation testing
- ✅ No secrets in code
- ✅ Security-focused code review

### Security Best Practices
- Validate all inputs thoroughly
- Use secure coding practices (no eval, exec, etc.)
- Handle errors gracefully without exposing internals
- Log security events appropriately
- Follow OWASP guidelines

## 📝 Pull Request Process

### Before Creating PR
1. ✅ Run all quality checks (linting, testing, security)
2. ✅ Update documentation if needed
3. ✅ Add/update tests for new functionality
4. ✅ Verify no breaking changes
5. ✅ Test locally with demo script

### PR Requirements
Every PR must include:
- **Linked Issue**: Reference the issue/ticket being addressed
- **Reuse Justification**: If adding new code, explain why existing solutions don't work
- **Test Coverage**: Maintain or improve test coverage
- **Documentation**: Update README, API docs, or comments as needed
- **Migration Notes**: If changes are breaking, provide migration guidance

### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Security validation performed

## Reuse Justification
Explain why new code was necessary instead of reusing existing solutions.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## 🎯 Areas for Contribution

### High-Priority Areas
1. **Detection Algorithms**: New steganography detection techniques
2. **Performance Optimization**: Improve processing speed and memory usage
3. **Language Support**: Multi-language text analysis capabilities
4. **Integration**: Better integration with other toolkit modules
5. **Documentation**: Examples, tutorials, and API documentation

### Detection Techniques to Add
- **Semantic Steganography**: Natural language generation patterns
- **Synonym Substitution**: Word replacement patterns
- **Punctuation Encoding**: Using punctuation for data hiding
- **Font-Based Techniques**: Different font/style usage patterns
- **Structural Patterns**: Paragraph and sentence structure analysis

### Technical Improvements
- **Caching**: Implement result caching for performance
- **Batch Processing**: Optimize batch operations
- **Async Processing**: Add async API endpoints
- **Monitoring**: Enhanced metrics and observability
- **Configuration**: Better configuration management

## 🏗️ Architecture Guidelines

### Module Structure
```
src/app/
├── services/           # Core detection logic
├── controllers/        # API endpoints
├── models/            # Data models
├── utils/             # Utility functions
└── config/            # Configuration management
```

### Design Principles
- **Modularity**: Each detection technique is a separate module
- **Extensibility**: Easy to add new detection methods
- **Performance**: Optimize for speed and memory usage
- **Security**: Input validation and secure coding practices
- **Testability**: Design for easy testing and mocking

## 📚 Resources

### Documentation
- [README.md](README.md) - Main documentation
- [API Documentation](http://localhost:5001/rai/v1/steganography/docs) - Swagger API docs
- [Security Policy](SECURITY.md) - Security guidelines

### External Resources
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Python Security Guidelines](https://python.org/dev/security/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/security/)

## 📞 Getting Help

### Community Support
- **Email**: infosysraitoolkit@infosys.com
- **Issues**: Create an issue for questions or problems
- **Discussions**: Use GitHub Discussions for general questions

### Development Questions
- Check existing issues and discussions first
- Provide minimal reproducible examples
- Include environment details (Python version, OS, etc.)
- Be respectful and constructive in communications

## 🎖️ Recognition

We value all contributions and will:
- Credit contributors in release notes
- Maintain a contributors list
- Provide feedback on all contributions
- Support contributors in their development journey

Thank you for making the Responsible AI Toolkit more secure and robust! 🛡️
