import pygame
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Portal 2D with Sounds - A Grok Creation")
clock = pygame.time.Clock()

# Initialize sound mixer
pygame.mixer.init()

# Load sound effects (placeholders - replace with your own sound files)
try:
    shoot_sound = pygame.mixer.Sound("portal_shoot.wav")  # Sound for shooting portals
    teleport_sound = pygame.mixer.Sound("portal_teleport.wav")  # Sound for teleporting
except FileNotFoundError:
    print("Sound files not found. Please add 'portal_shoot.wav' and 'portal_teleport.wav' to your directory.")
    shoot_sound = None
    teleport_sound = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Player settings
player_pos = [100, 100]
player_angle = 0
player_speed = 5
FOV = math.pi / 3  # Field of view

# Map (1 = wall, 0 = empty, 2 = blue portal, 3 = orange portal)
MAP_SIZE = 10
CELL_SIZE = 64
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 2, 1],  # Blue portal at (8, 6)
    [1, 0, 1, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 3, 1]   # Orange portal at (8, 9)
]

# Initial portal positions
blue_portal = (8 * CELL_SIZE, 6 * CELL_SIZE)
orange_portal = (8 * CELL_SIZE, 9 * CELL_SIZE)

def cast_rays():
    """Simple raycasting to simulate 3D walls and portals"""
    rays = []
    for i in range(60):  # Number of rays
        ray_angle = player_angle - FOV / 2 + (i / 60) * FOV
        ray_x, ray_y = player_pos[0], player_pos[1]
        ray_dx = math.cos(ray_angle)
        ray_dy = math.sin(ray_angle)
        distance = 0
        hit_wall = False
        hit_type = 1  # Default to wall

        while not hit_wall and distance < 1000:
            distance += 5
            ray_x = player_pos[0] + ray_dx * distance
            ray_y = player_pos[1] + ray_dy * distance
            map_x, map_y = int(ray_x // CELL_SIZE), int(ray_y // CELL_SIZE)

            if map_x < 0 or map_x >= MAP_SIZE or map_y < 0 or map_y >= MAP_SIZE:
                hit_wall = True
            elif game_map[map_y][map_x] in [1, 2, 3]:  # Wall or portal
                hit_wall = True
                hit_type = game_map[map_y][map_x]  # Record what was hit

        # Calculate wall/portal height based on distance
        height = min(HEIGHT, HEIGHT * 50 / (distance + 0.1))
        rays.append((ray_angle, distance, height, hit_type))
    return rays

def draw_3d(rays):
    """Draw the pseudo-3D view with visible portals"""
    screen.fill(BLACK)
    for i, (angle, dist, height, hit_type) in enumerate(rays):
        if hit_type == 1:  # Wall
            color = GRAY if dist < 500 else BLACK
        elif hit_type == 2:  # Blue portal
            color = BLUE
        elif hit_type == 3:  # Orange portal
            color = ORANGE
        pygame.draw.rect(screen, color, (i * WIDTH // 60, HEIGHT // 2 - height // 2, WIDTH // 60 + 1, height))

def draw_minimap():
    """Draw a top-down view of the map"""
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            color = WHITE if game_map[y][x] == 1 else BLACK
            if game_map[y][x] == 2:
                color = BLUE  # Blue portal
            elif game_map[y][x] == 3:
                color = ORANGE  # Orange portal
            pygame.draw.rect(screen, color, (x * 10 + 600, y * 10 + 50, 10, 10))
    # Draw player on minimap
    pygame.draw.circle(screen, RED, (int(player_pos[0] / CELL_SIZE * 10 + 600), int(player_pos[1] / CELL_SIZE * 10 + 50)), 3)

def shoot_portal(portal_type):
    """Shoot a portal (2 for blue, 3 for orange) in the direction the player is facing"""
    ray_x, ray_y = player_pos[0], player_pos[1]
    ray_dx = math.cos(player_angle)
    ray_dy = math.sin(player_angle)
    distance = 0
    hit_wall = False

    while not hit_wall and distance < 1000:
        distance += 5
        ray_x = player_pos[0] + ray_dx * distance
        ray_y = player_pos[1] + ray_dy * distance
        map_x, map_y = int(ray_x // CELL_SIZE), int(ray_y // CELL_SIZE)

        if map_x < 0 or map_x >= MAP_SIZE or map_y < 0 or map_y >= MAP_SIZE:
            return  # Out of bounds, no portal placed
        elif game_map[map_y][map_x] == 1:  # Hit a wall
            # Clear previous portal of this type
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    if game_map[y][x] == portal_type:
                        game_map[y][x] = 1  # Revert to wall
            # Place new portal
            game_map[map_y][map_x] = portal_type
            if portal_type == 2:
                global blue_portal
                blue_portal = (map_x * CELL_SIZE, map_y * CELL_SIZE)
            elif portal_type == 3:
                global orange_portal
                orange_portal = (map_x * CELL_SIZE, map_y * CELL_SIZE)
            # Play shoot sound
            if shoot_sound:
                shoot_sound.play()
            hit_wall = True

def move_player():
    """Handle player movement and portal teleportation"""
    global player_pos, player_angle
    keys = pygame.key.get_pressed()
    new_x, new_y = player_pos[0], player_pos[1]

    if keys[pygame.K_w]:
        new_x += math.cos(player_angle) * player_speed
        new_y += math.sin(player_angle) * player_speed
    if keys[pygame.K_s]:
        new_x -= math.cos(player_angle) * player_speed
        new_y -= math.sin(player_angle) * player_speed
    if keys[pygame.K_a]:
        player_angle -= 0.05
    if keys[pygame.K_d]:
        player_angle += 0.05

    # Collision detection
    map_x, map_y = int(new_x // CELL_SIZE), int(new_y // CELL_SIZE)
    if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
        if game_map[map_y][map_x] == 0:  # Empty space
            player_pos = [new_x, new_y]
        elif game_map[map_y][map_x] == 2 and orange_portal:  # Blue portal
            player_pos = [orange_portal[0] + CELL_SIZE, orange_portal[1]]  # Teleport to orange
            if teleport_sound:
                teleport_sound.play()
        elif game_map[map_y][map_x] == 3 and blue_portal:  # Orange portal
            player_pos = [blue_portal[0] - CELL_SIZE, blue_portal[1]]  # Teleport to blue
            if teleport_sound:
                teleport_sound.play()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click for orange portal
                shoot_portal(3)
            elif event.button == 3:  # Right click for blue portal
                shoot_portal(2)

    move_player()
    rays = cast_rays()
    draw_3d(rays)
    draw_minimap()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()