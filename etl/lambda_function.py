import json
import pandas as pd
from datetime import datetime
import requests

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


def get_data(player_id, page, PER_PAGE=490):
    url = 'https://api.start.gg/gql/alpha'
    
    query = """
      query PlayerQuery {
      player(id: "{player_id}") {
        id
        gamerTag
        sets(page: {page}, perPage: 490) {
          nodes {
            event {
              tournament {
                slug
                startAt
              }
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


def get_events(result):
    events = result['data']['player']['sets']['nodes']
    events = [event['event']['tournament'] for event in events]
    return events

def get_datetime(timestamp):
    # Convert timestamp to datetime object
    datetime_object = datetime.fromtimestamp(timestamp)
    
    # Format datetime object as a readable string
    readable_date_time = datetime_object.strftime("%m-%Y")
    
    return readable_date_time

def make_df(gamertag, events):
    df = pd.DataFrame(events)
    df = df.drop_duplicates().reset_index(drop=True)
    df['startAt'] = df.startAt.map(lambda ts: get_datetime(ts))
    df['gamertag'] = gamertag
    reordered_df = df[['gamertag', 'slug', 'startAt']]
    return reordered_df

def get_all_events(player_id):
    page = 1
    all_events = []
    while True:
        # print('page', page)
        result = get_data(player_id, page)
        events = get_events(result)
        if events == []:
            break
        all_events.extend(events)
        page += 1
    return all_events

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
    
    event_df = pd.DataFrame(columns=['gamertag', 'slug', 'startAt'])
    for player in players:
        events = get_all_events(player['id'])
        df = make_df(player['gamertag'], events)
        event_df = pd.concat([event_df, df]).reset_index(drop=True)
    
    event_df.slug = event_df.slug.map(lambda event: event.lstrip('tournament/')) # TODO do upstream
    
    
    #
    # Make JSON
    #
    print(event_df)
    event_df['year'] = event_df.startAt.apply(lambda x: int(x.split('-')[1]))
    df_2024 = event_df[event_df.year == 2024].reset_index(drop=True)
    
    sorted_grouped_data = sorted(
        df_2024.groupby('slug'),
        key=lambda x: x[1]['startAt'].iloc[0]
    )
    
    tournaments = [
        {
            'slug': group['slug'].iloc[0],
            'startAt': group['startAt'].iloc[0],
            'gamertag': group['gamertag'].tolist()
        }
        for _, group in sorted_grouped_data
    ]
    
    tournaments_json = json.dumps(tournaments)
    
    put('tournaments.json', tournaments_json)

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }

