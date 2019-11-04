import os
import json
import pygame
from source import game_functions, settings
from source import constants as c


class Player(pygame.sprite.Sprite):
    def __init__(self, player_name):
        pygame.sprite.Sprite.__init__(self)
        self.player_name = player_name
        self.load_data()
        self.setup_timer()
        self.setup_state()
        self.setup_speed()
        self.load_images()
        
        if c.DEBUG:
            self.big = True

        self.frame_index = 0
        self.state = c.WALK
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self, keys, game_info):
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state(keys)
        self.check_if_hurt_invincible()
        self.check_if_invincible()
        self.animation()

    def load_data(self):
        player_file = str(self.player_name) + '.json'
        file_path = os.path.join('assets', 'data', player_file)
        f = open(file_path)
        self.player_data = json.load(f)

    def animation(self):
        if self.facing_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def start_death_jump(self):
        self.dead = True
        self.y_vel = -11
        self.gravity = .5
        self.frame_index = 6
        self.state = c.DEATH_JUMP

    def restart(self):
        if self.dead:
            self.dead = False
            self.big = False
            self.set_player_image(self.small_normal_frames, 0)
            self.right_frames = self.small_normal_frames[0]
            self.left_frames = self.small_normal_frames[1]
        self.state = c.STAND

    def jumping(self, keys):
        self.allow_jump = False
        self.frame_index = 4
        self.gravity = c.JUMP_GRAVITY
        self.y_vel += self.gravity

        if self.y_vel >= 0 and self.y_vel < self.max_y_vel:
            self.gravity = c.GRAVITY
            self.state = c.FALL

        if keys[game_functions.keybinding['right']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        elif keys[game_functions.keybinding['left']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel, True)

        if not keys[game_functions.keybinding['jump']]:
            self.gravity = c.GRAVITY
            self.state = c.FALL

    def walking(self, keys):
        self.check_to_allow_jump(keys)

        if self.frame_index == 0:
            self.frame_index += 1
            self.walking_timer = self.current_time
        elif (self.current_time - self.walking_timer >
              self.calculate_animation_speed()):
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel

        if keys[game_functions.keybinding['jump']]:
            if self.allow_jump:
                self.state = c.JUMP
                if abs(self.x_vel) > 4:
                    self.y_vel = self.jump_vel - .5
                else:
                    self.y_vel = self.jump_vel

        if keys[game_functions.keybinding['left']]:
            self.facing_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND

            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel, True)
        elif keys[game_functions.keybinding['right']]:
            self.facing_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND

            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        else:
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND

    def falling(self, keys):
        self.y_vel = self.cal_vel(self.y_vel, self.max_y_vel, self.gravity)

        if keys[game_functions.keybinding['right']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        elif keys[game_functions.keybinding['left']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel, True)

    def big_mario(self):
        timer_list = [135, 200, 365, 430, 495, 560, 625, 690, 755, 820, 885]
        size_list = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]
        frames = [(self.small_normal_frames, 0), (self.small_normal_frames, 7),
                    (self.big_normal_frames, 0)]
        if self.transition_timer == 0:
            self.big = True
            self.change_index = 0
            self.transition_timer = self.current_time
        elif (self.current_time - self.transition_timer) > timer_list[self.change_index]:
            if (self.change_index + 1) >= len(timer_list):
                # player becomes big
                self.transition_timer = 0
                self.set_player_image(self.big_normal_frames, 0)
                self.state = c.WALK
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames
            else:
                frame, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frame, frame_index)
            self.change_index += 1

    def small_mario(self):
        timer_list = [265, 330, 395, 460, 525, 590, 655, 720, 785, 850, 915]
        size_list = [0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
        frames = [(self.big_normal_frames, 4), (self.big_normal_frames, 8),
                    (self.small_normal_frames, 8)]

        if self.transition_timer == 0:
            self.change_index = 0
            self.transition_timer = self.current_time
        elif (self.current_time - self.transition_timer) > timer_list[self.change_index]:
            if (self.change_index + 1) >= len(timer_list):
                self.transition_timer = 0
                self.set_player_image(self.small_normal_frames, 0)
                self.state = c.WALK
                self.big = False
                self.hurt_invincible = True
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames
            else:
                frame, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frame, frame_index)
            self.change_index += 1

    def setup_timer(self):
        self.walking_timer = 0
        self.death_timer = 0
        self.flagpole_timer = 0
        self.transition_timer = 0
        self.hurt_invincible_timer = 0
        self.invincible_timer = 0

    def setup_speed(self):
        speed = self.player_data[c.PLAYER_SPEED]
        self.x_vel = 0
        self.y_vel = 0
        
        self.max_walk_vel = speed[c.MAX_WALK_SPEED]
        self.max_run_vel = speed[c.MAX_RUN_SPEED]
        self.max_y_vel = speed[c.MAX_Y_VEL]
        self.walk_accel = speed[c.WALK_ACCEL]
        self.run_accel = speed[c.RUN_ACCEL]
        self.jump_vel = speed[c.JUMP_VEL]
        
        self.gravity = c.GRAVITY
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

    def load_images(self):
        sheet = settings.GFX['mario_bros']
        frames_list = self.player_data[c.PLAYER_FRAMES]

        self.right_frames = []
        self.left_frames = []

        self.right_small_normal_frames = []
        self.left_small_normal_frames = []
        self.right_big_normal_frames = []
        self.left_big_normal_frames = []

        for name, frames in frames_list.items():
            for frame in frames:
                image = game_functions.get_image(sheet, frame['x'], frame['y'],
                                                 frame['width'], frame['height'],
                                                 c.BLACK, c.SIZE_MULTIPLIER)
                left_image = pygame.transform.flip(image, True, False)

                if name == c.RIGHT_SMALL_NORMAL:
                    self.right_small_normal_frames.append(image)
                    self.left_small_normal_frames.append(left_image)
                elif name == c.RIGHT_BIG_NORMAL:
                    self.right_big_normal_frames.append(image)
                    self.left_big_normal_frames.append(left_image)
        
        self.small_normal_frames = [self.right_small_normal_frames,
                                    self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames,
                                    self.left_big_normal_frames]
                                    
        self.all_images = [self.right_small_normal_frames,
                           self.left_small_normal_frames,
                           self.right_big_normal_frames,
                           self.left_big_normal_frames]
        
        self.right_frames = self.small_normal_frames[0]
        self.left_frames = self.small_normal_frames[1]

    def setup_state(self):
        self.facing_right = True
        self.allow_jump = True
        self.allow_fireball = True
        self.dead = False
        self.big = False
        self.fire = False
        self.hurt_invincible = False
        self.invincible = False
        self.crouching = False

    def handle_state(self, keys):
        if self.state == c.STAND:
            self.standing(keys)
        elif self.state == c.WALK:
            self.walking(keys)
        elif self.state == c.JUMP:
            self.jumping(keys)
        elif self.state == c.FALL:
            self.falling(keys)
        elif self.state == c.DEATH_JUMP:
            self.jumping_to_death()
        elif self.state == c.FLAGPOLE:
            self.flag_pole_sliding()
        elif self.state == c.WALK_AUTO:
            self.walking_auto()
        elif self.state == c.END_OF_LEVEL_FALL:
            self.y_vel += self.gravity
        elif self.state == c.IN_CASTLE:
            self.frame_index = 0
        elif self.state == c.SMALL_TO_BIG:
            self.big_mario()
        elif self.state == c.BIG_TO_SMALL:
            self.small_mario()
        elif self.state == c.DOWN_TO_PIPE:
            self.y_vel = 1
            self.rect.y += self.y_vel
        elif self.state == c.UP_OUT_PIPE:
            self.y_vel = -1
            self.rect.y += self.y_vel
            if self.rect.bottom < self.up_pipe_y:
                self.state = c.STAND

    def check_to_allow_jump(self, keys):
        if not keys[game_functions.keybinding['jump']]:
            self.allow_jump = True

    def standing(self, keys):
        self.check_to_allow_jump(keys)

        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0

        if keys[game_functions.keybinding['down']]:
            self.update_crouch_or_not(True)

        if keys[game_functions.keybinding['left']]:
            self.facing_right = False
            self.update_crouch_or_not()
            self.state = c.WALK
        elif keys[game_functions.keybinding['right']]:
            self.facing_right = True
            self.update_crouch_or_not()
            self.state = c.WALK
        elif keys[game_functions.keybinding['jump']]:
            if self.allow_jump:
                self.state = c.JUMP
                self.y_vel = self.jump_vel
        
        if not keys[game_functions.keybinding['down']]:
            self.update_crouch_or_not()

    def update_crouch_or_not(self, isDown=False):
        if not self.big:
            self.crouching = True if isDown else False
            return
        if not isDown and not self.crouching:
            return
        
        self.crouching = True if isDown else False
        frame_index = 7 if isDown else 0 
        bottom = self.rect.bottom
        left = self.rect.x
        if self.facing_right:
            self.image = self.right_frames[frame_index]
        else:
            self.image = self.left_frames[frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left
        self.frame_index = frame_index
    
    def jumping_to_death(self):
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 500:
            self.rect.y += self.y_vel
            self.y_vel += self.gravity

    def cal_vel(self, vel, max_vel, accel, isNegative=False):
        if isNegative:
            new_vel = vel * -1
        else:
            new_vel = vel
        if (new_vel + accel) < max_vel:
            new_vel += accel
        else:
            new_vel = max_vel
        if isNegative:
            return new_vel * -1
        else:
            return new_vel

    def calculate_animation_speed(self):
        if self.x_vel == 0:
            animation_speed = 130
        elif self.x_vel > 0:
            animation_speed = 130 - (self.x_vel * 13)
        else:
            animation_speed = 130 - (self.x_vel * 13 * -1)
        return animation_speed

    def flag_pole_sliding(self):
        self.state = c.FLAGPOLE
        self.x_vel = 0
        self.y_vel = 5

        if self.flagpole_timer == 0:
            self.flagpole_timer = self.current_time
        elif self.rect.bottom < 493:
            if (self.current_time - self.flagpole_timer) < 65:
                self.frame_index = 9
            elif (self.current_time - self.flagpole_timer) < 130:
                self.frame_index = 10
            else:
                self.flagpole_timer = self.current_time
        elif self.rect.bottom >= 493:
            self.frame_index = 10

    def walking_auto(self):
        self.max_x_vel = 5
        self.x_accel = self.walk_accel
        
        self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        
        if (self.walking_timer == 0 or (self.current_time - self.walking_timer) > 200):
            self.walking_timer = self.current_time
        elif (self.current_time - self.walking_timer >
                    self.calculate_animation_speed()):
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time

    def set_player_image(self, frames, frame_index):
        self.frame_index = frame_index
        if self.facing_right:
            self.right_frames = frames[0]
            self.image = frames[0][frame_index]
        else:
            self.left_frames = frames[1]
            self.image = frames[1][frame_index]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def check_if_hurt_invincible(self):
        if self.hurt_invincible:
            if self.hurt_invincible_timer == 0:
                self.hurt_invincible_timer = self.current_time
                self.hurt_invincible_timer2 = self.current_time
            elif (self.current_time - self.hurt_invincible_timer) < 2000:
                if (self.current_time - self.hurt_invincible_timer2) < 35:
                    self.image.set_alpha(0)
                elif (self.current_time - self.hurt_invincible_timer2) < 70:
                    self.image.set_alpha(255)
                    self.hurt_invincible_timer2 = self.current_time
            else:
                self.hurt_invincible = False
                self.hurt_invincible_timer = 0
                for frames in self.all_images:
                    for image in frames:
                        image.set_alpha(255)

    def check_if_invincible(self):
        if self.invincible:
            if self.invincible_timer == 0:
                self.invincible_timer = self.current_time
                self.invincible_timer2 = self.current_time
            elif (self.current_time - self.invincible_timer) < 10000:
                if (self.current_time - self.invincible_timer2) < 35:
                    self.image.set_alpha(0)
                elif (self.current_time - self.invincible_timer2) < 70:
                    self.image.set_alpha(255)
                    self.invincible_timer2 = self.current_time
            elif (self.current_time - self.invincible_timer) < 12000:
                if (self.current_time - self.invincible_timer2) < 100:
                    self.image.set_alpha(0)
                elif (self.current_time - self.invincible_timer2) < 200:
                    self.image.set_alpha(255)
                    self.invincible_timer2 = self.current_time
            else:
                self.invincible = False
                self.invincible_timer = 0
                for frames in self.all_images:
                    for image in frames:
                        image.set_alpha(255)
