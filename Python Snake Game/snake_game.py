import pygame
import random
import asyncio
import platform

# Constants
INITIAL_TAIL = 4
TILE_COUNT = 20
FPS = 15
GRID_SIZE = 500 // TILE_COUNT  # Canvas is 500x500, so grid_size = 25
BUTTON_SIZE = 60
BUTTON_MARGIN = 10
CANVAS_SIZE = 500
GUI_HEIGHT = BUTTON_SIZE + 2 * BUTTON_MARGIN
WINDOW_WIDTH = CANVAS_SIZE
WINDOW_HEIGHT = CANVAS_SIZE + GUI_HEIGHT

class Snake:
    def __init__(self):
        self.fixed_tail = False
        self.walls = True
        self.tile_count = TILE_COUNT
        self.grid_size = GRID_SIZE
        self.initial_player = (self.tile_count // 2, self.tile_count // 2)
        self.player = [self.initial_player[0], self.initial_player[1]]
        self.velocity = [0, 0]
        self.fruit = [1, 1]
        self.trail = []
        self.tail = INITIAL_TAIL
        self.points = 0
        self.points_max = 0
        self.last_action = 'none'
        self.screen = None
        self.font = None
        self.buttons = []

    def setup(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - ScamShieldTech")
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        
        # Define buttons: (rect, action, chevron_points)
        button_y = CANVAS_SIZE + BUTTON_MARGIN
        self.buttons = [
            # Up button
            {
                'rect': pygame.Rect(WINDOW_WIDTH // 2 - BUTTON_SIZE // 2, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'up',
                'chevron_points': [(30, 15), (15, 30), (45, 30)]  # Up arrow
            },
            # Left button
            {
                'rect': pygame.Rect(WINDOW_WIDTH // 2 - BUTTON_SIZE * 2 - BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'left',
                'chevron_points': [(45, 15), (30, 30), (45, 45)]  # Left arrow
            },
            # Down button
            {
                'rect': pygame.Rect(WINDOW_WIDTH // 2 - BUTTON_SIZE // 2, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'down',
                'chevron_points': [(15, 15), (45, 15), (30, 30)]  # Down arrow
            },
            # Right button
            {
                'rect': pygame.Rect(WINDOW_WIDTH // 2 + BUTTON_SIZE + BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'right',
                'chevron_points': [(15, 15), (30, 30), (15, 45)]  # Right arrow
            },
            # Pause button
            {
                'rect': pygame.Rect(BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'pause',
                'text': "||"
            },
            # Reset button
            {
                'rect': pygame.Rect(WINDOW_WIDTH - BUTTON_SIZE - BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'reset',
                'text': "R"
            },
            # Wall toggle button
            {
                'rect': pygame.Rect(WINDOW_WIDTH - 2 * BUTTON_SIZE - 2 * BUTTON_MARGIN, button_y, BUTTON_SIZE, BUTTON_SIZE),
                'action': 'toggle_wall',
                'text': "W"
            }
        ]
        self.reset()

    def reset(self):
        self.screen.fill((0, 0, 0))
        self.tail = INITIAL_TAIL
        self.points = 0
        self.velocity = [0, 0]
        self.player = [self.initial_player[0], self.initial_player[1]]
        self.last_action = 'none'
        self.trail = [(self.player[0], self.player[1])]
        for i in range(INITIAL_TAIL - 1):
            self.trail.append((self.player[0], self.player[1] + i + 1))
        self.random_fruit()

    def random_fruit(self):
        self.fruit = [
            random.randint(1, self.tile_count - 2),
            random.randint(1, self.tile_count - 2)
        ]
        if (self.fruit[0], self.fruit[1]) in self.trail:
            self.random_fruit()

    def action(self, direction):
        if direction == 'up' and self.last_action != 'down':
            self.velocity = [0, -1]
            self.last_action = 'up'
        elif direction == 'down' and self.last_action != 'up':
            self.velocity = [0, 1]
            self.last_action = 'down'
        elif direction == 'left' and self.last_action != 'right':
            self.velocity = [-1, 0]
            self.last_action = 'left'
        elif direction == 'right' and self.last_action != 'left':
            self.velocity = [1, 0]
            self.last_action = 'right'
        elif direction == 'pause':
            self.velocity = [0, 0]
        elif direction == 'reset':
            self.reset()
        elif direction == 'toggle_wall':
            self.walls = not self.walls

    def clear_top_score(self):
        self.points_max = 0

    def draw_button(self, button):
        # Draw button background
        pygame.draw.rect(self.screen, (68, 68, 68), button['rect'], border_radius=5)
        pygame.draw.rect(self.screen, (102, 102, 102), button['rect'], width=5, border_radius=5)
        
        # Center for chevron or text
        center_x = button['rect'].x + BUTTON_SIZE // 2
        center_y = button['rect'].y + BUTTON_SIZE // 2
        
        if 'chevron_points' in button:
            # Draw chevron (translated to button's position)
            points = [(center_x + x - 30, center_y + y - 30) for x, y in button['chevron_points']]
            pygame.draw.polygon(self.screen, (255, 255, 255), points)
        elif 'text' in button:
            # Draw text
            text = self.font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)

    def loop(self):
        stopped = self.velocity == [0, 0]

        self.player[0] += self.velocity[0]
        self.player[1] += self.velocity[1]

        # Wall collision
        if self.walls and (self.player[0] < 0 or self.player[0] >= self.tile_count or
                           self.player[1] < 0 or self.player[1] >= self.tile_count):
            self.reset()
            return

        # Wrap around if no walls
        if not self.walls:
            if self.player[0] < 0:
                self.player[0] = self.tile_count - 1
            elif self.player[0] >= self.tile_count:
                self.player[0] = 0
            if self.player[1] < 0:
                self.player[1] = self.tile_count - 1
            elif self.player[1] >= self.tile_count:
                self.player[1] = 0

        # Clear canvas
        self.screen.fill((0, 0, 0))

        # Draw walls
        if self.walls:
            pygame.draw.rect(self.screen, (51, 51, 51), (0, 0, CANVAS_SIZE, self.grid_size))
            pygame.draw.rect(self.screen, (51, 51, 51), (0, CANVAS_SIZE - self.grid_size, CANVAS_SIZE, self.grid_size))
            pygame.draw.rect(self.screen, (51, 51, 51), (0, 0, self.grid_size, CANVAS_SIZE))
            pygame.draw.rect(self.screen, (51, 51, 51), (CANVAS_SIZE - self.grid_size, 0, self.grid_size, CANVAS_SIZE))

        # Update snake trail
        if not stopped:
            self.trail.append((self.player[0], self.player[1]))
            while len(self.trail) > self.tail:
                self.trail.pop(0)

        # Check for self-collision
        if not stopped and (self.player[0], self.player[1]) in self.trail[:-1]:
            self.reset()
            return

        # Draw snake
        for x, y in self.trail[:-1]:
            pygame.draw.rect(self.screen, (76, 175, 80),
                             (x * self.grid_size + 2, y * self.grid_size + 2,
                              self.grid_size - 4, self.grid_size - 4))
        x, y = self.trail[-1]
        pygame.draw.rect(self.screen, (139, 195, 74),
                         (x * self.grid_size + 2, y * self.grid_size + 2,
                          self.grid_size - 4, self.grid_size - 4))

        # Check for fruit
        if self.player == self.fruit:
            if not self.fixed_tail:
                self.tail += 1
            self.points += 1
            if self.points > self.points_max:
                self.points_max = self.points
            self.random_fruit()

        # Draw fruit
        pygame.draw.circle(self.screen, (244, 67, 54),
                           ((self.fruit[0] + 0.5) * self.grid_size,
                            (self.fruit[1] + 0.5) * self.grid_size),
                           self.grid_size / 2 - 2)

        # Draw UI
        if not stopped:
            text = self.font.render("(ESC) Reset", True, (255, 255, 255, 128))
            self.screen.blit(text, (10, CANVAS_SIZE - 30))
            text = self.font.render("(SPACE) Pause", True, (255, 255, 255, 128))
            self.screen.blit(text, (10, CANVAS_SIZE - 10))

        if stopped:
            text = self.font.render("PRESS ARROW KEYS OR BUTTONS TO START", True, (255, 255, 255, 204))
            self.screen.blit(text, (20, CANVAS_SIZE - 20))
            if self.points > 0:
                text = self.font.render(f"GAME OVER! SCORE: {self.points}", True, (255, 255, 255, 204))
                self.screen.blit(text, (20, CANVAS_SIZE - 40))

        text = self.font.render(f"SCORE: {self.points}", True, (255, 255, 255))
        self.screen.blit(text, (CANVAS_SIZE - 100, 30))
        text = self.font.render(f"HIGH: {self.points_max}", True, (255, 255, 255))
        self.screen.blit(text, (CANVAS_SIZE - 100, 50))

        # Draw GUI buttons
        for button in self.buttons:
            self.draw_button(button)

        pygame.display.flip()

async def main():
    snake = Snake()
    snake.setup()
    
    # Handle events
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    snake.action('left')
                elif event.key == pygame.K_UP:
                    snake.action('up')
                elif event.key == pygame.K_RIGHT:
                    snake.action('right')
                elif event.key == pygame.K_DOWN:
                    snake.action('down')
                elif event.key == pygame.K_SPACE:
                    snake.action('pause')
                elif event.key == pygame.K_ESCAPE:
                    snake.action('reset')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in snake.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        snake.action(button['action'])

        snake.loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())