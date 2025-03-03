import os

class ScraperConfig:
    # Odds update settings
    ODDS_PUBLISH_INTERVAL = float(os.getenv("ODDS_PUBLISH_INTERVAL", 5.0))
    ODDS_UPDATE_PROBABILITY = float(os.getenv("ODDS_UPDATE_PROBABILITY", 0.2))  # 20% chance of updating
    ODDS_CLOSE_PROBABILITY = float(os.getenv("ODDS_CLOSE_PROBABILITY", 0.2))  # 20% chance of closing

    # Vig (Bookmaker's margin)
    VIG_PERCENTAGE = float(os.getenv("VIG_PERCENTAGE", 0.05))  # 5% vig

    # Odds range
    HOME_WIN_ODDS_MIN = float(os.getenv("HOME_WIN_ODDS_MIN", 1.6))
    HOME_WIN_ODDS_MAX = float(os.getenv("HOME_WIN_ODDS_MAX", 3.2))

    MATCHES = ["Man Utd vs Chelsea", "Liverpool vs Arsenal", "Barcelona vs Real Madrid"]
    BOOKMAKERS = ["Bet365", "Smarkets", "Betfair"]

scraper_config = ScraperConfig()
