import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from client import Network
import random, math
import os

# pygame init
pygame.font.init()
pygame.mixer.init()

# play music
pygame.mixer.music.load('bubblegum.mp3')
pygame.mixer.music.set_volume(0.075)
pygame.mixer.music.play(-1, start=15)

# Constants
PLAYER_RADIUS = 10
START_VEL = 4
BALL_RADIUS = 5

W, H = 1200, 830
VIEWPORT_W, VIEWPORT_H = 600, 415  # Viewport dimensions
VIEWPORT_SCALE = 2  # Scale factor for zooming in

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

COLORS = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]

# Dynamic Variables
players = {}
balls = []

# FUNCTIONS

def convert_time(t):
    """
    converts a time given in seconds to a time in
    minutes

    :param t: int
    :return: string
    """
    if type(t) == str:
        return t

    if int(t) < 60:
        return str(t) + "s"
    else:
        minutes = str(t // 60)
        seconds = str(t % 60)

        if int(seconds) < 10:
            seconds = "0" + seconds

        return minutes + ":" + seconds

def draw_grid(surface, width, height, grid_size):
    """
    Draws a grid on the given surface.

    :param surface: pygame.Surface, surface to draw on
    :param width: int, width of the surface
    :param height: int, height of the surface
    :param grid_size: int, size of each grid cell
    """
    surface.fill((255, 255, 255))  # Fill surface with white color
    for x in range(0, width, grid_size):
        pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, height))
    for y in range(0, height, grid_size):
        pygame.draw.line(surface, (200, 200, 200), (0, y), (width, y))

def redraw_window(players, balls, game_time, score, player, background):
    """
    Draws each frame.

    :param players: dict, representing players
    :param balls: list, representing balls
    :param game_time: int, game time
    :param score: float, player's score
    :param player: dict, representing the current player
    :param background: pygame.Surface, the background surface with the grid
    """
    WIN.fill((255, 255, 255))  # Fill screen white to clear old frames

    # Create a surface for the viewport
    viewport = pygame.Surface((VIEWPORT_W, VIEWPORT_H))

    # Draw the background with the grid onto the viewport
    viewport.blit(background, (0, 0), (player["x"] - VIEWPORT_W // 2, player["y"] - VIEWPORT_H // 2, VIEWPORT_W, VIEWPORT_H))

    # Calculate the offset for centering the player in the viewport
    offset_x = VIEWPORT_W // 2 - player["x"]
    offset_y = VIEWPORT_H // 2 - player["y"]

    # Draw all the orbs/balls on the viewport
    for ball in balls:
        pygame.draw.circle(viewport, ball[2], (ball[0] + offset_x, ball[1] + offset_y), BALL_RADIUS)

    # Draw each player in the list on the viewport
    for player_id in sorted(players, key=lambda x: players[x]["score"]):
        p = players[player_id]
        pygame.draw.circle(viewport, p["color"], (p["x"] + offset_x, p["y"] + offset_y), PLAYER_RADIUS + round(p["score"]))
        # Render and draw name for each player
        text = NAME_FONT.render(p["name"], 1, (0, 0, 0))
        viewport.blit(text, (p["x"] + offset_x - text.get_width() / 2, p["y"] + offset_y - text.get_height() / 2))

    # Draw the scaled viewport onto the main window
    scaled_viewport = pygame.transform.scale(viewport, (W, H))
    WIN.blit(scaled_viewport, (0, 0))

    # Draw scoreboard on the main window
    sort_players = list(reversed(sorted(players, key=lambda x: players[x]["score"])))
    title = TIME_FONT.render("Scoreboard", 1, (255, 0, 0))
    start_y = 40
    x = W - title.get_width() - 10
    WIN.blit(title, (x, 5))

    ran = min(len(players), 3)
    for count, i in enumerate(sort_players[:ran]):
        text = SCORE_FONT.render(str(count + 1) + ". " + str(players[i]["name"]) + " " + str(players[i]["score"]), 1, (255, 0, 0))
        WIN.blit(text, (x, start_y + count * 20))

    # Draw time on the main window
    text = TIME_FONT.render("Time: " + convert_time(game_time), 1, (255, 0, 0))
    WIN.blit(text, (10, 10))
    # Draw score on the main window
    text = TIME_FONT.render("Score: " + str(round(score)), 1, (255, 0, 0))
    WIN.blit(text, (10, 15 + text.get_height()))

def main(name):
    """
    Function for running the game, includes the main loop of the game.

    :param name: str, player's name
    """
    global players

    # Start by connecting to the network
    server = Network()
    current_id = server.connect(name)
    if current_id is None:
        print("Failed to connect to the server.")
        return
    
    balls, players, game_time = server.send("get")

    # Setup the clock, limit to 70fps
    clock = pygame.time.Clock()
    
    # Create background surface
    background = pygame.Surface((W, H))
    draw_grid(background, W, H, 50)

    title = TIME_FONT.render("Scoreboard", 1, (255, 0, 0))
    start_y = 40
    x = W - title.get_width() - 10
    WIN.blit(title, (x, 5))
    
    run = True
    while run:
        clock.tick(70)  # 70 fps max
        player = players[current_id]
        vel = START_VEL - round(player["score"] / 50)
        if vel <= 1:
            vel = 1
        mouse_x, mouse_y = pygame.mouse.get_pos()
        data = ""
        dX = mouse_x - (W / 2)
        if dX >= PLAYER_RADIUS:
            if player["x"] + vel + (PLAYER_RADIUS + player["score"]) <= W:
                player["x"] += vel
        elif dX <= -PLAYER_RADIUS:
            if player["x"] - vel - (PLAYER_RADIUS) - player["score"] >= 0:
                player["x"] -= vel

        dY = mouse_y - (H / 2)
        if dY >= PLAYER_RADIUS:
            if player["y"] + vel + (PLAYER_RADIUS + player["score"]) <= H:
                player["y"] += vel
        elif dY <= -PLAYER_RADIUS:
            if player["y"] - vel - (PLAYER_RADIUS) - player["score"] >= 0:
                player["y"] -= vel

        data = "move " + str(player["x"]) + " " + str(player["y"])

        # Send data to server and receive back all players information
        balls, players, game_time = server.send(data)

        for event in pygame.event.get():
            # If user hits red x button close window
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # If user hits a escape key close program
                if event.key == pygame.K_ESCAPE:
                    run = False
        
        # Redraw window then update the frame
        redraw_window(players, balls, game_time, player["score"], player, background)
        pygame.display.update()

    server.disconnect()
    pygame.quit()
    quit()

# Get user's name
while True:
    name = input("Please enter your name: ")
    if 0 < len(name) < 20:
        break
    else:
        print("Error, this name is not allowed (must be between 1 and 19 characters [inclusive])")

# Make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)

# Setup pygame window
WIN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Agar.io")

# Start game
main(name)
