import pygame
from game.game_engine import GameEngine

# Initialize pygame/Start application
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Marble Tilt Maze - Pygame Version")

# Clock
clock = pygame.time.Clock()
FPS = 60


def main():
    difficulty = "Medium"

    while True:
        engine = GameEngine(WIDTH, HEIGHT, difficulty)
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                engine.handle_event(event)

            engine.handle_input()
            engine.update()
            engine.render(SCREEN)

            pygame.display.flip()
            clock.tick(FPS)

            # ── Task 3: replay / quit after game over ──────────────
            if engine.wants_quit:
                pygame.quit()
                return
            if engine.wants_replay:
                difficulty = engine.replay_difficulty
                break  # restart the outer while-loop with the new engine

    pygame.quit()


if __name__ == "__main__":
    main()
