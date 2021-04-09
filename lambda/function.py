import base64
import boto3
import json
import random
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
   
    # Handle the Proxy Paths for both Assets and Apis
    if event['pathParameters']:
        isBase64Encoded = False
        bodyData = None
        
        # Handle Message API - Post Request      
        if event['pathParameters']['proxy']=='message':
            print(event["httpMethod"])
            if event["httpMethod"] == "POST":
                print(event['body'])
                decoded= base64.b64decode(event['body'])
                print(decoded)
                userMessage = json.loads(decoded)
                dynamodb = boto3.resource('dynamodb')
                message1 = dynamodb.Table('WebMessage')
                
                eventDateTime = (datetime.now()).strftime("%m-%d-%Y %H:%M:%S")
                userid = userMessage['userid']
                uname = userMessage['name']
                message = userMessage['message']
                
                # Putting a try/catch to log to user when some error occurs
                try:
                    
                    message1.put_item(
                       Item={
                            'userid': userid,
                            'name': uname,
                            'message': message
                        }
                    )
                    
                    return {
                        'headers': { "Content-type": "application/json" },
                        'statusCode': 200,
                        'body': json.dumps("Message Received Successfully"),
                    }
                except Exception as e:
                    print(e)
                    print('Closing lambda function')
                    return {
                            'statusCode': 400,
                            'body': json.dumps('Error saving the Message')
                    }
                
                
                
                return {
                    'headers': { "Content-type": "application/json" },
                    'statusCode': 200,
                    'body': json.dumps("Message Received Successfully"),
                }
              
              # Handle Assets Requests
        else:
        
            try:
                response = s3.get_object(
                Bucket='nithya-images',
                Key='assets/'+ event['pathParameters']['proxy'],
                )
                print(response['ContentType'])
           
                if response['ContentType'].find('image/') != -1:
                    isBase64Encoded = True
    
                if response['ContentType'].find('binary/') != -1:
                    isBase64Encoded = True
    
                data = response['Body'].read()
    
                if isBase64Encoded:
                    print('yes it is a binary stream')
                    bodyData = base64.b64encode(data).decode('utf-8')
                else:
                    print('No it is not a binary stream')
                    bodyData = data 
                return {
                        'headers': { "Content-Type": response['ContentType'],
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                        },
                        'statusCode': 200,
                        'body': bodyData,
                        'isBase64Encoded': isBase64Encoded
                    }
            except Exception as e:
                return {
                  'headers': { "Content-type": "text/html" },
                  'statusCode': 404
                }
    else:
        # Handle Root Requests
        print("request is come for index page")
        try:
            response = s3.get_object(
            Bucket='nithya-images',
            Key='index.html',
            )
            body = response['Body'].read()
            print("Index Page is getting read")
            print(body)
       
            return {
                'headers': { "Content-Type": "text/html",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'statusCode': 200,
                'body':body,
                'isBase64Encoded': False
            }
        except Exception as e:
            print("error occured due to key not found")
            print(e)
            return sendErrorPage()
            
# Handle 404
def sendErrorPage():
    try:
        return {
            'headers': { "Content-type": "text/html" },
            'statusCode': 404,
            'body': "<h1>Content Not Found</h1>",
        }
            
    except Exception as e:
        print("error Happened while fetching the error image")
        print(e)
    
