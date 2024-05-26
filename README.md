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

```
slug                                             startAt            
tournament/port-priority-8-5                     2023-11-10 15:00:00    9
tournament/ludwig-smash-invitational             2022-10-21 13:00:00    9
tournament/genesis-9-1                           2023-01-20 12:00:00    9
tournament/double-down-2022                      2022-07-08 07:00:00    8
tournament/genesis-x                             2024-02-16 13:00:00    8
                                                                       ..
tournament/icarus-v                              2019-04-27 04:00:00    1
tournament/icarus-2023                           2023-06-03 03:00:00    1
tournament/ibp-masters-showdown                  2017-11-11 15:00:00    1
tournament/ib-games-4-the-end-of-sisqui-s-reign  2023-06-01 12:00:00    1
tournament/ya-es-viernes-3-bici-weekly-1         2020-07-10 23:30:00    1
Length: 2031, dtype: int64
```

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
