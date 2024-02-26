import json
import boto3
import logging
import utils
import threading
import time
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
def lambda_handler(event, context):
    print("Test")
    print(event)
    apig_management_client = boto3.client(
            'apigatewaymanagementapi', 
            endpoint_url = "https://v832tufeoc.execute-api.ap-south-1.amazonaws.com/test/@connections"
        )
    print("https://" + event["requestContext"]["domainName"] + "/test")    
    if event.get('requestContext', {}).get('http', {}).get('method') == 'POST' and event['requestContext']['routeKey'] == 'POST /test':
        print("event from http call", event)
        # New REST API trigger logic
        body = json.loads(event['body'])
        connection_id = body['connectionId']
        message = body['message']
        print("connection_id",connection_id)
        return send_Message(apig_management_client, connection_id, message)
    elif 'requestContext' in event and 'routeKey' in event['requestContext']:
        """
        Routes WebSocket events to the appropriate handler function.
        """
        route_key = event['requestContext']['routeKey']
        print("Websocket route_key",route_key)
        try:
            # Route the event to the appropriate handler function based on the route key
            if route_key == '$connect':
                return connect(event, context)
                
            elif route_key == '$disconnect':
                return disconnect(event, context)
                
            elif route_key == 'sendMessage':
                return send_Message(event, context)
            elif route_key == 'fetchDetails':
                return fetch_details(event, context)
        
            elif route_key == '$default':
                return {'statusCode': 400, 'body': 'Default route key'}
            else:
                return {'statusCode': 400, 'body': 'Invalid route key'}
        
        except Exception as e:
            response_data={'message':'Bad request','error':str(e)}
            return utils.response(response_data)  
def send_Message(apig_management_client, connection_id, message):
    print("Sending Message to ",connection_id)
    try:
        apig_management_client.post_to_connection(Data=json.dumps(message), ConnectionId=connection_id)
        logger.info("Message sent to: %s", connection_id)
        print("Message sent to: ", connection_id)
    except ClientError as e:
        logger.error(e)
    except apig_management_client.exceptions.GoneException:
        logger.error("Failed to send message. Connection ID %s is gone.", connection_id)
        print("Failed to send message. Connection ID %s is gone.", connection_id)
        # Here you could delete the connection ID from your storage if you were using DynamoDB or similar
    except Exception as e:
        logger.error("Exception sending message to %s: %s", connection_id, e)
        print("Exception sending message to %s: %s", connection_id, e)
        raise e
    return {'statusCode': 200, 'body': 'This is your message'}
    #return {'statusCode': 200, 'body': 'This is your message'}   
def connect(event, context):
    connectionId = event['requestContext']['connectionId']
    print("Connection called", connectionId)
    # Correctly define your API Gateway Management API client
    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/test"  # Ensure this matches your API's base URL
    apig_management_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
    # Prepare a welcome message including the connection ID
    welcome_message = {'message': f'Welcome! Your connection ID is {connectionId}.'}
    # Send the welcome message to the connected client
    try:
        apig_management_client.post_to_connection(
            ConnectionId=connectionId,
            Data=json.dumps(welcome_message)
        )
        print("Welcome message sent to: ", connectionId)
    except Exception as e:
        print("Failed to send welcome message to ", connectionId, ": ", str(e))
    
    return {'statusCode': 200, 'body': 'Connected.'}
def disconnect(event, context):
    connection_id = event['requestContext']['connectionId']
    logger.info(f'WebSocket connection closed: {connection_id}')
    return {'statusCode': 200, 'body': 'Thanks for joining!'}
def fetch_details(event, context):
    connection_id = event['requestContext']['connectionId']
    print("event for fetch_details", event['body'])
    return {'statusCode': 200, 'body': f'Successfully recieved details from {connection_id}'}



#####My code
# import json
# import boto3

# def lambda_handler(event, context):
#     # Determine the route key from the event
#     print('event',event)
#     route_key = event['requestContext'].get('routeKey')
#     print('route_key',route_key)
#     # Handle connection
#     if route_key == '$connect':
#         connectionId = event['requestContext']['connectionId']
#         print(f"Connect requested by {connectionId}")
#         # Your logic for handling a new connection (e.g., saving connection ID to a database)
#         return {'statusCode': 200}

#     # Handle disconnection
#     elif route_key == '$disconnect':
#         connectionId = event['requestContext']['connectionId']
#         print(f"Disconnect requested by {connectionId}")
#         # Your logic for handling a disconnection (e.g., removing connection ID from a database)
#         return {'statusCode': 200}

#     # Handle sendMessage or other custom action
#     elif route_key == 'sendEvents':
#         connectionId = event['requestContext']['connectionId']
#         message = json.loads(event['body'])['message']
        
#         # Example logic for processing the message
#         print(f"Message from {connectionId}: {message}")
        
#         # Optionally, send a response back to the client
#         apig_management = boto3.client('apigatewaymanagementapi',
#                                       endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}")
#         apig_management.post_to_connection(
#             ConnectionId=connectionId,
#             Data=json.dumps({'message': 'Received your message: ' + message})
#         )
        
#         return {'statusCode': 200}

#     else:
#         # Unrecognized route key
#         print("Received unrecognized route key:", route_key)
#         return {'statusCode': 400, 'body': 'Unrecognized route key'}
