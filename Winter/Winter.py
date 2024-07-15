import io
import math
import random
import sys

import pygame
from gtts import gTTS
from playsound import playsound
import threading

import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play


class Winter:
    def __init__(self):
        self.microphone = None
        self.recognizer = None
        self.name = "Winter"
        self.message = ""
        self.status = "Listening..."
        self.version = "1.0"
        self.rise_music_url = 'sounds/rise.mp3'
        self.fall_music_url = 'sounds/fall.mp3'
        self.is_awake = True

    class Dot:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.base_radius = 3
            self.radius = self.base_radius
            self.color = (0, 150, 255)
            self.pulse_speed = random.uniform(0.05, 0.2)

        def pulse(self):
            self.radius += self.pulse_speed
            if self.radius >= self.base_radius + 2 or self.radius <= self.base_radius - 2:
                self.pulse_speed = -self.pulse_speed

        def draw(self, screen):
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

    def create_dots_around_text(self, text_rect, num_dots=250):
        dots = []
        for _ in range(num_dots):
            angle = random.uniform(0, 2 * 3.14159)
            radius = random.uniform(100, 200)
            x = text_rect.centerx + radius * math.cos(angle)
            y = text_rect.centery + radius * math.sin(angle)
            dots.append(Winter.Dot(x, y))
        return dots

    def show_screen(self):
        running = True
        pygame.init()

        # Screen dimensions
        WIDTH, HEIGHT = 800, 600
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("WINTER")

        # Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        BLUE = (0, 150, 255)
        clock = pygame.time.Clock()
        messages = ["Hello!", "I am Knox.", "How can I assist you today?", "Weather forecast is available.",
                    "Ask me anything!"]
        message_index = 0
        message_timer = 0

        # Prepare text rendering
        font = pygame.font.SysFont(None, 48)

        while running:
            message_text_surface = font.render(self.message, True, WHITE)
            status_text_surface = font.render(self.status, True, WHITE)
            message_text_rect = message_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
            status_text_rect = status_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            dots_rect = message_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            # Create dots around the text
            dots = self.create_dots_around_text(dots_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.kill()

            # Clear the screen
            screen.fill(BLACK)

            # Draw dots and pulse them
            for dot in dots:
                dot.pulse()
                dot.draw(screen)

            # Update the display text
            screen.blit(message_text_surface, message_text_rect)
            screen.blit(status_text_surface, status_text_rect)

            # Pause before showing the next message
            message_timer += 1
            # if message_timer > 240:  # Adjust the pause duration as needed
            #     message_index = (message_index + 1) % len(messages)
            #
            #     message_text_surface = font.render(self.message, True, WHITE)
            #     status_text_surface = font.render(self.status, True, WHITE)
            #
            #     message_text_rect = message_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
            #     status_text_rect = status_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            #
            #     dots = self.create_dots_around_text(status_text_rect)
            #     message_timer = 0

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(120)

    # Quit Pygame
    def start_show_screen_thread(self):
        show_screen_thread = threading.Thread(target=self.show_screen)
        show_screen_thread.daemon = True
        show_screen_thread.start()

    def start(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        welcome_lines = [
            f"Hello! I'm {self.name}, your personal AI assistant.",
            f"Welcome aboard! I'm {self.name}, version {self.version}.",
            f"Greetings! I'm {self.name}, here to assist you.",
            f"Good day! I'm {self.name}, ready to help you.",
            f"Hi there! I'm {self.name}, at your service.",
            f"Salutations! I'm {self.name}, version {self.version}.",
            f"Hey! I'm {self.name}, your AI assistant.",
            f"Welcome! I'm {self.name}, version {self.version}.",
            f"Hello there! I'm {self.name}, your assistant.",
            f"Greetings! I'm {self.name}, version {self.version}.",
            f"Hey there! I'm {self.name}, your virtual assistant.",
            f"Good day! I'm {self.name}, version {self.version}.",
            f"Hi! I'm {self.name}, here to assist you.",
            f"Hello! I'm {self.name}, version {self.version}, at your command.",
            f"Welcome! I'm {self.name}, your trusted assistant."
        ]

        index = random.randint(0, len(welcome_lines) - 1)
        return welcome_lines[index]

    def speak(self, text):
        try:
            self.message = text
            tts = gTTS(text=text, lang="en-IN")
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)

            audio = AudioSegment.from_file(audio_fp, format="mp3")
            play(audio)
            print(text)
        except Exception as e:
            print(e)

    @staticmethod
    def __play(file):
        threading.Thread(target=playsound, args=(file,)).start()

    def recognize(self, next_round, ask_anything_else):
        with self.microphone as source:

            if next_round:
                if ask_anything_else:
                    anything_else = [
                        "Is there anything else I can help you with?",
                        "Do you need assistance with anything else?",
                        "Can I assist you with something else?",
                        "Is there anything more you need?",
                        "Do you need help with anything else?",
                        "Is there anything further you require?",
                        "Anything else you'd like assistance with?",
                        "Do you have any other requests?",
                        "Is there something more I can do for you?",
                        "Any other questions or concerns?",
                        "Would you like help with anything else?",
                        "Is there another way I can assist you?",
                        "Do you have any other needs?",
                        "Anything else I can support you with?",
                        "Do you need anything else from me?"
                    ]
                    random_no = random.randint(0, len(anything_else) - 1)
                    self.speak(anything_else[random_no])

            self.recognizer.adjust_for_ambient_noise(source)
            self.status = "Listening..."
            print("Listening...")
            self.__play(self.rise_music_url)
            audio = self.recognizer.listen(source)

            response = {
                "success": True,
                "error": None,
                "transcription": None
            }
            try:
                response["transcription"] = self.recognizer.recognize_google(audio)
            except sr.RequestError:
                response["success"] = False
                response["error"] = "API unavailable"
            except sr.UnknownValueError:
                response["error"] = "Unable to recognize speech"
            self.status = "Thinking..."
            return response

    def sleep(self):
        self.__play(self.fall_music_url)
        self.is_awake = False
        pygame.quit()
        self.listen_for_wake_word()

    def listen_for_wake_word(self):
        print("Listening for wake word...")
        while not self.is_awake:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)

            try:
                transcription = self.recognizer.recognize_google(audio).lower()
                print(transcription)
                if self.name.lower() in transcription:
                    self.is_awake = True
                    import Main
                    Main.main(from_wake_word=True)
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                continue

    def kill(self):
        goodbye_greetings = [
            "Goodbye! Have a wonderful day!",
            "See you later! Take care!",
            "Farewell! Stay safe!",
            "Goodbye! Hope to assist you again soon!",
            "Take care! See you next time!",
            "Goodbye! Don't hesitate to return if you need anything!",
            "Farewell! Have a great time!",
            "Goodbye! Wishing you all the best!",
            "See you soon! Stay well!",
            "Goodbye! Thanks for stopping by!",
            "Take care! Looking forward to our next interaction!",
            "Goodbye! Have a fantastic day!",
            "Farewell! Until we meet again!",
            "Goodbye! Stay positive and happy!",
            "See you later! Enjoy your day!"
        ]
        random_no = random.randint(0, len(goodbye_greetings) - 1)
        self.speak(goodbye_greetings[random_no])
        playsound(self.fall_music_url)
        pygame.quit()
        sys.exit(0)
