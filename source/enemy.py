import pygame
from source import game_functions, settings
from source import constants as c

    
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    
    def setup_enemy(self, x, y, direction, name, sheet, frame_rect_list, in_range, range_start,
                    range_end, is_vertical=False):
        self.frames = []
        self.frame_index = 0
        self.animate_timer = 0
        self.gravity = 1.5
        self.state = c.WALK
        
        self.name = name
        self.direction = direction
        self.load_frames(sheet, frame_rect_list)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.in_range = in_range
        self.range_start = range_start
        self.range_end = range_end
        self.is_vertical = is_vertical
        self.set_velocity()
        self.death_timer = 0
    
    def load_frames(self, sheet, frame_rect_list):
        for frame_rect in frame_rect_list:
            self.frames.append(game_functions.get_image(sheet, *frame_rect,
                                                        c.BLACK, c.SIZE_MULTIPLIER))

    def set_velocity(self):
        if self.is_vertical:
            self.x_vel = 0
            self.y_vel = c.ENEMY_SPEED
        else:
            self.x_vel = c.ENEMY_SPEED *-1 if self.direction == c.LEFT else c.ENEMY_SPEED
            self.y_vel = 0
    
    def update(self, game_info, level):
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()
        self.animation()
        self.update_position(level)

    def handle_state(self):
        if (self.state == c.WALK or
            self.state == c.FLY):
            self.walking()
        elif self.state == c.FALL:
            self.falling()
        elif self.state == c.JUMPED_ON:
            self.jumped_on()
        elif self.state == c.DEATH_JUMP:
            self.death_jumping()
        elif self.state == c.SHELL_SLIDE:
            self.shell_sliding()
        elif self.state == c.REVEAL:
            self.revealing()
    
    def walking(self):
        if (self.current_time - self.animate_timer) > 125:
            if self.direction == c.RIGHT:
                if self.frame_index == 4:
                    self.frame_index += 1
                elif self.frame_index == 5:
                    self.frame_index = 4
            else:
                if self.frame_index == 0:
                    self.frame_index += 1
                elif self.frame_index == 1:
                    self.frame_index = 0
            self.animate_timer = self.current_time
    
    def falling(self):
        if self.y_vel < 10:
            self.y_vel += self.gravity
    
    def jumped_on(self):
        pass

    def death_jumping(self):
        self.rect.y += self.y_vel
        self.rect.x += self.x_vel
        self.y_vel += self.gravity
        if self.rect.y > c.SCREEN_HEIGHT:
            self.kill()

    def shell_sliding(self):
        if self.direction == c.RIGHT:
            self.x_vel = 10
        else:
            self.x_vel = -10

    def revealing(self):
        pass

    def start_death_jump(self, direction):
        self.y_vel = -8
        self.x_vel = 2 if direction == c.RIGHT else -2
        self.gravity = .5
        self.frame_index = 3
        self.state = c.DEATH_JUMP

    def animation(self):
        self.image = self.frames[self.frame_index]
    
    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)

        if self.in_range and self.is_vertical:
            if self.rect.y < self.range_start:
                self.rect.y = self.range_start
                self.y_vel = c.ENEMY_SPEED
            elif self.rect.bottom > self.range_end:
                self.rect.bottom = self.range_end
                self.y_vel = -1 * c.ENEMY_SPEED

        self.rect.y += self.y_vel
        if (self.state != c.DEATH_JUMP and 
            self.state != c.FLY):
            self.check_y_collisions(level)
        
        if self.rect.x <= 0:
            self.kill()
        elif self.rect.y > (level.viewport.bottom):
            self.kill()
    
    def check_x_collisions(self, level):
        if self.in_range and not self.is_vertical:
            if self.rect.x < self.range_start:
                self.rect.x = self.range_start
                self.change_direction(c.RIGHT)
            elif self.rect.right > self.range_end:
                self.rect.right = self.range_end
                self.change_direction(c.LEFT)
        else:
            collider = pygame.sprite.spritecollideany(self, level.ground_step_pipe_group)
            if collider:
                if self.direction == c.RIGHT:
                    self.rect.right = collider.rect.left
                    self.change_direction(c.LEFT)
                elif self.direction == c.LEFT:
                    self.rect.left = collider.rect.right
                    self.change_direction(c.RIGHT)

        if self.state == c.SHELL_SLIDE:
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                level.update_score(100, enemy, 0)
                level.move_to_dying_group(level.enemy_group, enemy)
                enemy.start_death_jump(self.direction)

    def change_direction(self, direction):
        self.direction = direction
        if self.direction == c.RIGHT:
            self.x_vel = c.ENEMY_SPEED
            if self.state == c.WALK or self.state == c.FLY:
                self.frame_index = 4
        else:
            self.x_vel = c.ENEMY_SPEED * -1
            if self.state == c.WALK or self.state == c.FLY:
                self.frame_index = 0

    def check_y_collisions(self, level):
        # decrease runtime delay: when enemey is on the ground, don't check brick and box
        if self.rect.bottom >= c.GROUND_HEIGHT:
            sprite_group = level.ground_step_pipe_group
        else:
            sprite_group = pygame.sprite.Group(level.ground_step_pipe_group,
                            level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)
        if sprite and sprite.name != c.MAP_SLIDER:
            if self.rect.top <= sprite.rect.top:
                self.rect.bottom = sprite.rect.y
                self.y_vel = 0
                self.state = c.WALK
        level.check_is_falling(self)

