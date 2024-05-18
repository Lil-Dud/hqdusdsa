import random

import pygame
from Stuff.part import Particle
import math
from Stuff.Ouchies import Ouch
class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False,}
        self.dewit = ''
        self.anime_offset = (-3, -3)
        self.flip = False
        self.set_dewit('idle')
        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_dewit(self, it):
        if it != self.dewit:
            self.dewit = it
            self.animation = self.game.assets[self.type + '/' + self.dewit].copy()


    def update(self, tilemap, movement = (0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False,}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.touchable(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.touchable(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        self.last_movement = movement
        self.animation.update()
    def render(self, surf, offset = (0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] +self.anime_offset[0], self.pos[1] - offset[1] + self.anime_offset[1]))


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        self.walk = 0
    def update(self, tilemap, movement=(0, 0)):
        if self.walk:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walk = max(0, self.walk - 1)
            if not self.walk:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.oof.append(Ouch(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))

                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        self.game.oof.append(Ouch(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walk = random.randint(30, 120)

        super().update(tilemap, movement=movement)
        if movement[0] != 0:
            self.set_dewit('run')
        else:
            self.set_dewit('idle')
        if abs (self.game.player.vroom) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.oof.append(Ouch(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'SHINYS', self.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame=random.randint(0, 7)))
                self.game.oof.append(Ouch(self.rect().center, 0, 5 + random.random()))
                self.game.oof.append(Ouch(self.rect().center, math.pi, 5 + random.random()))
                return True
        if len(self.game.sword):
            if self.rect().collidepoint(self.game.sword[0][0]):
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.oof.append(Ouch(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'SHINYS', self.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame=random.randint(0, 7)))
                self.game.oof.append(Ouch(self.rect().center, 0, 5 + random.random()))
                self.game.oof.append(Ouch(self.rect().center, math.pi, 5 + random.random()))
                return True
            if self.rect().collidepoint(self.game.sword[1][0]):
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.oof.append(Ouch(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'SHINYS', self.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame=random.randint(0, 7)))
                self.game.oof.append(Ouch(self.rect().center, 0, 5 + random.random()))
                self.game.oof.append(Ouch(self.rect().center, math.pi, 5 + random.random()))
                return True
            if self.rect().collidepoint(self.game.sword[2][0]):
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.oof.append(Ouch(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'SHINYS', self.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame=random.randint(0, 7)))
                self.game.oof.append(Ouch(self.rect().center, 0, 5 + random.random()))
                self.game.oof.append(Ouch(self.rect().center, math.pi, 5 + random.random()))
                return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0],self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 3
        self.vroom = 0
        self.hya = 0
        self.slide = False
    def render(self, surf, offset = (0, 0)):
        if abs(self.vroom) <= 50:
            super().render(surf, offset=offset)

    def slash(self):
        if self.flip:
            self.game.sword.append([[self.rect().centerx - 7, self.rect().centery], 0, 0])
            self.game.sword.append([[self.rect().centerx - 12, self.rect().centery], 0, 0])
            self.game.sword.append([[self.rect().centerx - 17, self.rect().centery], 0, 0])
        else:
            self.game.sword.append([[self.rect().centerx + 7, self.rect().centery], 0, 0])
            self.game.sword.append([[self.rect().centerx + 12, self.rect().centery], 0, 0])
            self.game.sword.append([[self.rect().centerx + 17, self.rect().centery], 0, 0])
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        self.air_time += 1
        if self.air_time > 100:
            self.game.dead += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2 + self.game.J
        self.slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.slide = True
            self.air_time = 5
            self.jumps = 2
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_dewit('wall_slide')


        if not self.slide:
            if self.air_time > 4:
               self.set_dewit('jump')
            elif movement[0] != 0:
                self.set_dewit('run')
            else:
                self.set_dewit('idle')
        if abs(self.vroom) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'SHINYS', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))


        if self.vroom > 0:
            self.vroom = max(0, self.vroom - 1)
        if self.vroom < 0:
            self.vroom = min(0, self.vroom + 1)
        if abs(self.vroom) > 50:
            self.velocity[0] = abs(self.vroom) / self.vroom * 8
            if abs(self.vroom) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.vroom) / self.vroom * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'SHINYS', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)


    def dash(self):
        if not self.vroom:
            if self.flip:
                self.vroom = -60
            else: self.vroom = 60
    def jump(self):
        if self.slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
