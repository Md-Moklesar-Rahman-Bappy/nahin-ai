# Contributing to Nahin AI

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues
- Use GitHub Issues for bugs and feature requests
- Include system info (Windows version, Python version)
- Provide reproduction steps for bugs

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add feature: your feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

### Coding Standards
- Follow PEP 8
- Add type hints where possible
- Include docstrings
- Test on Windows

## Development Setup

```powershell
git clone https://github.com/Md-Moklesar-Rahman-Bappy/nahin-ai.git
cd nahin-ai
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Testing

```powershell
pytest tests/
```

## Questions?

Open an issue for discussion.
