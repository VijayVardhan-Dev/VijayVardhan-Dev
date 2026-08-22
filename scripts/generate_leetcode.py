import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

USERNAME = "Vardhan_Dev00"
API_BASE = "https://leetcode-stats.tashif.codes"

OUTPUT = Path("assets/leetcode-dashboard.svg")


def fetch(endpoint):
    url = f"{API_BASE}/{USERNAME}/{endpoint}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


stats_response = fetch("stats")
heatmap_response = fetch("heatmap")

stats = stats_response["data"]
heatmap = heatmap_response["data"]

total_solved = stats["totalSolved"]
easy = stats["byDifficulty"]["easy"]
medium = stats["byDifficulty"]["medium"]
hard = stats["byDifficulty"]["hard"]

# ---------------------------------------------------------
# Build last 12 months of activity
# ---------------------------------------------------------

activity = {}

for item in heatmap.get("dailyContributions", []):
    activity[item["date"]] = item.get("count", 0)


today = datetime.now().date()

# Start roughly 1 year ago.
start_date = today - timedelta(days=364)

# Align to Sunday so the grid looks clean.
start_date -= timedelta(days=(start_date.weekday() + 1) % 7)


def level(count):
    if count == 0:
        return "#161616"
    if count <= 1:
        return "#3A3A3A"
    if count <= 3:
        return "#777777"
    return "#FFFFFF"


# ---------------------------------------------------------
# SVG
# ---------------------------------------------------------

WIDTH = 1200
HEIGHT = 390

svg = f'''<svg width="{WIDTH}" height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
fill="none"
xmlns="http://www.w3.org/2000/svg">

<rect width="1200" height="390" fill="#000000"/>

<rect
    x="1"
    y="1"
    width="1198"
    height="388"
    stroke="#333333"
    stroke-width="2"
/>

<!-- Header -->

<text
    x="42"
    y="48"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="20"
    font-weight="700"
    letter-spacing="2"
>
LEETCODE
</text>

<text
    x="1158"
    y="48"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="18"
    text-anchor="end"
>
{today.year}
</text>

<line
    x1="42"
    y1="70"
    x2="1158"
    y2="70"
    stroke="#222222"
/>

<!-- Statistics -->

<text x="70" y="118"
fill="#FFFFFF"
font-family="monospace"
font-size="28"
text-anchor="middle">
{total_solved}
</text>

<text x="365" y="118"
fill="#FFFFFF"
font-family="monospace"
font-size="28"
text-anchor="middle">
{easy}
</text>

<text x="660" y="118"
fill="#FFFFFF"
font-family="monospace"
font-size="28"
text-anchor="middle">
{medium}
</text>

<text x="955" y="118"
fill="#FFFFFF"
font-family="monospace"
font-size="28"
text-anchor="middle">
{hard}
</text>

<text x="70" y="143"
fill="#888888"
font-family="monospace"
font-size="12"
text-anchor="middle"
letter-spacing="1">
SOLVED
</text>

<text x="365" y="143"
fill="#888888"
font-family="monospace"
font-size="12"
text-anchor="middle"
letter-spacing="1">
EASY
</text>

<text x="660" y="143"
fill="#888888"
font-family="monospace"
font-size="12"
text-anchor="middle"
letter-spacing="1">
MEDIUM
</text>

<text x="955" y="143"
fill="#888888"
font-family="monospace"
font-size="12"
text-anchor="middle"
letter-spacing="1">
HARD
</text>

<line
    x1="42"
    y1="165"
    x2="1158"
    y2="165"
    stroke="#222222"
/>

<!-- Heatmap title -->

<text
    x="42"
    y="195"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="12"
    letter-spacing="1"
>
SUBMISSION ACTIVITY
</text>

<g transform="translate(42 215)">
'''

# ---------------------------------------------------------
# Heatmap
# ---------------------------------------------------------

CELL = 14
GAP = 5

for week in range(53):

    for day in range(7):

        current = start_date + timedelta(
            days=week * 7 + day
        )

        if current > today:
            continue

        date_string = current.isoformat()

        count = activity.get(date_string, 0)

        x = week * (CELL + GAP)
        y = day * (CELL + GAP)

        svg += f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    fill="{level(count)}"
/>
'''

svg += '''
</g>

<!-- Legend -->

<text
    x="42"
    y="340"
    fill="#777777"
    font-family="monospace"
    font-size="11"
>
LESS
</text>

<rect x="78" y="330" width="13" height="13" fill="#161616"/>
<rect x="98" y="330" width="13" height="13" fill="#3A3A3A"/>
<rect x="118" y="330" width="13" height="13" fill="#777777"/>
<rect x="138" y="330" width="13" height="13" fill="#FFFFFF"/>

<text
    x="161"
    y="340"
    fill="#777777"
    font-family="monospace"
    font-size="11"
>
MORE
</text>

<!-- Footer -->

<line
    x1="42"
    y1="355"
    x2="1158"
    y2="355"
    stroke="#222222"
/>

<text
    x="600"
    y="378"
    fill="#888888"
    font-family="monospace"
    font-size="11"
    text-anchor="middle"
    letter-spacing="1"
>
DATA STRUCTURES  ·  ALGORITHMS  ·  PROBLEM SOLVING
</text>

</svg>
'''

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(svg, encoding="utf-8")

print(
    f"Updated LeetCode dashboard: "
    f"{total_solved} solved | "
    f"Easy {easy} | "
    f"Medium {medium} | "
    f"Hard {hard}"
)
