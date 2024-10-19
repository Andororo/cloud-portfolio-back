import json
import boto3
from boto3.dynamodb.types import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VisitedTable_SAM')  # Replace with your DynamoDB table name

def lambda_handler(event, context):
    try:
        # # List of allowed origins
        allowed_origins = [
            'https://sam.andrewclouddev.net',
            'http://localhost:3000',
            'https://andrewclouddev.net'
        ]

        # Testing: prints the event in cloudwatch when API gateway is triggered
        print("Event: ", json.dumps(event, indent=2))

        # Get headers from the event
        headers = event.get('headers', {})
        # Extract the Origin or Referer headers
        origin = headers.get('origin') or headers.get('referer') or headers.get('Origin')
        print(origin)

        if origin and origin in allowed_origins:
            print(f"Origin: {origin}")
            allowed_origin = origin
        else:
            print("No Origin header present.")
            allowed_origin = null

        body_key = event['body']
        print(body_key)
        response = table.get_item(
            Key = {
                'site_name': 'andrewclouddev.net'
            }    
        )
        updated_total_visits = float(response['Item']['total_visits'])
        
        if body_key != 'true':
            # Increment total_visits attribute
            response = table.update_item(
                Key={
                    'site_name': 'andrewclouddev.net'  # Assuming 'visitor_count' is your partition key
                },
                UpdateExpression="SET total_visits = total_visits + :inc",
                ExpressionAttributeValues={
                    ':inc': 1
                },
                ReturnValues="UPDATED_NEW"
            )
            # Convert Decimal to float for JSON serialization
            updated_total_visits = float(response['Attributes']['total_visits'])
            message = 'Success! Visitor count updated successfully!'
            
        else:
            message = 'Success! Welcome back, visitor! No update needed.'

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': allowed_origin,
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS, GET, POST',
            },
            'body': json.dumps({
                'message': message,
                'total_visits': updated_total_visits
            })
        }
    
    except Exception as e:
        # Return an error response if something goes wrong
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
