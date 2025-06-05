# PhysioSOAP MVP

A minimal viable product that converts voice-recorded physiotherapy sessions into structured PDF SOAP reports using AI technology.

## 🎯 Overview

PhysioSOAP MVP automates the conversion of therapy session audio recordings into professional, structured SOAP (Subjective, Objective, Assessment, Plan) documentation. The system uses a modern MCP (Model Context Protocol) server-client architecture for maximum modularity and scalability.

### Pipeline Stages

1. **Audio Transcription** - Uses OpenAI Whisper API to convert audio to text
2. **SOAP Extraction** - Uses GPT-4o-mini to extract structured SOAP components with expert prompting
3. **PDF Generation** - Renders professional PDF reports using WeasyPrint and Jinja2 templates

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Audio Input    │    │   Transcription │    │ SOAP Extraction │
│   (WAV/MP3)     │───▶│     Server      │───▶│     Server      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐            │
│  PDF Output     │◀───│     Render      │◀───────────┘
│                 │    │     Server      │
└─────────────────┘    └─────────────────┘
```

### Components

- **Main AI Agent** (`workflow.py`) - Orchestrates the complete pipeline
- **MCP Servers** (`servers/`) - Independent services for each processing stage
- **MCP Clients** (`clients/`) - Communication interfaces for servers
- **Pydantic Models** (`models/`) - Type-safe data validation and serialization
- **Templates** (`templates/`) - Professional HTML/PDF report templates

## 📋 Requirements

- Python 3.9+
- OpenAI API key with access to:
  - GPT-4o-mini (text generation)
  - Whisper-1 (audio transcription)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd physiosoap
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Copy the environment template
   cp .env.template .env
   
   # Edit .env and add your OpenAI API key
   nano .env
   ```

4. **Set up directories:**
   ```bash
   mkdir audio output
   ```

## ⚙️ Configuration

Edit the `.env` file with your settings:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_GPT=gpt-4o-mini
OPENAI_MODEL_WHISPER=whisper-1
MAX_TOKENS=2048

# Directory Configuration
PDF_OUTPUT_DIR=./output
AUDIO_INPUT_DIR=./audio

# HIPAA Configuration
HIPAA_MODE=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🎵 Usage

### Basic Usage

Process an audio file to generate a SOAP PDF report:

```bash
python workflow.py path/to/session.mp3
```

### Advanced Usage

```bash
# Custom output filename
python workflow.py session.wav --output "patient_john_doe_session_1"

# Verbose logging
python workflow.py session.mp3 --verbose
```

### Supported Audio Formats

- MP3, MP4, MPEG, MPGA, M4A, WAV, WebM
- Maximum file size: 25MB (larger files are automatically chunked)

### Example Workflow

1. Place your audio file in the `./audio` directory
2. Run the workflow:
   ```bash
   python workflow.py ./audio/therapy_session.mp3
   ```
3. The generated PDF will be saved in `./output/`

## 📊 SOAP Documentation

The system follows physiotherapy best practices for SOAP documentation:

### Subjective
- Patient's self-reported symptoms and pain levels
- Functional limitations and daily activity impacts
- Changes since last treatment
- Patient goals and concerns

### Objective  
- Range of motion measurements
- Strength testing results
- Functional assessments
- Gait analysis and movement patterns
- Special tests and findings

### Assessment
- Clinical reasoning combining S&O findings
- Progress toward established goals
- Prognosis and rehabilitation potential
- Problem prioritization

### Plan
- Interventions performed
- Home exercise program
- Patient education provided
- Future session planning
- Referrals or recommendations

## 🔧 Development

### MCP Server Architecture

Each component runs as an independent MCP server:

```bash
# Start individual servers
python -m servers.transcribe_server
python -m servers.extract_server  
python -m servers.render_server
```

### Client Usage

Use clients programmatically:

```python
from clients.transcribe import transcribe_audio_file
from clients.extract import extract_soap_from_text
from clients.render import render_soap_to_pdf

# Transcribe audio
text = await transcribe_audio_file("session.mp3")

# Extract SOAP
soap_model = await extract_soap_from_text(text)

# Generate PDF
pdf_path = await render_soap_to_pdf(soap_model)
```

### Custom Templates

Modify `templates/soap_report.html` to customize PDF appearance:

- Professional styling with color-coded SOAP sections
- Clinic logo and therapist signature support
- HIPAA compliance footer
- Print-optimized layout

## 🔒 HIPAA Compliance

The system includes HIPAA-ready features:

- **PHI Redaction** - Automatic redaction of sensitive information in logs
- **Secure Storage** - Configurable for BAA-compliant object storage
- **Access Controls** - Modular architecture supports authentication layers
- **Audit Logging** - Comprehensive structured logging with workflow tracking

### HIPAA Mode

Enable HIPAA mode in `.env`:
```bash
HIPAA_MODE=true
```

This automatically redacts:
- Patient names in logs
- Phone numbers
- Email addresses  
- Social Security Numbers

## 📈 Performance

### Typical Processing Times
- **Transcription**: ~30-60 seconds per audio minute
- **SOAP Extraction**: ~10-30 seconds per session
- **PDF Generation**: ~2-5 seconds per report

### Scalability Features
- Automatic audio chunking for large files
- Token-aware text processing
- Exponential backoff retry logic
- Concurrent MCP server architecture

## 🛠️ Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   ```bash
   # Check API key and quota
   export OPENAI_API_KEY=your_key_here
   ```

2. **WeasyPrint Dependencies**
   ```bash
   # On Windows, may need additional packages
   pip install weasyprint --no-cache-dir
   ```

3. **Audio Format Issues**
   ```bash
   # Convert unsupported formats using ffmpeg
   ffmpeg -i input.mov output.mp3
   ```

### Logs and Debugging

Enable verbose logging:
```bash
LOG_LEVEL=DEBUG python workflow.py session.mp3 --verbose
```

Check logs in structured JSON format when `LOG_FORMAT=json`.

## 🔮 Production Considerations

Before deploying to production:

1. **Replace OpenAI APIs** with HIPAA-compliant alternatives
2. **Implement authentication** and access controls
3. **Use secure storage** (AWS S3 with BAA, Azure HIPAA, etc.)
4. **Add data encryption** at rest and in transit
5. **Implement audit trails** and compliance monitoring
6. **Set up monitoring** and alerting systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed error information
4. Include logs and configuration (redacted of PHI)

---

**⚠️ Important**: This is a development MVP. Ensure HIPAA compliance and security requirements are met before processing real patient data. 