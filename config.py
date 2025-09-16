import os

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_PROFILE = os.getenv('AWS_PROFILE', 'speech-formatter-user')

# AWS Transcribe settings
TRANSCRIBE_BUCKET = os.getenv('TRANSCRIBE_BUCKET', 'speech-formatter-audio-185749752590')
TRANSCRIBE_JOB_PREFIX = 'speech-formatter'

# AWS Bedrock settings  
BEDROCK_MODEL_ID = 'amazon.nova-lite-v1:0'

# Template storage
TEMPLATE_BUCKET = os.getenv('TEMPLATE_BUCKET', 'speech-formatter-templates-185749752590')

# Document formatting prompts
EMAIL_TONES = {
    "Professional": "professional and formal",
    "Friendly": "warm and friendly but professional", 
    "Direct": "direct and concise",
    "Casual": "casual and conversational"
}

DOCUMENT_PROMPTS = {
    "Email": """
    Format this text as a {tone} email. Use proper structure with:
    - Clear subject line
    - Appropriate greeting
    - Well-organized body paragraphs
    - Professional closing
    
    Text to format: {text}
    """,
    
    "Meeting Minutes": """
    Format this text as professional meeting minutes with:
    - Date and attendees section
    - Clear discussion points
    - Action items with owners
    - Next steps
    
    Text to format: {text}
    """,
    
    "Narrative": """
    Format this text as a clear narrative report with:
    - Logical flow and structure
    - Clear paragraphs
    - Summary of key points
    
    Text to format: {text}
    """,
    
    "Briefing Doc": """
    Format this text as an executive briefing document with:
    - Executive summary
    - Key findings
    - Recommendations
    - Clear, concise language
    
    Text to format: {text}
    """
}
