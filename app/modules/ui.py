import pygame
import os

class Text:
    def __init__(self, screen, font, color):
        self.screen = screen
        self.font = font
        self.color = color

    def draw(self, text, pos, value):
        full_text = f"{text} {value}"
        text_surface = self.font.render(full_text, True, self.color)
        self.screen.blit(text_surface, pos)

class Circular:
    def __init__(self, screen, center, radius, color, color2, color4, font):
        self.screen = screen
        self.center = center
        self.radius = radius
        self.color = color
        self.color2 = color2
        self.color4 = color4
        self.font = font

    def draw_hour_ticks(self, get_sn_angle):
        for hour in range(24):
            angle_divisions = ((hour * 360 / 24) + get_sn_angle)
            vec_outer = pygame.math.Vector2(0, -self.radius).rotate(-angle_divisions)
            vec_inner = pygame.math.Vector2(0, -(self.radius - 15)).rotate(-angle_divisions)

            end_x, end_y = self.center[0] + vec_outer.x, self.center[1] + vec_outer.y
            start_x, start_y = self.center[0] + vec_inner.x, self.center[1] + vec_inner.y

            pygame.draw.line(self.screen, self.color, (start_x, start_y), (end_x, end_y), 2)

            digit_vec = pygame.math.Vector2(0, -(self.radius - 25)).rotate(-angle_divisions)
            digit_x, digit_y = self.center[0] + digit_vec.x, self.center[1] + digit_vec.y

            digit = self.font.render(str(hour), True, self.color2)
            digit_rect = digit.get_rect(center=(digit_x, digit_y))
            self.screen.blit(digit, digit_rect)

    def draw_clock_hand(self, lst_angle):
        assets_path = os.path.join(os.path.dirname(__file__), os.pardir, "assets", "stars.png")
        image = pygame.image.load(assets_path).convert_alpha()
        image.set_colorkey((0, 0, 0))

        # Rotate image
        rotated_image = pygame.transform.rotate(image, lst_angle)
        rect = rotated_image.get_rect(center=(self.center[0], self.center[1]))  # Keep it centered
        self.screen.blit(rotated_image, rect.topleft)  # Draw rotated image

    def draw_border(self):
        pygame.draw.circle(self.screen, self.color2, self.center, self.radius, 1)