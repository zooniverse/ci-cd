import requests

def lambda_handler(event, context):
    print("Executing test lambda function.")
    return {
        'statusCode': 200,
        'body': 'Success'
    }