import json
import pandas as pd
from datetime import datetime
import requests

from dotenv import load_dotenv
load_dotenv()

import os

import boto3
from botocore.exceptions import ClientError

import gspread
from gspread_dataframe import set_with_dataframe


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


if __name__ == '__main__':
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

    #
    # Make DataFrame UI for Looker
    #
    tournaments_df = pd.DataFrame(deduped_tournaments)
    tournaments_df['#'] = tournaments_df['gamertag'].map(len)
    tournaments_df['url'] = tournaments_df['slug'].map(lambda slug: f'https://www.start.gg/{slug}/overview')
    tournaments_df['Players'] = tournaments_df['gamertag'].map(lambda gamertag: ', '.join(gamertag))
    tournaments_df['Date'] = tournaments_df['startAt']

    #
    # Write to Google Sheets
    #
    worksheet = spreadsheet.worksheet('Sheet1')
    worksheet.clear()
    set_with_dataframe(worksheet, tournaments_df)

