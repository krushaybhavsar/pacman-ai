import pygame
import sys
import copy
from settings import *
from player_class import *
from enemy_class import *

pygame.init()
vec = pygame.math.Vector2

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH // COLS
        self.cell_height = MAZE_HEIGHT // ROWS
        self.walls = []
        self.coins = []
        self.enemies = []
        self.e_pos = []
        self.p_pos = None
        self.load()
        self.player = Player(self, vec(self.p_pos))
        self.make_enemies()
    
    def run(self):
        while self.running:
            if self.state == 'start':
                self.start__events()
                self.start__update()
                self.start__draw()
            elif self.state == 'playing':
                self.playing__events()
                self.playing__update()
                self.playing__draw()
            elif self.state == 'game over':
                self.game_over__events()
                self.game_over__update()
                self.game_over__draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
    
    ############# HELPER FUNCTIONS ############
    def draw_text(self, words, screen, pos, size, color, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, color)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0] - text_size[0] // 2
            pos[1] = pos[1] - text_size[1] // 2
        screen.blit(text, pos)

    def load(self):
        self.background = pygame.image.load('maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))
        
        # Opening walls file and creating walls list with co-ords of walls
        with open('walls.txt', 'r') as file:
            for yindx, line in enumerate(file):
                for xindx, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(xindx, yindx))
                    elif char == "C":
                        self.coins.append(vec(xindx, yindx))
                    elif char == "P":
                        self.p_pos = [xindx, yindx]
                    elif char in ["2", "3", "4", "5"]:
                        self.e_pos.append([xindx, yindx])
                    elif char == "B":
                        pygame.draw.rect(self.background, BLACK, (xindx*self.cell_width, yindx*self.cell_height, self.cell_width, self.cell_height))

    def make_enemies(self):
        for idx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def draw_grid(self):
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.background, GREY, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.background, GREY, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))
        # for coin in self.coins:
            # pygame.draw.rect(self.background, (167, 179, 34), (coin.x*self.cell_width, coin.y*self.cell_height, self.cell_width, self.cell_height))
    
    def reset(self):
        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0
        self.coins = []
        with open('walls.txt', 'r') as file:
            for yindx, line in enumerate(file):
                for xindx, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(xindx, yindx))
        self.state = "playing"
            
    ############# INTRO FUNCTIONS #############

    def start__events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'playing'

    def start__update(self):
        pass

    def start__draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACEBAR', self.screen, [WIDTH//2, HEIGHT//2 - 25], START_TEXT_SIZE, WHITE, START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [WIDTH//2, HEIGHT//2 + 25], START_TEXT_SIZE, WHITE, START_FONT, centered=True)
        self.draw_text('HIGH SCORE', self.screen, [40, 1], 15, WHITE, START_FONT)
        pygame.display.update()

    ############# PLAYING FUNCTIONS #############

    def playing__events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1,0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1,0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0,-1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0,1))

    def playing__update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update()
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                self.remove_life()

    def playing__draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (TOP_BOTTOM_BUFFER//2, TOP_BOTTOM_BUFFER//2))
        self.draw_coins()
        # self.draw_grid()
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score), self.screen, [40, 1], 15, WHITE, START_FONT)
        self.draw_text('HIGH SCORE: 0', self.screen, [WIDTH//2 + 50, 1], 15, WHITE, START_FONT)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    def remove_life(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0
    
    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (255, 255, 255), (int(coin.x * self.cell_width) + self.cell_width // 2 + TOP_BOTTOM_BUFFER // 2, int(coin.y * self.cell_height) + self.cell_height // 2 + TOP_BOTTOM_BUFFER // 2), 2)
    
    ############ GAME OVER FUNCTIONS ############

    def game_over__events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over__update(self):
        pass

    def game_over__draw(self):
        self.screen.fill(BLACK)
        quit_text = "Press escape to quit"
        again_text = "Press the space bar to play again"
        self.draw_text("GAME OVER", self.screen, [WIDTH//2, HEIGHT//2 - 75], 60, RED, "arial", centered=True)
        self.draw_text(again_text, self.screen, [WIDTH//2, HEIGHT//2 + 60], 30, WHITE, "arial", centered=True)
        self.draw_text(quit_text, self.screen, [WIDTH//2, HEIGHT//2 + 100], 30, WHITE, "arial", centered=True)
        pygame.display.update()
