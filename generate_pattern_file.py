########################
# generate_pattern_file
# author: NUAA-XSF
########################

import sys

import pygame
import numpy as np

from configuration import *


class Generator:
    def __init__(self, save_path, pattern_name, font_file):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.running = True
        self.map = np.zeros((MAP_HEIGHT,MAP_WIDTH)).astype(np.int8)
        self.grid = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
        self.grid.set_colorkey(BLACK)
        self.font_file = font_file
        self.draw_grid(self.grid, GRAY1)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    def run(self):
        map_rgb = np.zeros((MAP_HEIGHT, MAP_WIDTH, 3), dtype = np.int)
        while self.running:
            self.clock.tick(FPS)
            self.event()
            map_rgb[self.map == 1] = list(RED)
            map_rgb[self.map == 0] = list(GRAY)
            map_resize = np.repeat(map_rgb, BLOCK_HEIGHT, axis=0)
            map_resize = np.repeat(map_resize, BLOCK_WIDTH, axis=1)
            map_resize = np.flip(np.rot90(map_resize), 0)
            map_resize_surf = pygame.surfarray.make_surface(map_resize).convert()
            map_resize_surf.blit(self.grid, (0, 0))
            self.screen.fill(BLACK)
            self.screen.blit(map_resize_surf, (0,0))
            self.draw_text(self.screen, self.font_file, 'Generator', 20, BLACK, 20, 10)
            pygame.display.flip()
        self.quit()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = 0
                if event.key == pygame.K_s:
                    self.save_pattern()
        # if any(pygame.mouse.get_pressed()):
        x, y= pygame.mouse.get_pos()
        index_x , index_y = x // BLOCK_WIDTH, y // BLOCK_HEIGHT
        self.map[index_y,index_x] = 1


    def quit(self):
        pygame.quit()
        sys.exit()

    def draw_grid(self, surface, color):
        for h in range(MAP_HEIGHT):
                pygame.draw.line(surface, color, (0, h*BLOCK_HEIGHT), (SCREEN_WIDTH, h*BLOCK_HEIGHT))
        pygame.draw.line(surface, color, (0, SCREEN_HEIGHT-1 ), (SCREEN_WIDTH-1,SCREEN_HEIGHT-1 ))
        for w in range(MAP_WIDTH):
                pygame.draw.line(surface, color, (w*BLOCK_WIDTH, 0), (w*BLOCK_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(surface, color, (SCREEN_WIDTH-1, 0), (SCREEN_WIDTH-1, SCREEN_HEIGHT-1 ))

    def draw_text(self, surf, font_file, text, size, color, x, y):
        font = pygame.font.Font(font_file, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        surf.blit(text_surface, text_rect)

    def save_pattern(self):
        print('save pattern successfully')

if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('--save_path', type=str, default='/rle/my_rle', help='what path you want to save')
    parser.add_argument('--pattern_name', type=str, default='box', help='what pattern name you want to use')
    opt = parser.parse_args()
    # pattern_file = opt.pattern + '.rle'
    dirname= os.path.dirname(os.path.abspath(__file__))
    # rle_folder = os.path.join(dirname, 'rle')
    #
    # for path, folder, file in os.walk(rle_folder):
    #     if pattern_file in file:
    #         rle_file = os.path.join(path, pattern_file)
    # try:
    #     rle_file
    # except NameError:
    #     print('pattern file not exist, default use test.rle')
    #     rle_file = os.path.join(rle_folder, 'test.rle')

    font_folder = os.path.join(dirname, 'font')
    font_file = os.path.join(font_folder, 'SourceHanSansSC-Normal.otf')
    game = Generator(opt.save_path, opt.pattern_name, font_file)
    game.run()
