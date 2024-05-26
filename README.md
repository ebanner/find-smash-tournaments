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
2023-01 genesis-9-1 → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny, Riddles, Tea
2023-11 port-priority-8-5 → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny, Riddles, Tea
2022-10 ludwig-smash-invitational → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny, Riddles, Tea
2022-07 double-down-2022 → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles, Tea
2021-11 instage-2021 → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles, Tea
2019-12 2gg-kongo-saga → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles, Tea
2022-09 smash-ultimate-summit-5-presented-by-coinbase → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny, Riddles
2023-05 battle-of-bc-5-5 → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny, Riddles
2024-02 genesis-x → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles, Tea
2022-12 scuffed-world-tour → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny, Riddles
2023-12 watch-the-throne → Tweek, MkLeo, Sparg0, Light, あcola, Glutonny
2020-02 frostbite-2020 → Tweek, MkLeo, Light, Glutonny, Riddles, Tea
2022-03 smash-ultimate-summit-4 → Tweek, MkLeo, Sparg0, Light, Glutonny, Tea
2019-04 2gg-prime-saga-1 → Tweek, MkLeo, Sparg0, Light, Glutonny, Tea
2022-04 genesis-8 → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles
2023-01 let-s-make-big-moves-2023 → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles
2022-08 super-smash-con-2022 → Tweek, MkLeo, Light, あcola, Glutonny, Riddles
2023-03 smash-ultimate-summit-6 → Tweek, MkLeo, Sparg0, あcola, Glutonny, Riddles
2022-03 collision-2022 → Tweek, MkLeo, Sparg0, Light, Glutonny, Riddles
2024-05 12-kagaribi-12 → MkLeo, Sparg0, あcola, Glutonny, Tea
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

## Data Source

All data comes from the [start.gg Developer API](https://developer.start.gg/docs/intro/) - thank you!
