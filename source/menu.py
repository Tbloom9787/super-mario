import pygame
from source import game_functions, scoreboard, settings
from source import constants as c


class Menu(game_functions.State):
    def __init__(self):
        game_functions.State.__init__(self)
        persist = {c.COIN_TOTAL: 0,
                   c.SCORE: 0,
                   c.LIVES: 3,
                   c.TOP_SCORE: 0,
                   c.CURRENT_TIME: 0.0,
                   c.LEVEL_NUM: 1,
                   c.PLAYER_NAME: c.PLAYER_MARIO}
        self.startup(0.0, persist)

    def update(self, surface, keys, current_time):
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.player_image = self.player_list[self.player_index][0]
        self.player_rect = self.player_list[self.player_index][1]
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        surface.blit(self.background, self.viewport, self.viewport)
        surface.blit(self.image_dict['GAME_NAME_BOX'][0],
                     self.image_dict['GAME_NAME_BOX'][1])
        surface.blit(self.player_image, self.player_rect)
        surface.blit(self.cursor.image, self.cursor.rect)
        self.overhead_info.draw(surface)
    
    def startup(self, current_time, persist):
        self.next = c.LOAD_SCREEN
        self.persist = persist
        self.game_info = persist
        self.overhead_info = scoreboard.Scoreboard(self.game_info, c.MAIN_MENU)

        self.setup_background()
        self.setup_player()
        self.setup_cursor()
        
    def setup_background(self):
        self.background = settings.GFX['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background,
                                    (int(self.background_rect.width*c.BACKGROUND_MULTIPLIER),
                                    int(self.background_rect.height*c.BACKGROUND_MULTIPLIER)))

        self.viewport = settings.SCREEN.get_rect(bottom=settings.SCREEN_RECT.bottom)
        self.image_dict = {}
        image = game_functions.get_image(settings.GFX['title_screen'], 1, 60, 176, 88,
                                         (255, 0, 220), c.SIZE_MULTIPLIER)
        rect = image.get_rect()
        rect.x, rect.y = (170, 100)
        self.image_dict['GAME_NAME_BOX'] = (image, rect)

    def setup_player(self):
        self.player_list = []
        player_rect_info = [(178, 32, 12, 16), (178, 128, 12, 16)]
        for rect in player_rect_info:
            image = game_functions.get_image(settings.GFX['mario_bros'],
                                             *rect, c.BLACK, 2.9)
            rect = image.get_rect()
            rect.x, rect.bottom = 110, c.GROUND_HEIGHT
            self.player_list.append((image, rect))
        self.player_index = 0

    def setup_cursor(self):
        self.cursor = pygame.sprite.Sprite()
        self.cursor.image = game_functions.get_image(settings.GFX[c.ITEM_SHEET], 24, 160, 8, 8, c.BLACK, 3)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 358)
        self.cursor.rect = rect
        self.cursor.state = c.PLAYER1

    def update_cursor(self, keys):
        if self.cursor.state == c.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pygame.K_DOWN]:
                self.cursor.state = c.PLAYER2
                self.player_index = 1
                self.game_info[c.PLAYER_NAME] = c.PLAYER_LUIGI
        elif self.cursor.state == c.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pygame.K_UP]:
                self.cursor.state = c.PLAYER1
                self.player_index = 0
                self.game_info[c.PLAYER_NAME] = c.PLAYER_MARIO
        if keys[pygame.K_RETURN]:
            self.reset_game_info()
            self.done = True
    
    def reset_game_info(self):
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_NUM] = 1
        
        self.persist = self.game_info


class LoadScreen(game_functions.State):
    def __init__(self):
        game_functions.State.__init__(self)
        self.time_list = [2400, 2600, 2635]

    def update(self, surface, keys, current_time):
        if (current_time - self.start_time) < self.time_list[0]:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        elif (current_time - self.start_time) < self.time_list[1]:
            surface.fill(c.BLACK)
        elif (current_time - self.start_time) < self.time_list[2]:
            surface.fill((106, 150, 252))
        else:
            self.done = True

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist
        self.next = self.set_next_state()

        info_state = self.set_info_state()
        self.overhead_info = scoreboard.Scoreboard(self.game_info, info_state)

    def set_next_state(self):
        return c.LEVEL

    def set_info_state(self):
        return c.LOAD_SCREEN


class GameOver(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.time_list = [3000, 3200, 3235]

    def set_next_state(self):
        return c.MAIN_MENU

    def set_info_state(self):
        return c.GAME_OVER


class TimeOut(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.time_list = [2400, 2600, 2635]

    def set_next_state(self):
        if self.persist[c.LIVES] == 0:
            return c.GAME_OVER
        else:
            return c.LOAD_SCREEN

    def set_info_state(self):
        return c.TIME_OUT
