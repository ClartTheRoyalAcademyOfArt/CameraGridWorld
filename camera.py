import random
import pygame
import sys





class Game:

    def __init__(self):
        
        pygame.init()

        # Define all loopmodes and their Boolean
        self.loopmode = {"main_game_loop": False}

        # GAME CONSTS
        self.clock = pygame.time.Clock()
        self.MAX_CAMERA_PAN_SPEED = 1000
        self.DEFAULT_CELL_SIZE = 40
        self.ZOOM_SPEED = 1.1
        self.WINDOW_WIDTH_DEFAULT, self.WINDOW_HEIGHT_DEFAULT = 1280, 720 
        self.SCREEN = pygame.display.set_mode((self.WINDOW_WIDTH_DEFAULT, self.WINDOW_HEIGHT_DEFAULT))

        # GRID INIT VARS
        self.GRID_WIDTH, self.GRID_HEIGHT = 1000, 1000
        self.CELL_SIZE = self.DEFAULT_CELL_SIZE
        self.offset_x, self.offset_y = 0, 0
        self.cell_types =[(108, 223, 92),
                          (255, 250, 137),
                          (108, 111, 108),
                          (75, 236, 255)]
        self.grid = [[random.choice(self.cell_types) for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]

        # Font
        self.FONT = pygame.font.Font(None, 36)



    def main_game_loop(self):

        self.loopmode["main_game_loop"] = True 

        # Main loop for the game
        while self.loopmode["main_game_loop"]:
   
            self.dt = self.clock.tick(60) / 1000.0

            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

            # Mainloop event handler
            for event in pygame.event.get():
            
                if event.type == pygame.QUIT:

                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Zoom in
                        new_size = min(int(self.CELL_SIZE * self.ZOOM_SPEED), 100)
                        scale = new_size / self.CELL_SIZE
                        self.CELL_SIZE = new_size

                        self.offset_x = (self.offset_x - self.mouse_x) * scale + self.mouse_x
                        self.offset_y = (self.offset_y - self.mouse_y) * scale + self.mouse_y

                    elif event.button == 5:  # Zoom out
                        new_size = max(int(self.CELL_SIZE / self.ZOOM_SPEED), 10)
                        scale = new_size / self.CELL_SIZE
                        self.CELL_SIZE = new_size

                        self.offset_x = (self.offset_x - self.mouse_x) * scale + self.mouse_x
                        self.offset_y = (self.offset_y - self.mouse_y) * scale + self.mouse_y

            keys = pygame.key.get_pressed()
            self.offset_x += (keys[pygame.K_a] - keys[pygame.K_d]) * self.MAX_CAMERA_PAN_SPEED * self.dt
            self.offset_y += (keys[pygame.K_w] - keys[pygame.K_s]) * self.MAX_CAMERA_PAN_SPEED * self.dt
            
            self.SCREEN.fill((20,20,20))


            start_col = max(0, int(-self.offset_x // self.CELL_SIZE))
            end_col = min(self.GRID_WIDTH, int((self.WINDOW_WIDTH_DEFAULT - self.offset_x) // self.CELL_SIZE) + 1)

            start_row = max(0, int(-self.offset_y // self.CELL_SIZE))
            end_row = min(self.GRID_HEIGHT, int((self.WINDOW_HEIGHT_DEFAULT - self.offset_y) // self.CELL_SIZE) + 1)

            for row in range(start_row, end_row):
                for col in range(start_col, end_col):
                    # Calculate cell position
                    x = round(col * self.CELL_SIZE + self.offset_x)
                    y = round(row * self.CELL_SIZE + self.offset_y)
                    
                    # Slightly enlarge the cell to overlap edges
                    pygame.draw.rect(self.SCREEN, self.grid[row][col], (x, y, round(self.CELL_SIZE) + 1, round(self.CELL_SIZE) + 1))

            # End of loop
            self.fps = int(self.clock.get_fps())
            self.fps_text = self.FONT.render(f"{self.fps}", True, (0, 0, 0))
            self.SCREEN.blit(self.fps_text, (10, 10))
            pygame.display.update()
    


    def quit_game(self):

        pygame.quit()
        sys.exit()



    def game_begin(self):

        self.loopmode = {key: False for key in self.loopmode}
        self.main_game_loop()





if __name__ == "__main__":
    game = Game()
    game.game_begin()