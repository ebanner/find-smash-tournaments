import json
import pandas as pd
from datetime import datetime
import requests

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os

import json

import boto3


s3 = boto3.client('s3')

BUCKET = 'smash-tournaments'


def get_gmail_app_password():

    secret_name = "GMAIL_APP_PASSWORD"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret_json = get_secret_value_response['SecretString']

    secret_dict = json.loads(secret_json)
    gmail_app_password = secret_dict[secret_name]
    return gmail_app_password


def send_email(subject, body):
    # Set up the sender and receiver emails
    sender_email = os.environ['SENDER_EMAIL']
    receiver_email = os.environ['RECIPIENT_EMAIL']
    password = get_gmail_app_password() # Use an app-specific password or OAuth for security

    # Create a MIMEMultipart object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Set up the Gmail server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use Gmail's SMTP server
        server.starttls()  # Start the server in TLS mode
        server.login(sender_email, password)  # Log in to your Gmail account
        server.sendmail(sender_email, receiver_email, msg.as_string())  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()  # Close the connection


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


def fetch_tournament_data(player_id, page, PER_PAGE=490):
    url = 'https://api.start.gg/gql/alpha'
    
    query = """
      query PlayerQuery {
      player(id: "{player_id}") {
        user {
          tournaments(query: { page: {page}, perPage: 500 }) {
            nodes {
              name
              slug
              startAt
            }
          }
        }
      }
    }""".replace('{page}', str(page)).replace('{player_id}', str(player_id))
    
    token = os.environ['START_GG_TOKEN']
    headers = { 
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'  # if authentication is needed
    }   
    
    response = requests.post(url, json={'query': query}, headers=headers)
    result = response.json()

    return result


TOURNAMENT_TO_EVENT = { 
    '12-with-kowloon-12-with-kagaribi': 'sp-ultimate-singles',
    'genesis-x': 'ultimate-singles',
    'supernova-2024': 'ultimate-1v1-singles',
    "ultimate-fighting-arena-2024-3": "super-smash-bros-ultimate-solo-switch",
    "s-factor-11": "smash-bros-ultimate-singles",
    "pre-s-factor-11": "ultimate-singles",
    "ceo-2024-6": "super-smash-bros-ultimate-1v1",
    "the-coinbox-105": "ultimate-singles",
    "the-to-go-box-3-ultimate-final-smash-meter-on": "ultimate-singles",
    "the-to-go-box-2-ultimate-sonic-steve-pikachu-banned": "ultimate-singles",
    "con-2024-7": "ssbu-1v1",
    "the-coinbox-102": "ultimate-singles",
    "get-on-my-level-x-canadian-fighting-game-championships": "super-smash-bros-ultimate-singles",
    "delta-8": "singles",
    "lvl-up-expo-2024": "smash-ultimate-singles-starts-saturday",
    "kroger-gaming-presents-the-luminosity-invitational": "ultimate-singles",
    "diamond-dust": "ultimate-singles",
    "battle-of-bc-6-7": "ultimate-singles",
    "the-pregame-bobc6-pre-event": "ultimate-singles",
    "the-coinbox-97-steve-banned": "ultimate-singles",
    "best-of-the-west-ii-misfire": "ultimate-singles",
    "the-coinbox-96-steve-banned": "ultimate-singles",
    "collision-2024-6": "ultimate-singles",
    "the-coinbox-95-steve-banned": "ultimate-singles",
    "bonito-harbor": "ultimate-singles",
    "cirque-du-cfl-3-ft-zomba-moist-light-miya-asimo": "smash-ultimate-1v1",
    "the-coinbox-94-steve-unbanned": "ultimate-singles",
    "the-coinbox-93-steve-banned": "ultimate-singles",
    "king-con": "ssbu-1v1",
    "d-jo-106": "ultimate-singles",
    "pre-genesis-x-at-guildhouse-ultimate-melee-sf6": "smash-ultimate-singles-switch-6-00-pm",
    "the-coinbox-89-steve-banned": "ultimate-singles",
    "the-coinbox-87": "ultimate-singles",
    "9with": "kowloon",
    "sp-10-umeburasp-10": "singles",
    "luminosity-makes-big-moves-2024": "ultimate-singles",
    "the-coinbox-110": "ultimate-singles",
    "regen-2024": "ultimate-singles-sat-sun",
    "riptide-2024-5": "ultimate-singles",
}


def get_tournaments(result):
    tournaments = result['data']['player']['user']['tournaments']['nodes']
    for tournament in tournaments:
        slug = tournament['slug'].removeprefix('tournament/')
        tournament['event'] = TOURNAMENT_TO_EVENT.get(slug, '')
        tournament['slug'] = slug
    return tournaments


def make_df(gamertag, tournaments):
    df = pd.DataFrame(tournaments)
    df = df.drop_duplicates().reset_index(drop=True)
    df['gamertag'] = gamertag
    reordered_df = df[['gamertag', 'name', 'slug', 'startAt', 'event']]
    return reordered_df


def get_all_tournaments(player_id):
    page = 1
    all_tournaments = []
    while True:
        # print('page', page)
        result = fetch_tournament_data(player_id, page)
        tournaments = get_tournaments(result)
        if tournaments == []:
            break
        all_tournaments.extend(tournaments)
        page += 1
    return all_tournaments


def lambda_handler(event, context):
    players = [
        {"gamertag": "Tweek", "id": 15768},
        {"gamertag": "MkLeo", "id": 222927},
        {"gamertag": "Sparg0", "id": 158026},
        {"gamertag": "Light", "id": 158871},
        {"gamertag": "あcola", "id": 2691639},
        {"gamertag": "Glutonny", "id": 6122},
        {"gamertag": "Riddles", "id": 160464},
        {"gamertag": "Tea", "id": 695882},
        {"gamertag": "Kurama", "id": 175623},
        {"gamertag": "Kola", "id": 18802},
    ]
    
    event_df = pd.DataFrame(columns=['gamertag', 'name', 'slug', 'startAt', 'event'])
    for player in players:
        tournaments = get_all_tournaments(player['id'])
        df = make_df(player['gamertag'], tournaments)
        event_df = pd.concat([event_df, df]).reset_index(drop=True)
    
    sorted_grouped_data = sorted(
        event_df.groupby('slug'),
        key=lambda x: x[1]['startAt'].iloc[0]
    )
    
    tournaments = [
        {
            'name': group['name'].iloc[0],
            'slug': group['slug'].iloc[0],
            'startAt': group['startAt'].iloc[0],
            'gamertag': group['gamertag'].tolist(),
            'event': group['event'].iloc[0],
        }
        for _, group in sorted_grouped_data
    ]
    
    tournaments_json = json.dumps(tournaments)
    

    #
    # Compare and see if there's a new tournament
    #
    existing_tournaments = get('tournaments.json')
    if tournaments_json != existing_tournaments:
        send_email(
            'New tournament added!',
            'Check https://ebanner.github.io/find-smash-tournaments for updates.'
        )

    put('tournaments.json', tournaments_json)

    return {
        'statusCode': 200,
        'body': 'Success!'
    }

