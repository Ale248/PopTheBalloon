import pygame
import os
import math
import random

# Center window
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Init
pygame.init()

# Game window
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
game_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Pop The Balloon")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (207, 173, 23)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_YELLOW = (255, 208, 0)

# Fonts
small_font = pygame.font.Font("freesansbold.ttf", 20)
medium_font = pygame.font.Font('freesansbold.ttf', 32)
large_font = pygame.font.Font('freesansbold.ttf', 64)

# Load images
background_img = pygame.image.load('background.png')
crosshair_img = pygame.image.load('crosshair.png')
balloon1_img = pygame.image.load('balloon1.png')

# Set icon of the window
pygame.display.set_icon(balloon1_img)

# Constants
BALLOON_CENTER = (64, 32)
BALLOON_RADIUS = 32
NUM_BALLOON = 5
BALLOON_MAX_SPEED = -6
BALLOON_MIN_SPEED = -4
BALLOON_X_UPPERBOUND = DISPLAY_WIDTH - 96
BALLOON_X_LOWERBOUND = -32
BALLOON_Y_UPPERBOUND = DISPLAY_HEIGHT + 300
BALLOON_Y_LOWERBOUND = DISPLAY_HEIGHT + 33
FPS = 60
TIME_LIMIT = 30

# Global values
pause = False
volume_val = 1.0


# Return x coordinate that make the text surface centered
# surf: The text surface to be centered
def get_x_center(surf):
    size = surf.get_size()
    x = (DISPLAY_WIDTH / 2) - (size[0] / 2)
    return x


# Return y coordinate that make the text centered
# surf: The text surface to be centered
def get_y_center(surf):
    size = surf.get_size()
    y = (DISPLAY_WIDTH / 2) - (size[1] / 2)
    return y


