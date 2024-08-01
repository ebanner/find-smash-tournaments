import json

import boto3


s3 = boto3.client('s3')

BUCKET = 'smash-tournaments'


def put(key, value):
    s3.put_object(Bucket=BUCKET, Key=key, Body=value)


def get(key):
    """If there is no key entry then return None"""

    try:
        object = s3.get_object(Bucket=BUCKET, Key=key)
    except Exception as e:
        print(e)
        return None

    value = object['Body'].read().decode('utf-8')
    return value


def delete(key):
    s3.delete_object(Bucket=BUCKET, Key=key)


def lambda_handler(event, context):
    tournaments_json = get('tournaments.json')
    tournaments = json.loads(tournaments_json)
    players = [ 
        'Tweek',
        'MkLeo',
        'Sparg0',
        'Light',
        'あcola',
        'Glutonny',
        'Riddles',
        'Tea',
        'Kurama',
        'Kola'
    ];  

    data = { 
        'players': players,
        'tournaments': tournaments,
    }   
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : True
        },
        'body': data
    }

