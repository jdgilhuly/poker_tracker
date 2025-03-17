# Poker ELO Tracker

This system tracks player performance in poker games using an ELO rating system. It processes game results from a CSV file, calculates ELO ratings after each session, and provides visualization of rating changes over time.

## Features

- Process poker session results from CSV files
- Calculate ELO ratings for each player
- Track rating changes over time
- Generate visualizations of rating progression
- Export ratings to CSV and JSON formats

## Requirements

- Python 3.6+
- Required packages: pandas, numpy, matplotlib

You can install the required packages with:

```bash
pip install pandas numpy matplotlib
```

## Usage

### Basic Usage

Run the script with default options:

```bash
python main.py
```

This will:
1. Read poker results from the default CSV file
2. Calculate ELO ratings for each player
3. Save ELO history to CSV
4. Save current ratings to JSON
5. Generate a plot of ELO changes over time

### Command Line Options

For more control, use these command line options:

```bash
python main.py --input your_data.csv --output-csv elo_data.csv --output-json ratings.json --output-plot elo.png
```

Available options:
- `--input` or `-i`: Input CSV file with poker results (default: "Poker Spreadsheet - Sheet1 (1).csv")
- `--output-csv`: Output CSV file for ELO history (default: "elo_history.csv")
- `--output-json`: Output JSON file for ELO ratings (default: "elo_ratings.json")
- `--output-plot`: Output PNG file for ELO history plot (default: "elo_history.png")
- `--no-plot`: Disable plotting ELO history

## Input CSV Format

The input CSV should have the following format:
- First column: Date of the poker session
- Other columns: Player names with their net profit/loss for each session

Example:
```
,Date,,Daniel,Andrew,Josh,Sean,Yahya
,2/22/2025,,3.5,-71.5,-102,-150,83.5
,2/26/2025,,19.75,,-27.75,28.75,16.75
```

Missing values indicate that the player did not participate in that session.

## ELO Rating System

The system uses a modified ELO rating system adapted for poker:
- Each player starts with an initial rating of 1500
- After each session, players gain or lose rating points based on their performance relative to other players
- The amount of points won or lost depends on the expected performance (based on current ratings) and the actual results
- The K-factor (which determines how much ratings can change) is dynamic based on the profit difference

## Output Files

- `elo_history.csv`: Contains the ELO ratings of all players after each session
- `elo_ratings.json`: Contains the current ratings, rankings, and history in JSON format
- `elo_history.png`: Visual plot of ELO ratings over time

## How to Add a New Poker Session

To add a new poker session:
1. Add a new row to your input CSV file with the date and each player's profit/loss
2. Run the script again to update the ELO ratings

## License

This project is available under the MIT License.