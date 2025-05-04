import pygame

class Tick:
    def __init__(self, length):
        self.next_tick = length
        self.length = length
 
    def elapse(self, ticks):
        if ticks > self.next_tick:
            self.next_tick += self.length
            return True
        return False

class Scanline:
    def __init__(self, screen, width, height, speed, ticker_length=2):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.speed = speed
        self.ticker = Tick(ticker_length)
        self.lines_position = list(range(0, self.HEIGHT + 1, 200))
        self.scanline = None
        self.create_scanline()

    def create_scanline(self):
        scanline = pygame.Surface((1, 200))
        scanline = scanline.convert_alpha()
        color = pygame.Color(0, 100, 155)
        color.a = 50
        for a in range(100):
            color.g -= 1
            scanline.set_at((0, a), color)
            scanline.set_at((0, 199 - a), color)
        self.scanline = pygame.transform.scale(scanline, (self.WIDTH, 200))

    def update(self):
        ticks = pygame.time.get_ticks()
        if self.ticker.elapse(ticks):
            for i in range(len(self.lines_position)):
                self.lines_position[i] -= self.speed
                if self.lines_position[i] < -199:
                    self.lines_position[i] = self.HEIGHT

    def draw(self):
        for line in self.lines_position:
            self.screen.blit(self.scanline, (0, line), None, pygame.BLEND_RGBA_MULT)
            self.screen.blit(self.scanline, (0, line), None)
