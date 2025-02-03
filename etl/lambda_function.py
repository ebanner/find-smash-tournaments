import json
import pandas as pd
from datetime import datetime
import requests

import time

import os

import boto3
from botocore.exceptions import ClientError

import gspread
from gspread_dataframe import set_with_dataframe


START_GG_API_URL = 'https://api.start.gg/gql/alpha'


def get_credentials_dict():
    secret_name = "FIND_SMASH_TOURNAMENTS_ETL"
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

    secret = get_secret_value_response['SecretString']

    secret_dict = json.loads(secret)

    credentials_dict = json.loads(secret_dict['SERVICE_ACCOUNT_KEY_JSON'])

    return credentials_dict


credentials_dict = get_credentials_dict()
gsheets_client = gspread.service_account_from_dict(credentials_dict)
spreadsheet = gsheets_client.open('Smash Tournaments')


def get_event_df(player):
    def fetch_tournament_data(player_id, page, PER_PAGE=490):
        
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
        
        response = requests.post(START_GG_API_URL, json={'query': query}, headers=headers)
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

    tournaments = get_all_tournaments(player['id'])
    event_df = make_df(player['gamertag'], tournaments)
    event_df['type'] = 'event'
    return event_df


def get_future_tournament_df(player):
    def fetch_tournaments(player_id, page):
        query = """
        query UserTournaments($playerId: ID!, $perPage: Int, $page: Int) {
          player(id: $playerId) {
            user {
              tournaments(query: { perPage: $perPage, page: $page, sortBy: "startAt" }) {
                nodes {
                  name
                  startAt
                  slug
                }
              }
            }
          }
        }"""

        variables = {
            "playerId": player_id,
            "perPage": 390,
            "page": page

        }

        token = os.environ['START_GG_TOKEN']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'  # if authentication is needed
        }

        response = requests.post(START_GG_API_URL, json={'query': query, 'variables': variables}, headers=headers)
        result = response.json()

        tournaments = result['data']['player']['user']['tournaments']['nodes']

        return tournaments

    def get_tournaments(player_id):
        all_tournaments = []
        page = 1
        while True:
            print('page', page)
            tournaments = fetch_tournaments(player_id, page)
            if tournaments == []:
                break
            all_tournaments.extend(tournaments)
            page += 1
        return all_tournaments

    tournaments = get_tournaments(player['id'])
    tournament_df = pd.DataFrame(tournaments)
    future_tournament_df = tournament_df[tournament_df.startAt > time.time()]
    future_tournament_df['type'] = 'tournament'
    future_tournament_df['gamertag'] = player['gamertag']
    return future_tournament_df


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
    
    df = pd.DataFrame(columns=['gamertag', 'name', 'slug', 'startAt', 'type'])
    for player in players:
        event_df = get_event_df(player)
        future_tournament_df = get_future_tournament_df(player)
        df = pd.concat([df, event_df, future_tournament_df]).reset_index(drop=True)

    sorted_grouped_data = sorted(
        df.groupby('slug'),
        key=lambda x: x[1]['startAt'].iloc[0]
    )
    
    tournaments = [
        {
            'name': group['name'].iloc[0],
            'slug': group['slug'].iloc[0],
            'startAt': group['startAt'].iloc[0],
            'gamertag': group['gamertag'].tolist(),
            'type': group['type'].iloc[0]
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

    tournament_names = df.name.unique()
    deduped_tournaments = []
    for name in tournament_names:
        tournaments_by_name = get_tournaments_by_name(tournaments, name)
        if len(tournaments_by_name) == 1:
            deduped_tournaments.append(tournaments_by_name[0])
        else:
            deduped_tournaments.append(dedupe_tournaments(tournaments_by_name)[0])

    #
    # Make DataFrame UI for Looker
    #
    tournaments_df = pd.DataFrame(deduped_tournaments)
    tournaments_df['#'] = tournaments_df['gamertag'].map(len)
    def get_url(row):
        print(row)
        if row['type'] == 'event':
            url = f'https://www.start.gg/{row.slug}/overview'
        elif row['type'] == 'tournament':
            url = f'https://www.start.gg/{row.slug}/details'
        return url
    tournaments_df['url'] = tournaments_df.apply(get_url, axis=1)
    tournaments_df['Players'] = tournaments_df['gamertag'].map(lambda gamertag: ', '.join(gamertag))
    tournaments_df['Date'] = tournaments_df['startAt']

    #
    # Write to Google Sheets
    #
    worksheet = spreadsheet.worksheet('Sheet1')
    worksheet.clear()
    set_with_dataframe(worksheet, tournaments_df)

    num_rows = len(tournaments_df)

    return {
        'statusCode': 200,
        'body': f'Success - {num_rows} rows written to Google Sheets!'
    }

