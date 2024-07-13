import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Visualization")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)


# Dot class to represent nodes
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = BLUE
        self.speed = [random.uniform(-1, 1), random.uniform(-1, 1)]

    def move(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        if self.x <= 0 or self.x >= WIDTH:
            self.speed[0] = -self.speed[0]
        if self.y <= 0 or self.y >= HEIGHT:
            self.speed[1] = -self.speed[1]

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# Create a list of dots
dots = [Dot(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(50)]


# Main loop

def main():
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update dots' positions
        for dot in dots:
            dot.move()

        # Clear the screen
        screen.fill(BLACK)

        # Draw dots
        for dot in dots:
            dot.draw(screen)

        # Draw lines between dots (simulating connections)
        for i in range(len(dots)):
            for j in range(i + 1, len(dots)):
                if math.hypot(dots[i].x - dots[j].x, dots[i].y - dots[j].y) < 100:
                    pygame.draw.line(screen, WHITE, (dots[i].x, dots[i].y), (dots[j].x, dots[j].y), 1)

        # Display text
        font = pygame.font.SysFont(None, 36)
        text = font.render("Winter", True, WHITE)
        screen.blit(text, (10, 10))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Quit Pygame
    pygame.quit()