# Get the highscore from a txt file
def get_high_score():
    # Default high score
    high_score = 0

    # Try to read the high score from a file
    try:
        high_score_file = open("high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
        print("The high score is", high_score)
    except IOError:
        # Error reading file, no high score
        print("There is no high score yet.")
    except ValueError:
        # There's a file there, but we don't understand the number.
        print("I'm confused. Starting with no high score.")

    return high_score


# Save highscore to the txt file
# new_high_score: The new high score to be saved
def save_high_score(new_high_score):
    try:
        # Write the file to disk
        high_score_file = open("high_score.txt", "w")
        high_score_file.write(str(new_high_score))
        high_score_file.close()
    except IOError:
        # Hm, can't write it.
        print("Unable to save the high score.")


# Show score and highscore on the game screen
# score: The current score
# high_score: The current high score
def show_score(score, high_score):
    # For text, render then blit
    if score > high_score:
        high_score = score
    score_text = medium_font.render("Score: " + str(score), True, WHITE)
    high_score_text = medium_font.render("High Score: " + str(high_score), True, WHITE)
    game_display.blit(high_score_text, (DISPLAY_WIDTH - high_score_text.get_width(), 0))
    game_display.blit(score_text, (0, 0))


# Draws an interactive button on the display
# msg: Text on the button
# x: X location of the top left coordinate of the button
# y: Y location of the top left coordinate of the button
# w: Button width
# h: Button height
# ic: Inactive color (when a mouse is not hovering)
# ac: Active color (when a mouse is hovering)
# action: Function to be called when button is clicked
def button(msg, x, y, w, h, ic, ac, action=None):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    if x + w > mouse_pos[0] > x and y + h > mouse_pos[1] > y:
        pygame.draw.rect(game_display, ac, (x, y, w, h))

        if mouse_click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(game_display, ic, (x, y, w, h))

    text_surface = small_font.render(msg, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    game_display.blit(text_surface, text_rect)


# Checks if crosshair is on a balloon
# balloon_c: X and Y coordinates of center of the balloon
# balloon_r: Radius of the balloon
# mouse_x: X coordinate of crosshair
# mouse_y: Y coordinate of crosshair
def is_over(balloon_c, balloon_r, mouse_x, mouse_y):
    distance = math.sqrt((math.pow(balloon_c[0] - mouse_x, 2)) + (math.pow(balloon_c[1] - mouse_y, 2)))
    if distance < balloon_r:
        return True
    return False


# Returns the X and Y coordinates of the center of a balloon itself
# x: X coordinate of top left box of the balloon
# y: Y coordinate of top left box of the balloon
def get_center(x, y):
    return BALLOON_CENTER[0] + x, BALLOON_CENTER[1] + y


# Shows the crosshair instead of mouse cursor
def game_cursor():
    mouse_pos = pygame.mouse.get_pos()
    pygame.mouse.set_visible(False)
    game_display.blit(crosshair_img, (mouse_pos[0] - 16, mouse_pos[1] - 16))


# Exits the application
def game_exit():
    pygame.quit()
    quit()


# Shows the pause screen
def game_pause():
    pygame.mixer.music.pause()
    pygame.mouse.set_visible(True)
    while pause:
        game_display.blit(background_img, (0, 0))
        pause_text = large_font.render("PAUSED", True, WHITE)
        game_display.blit(pause_text, (get_x_center(pause_text), 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_unpause()

        button("Resume", 330, 300, 140, 70, GREEN, BRIGHT_GREEN, game_unpause)
        button("Reset", 330, 400, 140, 70, YELLOW, BRIGHT_YELLOW, game_intro)
        button("Exit", 330, 500, 140, 70, RED, BRIGHT_RED, game_exit)

        pygame.display.update()
        clock.tick(FPS)


# Unpause the game
def game_unpause():
    global pause
    pause = False
    pygame.mixer.music.unpause()


# Shows the game intro screen
def game_intro():
    global pause
    # pause = False
    # game_unpause()
    intro = True
    high_score = get_high_score()
    while intro:
        pygame.mouse.set_visible(True)
        game_display.blit(background_img, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        title_text = large_font.render("POP THE BALLOON", True, WHITE)
        game_display.blit(title_text, (get_x_center(title_text), 150))
        balloon_small_img = pygame.transform.scale(balloon1_img, (96, 96))
        game_display.blit(balloon_small_img, (108, 154))
        game_display.blit(balloon_small_img, (541, 154))
        game_display.blit(balloon_small_img, (591, 154))

        high_text = medium_font.render("High Score: " + str(high_score), True, WHITE)
        game_display.blit(high_text, (get_x_center(high_text), 230))

        button("Start", 330, 300, 140, 70, GREEN, BRIGHT_GREEN, game_loop)
        button("Settings", 330, 400, 140, 70, YELLOW, BRIGHT_YELLOW, game_settings)
        button("Exit", 330, 500, 140, 70, RED, BRIGHT_RED, game_exit)

        pygame.display.update()
        clock.tick(FPS)


# Shows the game settings screen
def game_settings():
    global volume_val
    pygame.mixer.music.load('background.mp3')
    pygame.mixer.music.play(-1)
    rectangle = pygame.rect.Rect(((400 * volume_val) + 190), 341.5, 20, 20)
    drag = False
    offset_x = 0
    while True:
        pygame.mixer.music.set_volume(volume_val)
        game_display.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if rectangle.collidepoint(event.pos):
                        drag = True
                        mouse_x, mouse_y = event.pos
                        offset_x = rectangle.x - mouse_x
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drag = False
            elif event.type == pygame.MOUSEMOTION:
                if drag:
                    mouse_x, mouse_y = event.pos
                    rectangle.x = mouse_x + offset_x
                    if rectangle.x >= 590:
                        rectangle.x = 590
                    if rectangle.x <= 190:
                        rectangle.x = 190

        volume_val = (rectangle.x - 190) / 400

        volume_text = medium_font.render("Music Volume", True, WHITE)
        value_text = small_font.render(str(round(volume_val, 2)), True, WHITE)

        game_display.blit(volume_text, (get_x_center(volume_text), 230))
        game_display.blit(value_text, (650, 350))

        pygame.draw.line(game_display, WHITE, (200, 350), (600, 350), 5)
        pygame.draw.rect(game_display, RED, rectangle)

        button("Apply", 330, 450, 140, 70, GREEN, BRIGHT_GREEN, game_intro)
        pygame.display.update()
        clock.tick(FPS)


def show_time(seconds):
    time_text = medium_font.render("Time: " + str(seconds), True, WHITE)
    game_display.blit(time_text, (get_x_center(time_text), 0))


def game_over(score, high_score):
    pygame.mouse.set_visible(True)
    while True:
        game_display.blit(background_img, (0, 0))

        test_text = large_font.render("GAME OVER", True, WHITE)
        score_text = medium_font.render("Your Score: " + str(score), True, WHITE)
        high_score_text = medium_font.render("High Score: " + str(high_score), True, WHITE)
        game_display.blit(test_text, (get_x_center(test_text), 100))
        game_display.blit(high_score_text, (get_x_center(high_score_text), 180))
        game_display.blit(score_text, (get_x_center(score_text), 229))
        print(high_score_text.get_size())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_loop()

        button("Retry", 330, 300, 140, 70, GREEN, BRIGHT_GREEN, game_loop)
        button("Exit", 330, 400, 140, 70, RED, BRIGHT_RED, game_exit)

        pygame.display.update()
        clock.tick(60)


# Runs the game
def game_loop():
    start_ticks = pygame.time.get_ticks()
    global pause
    pause = False

    # Create multiple balloons
    balloons_x = []
    balloons_y = []
    balloons_speed = []
    for i in range(NUM_BALLOON):
        balloons_x.append(random.randint(BALLOON_X_LOWERBOUND, BALLOON_X_UPPERBOUND))
        balloons_y.append(random.randint(BALLOON_Y_LOWERBOUND, BALLOON_Y_UPPERBOUND))
        balloons_speed.append(random.randint(BALLOON_MAX_SPEED, BALLOON_MIN_SPEED))

    score = 0
    high_score = get_high_score()
    while True:
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        time_left = TIME_LIMIT - int(seconds)
        game_display.blit(background_img, (0, 0))
        pygame.mixer.music.set_volume(volume_val)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if score > high_score:
                    save_high_score(score)
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = True
                    game_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for i in range(NUM_BALLOON):
                        if is_over(get_center(balloons_x[i], balloons_y[i]), BALLOON_RADIUS, mouse_pos[0],
                                   mouse_pos[1]):
                            pop_sound = pygame.mixer.Sound('pop.wav')
                            pop_sound.play()
                            score += 1
                            balloons_x[i] = random.randint(BALLOON_X_LOWERBOUND, BALLOON_X_UPPERBOUND)
                            balloons_y[i] = random.randint(BALLOON_Y_LOWERBOUND, BALLOON_Y_UPPERBOUND)
                            balloons_speed[i] = random.randint(BALLOON_MAX_SPEED, BALLOON_MIN_SPEED)

        # Balloons movement
        for i in range(NUM_BALLOON):
            game_display.blit(balloon1_img, (balloons_x[i], balloons_y[i]))
            balloons_y[i] += balloons_speed[i]
            if balloons_y[i] <= -128:
                balloons_x[i] = random.randint(BALLOON_X_LOWERBOUND, BALLOON_X_UPPERBOUND)
                balloons_y[i] = random.randint(BALLOON_Y_LOWERBOUND, BALLOON_Y_UPPERBOUND)
                balloons_speed[i] = random.randint(BALLOON_MAX_SPEED, BALLOON_MIN_SPEED)

        if time_left < 0:
            game_over(score, high_score)
            break
        show_time(time_left)
        show_score(score, high_score)
        game_cursor()
        pygame.display.update()
        clock.tick(FPS)


# Begin running the game
game_settings()
game_intro()
game_loop()