class Goomba(Enemy):
    def __init__(self, x, y, direction, color, in_range,
                range_start, range_end, name=c.GOOMBA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, settings.GFX[c.ENEMY_SHEET],
                         frame_rect_list, in_range, range_start, range_end)
        # dead jump image
        self.frames.append(pygame.transform.flip(self.frames[2], False, True))
        # right walk images
        self.frames.append(pygame.transform.flip(self.frames[0], True, False))
        self.frames.append(pygame.transform.flip(self.frames[1], True, False))

    def get_frame_rect(self, color):
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(0, 34, 16, 16), (30, 34, 16, 16), 
                        (61, 30, 16, 16)]
        else:
            frame_rect_list = [(0, 4, 16, 16), (30, 4, 16, 16), 
                        (61, 0, 16, 16)]
        return frame_rect_list

    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 500:
            self.kill()

class Koopa(Enemy):
    def __init__(self, x, y, direction, color, in_range,
                range_start, range_end, name=c.KOOPA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, settings.GFX[c.ENEMY_SHEET],
                         frame_rect_list, in_range, range_start, range_end)
        # dead jump image
        self.frames.append(pygame.transform.flip(self.frames[2], False, True))
        # right walk images
        self.frames.append(pygame.transform.flip(self.frames[0], True, False))
        self.frames.append(pygame.transform.flip(self.frames[1], True, False))

    def get_frame_rect(self, color):
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(150, 0, 16, 24), (180, 0, 16, 24),
                        (360, 5, 16, 15)]
        elif color == c.COLOR_TYPE_RED:
            frame_rect_list = [(150, 30, 16, 24), (180, 30, 16, 24),
                        (360, 35, 16, 15)]
        else:
            frame_rect_list = [(150, 60, 16, 24), (180, 60, 16, 24),
                        (360, 65, 16, 15)]
        return frame_rect_list

    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.x = x
        self.rect.bottom = bottom
        self.in_range = False


def create_enemy(item, level):
    direction = c.LEFT if item['direction'] == 0 else c.RIGHT
    color = item[c.COLOR]
    if c.ENEMY_RANGE in item:
        in_range = item[c.ENEMY_RANGE]
        range_start = item['range_start']
        range_end = item['range_end']
    else:
        in_range = False
        range_start = range_end = 0

    if item['type'] == c.ENEMY_TYPE_GOOMBA:
        sprite = Goomba(item['x'], item['y'], direction, color,
            in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_KOOPA:
        sprite = Koopa(item['x'], item['y'], direction, color,
            in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_FLY_KOOPA:
        is_vertical = False if item['is_vertical'] == 0 else True
        sprite = FlyKoopa(item['x'], item['y'], direction, color,
            in_range, range_start, range_end, is_vertical)
    elif item['type'] == c.ENEMY_TYPE_PIRANHA:
        sprite = Piranha(item['x'], item['y'], direction, color,
            in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_FIRE_KOOPA:
        sprite = FireKoopa(item['x'], item['y'], direction, color,
            in_range, range_start, range_end, level)
    elif item['type'] == c.ENEMY_TYPE_FIRESTICK:
        sprite = []
        num = item['num']
        center_x, center_y = item['x'], item['y']
        for i in range(num):
            radius = i * 21 # 8 * 2.69 = 21
            sprite.append(FireStick(center_x, center_y, direction, color,
                radius))

    return sprite