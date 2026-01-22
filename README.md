# Form Automation Agent

Safe and legitimate form automation agent with compliance features.

## Features

- 🤖 AI-powered form analysis using Azure OpenAI
- 🌐 Browser automation with Playwright
- 🔒 Safety and compliance features
- 📊 Audit logging
- ✅ User approval workflow
- 🎯 Google Forms support

## Quick Start

### Prerequisites

- Python 3.11+
- Azure OpenAI account with API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/GokulanandM/Agentic-Form.git
cd Agentic-Form
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

5. Run the application:
```bash
python run.py
```

6. Access the application:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Usage

### Using the Web UI

1. Navigate to http://localhost:8000
2. Test your Azure OpenAI connection
3. Enter a form URL to analyze
4. Provide data to fill the form
5. Review and approve submission

### Using the API

```bash
# Analyze a form
curl -X POST http://localhost:8000/analyze-form \
  -H "Content-Type: application/json" \
  -d '{
    "form_url": "https://example.com/form",
    "api_key": "your-key",
    "endpoint": "https://your-resource.openai.azure.com/"
  }'

# Fill a form
curl -X POST http://localhost:8000/fill-form \
  -H "Content-Type: application/json" \
  -d '{
    "form_url": "https://example.com/form",
    "profile_data": {
      "full_name": "John Doe",
      "email": "john@example.com"
    },
    "user_confirmed": true
  }'
```

## Deployment

### Deploy to Render.com

This repository includes `render.yaml` for easy deployment to Render.com:

1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Set environment variables in Render dashboard
5. Deploy!

See `render.yaml` for configuration details.

## Project Structure

```
AgenticForm/
├── agents/           # AI and automation agents
│   ├── azure_agent.py    # Azure OpenAI integration
│   └── form_filler.py    # Playwright form automation
├── models/          # Data models and schemas
│   └── schemas.py
├── utils/           # Utilities
│   ├── safety.py         # Safety policies
│   └── logger.py         # Audit logging
├── templates/       # Web UI templates
├── static/          # Static files
├── tests/           # Unit tests
├── main.py         # FastAPI application
├── config.py       # Configuration management
└── requirements.txt
```

## Safety & Compliance

- ✅ Form authorization checks
- ✅ Rate limiting (10 submissions/hour)
- ✅ User approval workflow
- ✅ Complete audit logging
- ✅ CAPTCHA detection
- ✅ Error handling and retries

## License

MIT License

## Author

GokulanandM

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
