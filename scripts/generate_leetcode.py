import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USERNAME = "Vardhan_Dev00"

API_URL = (
    f"https://leetcode-stats.tashif.codes/"
    f"{USERNAME}/stats"
)

OUTPUT = Path("assets/leetcode-dashboard.svg")


def fetch_stats():
    request = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def get_level(count):
    if count == 0:
        return "#151515"
    if count <= 2:
        return "#3A3A3A"
    if count <= 5:
        return "#777777"
    return "#FFFFFF"


# --------------------------------------------------
# FETCH DATA
# --------------------------------------------------

data = fetch_stats()

if data.get("status") != "success":
    raise RuntimeError(f"LeetCode API error: {data}")


total_solved = data["totalSolved"]
easy = data["easySolved"]
medium = data["mediumSolved"]
hard = data["hardSolved"]
acceptance = data["acceptanceRate"]

submission_calendar = data["submissionCalendar"]


# --------------------------------------------------
# CONVERT UNIX TIMESTAMPS
# --------------------------------------------------

activity = {}

for timestamp, count in submission_calendar.items():

    date = datetime.fromtimestamp(
        int(timestamp),
        tz=timezone.utc
    ).date()

    activity[date] = count


# --------------------------------------------------
# DATE RANGE
# --------------------------------------------------

today = datetime.now(timezone.utc).date()

start_date = today - timedelta(days=364)

# Start on Sunday for a clean contribution-style grid.
start_date -= timedelta(
    days=(start_date.weekday() + 1) % 7
)


# --------------------------------------------------
# SVG CONFIG
# --------------------------------------------------

WIDTH = 1200
HEIGHT = 390

CELL = 14
GAP = 5

svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
fill="none"
>

<rect
    width="{WIDTH}"
    height="{HEIGHT}"
    fill="#000000"
/>

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    stroke="#333333"
    stroke-width="2"
/>


<!-- HEADER -->

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


<!-- STATISTICS -->


<text
    x="70"
    y="118"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="28"
    text-anchor="middle"
>
{total_solved}
</text>

<text
    x="365"
    y="118"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="28"
    text-anchor="middle"
>
{easy}
</text>

<text
    x="660"
    y="118"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="28"
    text-anchor="middle"
>
{medium}
</text>

<text
    x="955"
    y="118"
    fill="#FFFFFF"
    font-family="monospace"
    font-size="28"
    text-anchor="middle"
>
{hard}
</text>


<text
    x="70"
    y="143"
    fill="#888888"
    font-family="monospace"
    font-size="12"
    text-anchor="middle"
    letter-spacing="1"
>
SOLVED
</text>

<text
    x="365"
    y="143"
    fill="#888888"
    font-family="monospace"
    font-size="12"
    text-anchor="middle"
    letter-spacing="1"
>
EASY
</text>

<text
    x="660"
    y="143"
    fill="#888888"
    font-family="monospace"
    font-size="12"
    text-anchor="middle"
    letter-spacing="1"
>
MEDIUM
</text>

<text
    x="955"
    y="143"
    fill="#888888"
    font-family="monospace"
    font-size="12"
    text-anchor="middle"
    letter-spacing="1"
>
HARD
</text>


<line
    x1="42"
    y1="165"
    x2="1158"
    y2="165"
    stroke="#222222"
/>


<!-- SUBMISSION ACTIVITY -->

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


# --------------------------------------------------
# HEATMAP
# --------------------------------------------------

for week in range(53):

    for day in range(7):

        current_date = start_date + timedelta(
            days=(week * 7) + day
        )

        if current_date > today:
            continue

        count = activity.get(current_date, 0)

        x = week * (CELL + GAP)
        y = day * (CELL + GAP)

        fill = get_level(count)

        svg += f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    fill="{fill}"
/>
'''


svg += f'''
</g>


<!-- LEGEND -->

<text
    x="42"
    y="340"
    fill="#777777"
    font-family="monospace"
    font-size="11"
>
LESS
</text>

<rect
    x="78"
    y="330"
    width="13"
    height="13"
    fill="#151515"
/>

<rect
    x="98"
    y="330"
    width="13"
    height="13"
    fill="#3A3A3A"
/>

<rect
    x="118"
    y="330"
    width="13"
    height="13"
    fill="#777777"
/>

<rect
    x="138"
    y="330"
    width="13"
    height="13"
    fill="#FFFFFF"
/>

<text
    x="161"
    y="340"
    fill="#777777"
    font-family="monospace"
    font-size="11"
>
MORE
</text>


<!-- FOOTER -->

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


# --------------------------------------------------
# WRITE FILE
# --------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT.write_text(
    svg,
    encoding="utf-8"
)

print(
    f"""
LeetCode dashboard updated.

Username : {USERNAME}
Solved   : {total_solved}
Easy     : {easy}
Medium   : {medium}
Hard     : {hard}
Accept.  : {acceptance}%

Output   : {OUTPUT}
"""
)
