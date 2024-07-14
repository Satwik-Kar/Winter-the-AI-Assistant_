import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Talking Visualization")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)


# Dot class to represent pulsing dots around the text
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_radius = 3
        self.radius = self.base_radius
        self.color = BLUE
        self.pulse_speed = random.uniform(0.05, 0.2)

    def pulse(self):
        self.radius += self.pulse_speed
        if self.radius >= self.base_radius + 2 or self.radius <= self.base_radius - 2:
            self.pulse_speed = -self.pulse_speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))


# Create a list of dots around the text area
def create_dots_around_text(text_rect, num_dots=50):
    dots = []
    for _ in range(num_dots):
        angle = random.uniform(0, 2 * 3.14159)
        radius = random.uniform(50, 100)
        x = text_rect.centerx + radius * math.cos(angle)
        y = text_rect.centery + radius * math.sin(angle)
        dots.append(Dot(x, y))
    return dots


# Main loop
def main():
    running = True
    clock = pygame.time.Clock()
    messages = ["Hello!", "I am Knox.", "How can I assist you today?", "Weather forecast is available.",
                "Ask me anything!"]
    message_index = 0
    char_index = 0
    message_timer = 0

    # Prepare text rendering
    font = pygame.font.SysFont(None, 48)
    text = ""
    text_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 0, 0)

    # Create dots around the text
    dots = create_dots_around_text(text_rect)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(BLACK)

        # Draw dots and pulse them
        for dot in dots:
            dot.pulse()
            dot.draw(screen)

        # Update text typing effect
        if char_index < len(messages[message_index]):
            message_timer += 1
            if message_timer > 5:  # Adjust the speed of the typing effect
                text += messages[message_index][char_index]
                char_index += 1
                message_timer = 0
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surface, text_rect)
        else:
            if message_timer > 120:  # Pause before showing the next message
                message_index = (message_index + 1) % len(messages)
                char_index = 0
                text = ""
                message_timer = 0
                dots = create_dots_around_text(text_rect)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
