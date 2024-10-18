import unittest
from moto import mock_aws
import boto3
import pytest
from src.app import lambda_handler

# Sample Lambda function that interacts with DynamoDB
def setup_dynamodb():
    with mock_aws():
        # Create the DynamoDB table for testing
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='VisitedTable_SAM',
            KeySchema=[
                {
                    'AttributeName': 'site_name',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'site_name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        return table

class test_lambda_handler(unittest.TestCase):
    @mock_aws
    def test_dynamo_update(self):
        table = setup_dynamodb()
        table.put_item(
            Item={
                'site_name': 'andrewclouddev.net', 
                'total_visits': 0
                })

        table.update_item(
            Key={
                'site_name': 'andrewclouddev.net'
            },
            UpdateExpression="SET total_visits = total_visits + :inc",
            ExpressionAttributeValues={
                ':inc':1
            }
        )

        # Retrieve the item from DynamoDB to check if total_visits is 1
        response = table.get_item(
            Key={
                'site_name': 'andrewclouddev.net'
            }
        )
        item = response['Item']
        print(item)

        # Check if the total_visits attribute is indeed 1
        self.assertIsNotNone(item)
        self.assertEqual(item['total_visits'], 1)

if __name__ == '__main__':
    unittest.main()
