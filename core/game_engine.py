"""Temple Run Game Engine - Core game logic and state management"""

import json
import random
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Position:
    x: float
    y: float

@dataclass
class GameObject:
    position: Position
    width: float
    height: float
    active: bool = True

@dataclass
class Player(GameObject):
    lane: int = 1  # 0=left, 1=center, 2=right
    jumping: bool = False
    sliding: bool = False
    jump_height: float = 0

@dataclass
class Obstacle(GameObject):
    obstacle_type: str  # 'tree', 'rock', 'pit'
    lane: int

@dataclass
class Coin(GameObject):
    collected: bool = False

@dataclass
class GameState:
    score: int = 0
    distance: int = 0
    coins_collected: int = 0
    lives: int = 3
    speed_multiplier: float = 1.0
    game_over: bool = False
    paused: bool = False
    high_score: int = 0

class GameEngine:
    def __init__(self):
        self.reset_game()
        self.load_high_score()
        
        # Game constants
        self.LANE_POSITIONS = [150, 300, 450]  # X positions for lanes
        self.LANE_WIDTH = 100
        self.PLAYER_HEIGHT = 60
        self.PLAYER_WIDTH = 40
        self.OBSTACLE_HEIGHT = 60
        self.OBSTACLE_WIDTH = 50
        self.COIN_SIZE = 20
        self.JUMP_HEIGHT = 80
        self.SLIDE_DURATION = 1.0  # seconds
        
        # Spawn rates
        self.OBSTACLE_SPAWN_RATE = 0.02  # Probability per frame
        self.COIN_SPAWN_RATE = 0.03
        
    def reset_game(self):
        """Reset game to initial state"""
        self.state = GameState()
        self.player = Player(
            position=Position(300, 400),  # Center lane, bottom of screen
            width=self.PLAYER_WIDTH,
            height=self.PLAYER_HEIGHT,
            lane=1
        )
        self.obstacles: List[Obstacle] = []
        self.coins: List[Coin] = []
        self.last_update = time.time()
        self.slide_timer = 0
        self.jump_timer = 0
        
    def load_high_score(self):
        """Load high score from file"""
        try:
            score_file = Path("high_scores.json")
            if score_file.exists():
                with open(score_file, 'r') as f:
                    data = json.load(f)
                    self.state.high_score = data.get('high_score', 0)
        except Exception:
            self.state.high_score = 0
            
    def save_high_score(self):
        """Save high score to file"""
        try:
            if self.state.score > self.state.high_score:
                self.state.high_score = self.state.score
                with open("high_scores.json", 'w') as f:
                    json.dump({'high_score': self.state.high_score}, f)
        except Exception:
            pass
    
    def move_player(self, direction: str):
        """Move player between lanes or perform actions"""
        if self.state.game_over or self.state.paused:
            return
            
        if direction == "left" and self.player.lane > 0:
            self.player.lane -= 1
            self.player.position.x = self.LANE_POSITIONS[self.player.lane]
        elif direction == "right" and self.player.lane < 2:
            self.player.lane += 1
            self.player.position.x = self.LANE_POSITIONS[self.player.lane]
        elif direction == "up" and not self.player.jumping:
            self.player.jumping = True
            self.jump_timer = 0
        elif direction == "down" and not self.player.sliding:
            self.player.sliding = True
            self.slide_timer = 0
    
    def update_game(self, delta_time: float):
        """Update game state"""
        if self.state.game_over or self.state.paused:
            return
            
        # Update distance and score
        self.state.distance += int(100 * delta_time * self.state.speed_multiplier)
        self.state.score += int(10 * delta_time * self.state.speed_multiplier)
        
        # Increase speed over time
        self.state.speed_multiplier = min(3.0, 1.0 + self.state.distance / 10000)
        
        # Update player actions
        self._update_player_actions(delta_time)
        
        # Spawn new objects
        self._spawn_obstacles()
        self._spawn_coins()
        
        # Update object positions
        self._update_obstacles(delta_time)
        self._update_coins(delta_time)
        
        # Check collisions
        self._check_collisions()
        
        # Clean up off-screen objects
        self._cleanup_objects()
    
    def _update_player_actions(self, delta_time: float):
        """Update player jumping and sliding"""
        if self.player.jumping:
            self.jump_timer += delta_time
            if self.jump_timer < 0.5:  # Jump up
                self.player.jump_height = self.JUMP_HEIGHT * (self.jump_timer / 0.5)
            elif self.jump_timer < 1.0:  # Jump down
                self.player.jump_height = self.JUMP_HEIGHT * (1 - (self.jump_timer - 0.5) / 0.5)
            else:  # Landing
                self.player.jumping = False
                self.player.jump_height = 0
                self.jump_timer = 0
        
        if self.player.sliding:
            self.slide_timer += delta_time
            if self.slide_timer >= self.SLIDE_DURATION:
                self.player.sliding = False
                self.slide_timer = 0
    
    def _spawn_obstacles(self):
        """Spawn new obstacles"""
        if random.random() < self.OBSTACLE_SPAWN_RATE * self.state.speed_multiplier:
            lane = random.randint(0, 2)
            obstacle_type = random.choice(['tree', 'rock', 'pit'])
            
            obstacle = Obstacle(
                position=Position(self.LANE_POSITIONS[lane], -50),
                width=self.OBSTACLE_WIDTH,
                height=self.OBSTACLE_HEIGHT,
                obstacle_type=obstacle_type,
                lane=lane
            )
            self.obstacles.append(obstacle)
    
    def _spawn_coins(self):
        """Spawn new coins"""
        if random.random() < self.COIN_SPAWN_RATE:
            lane = random.randint(0, 2)
            coin = Coin(
                position=Position(self.LANE_POSITIONS[lane], -30),
                width=self.COIN_SIZE,
                height=self.COIN_SIZE
            )
            self.coins.append(coin)
    
    def _update_obstacles(self, delta_time: float):
        """Update obstacle positions"""
        speed = 300 * self.state.speed_multiplier
        for obstacle in self.obstacles:
            obstacle.position.y += speed * delta_time
    
    def _update_coins(self, delta_time: float):
        """Update coin positions"""
        speed = 300 * self.state.speed_multiplier
        for coin in self.coins:
            coin.position.y += speed * delta_time
    
    def _check_collisions(self):
        """Check for collisions between player and objects"""
        player_rect = self._get_player_rect()
        
        # Check obstacle collisions
        for obstacle in self.obstacles:
            if not obstacle.active:
                continue
                
            obstacle_rect = (
                obstacle.position.x - obstacle.width // 2,
                obstacle.position.y - obstacle.height // 2,
                obstacle.width,
                obstacle.height
            )
            
            if self._rects_collide(player_rect, obstacle_rect):
                if obstacle.obstacle_type == 'pit' and not self.player.jumping:
                    self._handle_collision()
                elif obstacle.obstacle_type in ['tree', 'rock'] and not self.player.sliding:
                    self._handle_collision()
                obstacle.active = False
        
        # Check coin collisions
        for coin in self.coins:
            if coin.collected:
                continue
                
            coin_rect = (
                coin.position.x - coin.width // 2,
                coin.position.y - coin.height // 2,
                coin.width,
                coin.height
            )
            
            if self._rects_collide(player_rect, coin_rect):
                coin.collected = True
                self.state.coins_collected += 1
                self.state.score += 50  # Bonus points for coins
    
    def _get_player_rect(self):
        """Get player collision rectangle"""
        y_offset = self.player.jump_height if self.player.jumping else 0
        height = self.PLAYER_HEIGHT // 2 if self.player.sliding else self.PLAYER_HEIGHT
        
        return (
            self.player.position.x - self.PLAYER_WIDTH // 2,
            self.player.position.y - height - y_offset,
            self.PLAYER_WIDTH,
            height
        )
    
    def _rects_collide(self, rect1: Tuple[float, float, float, float], 
                      rect2: Tuple[float, float, float, float]) -> bool:
        """Check if two rectangles collide"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        return (x1 < x2 + w2 and x1 + w1 > x2 and 
                y1 < y2 + h2 and y1 + h1 > y2)
    
    def _handle_collision(self):
        """Handle collision with obstacle"""
        self.state.lives -= 1
        if self.state.lives <= 0:
            self.state.game_over = True
            self.save_high_score()
    
    def _cleanup_objects(self):
        """Remove off-screen objects"""
        self.obstacles = [obs for obs in self.obstacles if obs.position.y < 600]
        self.coins = [coin for coin in self.coins if coin.position.y < 600]
    
    def pause_game(self):
        """Toggle game pause"""
        self.state.paused = not self.state.paused
    
    def get_game_objects(self) -> Dict:
        """Get all game objects for rendering"""
        return {
            'player': self.player,
            'obstacles': [obs for obs in self.obstacles if obs.active],
            'coins': [coin for coin in self.coins if not coin.collected],
            'state': self.state
        }