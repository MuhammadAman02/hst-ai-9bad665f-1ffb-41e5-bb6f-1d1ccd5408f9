"""Game Configuration Settings"""

from pydantic_settings import BaseSettings
from typing import Optional

class GameSettings(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = False
    game_title: str = "Temple Run Adventure"
    high_score_file: str = "high_scores.json"
    
    # Game mechanics
    game_speed: float = 0.05  # Game loop speed (seconds)
    player_speed: float = 200  # Player movement speed (pixels/second)
    obstacle_speed: float = 300  # Obstacle movement speed
    coin_value: int = 10  # Points per coin
    obstacle_penalty: int = 50  # Points lost when hitting obstacle
    
    class Config:
        env_file = ".env"

settings = GameSettings()