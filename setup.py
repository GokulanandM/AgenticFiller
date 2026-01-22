"""Setup script for the form automation agent."""
from setuptools import setup, find_packages

setup(
    name="form-automation-agent",
    version="1.0.0",
    description="Safe and legitimate form automation agent with compliance features",
    author="Form Automation Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "openai>=1.3.5",
        "playwright>=1.40.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "cryptography>=41.0.7",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.2",
        "aiofiles>=23.2.1",
        "python-json-logger>=2.0.7",
    ],
    python_requires=">=3.11",
)
