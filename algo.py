import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize player ELO ratings
INITIAL_ELO = 1500
K_BASE = 30  # Base K-factor

class PokerELO:
    def __init__(self, players):
        self.elo_ratings = {player: INITIAL_ELO for player in players}
        self.last_played = {player: None for player in players}  # Track last play date for each player

    def expected_score(self, Ra, Rb):
        """Calculate expected probability of winning."""
        return 1 / (1 + 10 ** ((Rb - Ra) / 400))

    def update_elo(self, session_results, session_date=None):
        """
        Update ELO based on a session result.
        session_results: dict of {player_name: net_profit}
        session_date: datetime object for the session date
        """
        if session_date is None:
            session_date = datetime.now()

        players = list(session_results.keys())
        profits = np.array(list(session_results.values()))

        avg_profit = np.mean(np.abs(profits)) + 1e-6  # Avoid division by zero

        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                A, B = players[i], players[j]
                Pa, Pb = session_results[A], session_results[B]

                # Determine actual scores
                Sa, Sb = (1, 0) if Pa > Pb else (0, 1) if Pa < Pb else (0.5, 0.5)

                # Expected scores
                Ea = self.expected_score(self.elo_ratings[A], self.elo_ratings[B])
                Eb = 1 - Ea  # Since Ea + Eb = 1

                # Dynamic K-factor based on profit difference
                K = K_BASE * (1 + abs(Pa - Pb) / avg_profit)

                # Update ratings
                self.elo_ratings[A] += K * (Sa - Ea)
                self.elo_ratings[B] += K * (Sb - Eb)

        # Update last played dates for all players in the session
        for player in players:
            self.last_played[player] = session_date

    def get_rankings(self):
        """Return rankings sorted by ELO."""
        return sorted(self.elo_ratings.items(), key=lambda x: x[1], reverse=True)

# Example Usage:
if __name__ == "__main__":
    players = ["A", "B", "C", "D"]
    elo_system = PokerELO(players)

    # Session 1
    session_1 = {"A": 10, "B": 5, "C": -15}
    elo_system.update_elo(session_1, datetime.now() - timedelta(days=60))

    # Session 2 (30 days later)
    session_2 = {"A": -30, "B": 20, "D": 10}
    elo_system.update_elo(session_2, datetime.now() - timedelta(days=30))

    # Get rankings
    rankings = elo_system.get_rankings()
    print("Poker ELO Rankings:")
    for rank, (player, rating) in enumerate(rankings, 1):
        print(f"{rank}. {player}: {round(rating, 2)}")
