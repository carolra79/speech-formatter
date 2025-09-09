# Speech-to-Document Formatter

AI-powered speech transcription and document formatting system that converts spoken words into professionally formatted emails.

## Features
- **Speech Input:** Browser microphone capture with real-time recording
- **AI Transcription:** AWS Transcribe speech-to-text conversion
- **Document Formatting:** AWS Bedrock (Claude) for intelligent email formatting
- **Custom Templates:** Uploadable sample documents and custom prompts
- **Professional Output:** Prevents slang, ensures proper grammar, includes clickable links
- **Cross-Platform:** HTML downloads compatible with macOS and Windows

## Architecture
- **Frontend:** Streamlit web interface
- **Speech Processing:** AWS Transcribe
- **AI Formatting:** AWS Bedrock (Claude)
- **Template Storage:** Local file storage with base64 encoding
- **Deployment:** ECS Fargate containerized deployment

## Local Development

### Prerequisites
- Python 3.11+
- AWS credentials configured
- Access to AWS Transcribe and Bedrock services

### Installation
```bash
git clone <repository-url>
cd speech-formatter
pip install -r requirements.txt
```

### Configuration
Update `config.py` with your AWS region:
```python
AWS_REGION = "us-east-1"  # Your preferred region
```

### Run Locally
```bash
streamlit run speech_formatter.py
```

## AWS Deployment

### Required AWS Resources
1. **ECS Cluster** (Fargate)
2. **ECR Repository** for Docker images
3. **IAM Role** with permissions for:
   - `transcribe:StartTranscriptionJob`
   - `transcribe:GetTranscriptionJob`
   - `bedrock:InvokeModel`

### Build and Deploy
```bash
# Build Docker image
docker build -t speech-formatter .

# Tag for ECR
docker tag speech-formatter:latest <account-id>.dkr.ecr.<region>.amazonaws.com/speech-formatter:latest

# Push to ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/speech-formatter:latest
```

### ECS Task Definition
- **Container Port:** 8501
- **Memory:** 1GB minimum
- **CPU:** 0.5 vCPU minimum
- **Health Check:** `/_stcore/health`

## Usage

1. **Record Audio:** Click "Start Recording" to capture speech
2. **Process:** Click "Transcribe & Format" to convert speech to formatted email
3. **Customize:** Use sidebar to modify email prompts and upload templates
4. **Download:** Export as HTML file with clickable links
5. **Clear:** Reset for new recording

## Document Types
- **Email:** ✅ Available with custom prompts and templates
- **Meeting Minutes:** 🚧 Coming Soon
- **Narrative:** 🚧 Coming Soon
- **Briefing Doc:** 🚧 Coming Soon

## Configuration Options

### Custom Email Prompts
- Personalized greetings and sign-offs
- Tone and style preferences
- Automatic link insertion rules
- Grammar and spelling preferences

### Template Management
- Upload reference documents (.txt, .docx, .pdf)
- Persistent storage between sessions
- Replace or delete existing templates

## Security Notes
- User settings stored locally (not in cloud)
- Audio processed through AWS Transcribe (temporary storage)
- No persistent audio storage in application
- Templates encoded in base64 for local storage

## Development Status
🚀 **Production Ready** - Core email functionality complete
🚧 **In Development** - Additional document types coming soon
