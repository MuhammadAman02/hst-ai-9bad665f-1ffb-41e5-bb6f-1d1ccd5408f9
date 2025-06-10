"""Game UI Components for Temple Run"""

from nicegui import ui
from typing import Dict, Any
from core.game_engine import GameEngine, GameObject

class GameRenderer:
    def __init__(self, game_engine: GameEngine):
        self.engine = game_engine
        self.game_container = None
        self.setup_styles()
    
    def setup_styles(self):
        """Setup CSS styles for the game"""
        ui.add_head_html("""
        <style>
        .game-container {
            position: relative;
            width: 600px;
            height: 500px;
            background: linear-gradient(180deg, #87CEEB 0%, #98FB98 50%, #8B4513 100%);
            border: 3px solid #8B4513;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 auto;
        }
        
        .game-road {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 200px;
            background: linear-gradient(90deg, #696969 0%, #A9A9A9 50%, #696969 100%);
            border-top: 3px solid #FFD700;
        }
        
        .lane-divider {
            position: absolute;
            width: 4px;
            height: 100%;
            background: repeating-linear-gradient(
                to bottom,
                #FFFF00 0px,
                #FFFF00 20px,
                transparent 20px,
                transparent 40px
            );
            animation: roadMove 0.5s linear infinite;
        }
        
        .lane-divider.left {
            left: 200px;
        }
        
        .lane-divider.right {
            right: 200px;
        }
        
        @keyframes roadMove {
            0% { background-position: 0 0; }
            100% { background-position: 0 40px; }
        }
        
        .player {
            position: absolute;
            width: 40px;
            height: 60px;
            background: #FF6B6B;
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
            border: 2px solid #FF4757;
            transition: left 0.2s ease-in-out;
            z-index: 10;
        }
        
        .player.jumping {
            animation: jump 1s ease-in-out;
        }
        
        .player.sliding {
            height: 30px;
            border-radius: 50%;
        }
        
        @keyframes jump {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-80px); }
        }
        
        .obstacle {
            position: absolute;
            border-radius: 5px;
            z-index: 5;
        }
        
        .obstacle.tree {
            background: #228B22;
            border: 2px solid #006400;
        }
        
        .obstacle.rock {
            background: #696969;
            border: 2px solid #2F4F4F;
        }
        
        .obstacle.pit {
            background: #8B4513;
            border: 2px solid #654321;
        }
        
        .coin {
            position: absolute;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, #FFD700 0%, #FFA500 100%);
            border: 2px solid #FF8C00;
            border-radius: 50%;
            z-index: 8;
            animation: coinSpin 1s linear infinite;
        }
        
        @keyframes coinSpin {
            0% { transform: rotateY(0deg); }
            100% { transform: rotateY(360deg); }
        }
        
        .game-hud {
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            display: flex;
            justify-content: space-between;
            color: white;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
            z-index: 15;
        }
        
        .game-over-screen {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 20;
        }
        
        .pause-screen {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 20;
        }
        
        .controls-info {
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        
        .heart {
            color: #FF0000;
            font-size: 18px;
        }
        </style>
        """)
    
    def create_game_display(self) -> ui.html:
        """Create the main game display"""
        self.game_container = ui.html("""
        <div class="game-container" id="gameContainer">
            <div class="game-road">
                <div class="lane-divider left"></div>
                <div class="lane-divider right"></div>
            </div>
            <div class="game-hud">
                <div>Score: <span id="score">0</span></div>
                <div>Distance: <span id="distance">0</span>m</div>
                <div>Coins: <span id="coins">0</span></div>
                <div>Lives: <span id="lives">♥♥♥</span></div>
                <div>High Score: <span id="highScore">0</span></div>
            </div>
        </div>
        """)
        return self.game_container
    
    def update_display(self, game_objects: Dict[str, Any]):
        """Update the game display with current game state"""
        if not self.game_container:
            return
            
        player = game_objects['player']
        obstacles = game_objects['obstacles']
        coins = game_objects['coins']
        state = game_objects['state']
        
        # Update HUD
        ui.run_javascript(f"""
        document.getElementById('score').textContent = '{state.score}';
        document.getElementById('distance').textContent = '{state.distance}';
        document.getElementById('coins').textContent = '{state.coins_collected}';
        document.getElementById('lives').textContent = '{"♥" * state.lives}';
        document.getElementById('highScore').textContent = '{state.high_score}';
        """)
        
        # Clear previous game objects
        ui.run_javascript("""
        const container = document.getElementById('gameContainer');
        const existingObjects = container.querySelectorAll('.player, .obstacle, .coin');
        existingObjects.forEach(obj => obj.remove());
        """)
        
        # Add player
        player_class = "player"
        if player.jumping:
            player_class += " jumping"
        if player.sliding:
            player_class += " sliding"
            
        ui.run_javascript(f"""
        const container = document.getElementById('gameContainer');
        const player = document.createElement('div');
        player.className = '{player_class}';
        player.style.left = '{player.position.x - player.width//2}px';
        player.style.bottom = '{500 - player.position.y - player.height}px';
        container.appendChild(player);
        """)
        
        # Add obstacles
        for obstacle in obstacles:
            ui.run_javascript(f"""
            const obstacle = document.createElement('div');
            obstacle.className = 'obstacle {obstacle.obstacle_type}';
            obstacle.style.left = '{obstacle.position.x - obstacle.width//2}px';
            obstacle.style.top = '{obstacle.position.y}px';
            obstacle.style.width = '{obstacle.width}px';
            obstacle.style.height = '{obstacle.height}px';
            container.appendChild(obstacle);
            """)
        
        # Add coins
        for coin in coins:
            ui.run_javascript(f"""
            const coin = document.createElement('div');
            coin.className = 'coin';
            coin.style.left = '{coin.position.x - coin.width//2}px';
            coin.style.top = '{coin.position.y}px';
            container.appendChild(coin);
            """)
        
        # Show game over screen
        if state.game_over:
            ui.run_javascript(f"""
            const gameOverScreen = document.createElement('div');
            gameOverScreen.className = 'game-over-screen';
            gameOverScreen.innerHTML = `
                <h2>Game Over!</h2>
                <p>Final Score: {state.score}</p>
                <p>Distance: {state.distance}m</p>
                <p>Coins Collected: {state.coins_collected}</p>
                <p>High Score: {state.high_score}</p>
                <button onclick="window.restartGame()" style="margin-top: 20px; padding: 10px 20px; font-size: 16px; background: #FF6B6B; color: white; border: none; border-radius: 5px; cursor: pointer;">Play Again</button>
            `;
            container.appendChild(gameOverScreen);
            """)
        
        # Show pause screen
        elif state.paused:
            ui.run_javascript("""
            const pauseScreen = document.createElement('div');
            pauseScreen.className = 'pause-screen';
            pauseScreen.innerHTML = `
                <h2>Game Paused</h2>
                <p>Press SPACE to resume</p>
            `;
            container.appendChild(pauseScreen);
            """)

