import pygame
from pygame import *
from noise import pnoise2
import random
import sys


class Game:

    def __init__(self):

        # Startup Vars
        pygame.init()

        self.game_main_loop = True

        # Game Constants
        self.clock = pygame.time.Clock()

        self.FPS_MODES = {"60": 60, "144": 144, "240": 240}
        self.FPS = self.FPS_MODES["60"]

        self.DEFAULT_CELL_SIZE = 10
        self.CELL_SIZE = self.DEFAULT_CELL_SIZE

        # Camera
        self.offset_x, self.offset_y = 0, 0
        self.MAX_CAMERA_PAN_SPEED = 500
        self.ZOOM_SPEED = 1.1

        # Screen Initialize
        self.DEFAULT_SCREEN_WIDTH, self.DEFAULT_SCREEN_HEIGHT = 1280, 720
        self.screen_width, self.screen_height = self.DEFAULT_SCREEN_WIDTH, self.DEFAULT_SCREEN_HEIGHT
        self.SCREEN = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.is_fullscreen = False

        pygame.display.set_caption("Camera Game with Regional Bias")

        # Grid Initialize
        self.GRID_WIDTH, self.GRID_HEIGHT = 500, 500

        self.cell_types = [
            (41, 208, 253),    # Water
            (251, 248, 145),  # Sand
            (99, 225, 88),    # Grass
            (55, 178, 45),      # Forest
            (112, 112, 112)   # Mountain
        ]

        # Perlin Noise Params
        self.SCALE = 50.0
        self.OCTAVES = 6
        self.PERSISTENCE = 0.4
        self.LACUNARITY = 2.0
        self.seed = random.randint(0, 100000)
        self.region_seed = random.randint(0, 100000)  # Separate seed for regional bias

        # Font/Text Setup (for FPS display)
        self.FONT = pygame.font.Font(None, 36)

        # Create world
        self.generate_world()

    def generate_world(self):

        """Generate the world with regional bias applied."""
        self.world_map = [[(0, 0, 0) for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]

        for y in range(self.GRID_HEIGHT):

            for x in range(self.GRID_WIDTH):

                nx = (x + self.seed) / self.SCALE
                ny = (y + self.seed) / self.SCALE

                # Generate primary noise
                noise_val = pnoise2(
                    nx, ny, octaves=self.OCTAVES, persistence=self.PERSISTENCE,
                    lacunarity=self.LACUNARITY, repeatx=1024, repeaty=1024, base=0
                )

                # Generate regional bias
                region_bias = pnoise2(
                    (x + self.region_seed) / (self.SCALE * 5),
                    (y + self.region_seed) / (self.SCALE * 5),
                    octaves=2, persistence=0.7, lacunarity=2.0,
                    repeatx=1024, repeaty=1024, base=1
                )

                # Combine primary noise with regional bias
                combined_noise = noise_val + 0.3 * region_bias

                # Assign colors based on combined noise with adjusted thresholds
                if combined_noise < -0.3:
                    color = self.cell_types[0]  # Water

                elif -0.3 <= combined_noise < -0.15:
                    color = self.cell_types[1]  # Sand

                elif -0.15 <= combined_noise < 0.2:
                    color = self.cell_types[2]  # Grass

                elif 0.2 <= combined_noise < 0.4:
                    color = self.cell_types[3]  # Forest

                else:
                    color = self.cell_types[4]  # Mountain

                self.world_map[y][x] = color

    def handle_event(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:

                if event.key == K_F11:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.SCREEN = pygame.display.set_mode((0, 0), FULLSCREEN)
                        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
                    else:
                        self.SCREEN = pygame.display.set_mode((self.DEFAULT_SCREEN_WIDTH, self.DEFAULT_SCREEN_HEIGHT))
                        self.screen_width, self.screen_height = self.DEFAULT_SCREEN_WIDTH, self.DEFAULT_SCREEN_HEIGHT

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 4:

                    new_size = min(self.CELL_SIZE * self.ZOOM_SPEED, 100)
                    scale = new_size / self.CELL_SIZE
                    self.CELL_SIZE = new_size

                    self.offset_x = (self.offset_x - pygame.mouse.get_pos()[0]) * scale + pygame.mouse.get_pos()[0]
                    self.offset_y = (self.offset_y - pygame.mouse.get_pos()[1]) * scale + pygame.mouse.get_pos()[1]

                elif event.button == 5:

                    new_size = max(self.CELL_SIZE / self.ZOOM_SPEED, 10)
                    scale = new_size / self.CELL_SIZE
                    self.CELL_SIZE = new_size

                    self.offset_x = (self.offset_x - pygame.mouse.get_pos()[0]) * scale + pygame.mouse.get_pos()[0]
                    self.offset_y = (self.offset_y - pygame.mouse.get_pos()[1]) * scale + pygame.mouse.get_pos()[1]

        keys = pygame.key.get_pressed()
        movement_speed = self.MAX_CAMERA_PAN_SPEED * (self.dt / 1000.0)

        # Update offset using normalized movement
        self.offset_x += (keys[K_a] - keys[K_d]) * movement_speed
        self.offset_y += (keys[K_w] - keys[K_s]) * movement_speed

    def render_world(self):

        start_col = max(0, int(-self.offset_x // self.CELL_SIZE) - 1)
        end_col = min(self.GRID_WIDTH, int((self.screen_width - self.offset_x) // self.CELL_SIZE) + 2)

        start_row = max(0, int(-self.offset_y // self.CELL_SIZE) - 1)
        end_row = min(self.GRID_HEIGHT, int((self.screen_height - self.offset_y) // self.CELL_SIZE) + 2)

        for y in range(start_row, end_row):

            for x in range(start_col, end_col):

                color = self.world_map[y][x]

                x_pos = int(x * self.CELL_SIZE + self.offset_x)
                y_pos = int(y * self.CELL_SIZE + self.offset_y)
                size = int(self.CELL_SIZE)

                # Ensure slight overlap to prevent gaps
                rect = pygame.Rect(x_pos, y_pos, size + 1, size + 1)

                pygame.draw.rect(self.SCREEN, color, rect)

    def render_gui(self):

        fps = int(self.clock.get_fps())
        fps_text = self.FONT.render(f"{fps}", True, (0, 0, 0))
        self.SCREEN.blit(fps_text, (10, 10))

    def main_loop(self):

        while self.game_main_loop:

            self.dt = self.clock.tick(self.FPS)
            self.SCREEN.fill((20, 20, 20))

            self.handle_event()
            self.render_world()
            self.render_gui()

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
