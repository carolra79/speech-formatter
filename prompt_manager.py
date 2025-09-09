import json
import os
import base64

SETTINGS_FILE = "email_settings.json"

DEFAULT_EMAIL_PROMPT = "Customise your email response with the tone, your personal greeting and sign off and any other information the model will use to get your emails right."

EXAMPLE_EMAIL_PROMPT = """Reformat the inputted text into a format suitable for work email.

Use as much of the inputted text as possible - it should form almost all of the outputted email text you create. 

Structure it in the following way:

1. Greeting
"Hi [firstname]"
If the name of the recipient isnt known use "Hi there," for greeting. If it is known, say "Hi <FIRSTNAME>"

2. Body
Use the inputted text as the body of the email. Break it into paragraphs of one to two sentences each.

3. 
Sign off
Include a sign-off that says:

"Thanks! 

Caroline"
Never sign off with "Best" or "Kind regards" - this too formal.

Only add extra text where it's essential to create an easy to read, friendly email.

Use a friendly, informal tone with smiley emojis to show friendliness

When I mention booking a call, include this link - https://prelude.amazon.com/s/41ogZzys/W8j2qL/-/caroline-rayfield

Check for correct grammar and punctuation UK spellings.

Don't use unnecessary phrases like "I wanted to let you know" or "I'm just getting in touch to say".

Don't say "I hope this email finds you well"

IMPORTANT: Never use slang or informal contractions like "wanna", "gonna", "coulda", "shoulda", "would've", etc. Use proper English words instead."""

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