class GameControls:
    def __init__(self, game_engine: GameEngine):
        self.engine = game_engine
    
    def create_controls(self):
        """Create game control buttons and instructions"""
        with ui.row().classes('w-full justify-center gap-4 mt-4'):
            ui.button('⬅️ Left', on_click=lambda: self.engine.move_player('left')).classes('bg-blue-500')
            ui.button('⬆️ Jump', on_click=lambda: self.engine.move_player('up')).classes('bg-green-500')
            ui.button('⬇️ Slide', on_click=lambda: self.engine.move_player('down')).classes('bg-yellow-500')
            ui.button('➡️ Right', on_click=lambda: self.engine.move_player('right')).classes('bg-blue-500')
            ui.button('⏸️ Pause', on_click=self.engine.pause_game).classes('bg-gray-500')
        
        with ui.column().classes('w-full text-center mt-4'):
            ui.markdown("""
            ### 🎮 Controls
            - **Arrow Keys**: Move left/right, jump, slide
            - **WASD Keys**: Alternative controls
            - **Space**: Pause/Resume
            - **R**: Restart game
            
            ### 🎯 Objective
            - Avoid obstacles by jumping or sliding
            - Collect golden coins for bonus points
            - Survive as long as possible!
            - Beat your high score!
            """).classes('text-sm text-gray-600')