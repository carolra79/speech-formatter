#!/usr/bin/env python3
"""Test AWS connections and permissions"""

import boto3
from config import AWS_REGION, AWS_PROFILE, TRANSCRIBE_BUCKET, TEMPLATE_BUCKET

def test_connections():
    try:
        session = boto3.Session(profile_name=AWS_PROFILE)
        
        # Test S3
        s3 = session.client('s3', region_name=AWS_REGION)
        print("✓ S3 connection successful")
        
        # Test buckets
        s3.head_bucket(Bucket=TRANSCRIBE_BUCKET)
        print(f"✓ Audio bucket accessible: {TRANSCRIBE_BUCKET}")
        
        s3.head_bucket(Bucket=TEMPLATE_BUCKET)
        print(f"✓ Template bucket accessible: {TEMPLATE_BUCKET}")
        
        # Test Transcribe
        transcribe = session.client('transcribe', region_name=AWS_REGION)
        transcribe.list_transcription_jobs(MaxResults=1)
        print("✓ Transcribe connection successful")
        
        # Test Bedrock
        bedrock = session.client('bedrock-runtime', region_name=AWS_REGION)
        print("✓ Bedrock connection successful")
        
        print("\n🎉 All AWS services are accessible!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nRequired IAM permissions:")
        print("- AmazonTranscribeFullAccess")
        print("- AmazonBedrockFullAccess") 
        print("- AmazonS3FullAccess")
        print("\nCurrent user needs these permissions added in AWS Console.")

if __name__ == "__main__":
    test_connections()
