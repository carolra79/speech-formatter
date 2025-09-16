# Speech-to-Document Formatter - Complete Deployment Manual

## Overview
AI-powered speech transcription and document formatting system that converts spoken words into professionally formatted emails using AWS Transcribe and Amazon Nova Lite.

## Architecture
- **Frontend:** Streamlit web interface with microphone recording
- **Compute:** EC2 t3.micro with Docker
- **Speech Processing:** AWS Transcribe for speech-to-text
- **AI Formatting:** Amazon Nova Lite (Bedrock) for email formatting
- **CDN:** CloudFront distribution for secure access
- **Security:** 5 security groups with CloudFront IP ranges only
- **Storage:** S3 buckets for audio files and templates
- **Automation:** Lambda function for CloudFront IP management

## AWS Resources Created

### Core Infrastructure
- **EC2 Instance:** `speech-formatter-server` (i-073998dcfd3e9909d)
- **Instance Type:** t3.micro (x86_64)
- **Key Pair:** `speech-formatter-key`
- **IAM Role:** `speech-formatter-ec2-role`

### Container & Build
- **ECR Repository:** `speech-formatter`
- **Docker Image:** `185749752590.dkr.ecr.us-east-1.amazonaws.com/speech-formatter:latest`
- **CodeBuild Project:** `speech-formatter-build`
- **CodeBuild Service Role:** `codebuild-speech-formatter-build-service-role`

### CDN & Security
- **CloudFront Distribution:** `speech-formatter-cdn`
- **Domain:** `d1umvgz6dlt9xs.cloudfront.net`
- **Security Groups:** 5 groups with 194 CloudFront IP ranges
  - `sg-094f72ff744348adb` (main)
  - `sg-017a35d536b81ec98` (cloudfront-sg-4)
  - `sg-08dc714bd18f1584f` (cloudfront-sg-3)
  - `sg-0dac64e3b0af792ab` (cloudfront-sg-2)
  - `sg-0eb4d951a3f1bfbe4` (cloudfront-sg-5)

### Automation
- **Lambda Function:** `update-cloudfront-security-group`
- **Lambda Role:** `update-cloudfront-security-group-role-kkcqjai4`
- **Schedule:** Weekly CloudFront IP updates

### Storage
- **S3 Buckets:**
  - `speech-formatter-audio-185749752590` (temporary audio files)
  - `speech-formatter-templates-185749752590` (document templates)

## Deployment Steps

### 1. Prerequisites
- AWS account with appropriate permissions
- Git repository: https://github.com/carolra79/speech-formatter.git
- Access to AWS Transcribe and Bedrock services

### 2. Launch EC2 Instance
```bash
# Instance Configuration
Name: speech-formatter-server
AMI: Amazon Linux 2023
Instance Type: t3.micro
Key Pair: speech-formatter-key
IAM Role: speech-formatter-ec2-role

# Security Groups (attach all 5):
- sg-094f72ff744348adb (main)
- sg-017a35d536b81ec98 (cloudfront-sg-4)
- sg-08dc714bd18f1584f (cloudfront-sg-3)
- sg-0dac64e3b0af792ab (cloudfront-sg-2)
- sg-0eb4d951a3f1bfbe4 (cloudfront-sg-5)
```

### 3. User Data Script (Optional)
```bash
#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Configure ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 185749752590.dkr.ecr.us-east-1.amazonaws.com
```

### 4. Manual Setup (if no User Data)
```bash
# SSH into instance
ssh -i "path/to/speech-formatter-key.pem" ec2-user@[PUBLIC-IP]

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Log out and back in
exit
ssh -i "path/to/speech-formatter-key.pem" ec2-user@[PUBLIC-IP]

# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 185749752590.dkr.ecr.us-east-1.amazonaws.com

# Pull and run container
docker pull 185749752590.dkr.ecr.us-east-1.amazonaws.com/speech-formatter:latest

docker run -d -p 8501:8501 --name speech-formatter \
  -e AWS_DEFAULT_REGION=us-east-1 \
  185749752590.dkr.ecr.us-east-1.amazonaws.com/speech-formatter:latest
```

### 5. Build Pipeline Setup
```bash
# CodeBuild Project Configuration
Project Name: speech-formatter-build
Source: GitHub (https://github.com/carolra79/speech-formatter.git)
Environment: Amazon Linux 2
Compute: 3 GB memory, 2 vCPUs
Service Role: codebuild-speech-formatter-build-service-role

# Buildspec.yml (in repository)
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image...
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
```

### 6. Create CloudFront Distribution
```bash
# CloudFront Configuration
Origin Domain: ec2-[PUBLIC-IP].compute-1.amazonaws.com
Protocol: HTTP only
Port: 8501
Cache Policy: CachingDisabled
Origin Request Policy: CORS-S3Origin
Viewer Protocol Policy: Redirect HTTP to HTTPS
Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
```

### 7. Lambda Function for IP Management
```python
import json
import boto3
import requests

def lambda_handler(event, context):
    # Get CloudFront IP ranges
    response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
    ip_ranges = response.json()
    
    cloudfront_ips = []
    for prefix in ip_ranges['prefixes']:
        if prefix['service'] == 'CLOUDFRONT':
            cloudfront_ips.append(prefix['ip_prefix'])
    
    # Update security groups
    ec2 = boto3.client('ec2')
    security_groups = [
        'sg-094f72ff744348adb',
        'sg-017a35d536b81ec98',
        'sg-08dc714bd18f1584f',
        'sg-0dac64e3b0af792ab',
        'sg-0eb4d951a3f1bfbe4'
    ]
    
    # Update each security group with current CloudFront IPs
    # (Implementation details in actual Lambda function)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Security groups updated successfully')
    }
```

