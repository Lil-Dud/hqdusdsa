import pygame
import random
import sys
import math
from Stuff.Entitys import PhysicsEntity, Player, Enemy
from Stuff.CPU import load_image, load_images, Animation
from Stuff.MapTime import MAP
from Stuff.FF7 import FF7_remake
from Stuff.part import Particle
from Stuff.Ouchies import Ouch
pygame.font.init()
font = pygame.font.SysFont('Comic sans MS', 30)

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('OIP.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/SHINYS': Animation(load_images('particles/SHINYS'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'sword': load_image('1.png'),
        }

        print(self.assets)
        self.clouds = FF7_remake(self.assets['clouds'], count =16)
        self.player = Player(self, (50, 50), (8, 15))
        self.tilemap = MAP(self, tile_size=16)
        self.level = 0
        self.load_map(self.level)
        self.M = 0
        self.J = 0
        self.points = 0
    def load_map(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.leafs = []
        self.player.air_time = 0

        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leafs.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        self.ememys = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.ememys.append(Enemy(self, spawner['pos'], (8, 15)))
        self.projectiles = []
        self.particles = []
        self.oof = []
        self.scroll = [0, 0]
        self.dead = 0
        self.loading = -30
        self.sword = []


    def run(self):
        print(self.player.rect())
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            text = font.render(str(self.points), False, (0, 0, 0))
            if not len(self.ememys):
                self.loading += 1
                if self.loading > 30:
                    self.level += 1
                    self.load_map(self.level)
            if self.loading < 0:
                self.loading += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.loading = min(30, self.loading + 1)
                if self.dead > 40:
                    self.load_map(self.level)


            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            for rect in self.leafs:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append((Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20))))
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset = render_scroll)

            for enemy in self.ememys.copy():

                enemy.render(self.display, offset=render_scroll)
                kill = enemy.update(self.tilemap, (0, 0))
                if kill:
                    self.ememys.remove(enemy)
                    self.points += 1
            if not self.dead:
                self.player.update(self.tilemap,(self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.oof.append(Ouch(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))

                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.vroom) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.oof.append(Ouch(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'SHINYS', self.player.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame=random.randint(0, 7)))


            for hit in self.sword.copy():
                hit[0][0] += hit[1]
                hit[2] += 1
                img = self.assets['sword']
                self.display.blit(img, (hit[0][0] - img.get_width() / 2 - render_scroll[0], hit[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(hit[0]):
                    self.sword.remove(hit)
                    for i in range(4):
                        self.oof.append(Ouch(hit[0], random.random() - 0.5 + (math.pi if hit[1] > 0 else 0), 2 + random.random()))

                elif hit[2] > 1:
                    self.sword.remove(hit)
                elif self.player.rect().collidepoint(hit[0]):
                    self.sword.remove(hit)

            for o in self.oof.copy():
                kill = o.update()
                o.render(self.display, offset=render_scroll)
                if kill:
                    self.oof.remove(o)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if kill:
                    self.particles.remove((particle))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_z:
                        Player.slash(self.player)
                    if event.key == pygame.K_b:
                        if self.points > 50:
                            self.M += 1
                            self.points -= 50
                    if event.key == pygame.K_v:
                        if self.points > 50:
                            self.J += 1
                            self.points -= 50



                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            if self.loading:
                BlackHole = pygame.Surface(self.display.get_size())
                pygame.draw.circle(BlackHole, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.loading)) * 8)
                BlackHole.set_colorkey((255, 255, 255))
                self.display.blit(BlackHole, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.screen.blit(text, (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
