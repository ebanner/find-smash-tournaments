# find-smash-tournaments

Find smash ultimate tournaments that my favorite players are competing in

## What is this?

Enter a list of my favorite smash players and find out which tournaments they're all competing in together e.g.

```
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
]
```

👇

![image](https://github.com/ebanner/find-smash-tournaments/assets/2068912/a0cacecd-8367-4996-b819-7c8743efc033)

## Output

The output of this is basically to generate a CSV with players and tournaments so we can group by the tournaments and see which ones have most of my favorite players in them e.g. 

```
gamertag,slug,startAt
Tweek,tournament/momocon-2024-7,2024-05-24 14:00:00
Tweek,tournament/get-on-my-level-x-canadian-fighting-game-championships,2024-05-17 10:00:00
Tweek,tournament/lvl-up-expo-2024,2024-04-26 12:00:00
Tweek,tournament/kroger-gaming-presents-the-luminosity-invitational,2024-04-20 10:30:00
Tweek,tournament/kawaii-kon-2024,2024-03-29 16:00:00
Tweek,tournament/collision-2024-6,2024-03-15 10:00:00
Tweek,tournament/the-coinbox-94-steve-unbanned,2024-03-06 18:00:00
Tweek,tournament/the-coinbox-93-steve-banned,2024-02-28 18:00:00
Tweek,tournament/genesis-x,2024-02-16 13:00:00
```

## Why?

Basically, I just want to know what the biggest smash tournaments are so I can watch them

## Data Source

All data comes from the [start.gg GraphQL API](https://developer.start.gg/docs/intro/) - thank you!

## 2024

![image](https://github.com/ebanner/find-smash-tournaments/assets/2068912/9a7fecf3-5d2e-4ece-848e-86178fc4b468)

## 2023

![image](https://github.com/ebanner/find-smash-tournaments/assets/2068912/7e6cfb3b-6698-43a0-9d88-a03aec30afc2)

## 2022

![image](https://github.com/ebanner/find-smash-tournaments/assets/2068912/21210e77-edd9-40b6-81e7-53d169721397)
