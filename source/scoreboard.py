import pygame
from source import game_functions, coin, settings
from source import constants as c


class Scoreboard:
    def __init__(self, game_info, state):
        self.coin_total = game_info[c.COIN_TOTAL]
        self.total_lives = game_info[c.LIVES]
        self.state = state
        self.game_info = game_info
        
        self.create_font_image_dict()
        self.create_info_labels()
        self.create_state_labels()
        self.flashing_coin = coin.Flash(280, 53)

    def update(self, level_info, level=None):
        self.level = level
        self.handle_level_state(level_info)
        
    def create_font_image_dict(self):
        self.image_dict = {}
        image_rect_list = [# 0 - 9
                           (3, 230, 7, 7), (12, 230, 7, 7), (19, 230, 7, 7),
                           (27, 230, 7, 7), (35, 230, 7, 7), (43, 230, 7, 7),
                           (51, 230, 7, 7), (59, 230, 7, 7), (67, 230, 7, 7),
                           (75, 230, 7, 7), 
                           # A - Z
                           (83, 230, 7, 7), (91, 230, 7, 7), (99, 230, 7, 7),
                           (107, 230, 7, 7), (115, 230, 7, 7), (123, 230, 7, 7),
                           (3, 238, 7, 7), (11, 238, 7, 7), (20, 238, 7, 7),
                           (27, 238, 7, 7), (35, 238, 7, 7), (44, 238, 7, 7),
                           (51, 238, 7, 7), (59, 238, 7, 7), (67, 238, 7, 7),
                           (75, 238, 7, 7), (83, 238, 7, 7), (91, 238, 7, 7),
                           (99, 238, 7, 7), (108, 238, 7, 7), (115, 238, 7, 7),
                           (123, 238, 7, 7), (3, 246, 7, 7), (11, 246, 7, 7),
                           (20, 246, 7, 7), (27, 246, 7, 7), (48, 246, 7, 7),
                           # -*
                           (68, 249, 6, 2), (75, 247, 6, 6)]
                           
        character_string = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -*'
        
        for character, image_rect in zip(character_string, image_rect_list):
            self.image_dict[character] = game_functions.get_image(settings.GFX['text_images'],
                                                                  *image_rect, (92, 148, 252), 2.9)

    def create_info_labels(self):
        self.score_text = []
        self.coin_count_text = []
        self.mario_label = []
        self.world_label = []
        self.time_label = []
        self.stage_label = []

        self.create_label(self.score_text, '000000', 75, 55)
        self.create_label(self.coin_count_text, '*00', 300, 55)
        self.create_label(self.mario_label, 'MARIO', 75, 30)
        self.create_label(self.world_label, 'WORLD', 450, 30)
        self.create_label(self.time_label, 'TIME', 625, 30)
        self.create_label(self.stage_label, '1-1', 472, 55)

        self.info_labels = [self.score_text, self.coin_count_text, self.mario_label,
                    self.world_label, self.time_label, self.stage_label]

    def create_state_labels(self):
        if self.state == c.MAIN_MENU:
            self.create_main_menu_labels()
        elif self.state == c.LOAD_SCREEN:
            self.create_player_image()
            self.create_load_screen_labels()
        elif self.state == c.LEVEL:
            self.create_level_labels()
        elif self.state == c.GAME_OVER:
            self.create_game_over_labels()
        elif self.state == c.TIME_OUT:
            self.create_time_out_labels()

    def create_player_image(self):
        self.life_times_image = game_functions.get_image(settings.GFX['text_images'],
                                                         75, 247, 6, 6, (92, 148, 252), 2.9)
        self.life_times_rect = self.life_times_image.get_rect(center=(378, 295))
        self.life_total_label = []
        self.create_label(self.life_total_label, str(self.total_lives), 450, 285)
        
        if self.game_info[c.PLAYER_NAME] == c.PLAYER_MARIO:
            rect = (178, 32, 12, 16)
        else:
            rect = (178, 128, 12, 16)
        self.player_image = game_functions.get_image(settings.GFX['mario_bros'],
                                                     *rect, (92, 148, 252), 2.9)
        self.player_rect = self.player_image.get_rect(center=(320, 290))

    def create_main_menu_labels(self):
        mario_game = []
        luigi_game = []
        top = []
        top_score = []

        self.create_label(mario_game, c.PLAYER1, 272, 360)
        self.create_label(luigi_game, c.PLAYER2, 272, 405)
        self.create_label(top, 'TOP - ', 290, 465)
        self.create_label(top_score, '000000', 400, 465)
        self.state_labels = [mario_game, luigi_game, top, top_score,
                            *self.info_labels]
    
    def create_load_screen_labels(self):
        world_label = []
        self.stage_label2 = []

        self.create_label(world_label, 'WORLD', 280, 200)
        self.create_label(self.stage_label2, '1-1', 430, 200)
        self.state_labels = [world_label, self.stage_label2,
                *self.info_labels, self.life_total_label]

    def create_level_labels(self):
        self.time = c.GAME_TIME_OUT
        self.current_time = 0

        self.clock_time_label = []
        self.create_label(self.clock_time_label, str(self.time), 645, 55)
        self.state_labels = [*self.info_labels, self.clock_time_label]

    def create_game_over_labels(self):
        game_label = []
        over_label = []
        
        self.create_label(game_label, 'GAME', 280, 300)
        self.create_label(over_label, 'OVER', 400, 300)
        
        self.state_labels = [game_label, over_label, *self.info_labels]

    def create_time_out_labels(self):
        timeout_label = []
        self.create_label(timeout_label, 'TIME OUT', 290, 310)
        self.state_labels = [timeout_label, *self.info_labels]

    def create_label(self, label_list, string, x, y):
        for letter in string:
            label_list.append(Character(self.image_dict[letter]))
        self.set_label_rects(label_list, x, y)
    
    def set_label_rects(self, label_list, x, y):
        for i, letter in enumerate(label_list):
            letter.rect.x = x + ((letter.rect.width + 3) * i)
            letter.rect.y = y
            if letter.image == self.image_dict['-']:
                letter.rect.y += 7
                letter.rect.x += 2
    
    def handle_level_state(self, level_info):
        self.score = level_info[c.SCORE]
        self.update_text(self.score_text, self.score)
        self.update_text(self.coin_count_text, level_info[c.COIN_TOTAL])
        self.update_text(self.stage_label, level_info[c.LEVEL_NUM])
        self.flashing_coin.update(level_info[c.CURRENT_TIME])
        if self.state == c.LOAD_SCREEN:
            self.update_text(self.stage_label2, level_info[c.LEVEL_NUM])
        if self.state == c.LEVEL:
            if (level_info[c.CURRENT_TIME] - self.current_time) > 1000:
                self.current_time = level_info[c.CURRENT_TIME]
                self.time -= 1
                self.update_text(self.clock_time_label, self.time, True)
    
    def update_text(self, text, score, reset=False):
        if reset and len(text) > len(str(score)):
            text.remove(text[0])
        index = len(text) - 1
        for digit in reversed(str(score)):
            rect = text[index].rect
            text[index] = Character(self.image_dict[digit])
            text[index].rect = rect
            index -= 1
        
    def draw(self, surface):
        self.draw_info(surface, self.state_labels)
        if self.state == c.LOAD_SCREEN:
            surface.blit(self.player_image, self.player_rect)
            surface.blit(self.life_times_image, self.life_times_rect)
        surface.blit(self.flashing_coin.image, self.flashing_coin.rect)
    
    def draw_info(self, surface, label_list):
        for label in label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)