## Application Configuration

### Environment Variables
```bash
AWS_DEFAULT_REGION=us-east-1
```

### Key Dependencies
```txt
streamlit==1.28.1
boto3==1.34.0
streamlit-mic-recorder==0.0.4  # Important: Use v0.0.4, not 0.0.5
requests==2.31.0
```

### Email Prompt Template
```python
EXAMPLE_EMAIL_PROMPT = """Reformat the input into a format suitable for work email.

Use as much of the input detail as possible.

Structure it in the following way:

Greeting: If the name of the recipient isn't known use "Hi there," for greeting. If it is known, say "Hi <FIRSTNAME>"

Body: Use the input as the body of the email. Break it into paragraphs of one to two sentences each.

Sign off: Include a sign-off that says: "Thanks
<my name>"

Never sign off with "Best" or "Kind regards" - this too formal.

Only add extra text where it's essential to create an easy to read, friendly email.

When I mention booking a call, include this link - <personal calender link>

Check for correct grammar and punctuation UK spellings.

Don't use unnecessary phrases like "I wanted to let you know" or "I'm just getting in touch to say".

Don't say "I hope this email finds you well"

IMPORTANT: Never use slang or informal contractions like "wanna", "gonna", "coulda", "shoulda". Proper contractions like "can't, won't, isn't" are fine."""
```

## Access URLs
- **Production:** https://d1umvgz6dlt9xs.cloudfront.net
- **Direct (Admin only):** http://[PUBLIC-IP]:8501 (if personal IP rule exists)

## Application Features
- **Speech Input:** Browser microphone capture with real-time recording
- **AI Transcription:** AWS Transcribe speech-to-text conversion
- **Document Formatting:** Amazon Nova Lite for intelligent email formatting
- **Custom Templates:** Uploadable sample documents and custom prompts
- **Professional Output:** Prevents slang, ensures proper grammar, includes clickable links
- **Cross-Platform:** HTML downloads compatible with macOS and Windows

## Maintenance

### Starting/Stopping
```bash
# Stop instance to save costs
aws ec2 stop-instances --instance-ids i-073998dcfd3e9909d

# Start instance when needed
aws ec2 start-instances --instance-ids i-073998dcfd3e9909d

# Container management
docker start speech-formatter
docker stop speech-formatter
docker restart speech-formatter
```

### Updates
```bash
# Trigger CodeBuild
aws codebuild start-build --project-name speech-formatter-build

# Pull new image
docker pull 185749752590.dkr.ecr.us-east-1.amazonaws.com/speech-formatter:latest

# Update container
docker stop speech-formatter
docker rm speech-formatter
docker run -d -p 8501:8501 --name speech-formatter \
  -e AWS_DEFAULT_REGION=us-east-1 \
  185749752590.dkr.ecr.us-east-1.amazonaws.com/speech-formatter:latest
```

### Git Repository Management
```bash
# Clone repository
git clone https://github.com/carolra79/speech-formatter.git
cd speech-formatter

# Make changes and commit
git add .
git commit -m "Update description"
git push

# Trigger automatic build via CodeBuild
```

## Monitoring
- **CloudWatch Logs:** `/aws/codebuild/speech-formatter-build`
- **Container Logs:** `docker logs speech-formatter`
- **Health Check:** Access CloudFront URL
- **Lambda Logs:** `/aws/lambda/update-cloudfront-security-group`

## Troubleshooting

### Common Issues
1. **Microphone Not Working:** Check streamlit-mic-recorder version (must be 0.0.4)
2. **Transcription Fails:** Verify IAM role has Transcribe permissions
3. **Formatting Fails:** Check Bedrock permissions for Nova Lite model
4. **Network Timeout:** Verify security groups allow CloudFront IPs
5. **Build Fails:** Check CodeBuild logs and GitHub connectivity

### Debug Commands
```bash
# Check container status
docker ps
docker logs speech-formatter

# Check AWS permissions
aws transcribe list-transcription-jobs
aws bedrock list-foundation-models

# Test microphone component
pip list | grep streamlit-mic-recorder
```

## Security Configuration

### Security Groups
- **No 0.0.0.0/0 inbound rules** (corporate compliant)
- **194 CloudFront IP ranges** across 5 security groups
- **Automatic IP updates** via Lambda function
- **HTTPS encryption** via CloudFront

### IAM Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "bedrock:InvokeModel",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "*"
        }
    ]
}
```

## Cost Optimization
- **Stop EC2 instance** when not in use (~$8.50/month savings)
- **CloudWatch log retention:** Set to 7-30 days
- **S3 lifecycle policies:** Delete temporary audio files after 7 days
- **Monitor Transcribe usage** for cost control

## Future Enhancements

### Planned Features
1. **Midway Security Integration**
   - SAML/OAuth authentication
   - Corporate user management
   - Session management

2. **Additional Document Types**
   - Meeting Minutes (structured format)
   - Narrative Documents (story/report format)
   - Briefing Documents (executive summary)
   - Custom document types

3. **Enhanced Features**
   - Document history/saved outputs
   - Batch processing multiple recordings
   - Export options (email integration, file downloads)
   - Analytics dashboard

## Backup & Recovery
- **Source code:** GitHub repository (https://github.com/carolra79/speech-formatter.git)
- **Docker images:** ECR repository with versioning
- **Templates:** S3 bucket with versioning enabled
- **Configuration:** Documented in this manual
- **Infrastructure:** Recreatable via this deployment guide

---
**Deployment Date:** 2025-09-09  
**Last Updated:** 2025-09-09  
**Version:** 1.0  
**Status:** Production Ready ✅  
**Git Repository:** https://github.com/carolra79/speech-formatter.git
