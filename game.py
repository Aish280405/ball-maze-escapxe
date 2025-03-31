import pygame
import math
import sys
import time
import random
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Escape the Maze")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ring_colors = [WHITE, RED, GREEN, YELLOW, CYAN]
ball_radius = 9
ball_speed = 0.4  
num_rings = 5
ring_radius = 80
ring_center = (screen_width // 2, screen_height // 2)
ring_thickness = 10
ring_speeds = [0.5, -1, 0.75, -0.5, 1]
slit_angle = 45  
ring_segments = 12  
ring_explosions = [[] for _ in range(num_rings)]

def check_collision(ball_pos, angle, ring_radius, ring_index):
    x, y = ball_pos
    ring_center_x, ring_center_y = screen_width // 2, screen_height // 2
    
    dist_to_center = math.hypot(x - ring_center_x, y - ring_center_y)
    
    ring_inner_radius = ring_radius + ring_index * 40
    ring_outer_radius = ring_inner_radius + ring_thickness
    if not (ring_inner_radius - ball_radius <= dist_to_center <= ring_outer_radius + ball_radius):
        return False
    
    normalized_angle = angle % 360
    
    start_angle = angles[ring_index]
    end_angle = (start_angle + 360 - slit_angle) % 360
    
    if start_angle > end_angle:
        in_slit = not (end_angle < normalized_angle < start_angle)
    else:
        in_slit = normalized_angle < start_angle or normalized_angle > end_angle
    
    if in_slit:
        return False
    
    ring_x = ring_center_x + ring_inner_radius * math.cos(math.radians(normalized_angle))
    ring_y = ring_center_y + ring_inner_radius * math.sin(math.radians(normalized_angle))
    
    point_dist = math.hypot(x - ring_x, y - ring_y)
    return point_dist < ball_radius + ring_thickness / 2

def reset_game():
    global ball_x, ball_y, start_time, game_over, game_won, ring_passed, ring_explosions, angles, ball_dx, ball_dy, ball_moving
    ball_x, ball_y = screen_width // 2, screen_height // 2
    start_time = time.time()
    game_over = False
    game_won = False
    ring_passed = [False] * num_rings
    angles = [0] * num_rings
    ring_explosions = [[] for _ in range(num_rings)]
    ball_dx, ball_dy = 0, 0
    ball_moving = False

def create_explosion(ring_index, ring_color, ring_radius):
    segment_angle = 360 / ring_segments
    for j in range(ring_segments):
        angle = j * segment_angle
        speed = random.uniform(2, 4)
        ring_explosions[ring_index].append({
            'angle': angle,
            'speed': speed,
            'distance': ring_radius,
            'color': ring_color
        })

reset_game()
clock = pygame.time.Clock()

running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not ball_moving:
                ball_moving = True
                angle = random.uniform(0, 360)
                ball_dx = math.cos(math.radians(angle)) * (ball_speed)
                ball_dy = math.sin(math.radians(angle)) * (ball_speed)

        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            reset_game()

    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, RED)
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))
        restart_text = font.render("Press Space to Restart", True, WHITE)
        screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 50))
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_won:
        font = pygame.font.Font(None, 74)
        text = font.render("Hooray!", True, GREEN)
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - 50))
        
        elapsed_time = time.time() - start_time
        time_text = font.render(f"Time: {elapsed_time:.2f} seconds", True, WHITE)
        screen.blit(time_text, (screen_width // 2 - time_text.get_width() // 2, screen_height // 2 + 30))
        
        pygame.display.flip()
        pygame.time.delay(2000)
        reset_game()
        continue

    if ball_moving:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ball_dx = -ball_speed
        if keys[pygame.K_RIGHT]:
            ball_dx = ball_speed
        if keys[pygame.K_UP]:
            ball_dy = -ball_speed
        if keys[pygame.K_DOWN]:
            ball_dy = ball_speed

        ball_x += ball_dx
        ball_y += ball_dy

    for i in range(num_rings):
        if not ring_passed[i] and not ring_explosions[i]:
            angles[i] = (angles[i] + ring_speeds[i]) % 360

            start_angle = angles[i]
            end_angle = start_angle + 360 - slit_angle
            pygame.draw.arc(
                screen,
                ring_colors[i],
                (ring_center[0] - ring_radius - i * 40,
                 ring_center[1] - ring_radius - i * 40,
                 (ring_radius + i * 40) * 2,
                 (ring_radius + i * 40) * 2),
                math.radians(start_angle),
                math.radians(end_angle),
                ring_thickness
            )
            collision_angle = math.degrees(math.atan2(ball_y - ring_center[1], ball_x - ring_center[0]))
            if collision_angle < 0:
                collision_angle += 360

            if check_collision((ball_x, ball_y), collision_angle, ring_radius, i):
                game_over = True
                break

            if not game_over and math.hypot(ball_x - ring_center[0], ball_y - ring_center[1]) > ring_radius + i * 40 + ball_radius:
                ring_passed[i] = True
                create_explosion(i, ring_colors[i], ring_radius + i * 40)

        elif ring_explosions[i]:
            for segment in ring_explosions[i]:
                segment['distance'] += segment['speed']
                segment_x = ring_center[0] + segment['distance'] * math.cos(math.radians(segment['angle']))
                segment_y = ring_center[1] + segment['distance'] * math.sin(math.radians(segment['angle']))

                pygame.draw.line(
                    screen,
                    segment['color'],
                    (int(segment_x), int(segment_y)),
                    (int(segment_x + 5 * math.cos(math.radians(segment['angle']))),
                     int(segment_y + 5 * math.sin(math.radians(segment['angle'])))),
                    ring_thickness // 2
                )

    if not game_over and math.hypot(ball_x - ring_center[0], ball_y - ring_center[1]) > ring_radius + (num_rings - 1) * 40 + ball_radius:
        game_won = True
    pygame.draw.circle(screen, BLUE, (int(ball_x), int(ball_y)), ball_radius)

    elapsed_time = time.time() - start_time
    font = pygame.font.Font(None, 36)
    time_text = font.render(f"Time: {elapsed_time:.2f} seconds", True, WHITE)
    screen.blit(time_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()