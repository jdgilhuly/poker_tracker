import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
from datetime import datetime
from algo import PokerELO

def load_poker_data(csv_file):
    """Load poker data from CSV file and clean it."""
    # Read CSV with correct handling of empty cells
    df = pd.read_csv(csv_file, header=0)

    # Fix the column names (first row contains headers)
    # Find the column containing 'Date'
    date_col = None
    for col in df.columns:
        if 'Date' in str(df[col].iloc[0]):
            date_col = col
            break

    if date_col:
        # Extract the real headers from the first row
        new_headers = {}
        for col in df.columns:
            if pd.notna(df[col].iloc[0]):
                new_headers[col] = df[col].iloc[0].strip()
            else:
                new_headers[col] = col

        # Rename columns
        df = df.rename(columns=new_headers)

        # Remove the first row (now in headers)
        df = df.iloc[1:].reset_index(drop=True)

    # Clean up unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Convert date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Drop rows with no data
    df = df.dropna(subset=['Date'], how='all')
    df = df.reset_index(drop=True)

    # Convert numeric values to float
    player_columns = [col for col in df.columns if col != 'Date']
    for col in player_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def process_poker_sessions(df):
    """Process each poker session and calculate ELO."""
    # Get all player names (columns except Date and unnamed columns)
    player_columns = [col for col in df.columns if col != 'Date' and not col.startswith('Unnamed')]

    # Initialize ELO system with all players
    elo_system = PokerELO(player_columns)

    # Store ELO history
    elo_history = []

    # Process each session
    for idx, row in df.iterrows():
        date = row['Date']

        # Create session results dictionary
        session_results = {}
        for player in player_columns:
            if pd.notna(row[player]):  # Only include players who participated in this session
                session_results[player] = row[player]

        # Skip if less than 2 players
        if len(session_results) < 2:
            continue

        # Update ELO ratings with session date
        elo_system.update_elo(session_results, date)

        # Store current ELO ratings with date
        current_ratings = {player: rating for player, rating in elo_system.elo_ratings.items()}
        current_ratings['Date'] = date
        elo_history.append(current_ratings)

        # Print results
        print(f"\nSession {idx+1} - {date.strftime('%Y-%m-%d')}:")
        print("Session Results:", session_results)
        print("Updated ELO Ratings:")
        rankings = elo_system.get_rankings()
        for rank, (player, rating) in enumerate(rankings, 1):
            print(f"{rank}. {player}: {round(rating, 2)}")

    # Create ELO history dataframe
    elo_history_df = pd.DataFrame(elo_history)
    return elo_history_df, elo_system

def plot_elo_history(elo_history_df, output_path='elo_history.png'):
    """Plot ELO ratings over time."""
    plt.figure(figsize=(12, 8))

    # Get player columns (all columns except 'Date')
    player_columns = [col for col in elo_history_df.columns if col != 'Date']

    # Plot each player's ELO rating
    for player in player_columns:
        plt.plot(elo_history_df['Date'], elo_history_df[player], marker='o', label=player)

    plt.title('Poker ELO Ratings Over Time')
    plt.xlabel('Date')
    plt.ylabel('ELO Rating')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"ELO history plot saved to {output_path}")
    plt.close()

def save_elo_to_json(elo_system, elo_history_df, output_file='elo_ratings.json'):
    """Save ELO ratings to JSON for easy access."""
    # Get current ratings
    current_ratings = {player: rating for player, rating in elo_system.elo_ratings.items()}

    # Get rankings
    rankings = elo_system.get_rankings()
    rankings_list = [{"rank": idx+1, "player": player, "rating": round(rating, 2)}
                     for idx, (player, rating) in enumerate(rankings)]

    # Format history for JSON
    history = []
    for _, row in elo_history_df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        session_ratings = {player: round(row[player], 2) for player in row.index if player != 'Date'}
        history.append({
            "date": date_str,
            "ratings": session_ratings
        })

    # Create JSON structure
    elo_data = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "current_ratings": current_ratings,
        "rankings": rankings_list,
        "history": history
    }

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(elo_data, f, indent=2)

    print(f"ELO ratings saved to {output_file}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Calculate poker ELO ratings from session results')
    parser.add_argument('--input', '-i', type=str, default='Poker Spreadsheet - Sheet1 (2).csv',
                        help='Input CSV file with poker results')
    parser.add_argument('--output-csv', type=str, default='elo_history.csv',
                        help='Output CSV file for ELO history')
    parser.add_argument('--output-json', type=str, default='elo_ratings.json',
                        help='Output JSON file for ELO ratings')
    parser.add_argument('--output-plot', type=str, default='elo_history.png',
                        help='Output PNG file for ELO history plot')
    parser.add_argument('--no-plot', action='store_true',
                        help='Disable plotting ELO history')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()

    # Load poker data
    poker_df = load_poker_data(args.input)

    # Process all sessions
    elo_history_df, final_elo = process_poker_sessions(poker_df)

    # Save ELO history to CSV
    elo_history_df.to_csv(args.output_csv, index=False)
    print(f"ELO history saved to {args.output_csv}")

    # Save ELO ratings to JSON
    save_elo_to_json(final_elo, elo_history_df, args.output_json)

    # Plot ELO history
    if not args.no_plot:
        plot_elo_history(elo_history_df, args.output_plot)

    # Print final rankings
    print("\nFinal Poker ELO Rankings:")
    rankings = final_elo.get_rankings()
    for rank, (player, rating) in enumerate(rankings, 1):
        print(f"{rank}. {player}: {round(rating, 2)}")

if __name__ == "__main__":
    main()