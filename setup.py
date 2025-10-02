"""
Setup configuration for Wakalat-AI Backend
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wakalat-ai-backend",
    version="1.0.0",
    author="BE Project VESIT Team",
    description="MCP Server for legal assistance in India",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BE-project-vesit/Wakalat-AI-Backend",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "mcp>=0.1.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "chromadb>=0.4.0",
        "openai>=1.3.0",
        "pypdf2>=3.0.0",
        "python-docx>=1.0.0",
        "pdfplumber>=0.10.0",
        "langchain>=0.1.0",
        "sentence-transformers>=2.2.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "loguru>=0.7.0",
        "pytest>=7.4.0",
    ],
    entry_points={
        "console_scripts": [
            "wakalat-ai=src.server:main",
        ],
    },
)
