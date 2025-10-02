# Contributing to Wakalat-AI Backend

Thank you for your interest in contributing to Wakalat-AI! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Wakalat-AI-Backend.git
   cd Wakalat-AI-Backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

4. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Code Style

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Format code with Black: `black src/`
- Lint with Flake8: `flake8 src/`
- Type check with mypy: `mypy src/`

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Run tests: `pytest tests/`
- Aim for high test coverage

## Commit Messages

Follow conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example:
```
feat: add support for High Court case search
fix: correct limitation period calculation for appeals
docs: update API documentation for precedent search
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes and commit them
3. Push to your fork: `git push origin feature/your-feature-name`
4. Open a Pull Request with a clear description of changes
5. Ensure CI checks pass
6. Wait for code review

## Areas for Contribution

### High Priority
- Integration with Indian Kanoon API
- Vector database setup with legal document embeddings
- LLM prompt engineering for legal analysis
- Document parsing improvements (PDF, DOCX)

### Medium Priority
- Multi-language support (Hindi, regional languages)
- Additional court databases integration
- Case outcome prediction models
- Enhanced limitation period calculations

### Low Priority
- UI improvements
- Documentation enhancements
- Performance optimizations
- Additional utility tools

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the technical aspects
- Help others learn and grow

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Contact the maintainers directly for sensitive issues

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
