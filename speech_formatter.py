import streamlit as st
import boto3
from datetime import datetime
import json
import uuid
from speech_processor import SpeechProcessor
from config import AWS_REGION
from prompt_manager import load_email_settings, save_email_settings, EXAMPLE_EMAIL_PROMPT, save_template_file
from streamlit_mic_recorder import mic_recorder

# Page config
st.set_page_config(
    page_title="Speech-to-Document Formatter",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = SpeechProcessor()
if 'transcription_job' not in st.session_state:
    st.session_state.transcription_job = None
if 'formatted_text' not in st.session_state:
    st.session_state.formatted_text = ""
if 'email_settings' not in st.session_state:
    st.session_state.email_settings = load_email_settings()
if 'recorder_key' not in st.session_state:
    st.session_state.recorder_key = 0

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Email settings
    st.subheader("Email Settings")
    
    # Custom prompt editor
    custom_prompt = st.text_area(
        "Custom Email Prompt:",
        value=st.session_state.email_settings["custom_prompt"],
        height=200,
        help=f"Example prompt:\n\n{EXAMPLE_EMAIL_PROMPT}"
    )
    
    if st.button("💾 Save Email Settings"):
        st.session_state.email_settings["custom_prompt"] = custom_prompt
        save_email_settings(st.session_state.email_settings)
        st.success("Email settings saved!")
    
    # Template upload section
    st.subheader("Email Template")
    
    # Show current template status
    if st.session_state.email_settings.get("template_filename"):
        st.success(f"📄 Template: {st.session_state.email_settings['template_filename']}")
        
        col_replace, col_delete = st.columns(2)
        with col_replace:
            replace_template = st.file_uploader("Replace template:", type=['txt', 'docx', 'pdf'], key="replace")
            if replace_template:
                template_data = save_template_file(replace_template.read(), replace_template.name)
                st.session_state.email_settings["template_file"] = template_data["content"]
                st.session_state.email_settings["template_filename"] = template_data["filename"]
                save_email_settings(st.session_state.email_settings)
                st.success("Template replaced!")
        
        with col_delete:
            if st.button("🗑️ Delete Template"):
                st.session_state.email_settings["template_file"] = None
                st.session_state.email_settings["template_filename"] = None
                save_email_settings(st.session_state.email_settings)
                st.success("Template deleted!")
    else:
        # Upload new template
        uploaded_template = st.file_uploader("Upload email template:", type=['txt', 'docx', 'pdf'])
        if uploaded_template:
            template_data = save_template_file(uploaded_template.read(), uploaded_template.name)
            st.session_state.email_settings["template_file"] = template_data["content"]
            st.session_state.email_settings["template_filename"] = template_data["filename"]
            save_email_settings(st.session_state.email_settings)
            st.success("Template uploaded!")

# Main content
st.title("🎤 Speech-to-Document Formatter")
st.markdown("Convert speech to professionally formatted documents using AI")

# Create two-column layout
left_col, right_col = st.columns([1, 1])

# LEFT COLUMN - All inputs and controls
with left_col:
    # Document type selection
    st.subheader("Document Type")
    options = [
        "Email",
        "Meeting Minutes (Coming Soon)",
        "Narrative (Coming Soon)", 
        "Briefing Doc (Coming Soon)"
    ]
    
    selected = st.selectbox("Choose format:", options)
    
    if "Coming Soon" in selected:
        st.warning("This document type is coming soon! Using Email format.")
        doc_type = "Email"
    else:
        doc_type = selected

    # Speech input section
    st.subheader("Speech Input - Record Audio")
    
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹️ Stop Recording",
        key=f'recorder_{st.session_state.recorder_key}'
    )
    
    if audio:
        st.audio(audio["bytes"])
        
        # Show clear button after processing is complete
        if st.session_state.transcription_job is None and st.session_state.formatted_text:
            if st.button("🗑️ Clear Recording"):
                st.session_state.formatted_text = ""
                st.session_state.recorder_key += 1  # Reset recorder component
                st.rerun()
        
        # Buttons side by side (only when no job running and no completed output)
        elif not st.session_state.transcription_job:
            col_transcribe, col_clear = st.columns(2)
            
            with col_transcribe:
                if st.button("🔄 Transcribe & Format", type="primary"):
                    try:
                        job_name = f"speech-job-{uuid.uuid4().hex[:8]}"
                        st.session_state.transcription_job = st.session_state.processor.transcribe_audio(
                            audio["bytes"], job_name
                        )
                        # Success message will show after page refreshes and cancel button appears
                    except Exception as e:
                        st.error(f"Error starting transcription: {str(e)}")
            
            with col_clear:
                if st.button("🗑️ Clear Recording"):
                    st.session_state.transcription_job = None
                    st.session_state.formatted_text = ""
                    st.session_state.recorder_key += 1  # Reset recorder component
                    st.rerun()

    # Status check for transcription
    if st.session_state.transcription_job:
        # Cancel button at the top (only during active processing)
        if st.button("❌ Cancel Processing"):
            st.session_state.transcription_job = None
            st.success("Processing cancelled!")
            st.rerun()
        
        # Show transcription started message
        st.success("Transcription started!")
        
        # Auto-check status
        with st.spinner("Checking transcription status..."):
            try:
                transcript = st.session_state.processor.get_transcription_result(
                    st.session_state.transcription_job
                )
                
                if transcript:
                    st.success("Transcription complete!")
                    
                    with st.spinner("Formatting document..."):
                        kwargs = {'custom_prompt': st.session_state.email_settings["custom_prompt"]}
                        formatted = st.session_state.processor.format_with_bedrock(
                            transcript, doc_type, **kwargs
                        )
                        st.session_state.formatted_text = formatted
                    
                    # Clear the job so cancel button disappears
                    st.session_state.transcription_job = None
                    st.success("Document formatted successfully!")
                    st.rerun()  # Refresh to show clear button instead
                else:
                    import time
                    time.sleep(2)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.transcription_job = None

    # Text input section
    st.subheader("Text Input")
    raw_text = st.text_area("Enter text to format:", height=150)
    
    if raw_text and st.button("✨ Format Text"):
        with st.spinner("Formatting with AI..."):
            try:
                kwargs = {'custom_prompt': st.session_state.email_settings["custom_prompt"]}
                formatted = st.session_state.processor.format_with_bedrock(
                    raw_text, doc_type, **kwargs
                )
                st.session_state.formatted_text = formatted
                st.success("Text formatted successfully!")
            except Exception as e:
                st.error(f"Error formatting: {str(e)}")

# RIGHT COLUMN - Output only
with right_col:
    st.subheader("Output")
    
    if st.session_state.formatted_text:
        # Display as markdown to render links
        st.markdown("**Formatted Document:**")
        st.markdown(st.session_state.formatted_text)
        
        # Convert markdown to HTML for download
        import re
        html_content = st.session_state.formatted_text
        # Convert markdown links [text](url) to HTML links
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
        # Convert line breaks to HTML
        html_content = html_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        # Wrap in basic HTML structure
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email</title>
</head>
<body>
    <p>{html_content}</p>
</body>
</html>"""
        
        st.download_button(
            label="📄 Download Document",
            data=html_content,
            file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
    else:
        st.info("Formatted document will appear here")
