"""Temple Run Game - Main Application"""

from nicegui import ui, app
import asyncio
import time
from core.game_engine import GameEngine
from app.components.game_ui import GameRenderer, GameControls
from app.config import settings

# Global game instance
game_engine = GameEngine()
game_renderer = GameRenderer(game_engine)
game_controls = GameControls(game_engine)

# Game loop control
game_loop_task = None
last_update_time = time.time()

async def game_loop():
    """Main game loop"""
    global last_update_time
    
    while True:
        current_time = time.time()
        delta_time = current_time - last_update_time
        last_update_time = current_time
        
        # Update game state
        game_engine.update_game(delta_time)
        
        # Update display
        game_objects = game_engine.get_game_objects()
        game_renderer.update_display(game_objects)
        
        # Sleep for smooth 60 FPS
        await asyncio.sleep(1/60)

def start_game_loop():
    """Start the game loop"""
    global game_loop_task
    if game_loop_task is None or game_loop_task.done():
        game_loop_task = asyncio.create_task(game_loop())

def restart_game():
    """Restart the game"""
    game_engine.reset_game()
    start_game_loop()

# JavaScript functions for game control
ui.add_head_html("""
<script>
// Global restart function
window.restartGame = function() {
    fetch('/restart', {method: 'POST'});
};

// Keyboard controls
document.addEventListener('keydown', function(event) {
    switch(event.key) {
        case 'ArrowLeft':
        case 'a':
        case 'A':
            fetch('/move/left', {method: 'POST'});
            event.preventDefault();
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            fetch('/move/right', {method: 'POST'});
            event.preventDefault();
            break;
        case 'ArrowUp':
        case 'w':
        case 'W':
            fetch('/move/up', {method: 'POST'});
            event.preventDefault();
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            fetch('/move/down', {method: 'POST'});
            event.preventDefault();
            break;
        case ' ':
            fetch('/pause', {method: 'POST'});
            event.preventDefault();
            break;
        case 'r':
        case 'R':
            fetch('/restart', {method: 'POST'});
            event.preventDefault();
            break;
    }
});
</script>
""")

@ui.page('/')
async def index():
    """Main game page"""
    ui.add_head_html('<title>Temple Run Adventure - Endless Runner Game</title>')
    
    # Header
    with ui.column().classes('w-full items-center'):
        ui.html('<h1 style="color: #8B4513; font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin: 20px 0;">🏃‍♂️ Temple Run Adventure</h1>')
        
        # Game display
        game_renderer.create_game_display()
        
        # Controls
        game_controls.create_controls()
        
        # Game stats
        with ui.row().classes('w-full justify-center gap-8 mt-6'):
            with ui.card().classes('p-4'):
                ui.label('🏆 High Score').classes('text-lg font-bold')
                ui.label(f'{game_engine.state.high_score}').classes('text-2xl text-blue-600')
            
            with ui.card().classes('p-4'):
                ui.label('🎮 How to Play').classes('text-lg font-bold')
                ui.label('Avoid obstacles, collect coins!').classes('text-sm')
    
    # Start the game loop
    start_game_loop()

# API endpoints for game controls
@app.post('/move/{direction}')
async def move_player(direction: str):
    """Handle player movement"""
    game_engine.move_player(direction)
    return {'status': 'ok'}

@app.post('/pause')
async def pause_game():
    """Handle game pause"""
    game_engine.pause_game()
    return {'status': 'ok'}

@app.post('/restart')
async def restart_game_endpoint():
    """Handle game restart"""
    restart_game()
    return {'status': 'ok'}

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'game': 'running'}

def main():
    """Run the game application"""
    ui.run(
        host=settings.host,
        port=settings.port,
        title=settings.game_title,
        favicon='🏃‍♂️',
        show=False,
        reload=settings.debug
    )

if __name__ == "__main__":
    main()