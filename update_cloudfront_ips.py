import boto3
import requests
import json

def lambda_handler(event, context):
    # Configuration
    SECURITY_GROUP_ID = 'sg-094f72ff744348adb'
    PORT = 8501
    DESCRIPTION = 'CloudFront Access - Auto Updated'
    
    try:
        # Get current CloudFront IP ranges
        response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
        ip_ranges = response.json()
        
        cloudfront_ips = [
            prefix['ip_prefix'] for prefix in ip_ranges['prefixes'] 
            if prefix['service'] == 'CLOUDFRONT'
        ]
        
        print(f"Found {len(cloudfront_ips)} CloudFront IP ranges")
        
        # Initialize EC2 client
        ec2 = boto3.client('ec2')
        
        # Get current security group rules
        sg_response = ec2.describe_security_groups(GroupIds=[SECURITY_GROUP_ID])
        current_rules = sg_response['SecurityGroups'][0]['IpPermissions']
        
        # Find existing CloudFront rules (port 8501 with CloudFront description)
        cloudfront_rules = []
        for rule in current_rules:
            if (rule.get('FromPort') == PORT and 
                rule.get('ToPort') == PORT and
                any('CloudFront' in ip_range.get('Description', '') 
                    for ip_range in rule.get('IpRanges', []))):
                cloudfront_rules.append(rule)
        
        # Remove existing CloudFront rules
        if cloudfront_rules:
            print(f"Removing {len(cloudfront_rules)} existing CloudFront rules")
            ec2.revoke_security_group_ingress(
                GroupId=SECURITY_GROUP_ID,
                IpPermissions=cloudfront_rules
            )
        
        # Add new CloudFront rules (in batches due to AWS limits)
        batch_size = 50  # AWS limit per request
        for i in range(0, len(cloudfront_ips), batch_size):
            batch = cloudfront_ips[i:i + batch_size]
            
            ip_permissions = [{
                'IpProtocol': 'tcp',
                'FromPort': PORT,
                'ToPort': PORT,
                'IpRanges': [
                    {
                        'CidrIp': ip,
                        'Description': DESCRIPTION
                    } for ip in batch
                ]
            }]
            
            ec2.authorize_security_group_ingress(
                GroupId=SECURITY_GROUP_ID,
                IpPermissions=ip_permissions
            )
            
            print(f"Added batch {i//batch_size + 1}: {len(batch)} IP ranges")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully updated security group with {len(cloudfront_ips)} CloudFront IP ranges',
                'security_group_id': SECURITY_GROUP_ID
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
