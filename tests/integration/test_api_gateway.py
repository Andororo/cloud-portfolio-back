import os
import boto3
import pytest
import requests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module='botocore')

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""

'''
Test API gateway by calling the associate Lambda Function, 
which then update the DynamoDB table
'''


class TestApiGateway:
    @pytest.fixture()
    def api_gateway_url(self):
        """ Get the API Gateway URL from Cloudformation Stack outputs """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError('Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack')

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n" f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "UpdateVisitorTableAPI"]
        
        if not api_outputs:
            raise KeyError(f"UpdateVisitorTableAPI not found in stack {stack_name}")
        
        return api_outputs[api_outputs[0]["OutputValue"]] # Extract url from stack outputs

    def test_api_gateway(self, api_gateway_url):
        """ Call the API Gateway endpoint and check the response """
        # api_url = self.api_gateway_url()

        # Define your headers
        headers = {
            'Origin': 'https://sam.andrewclouddev.net',
            'Content-Type': 'application/json'
        }
        try: 
            # test lambda function by making a GET request, triggers the associated Lambda Function
            response = requests.get(api_gateway_url, headers=headers)
            #Handle non-JSON responses
            if response.status_code != 200:
                raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
            # Parse JSON response safely
            response_json = response.json() if response.headers.get('Content-Type') == 'application/json' else {}
            # Check for the success message
            assert 'Success!' in response_json.get('message', ''), "Expected success message not found."
            # print(response.json())
            # assert response.status_code == 200
            # assert 'Success!' in response.json()['message'] #change the request body to successfully "connected to lambda function"
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request to {api_gateway_url} failed: {e}")
