import boto3
import json
import time
from config import AWS_REGION, AWS_PROFILE, TRANSCRIBE_BUCKET, BEDROCK_MODEL_ID, DOCUMENT_PROMPTS

class SpeechProcessor:
    def __init__(self):
        session = boto3.Session(profile_name=AWS_PROFILE)
        self.transcribe = session.client('transcribe', region_name=AWS_REGION)
        self.bedrock = session.client('bedrock-runtime', region_name=AWS_REGION)
        self.s3 = session.client('s3', region_name=AWS_REGION)
    
    def transcribe_audio(self, audio_file, job_name):
        """Upload audio to S3 and start transcription job"""
        # Upload to S3
        s3_key = f"audio/{job_name}.wav"
        
        # Handle both file objects and bytes
        if hasattr(audio_file, 'read'):
            # File-like object
            self.s3.upload_fileobj(audio_file, TRANSCRIBE_BUCKET, s3_key)
        else:
            # Raw bytes
            import io
            audio_buffer = io.BytesIO(audio_file)
            self.s3.upload_fileobj(audio_buffer, TRANSCRIBE_BUCKET, s3_key)
        
        # Start transcription
        job_uri = f"s3://{TRANSCRIBE_BUCKET}/{s3_key}"
        
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='wav',
            LanguageCode='en-US'
        )
        
        return job_name
    
    def get_transcription_result(self, job_name):
        """Get transcription result when job is complete"""
        response = self.transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )
        
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        
        if status == 'COMPLETED':
            transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            # Download and parse transcript
            import requests
            transcript_response = requests.get(transcript_uri)
            transcript_data = transcript_response.json()
            return transcript_data['results']['transcripts'][0]['transcript']
        elif status == 'FAILED':
            raise Exception("Transcription failed")
        else:
            return None  # Still in progress
    
    def format_with_bedrock(self, text, doc_type, **kwargs):
        """Use Bedrock to format text according to document type"""
        
        # Use custom prompt for emails if provided
        if doc_type == "Email" and 'custom_prompt' in kwargs:
            user_prompt = kwargs['custom_prompt']
            # Auto-append {text} placeholder if not present
            if '{text}' not in user_prompt:
                user_prompt += "\n\nText to format: {text}"
            
            # Add instruction for direct output
            user_prompt += "\n\nProvide only the formatted email, no explanations or meta-text."
            prompt = user_prompt.format(text=text)
        else:
            prompt = DOCUMENT_PROMPTS[doc_type].format(text=text)
        
        # Add hardcoded slang prevention to ALL prompts
        prompt += "\n\nIMPORTANT: Never use slang or informal contractions like 'wanna', 'gonna', 'coulda', 'shoulda', 'would've', etc. Use proper English words instead."
        prompt += "\n\nDo not duplicate greetings - use only one greeting at the start."
        prompt += "\n\nOnly include booking links when the input text specifically mentions booking a call, meeting, or appointment."
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = self.bedrock.invoke_model(
            body=body,
            modelId=BEDROCK_MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        response_text = response_body['content'][0]['text']
        
        # Clean up response - remove AI meta-text
        lines_to_remove = [
            "AI-Formatted Document:",
            "Here's the reformatted text",
            "Here is the reformatted text", 
            "Reformatted email:",
            "Formatted email:",
            "Here's the email:",
            "Here is the email:"
        ]
        
        lines = response_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and meta-text
            if line and not any(meta in line for meta in lines_to_remove):
                cleaned_lines.append(line)
        
        return '\n\n'.join(cleaned_lines)
