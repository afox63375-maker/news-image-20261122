[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/afox63375-maker/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/afox63375-maker/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# Sunday 22 November 2026 — The World in One Day (remake)

A single-page newspaper front page that sums up Sunday 22 November 2026
in 35 stories, rebuilt around the front-page discipline of the day's
top-ranked entry: a cream broadsheet sheet, a giant serif date, a strip
of big red numbers, and a regional count bar — with every story carried
by a picture that shows the story itself.

## What is on the page

- **Three lead stories, fully illustrated.** COP31 delegates sit around
  a long table under a globe and a wall clock near the 03:00 deadline;
  drones and missile streaks fill the night sky over Kyiv's skyline;
  a shore plant and a tanker burn in Bahrain.
- **Ten more stories as illustrated cards** (4–13): a cargo ship ablaze
  in the Gulf of Finland, a capsizing mourners' boat in Bayelsa, a
  handshake in Jerusalem, an aid truck in Gaza, a fugitive held in
  Sinaloa, a pylon over dark Tehran houses, a falling chart under a
  magnifying glass for the Nvidia probe, a heart monitor for Bolsonaro's
  intensive care, and a submarine for the AUKUS row.
- **A Sunday weather strip**: forecast highs and lows with drawn icons
  for Antalya, Kyiv, Manama, Tehran, Sinaloa and Canberra.
- **A dotted world map** whose numbered pins match the story numbers
  and are coloured by region, beside a 22-item brief list (14–35).
- **A date check box** stating the wire cut-off time and naming the
  stories left out as other days' news.

## How it is made

Every picture, the map and the icons are drawn in code with Pillow
primitives — no photographs and no image assets. The drawing is
deterministic: run it twice and the PNG is byte-identical.

`main.py` is the repository entrypoint. It uses only the Python
standard library: it validates the bundled `entry.png` (PNG signature,
chunk CRCs, an IHDR no larger than 1024×1024, at most 1 MiB, IDAT
present, IEND last) and copies the bytes unchanged to
`$MAKEFUN_OUTPUT_DIR/entry.png`.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
