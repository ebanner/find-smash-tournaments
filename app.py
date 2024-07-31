from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/')
def hello_world():
    with open('2024_tournaments.json') as file:
        tournaments = json.load(file)

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

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

