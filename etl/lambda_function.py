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
    except Exception as e:
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
          events(query: { page: {page}, perPage: {per_page} }) {
            nodes {
              tournament {
                name
              }
              slug
              startAt
            }
          }
        }
      }
    }""".replace('{page}', str(page)).replace('{player_id}', str(player_id)).replace('{per_page}', str(PER_PAGE))
    
    token = os.environ['START_GG_TOKEN']
    headers = { 
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'  # if authentication is needed
    }   
    
    response = requests.post(url, json={'query': query}, headers=headers)
    result = response.json()

    return result


def get_tournaments(result):
    tournaments = result['data']['player']['user']['events']['nodes']
    for tournament in tournaments:
        tournament['name'] = tournament['tournament']['name']
        del tournament['tournament']
    return tournaments


def make_df(gamertag, tournaments):
    df = pd.DataFrame(tournaments)
    df = df.drop_duplicates().reset_index(drop=True)
    df['gamertag'] = gamertag
    reordered_df = df[['gamertag', 'name', 'slug', 'startAt']]
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
    
    event_df = pd.DataFrame(columns=['gamertag', 'name', 'slug', 'startAt'])
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
        }
        for _, group in sorted_grouped_data
    ]

    def get_tournaments_by_name(tournaments, name):
        tournaments_by_name = [tournament for tournament in tournaments if tournament['name'] == name]
        return tournaments_by_name

    def dedupe_tournaments(tournaments):
        max_players = 0
        max_idx = -1
        for i, tournament in enumerate(tournaments):
            players = tournament['gamertag']
            num_players = len(players)
            if num_players > max_players:
                max_players = num_players
                max_idx = i
        return tournaments[max_idx:max_idx+1]

    tournament_names = event_df.name.unique()
    deduped_tournaments = []
    for name in tournament_names:
        tournaments_by_name = get_tournaments_by_name(tournaments, name)
        if len(tournaments_by_name) == 1:
            deduped_tournaments.append(tournaments_by_name[0])
        else:
            deduped_tournaments.append(dedupe_tournaments(tournaments_by_name)[0])

    sorted_tournaments = list(sorted(deduped_tournaments, key=lambda x: x['startAt'], reverse=True))

    tournaments_json = json.dumps(sorted_tournaments)

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

