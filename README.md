# World Cup 2026 Analyzer
#### Video Demo: https://youtu.be/UhRFJhXHXpY
🌐 **Live app:** https://world-cup-2026-bet-analyzer.streamlit.app/
#### Description:

## What is this project?

This is a data analysis tool for the 2026 FIFA World Cup. It takes historical World Cup data — every match, every goal, every card, from Uruguay 1930 all the way to Qatar 2022 — and turns it into statistics that help you understand what's likely to happen in a match between any two of the 48 teams competing this year.

The idea came from sports betting, but the tool is really about data. It doesn't tell you what to bet. It tells you what the numbers say — and you decide what to do with that.

You pick two teams, hit Analyze, and get a full statistical breakdown: expected goals, card probabilities, corner markets, period-by-period goal likelihood, and an interactive chart showing when each team is most dangerous throughout a match.

## The data

The heart of the project is four CSV files stored in the `data/` folder.

**`matches.csv`** — every World Cup match from 1930 to 2022. Who played, who won, what the score was, whether it went to extra time or penalties. This is the backbone that connects everything else.

**`goals.csv`** — every goal in World Cup history. The minute it happened, the match period, the team, the player, and whether it was a penalty or an own goal. This is where the minute-by-minute probability chart comes from.

**`bookings.csv`** — every yellow and red card since 1970. It distinguishes between yellow cards, direct reds, and second yellows — which made it possible to calculate things like "how likely is this team to get a second yellow card once they've already received a first?"

**`Fifa_world_cup_matches.csv`** — this one only covers Qatar 2022, but it's packed with detail: possession, corners, attempts on target and off target, offsides, fouls, free kicks, goals inside and outside the penalty area, and more. It's what powers the corners and possession analysis.

## The code

### `project.py`

This is where everything happens. It has a `main()` function and four additional functions.

**`load_data()`** loads all four CSVs into pandas DataFrames. It also cleans the possession columns in the Qatar dataset, which store values like "42%" as strings — those get converted to actual numbers before anything else runs.

**`get_team_stats()`** is the most complex function. You give it a team name and it goes through the historical data to build a complete statistical profile: goals scored and conceded broken down by time period, cards, probability of a second yellow, probability of a direct red, goals at each individual minute of the match, and — if the team played in Qatar 2022 — corners, possession, fouls, and more. It also calculates a confidence level based on how many World Cup matches the team has played. Teams with less data get flagged so you know how much to trust the numbers.

**`calculate_markets()`** takes the stats from two teams and combines them into betting market outputs. It calculates over/under markets for goals, corners, and cards, whether both teams are likely to score (BTTS), and period-by-period goal probabilities that weigh each team's attack against the other's defense.

**`generate_report()`** takes all of that and displays it as a proper web interface using Streamlit — metrics, side-by-side comparisons, and the Plotly chart.

**`plot_goal_probability()`** builds the interactive minute-by-minute chart. The raw data is very noisy (most minutes have zero goals), so it gets smoothed with a rolling average and rendered as a spline curve. The chart is split into three zones — 0–30, 31–60, 61–90 — with the period-level probabilities shown directly on the chart.

### `test_project.py`

Three pytest tests cover the core functions: one checks that the data loads correctly, one checks that the stats function returns sensible output for a known team, and one checks that the markets dictionary has the right structure and types.

### `requirements.txt`

The external libraries the project depends on:

- **pandas** — handles all the data loading, filtering, and statistical calculations. Every time the tool searches for a team's matches or counts goals by minute, that's pandas.
- **streamlit** — turns the Python script into a web application. Without it, the tool would be a command-line program. With it, anyone can use it from a browser.
- **plotly** — powers the interactive minute-by-minute goal probability chart. It handles the smoothing, the color zones, and the annotations.
- **pytest** — runs the automated tests in `test_project.py` to verify the core functions work correctly.

## Design decisions

**Two datasets instead of one.** The GitHub dataset goes back to 1930 and covers goals and cards in detail, but it doesn't have corners or possession. The Kaggle dataset has all of that but only for Qatar 2022. Using both together gives the tool depth and breadth that neither dataset has alone.

**Confidence levels.** Argentina has played over 90 World Cup matches. Some teams in 2026 are making their debut and have zero historical data. Without a confidence indicator, the tool would show a "0%" probability and the user wouldn't know if that means "this never happens" or "we have no data." The confidence level (alta/media/baja) makes that distinction clear.

**Streamlit over a terminal interface.** The original plan was a command-line tool, but Streamlit made it possible to build a proper web interface without leaving Python. The result is something anyone can use without knowing how to run a script.

**Smoothing the chart.** A raw minute-by-minute chart looked like noise — spikes at random minutes, flat zeros everywhere else. A rolling average with spline interpolation turns that into a curve that actually tells you something: when a team tends to score, and when they tend to concede.