class GameStats:
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.y_vel = -3
        self.create_images_dict()
        self.score = score
        self.create_score_digit()
        self.distance = 130 if self.score == 1000 else 75

    def create_images_dict(self):
        self.image_dict = {}
        digit_rect_list = [(1, 168, 3, 8), (5, 168, 3, 8),
                           (8, 168, 4, 8), (0, 0, 0, 0),
                           (12, 168, 4, 8), (16, 168, 5, 8),
                           (0, 0, 0, 0), (0, 0, 0, 0),
                           (20, 168, 4, 8), (0, 0, 0, 0)]
        digit_string = '0123456789'
        for digit, image_rect in zip(digit_string, digit_rect_list):
            self.image_dict[digit] = game_functions.get_image(settings.GFX[c.ITEM_SHEET],
                                                              *image_rect, c.BLACK, c.BRICK_SIZE_MULTIPLIER)

    def create_score_digit(self):
        self.digit_group = pygame.sprite.Group()
        self.digit_list = []
        for digit in str(self.score):
            self.digit_list.append(Digit(self.image_dict[digit]))

        for i, digit in enumerate(self.digit_list):
            digit.rect = digit.image.get_rect()
            digit.rect.x = self.x + (i * 10)
            digit.rect.y = self.y

    def update(self, score_list):
        for digit in self.digit_list:
            digit.rect.y += self.y_vel

        if (self.y - self.digit_list[0].rect.y) > self.distance:
            score_list.remove(self)

    def draw(self, screen):
        for digit in self.digit_list:
            screen.blit(digit.image, digit.rect)


class Digit(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()


class Character(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
