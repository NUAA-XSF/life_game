#######################################################
# life game version 0.2
# author: NUAA-XSF
# download pattern (rle file) form http://copy.sh/life/
#######################################################

import re
import random
import sys
import os

import pygame
import numpy as np

from configuration import *


class Run:
    def __init__(self, rle_file, font_file):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True
        self.generation = 0
        self.last_time = pygame.time.get_ticks()
        self.map = np.zeros((MAP_HEIGHT, MAP_WIDTH)).astype(np.int8)
        self.grid = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
        self.grid.set_colorkey(BLACK)
        self.rle_file = rle_file
        self.font_file = font_file
        self.pause = False
        self.draw_grid(self.grid, GRAY1)
        self.parse_rle(self.rle_file, self.map)

    def do_rule(self, map_rgb):
        eight_grid_sum = self.conv2d(self.map)

        map_copy = self.map.copy()
        self.map[:, :] = 0

        # rule : B3/S23
        self.map[(map_copy == 1) & (eight_grid_sum < 3)] = 0
        self.map[(map_copy == 1) & (eight_grid_sum > 4)] = 0
        self.map[(map_copy == 1) & (eight_grid_sum == 3)] = 1
        self.map[(map_copy == 1) & (eight_grid_sum == 4)] = 1
        self.map[(map_copy == 0) & (eight_grid_sum == 3)] = 1
        alive_num = np.sum(self.map == 1)
        map_rgb[self.map == 1] = list(RED)
        map_rgb[self.map == 0] = list(GRAY)
        map_resize = np.repeat(map_rgb, BLOCK_HEIGHT, axis=0)
        map_resize = np.repeat(map_resize, BLOCK_WIDTH, axis=1)
        map_resize = np.flip(np.rot90(map_resize), 0)
        map_resize_surf = pygame.surfarray.make_surface(map_resize).convert()
        map_resize_surf.blit(self.grid, (0, 0))
        self.generation += 1
        return map_resize_surf, alive_num

    def run(self):
        map_rgb = np.zeros((MAP_HEIGHT, MAP_WIDTH, 3), dtype=np.int)
        while self.running:
            self.clock.tick(FPS)
            self.event()
            if not self.pause:
                map_resize_surf, alive_num = self.do_rule(map_rgb)
            self.screen.fill(BLACK)
            self.screen.blit(map_resize_surf, (0, 0))
            t = pygame.time.get_ticks()
            interval = t - self.last_time
            self.last_time = t
            self.draw_text(self.screen, self.font_file, ':'.join(['generaion', str(self.generation)]), 20, BLACK, 20,
                           10)
            self.draw_text(self.screen, self.font_file, ':'.join(['alive', str(alive_num)]), 20, BLACK, 20, 30)
            self.draw_text(self.screen, self.font_file, ':'.join(['fps', str(0 if self.pause else 1000 // interval)]),
                           20, BLACK, 20, 50)
            self.draw_text(self.screen, self.font_file, ':'.join(['state', 'puase' if self.pause else 'run']), 20,
                           BLACK, 20, 70)
            pygame.display.flip()

        self.quit()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.pause = not self.pause
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def quit(self):
        pygame.quit()
        sys.exit()

    @staticmethod
    def draw_grid(surface, color):
        for h in range(MAP_HEIGHT):
            pygame.draw.line(surface, color, (0, h * BLOCK_HEIGHT), (SCREEN_WIDTH, h * BLOCK_HEIGHT))
        pygame.draw.line(surface, color, (0, SCREEN_HEIGHT - 1), (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1))
        for w in range(MAP_WIDTH):
            pygame.draw.line(surface, color, (w * BLOCK_WIDTH, 0), (w * BLOCK_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(surface, color, (SCREEN_WIDTH - 1, 0), (SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1))

    @staticmethod
    def draw_text(surf, font_file, text, size, color, x, y):
        font = pygame.font.Font(font_file, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        surf.blit(text_surface, text_rect)

    @staticmethod
    def parse_rle(file, m):
        # 解析rle文件
        with open(file, 'r') as f:
            lines = f.readlines()

        state = []
        w_h_rule = []
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            if line[0] == 'x':
                w_h_rule.append(line)
            elif line[0] in 'bo$!123456789':
                state.append(line)
            else:
                raise Exception('Error RLE file format.')

        w, h, rule = w_h_rule[0].split(',')
        w = int(w[w.find('=') + 1:], 10)
        h = int(h[h.find('=') + 1:], 10)

        if w >= MAP_WIDTH or h >= MAP_HEIGHT:
            raise Exception('Too large width or height.')

        rule = rule[rule.find('='):]
        state = ''.join(state)
        if state[-1] == '!':
            state = state[:-1]  # delete '!'
        else:
            raise Exception('Error RLE file format.')

        state = state.split('$')

        def _repeat_state(s):
            new_line = []
            if not s:
                new_line.append('b' * w)
                return new_line
            end_num = 0
            num_list = re.findall(r'\d+', s)
            if s[-1].isdigit():
                end_num = int(num_list[-1], 10) - 1
                s = s[:-(len(num_list[-1]))]
                num_list.pop()
            for n in num_list:
                s = s[:s.find(n)] + s[s.find(n) + len(n)] * int(n, 10) + s[s.find(n) + len(n) + 1:]
            if len(s) < w:
                s = s + 'b' * (w - len(s))
            if len(s) > w:
                raise Exception('Error RLE file format.')

            new_line.append(s)
            for l in range(end_num):
                new_line.append('b' * w)
            return new_line

        state = [_repeat_state(s) for s in state]
        new_state = []
        for l in state:
            new_state.extend(l)

        if len(new_state) != h:
            raise Exception('Error RLE file format.')

        state = new_state

        # Random initial position
        x = random.randint(0, m.shape[1] - w)
        y = random.randint(0, m.shape[0] - h)
        for row in range(h):
            m[row + y, x:x + w] = [1 if c == 'o' else 0 for c in state[row]]

    @staticmethod
    def conv2d(x, pad=0):
        h, w = x.shape
        x = np.pad(x, ((1, 1), (1, 1)), 'constant', constant_values=(0, 0))
        b = x[1:w + 1, 1:h + 1] \
            + x[1:w + 1, 0:h] \
            + x[1:w + 1, 2:h + 2] \
            + x[0:w, 1:h + 1] \
            + x[0:w, 0:h] \
            + x[0:w, 2:h + 2] \
            + x[2:w + 2, 1:h + 1] \
            + x[2:w + 2, 0:h] \
            + x[2:w + 2, 2:h + 2]
        return b


if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern', type=str, default='box', help='what pattern you want to show')
    # parser.add_argument('--color', type=str, default='blue', help='what color cell is')
    opt = parser.parse_args()
    pattern_file = opt.pattern + '.rle'
    dirname = os.path.dirname(os.path.abspath(__file__))
    rle_folder = os.path.join(dirname, 'rle')
    print(rle_folder)
    for path, folder, file in os.walk(rle_folder):
        if pattern_file in file:
            rle_file = os.path.join(path, pattern_file)
    try:
        rle_file
    except NameError:
        print('pattern file not exist, default use test.rle')
        rle_file = os.path.join(rle_folder, 'test.rle')

    font_folder = os.path.join(dirname, 'font')
    font_file = os.path.join(font_folder, 'SourceHanSansSC-Normal.otf')
    game = Run(rle_file, font_file)
    game.run()
