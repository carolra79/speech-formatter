import json
import os
import base64

SETTINGS_FILE = "email_settings.json"

DEFAULT_EMAIL_PROMPT = "Customise your email response with the tone, your personal greeting and sign off and any other information the model will use to get your emails right."

EXAMPLE_EMAIL_PROMPT = """The basic prompt in the code is: 

Format this text as a professional email. Use proper structure with:
- Clear subject line
- Appropriate greeting
- Well-organized body paragraphs
- Professional closing
- Use as much of the input text as possible but do not add additional data or invent information.

Use the custom email prompt to add personalised details such as:
- Sign off: Include a sign-off that says: "Thanks <your name>"
- Never use emojis
- Keep the tone informal but professional"""

def load_email_settings():
    """Load email settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {
        "custom_prompt": DEFAULT_EMAIL_PROMPT,
        "template_file": None,
        "template_filename": None
    }

def save_email_settings(settings):
    """Save email settings to file"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def save_template_file(file_content, filename):
    """Save template file as base64 encoded string"""
    return {
        "content": base64.b64encode(file_content).decode('utf-8'),
        "filename": filename
    }

def load_template_file(template_data):
    """Load template file from base64 encoded string"""
    if template_data:
        return base64.b64decode(template_data["content"].encode('utf-8'))
    return None
