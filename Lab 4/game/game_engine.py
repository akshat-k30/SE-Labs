import pygame
import math
import os
from .marble import Marble
from .wall import Wall

# Game Engine

WHITE = (255, 255, 255)
DARK = (40, 40, 50)
WALL_COLOR = (90, 90, 110)
GOAL_COLOR = (60, 200, 120)
OVERLAY_BG = (20, 20, 30, 200)
TITLE_COLOR = (255, 220, 80)
TEXT_COLOR = (220, 220, 230)
HIGHLIGHT_COLOR = (100, 200, 255)
WIN_COLOR = (80, 220, 120)
LOSE_COLOR = (220, 80, 80)
BUTTON_COLOR = (70, 70, 90)
BUTTON_HOVER = (100, 100, 130)
BUTTON_TEXT = (240, 240, 255)

# ── Difficulty presets ──────────────────────────────────────────────
DIFFICULTY = {
    "Easy":   {"tilt_strength": 0.4,  "friction": 0.03, "max_speed": 7,  "time_limit_ms": 60000},
    "Medium": {"tilt_strength": 0.6,  "friction": 0.02, "max_speed": 9,  "time_limit_ms": 45000},
    "Hard":   {"tilt_strength": 0.85, "friction": 0.01, "max_speed": 12, "time_limit_ms": 30000},
}


class GameEngine:
    def __init__(self, width, height, difficulty="Medium"):
        self.width = width
        self.height = height

        self.marble = Marble(50, 50)
        preset = DIFFICULTY[difficulty]
        self.tilt_strength = preset["tilt_strength"]
        self.friction = preset["friction"]
        self.max_speed = preset["max_speed"]
        self.time_limit_ms = preset["time_limit_ms"]
        self.difficulty = difficulty

        self.walls = self._build_maze()
        self.goal_x, self.goal_y, self.goal_radius = width - 60, height - 60, 22

        self.start_ticks = pygame.time.get_ticks()

        self.font = pygame.font.SysFont("Arial", 26)
        self.font_large = pygame.font.SysFont("Arial", 44, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.game_over = False
        self.result = None  # "solved" or "timeout"
        self.finish_time_ms = None

        # ── Task 4: sound effects ──────────────────────────────────
        self._sounds_loaded = False
        self._load_sounds()
        self._last_bounce_time = 0  # cooldown to avoid rapid-fire bounce sound

        # ── Task 3: replay / menu state ────────────────────────────
        self.show_end_screen = False
        self.wants_replay = False       # set to True when user picks a difficulty
        self.replay_difficulty = None
        self.wants_quit = False

        # Button rects (computed in _render_end_screen)
        self._buttons = []  # list of (pygame.Rect, label, action)

    # ── Sound loading ──────────────────────────────────────────────
    def _load_sounds(self):
        sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
        try:
            self.snd_bounce  = pygame.mixer.Sound(os.path.join(sounds_dir, "bounce.wav"))
            self.snd_goal    = pygame.mixer.Sound(os.path.join(sounds_dir, "goal.wav"))
            self.snd_timeout = pygame.mixer.Sound(os.path.join(sounds_dir, "timeout.wav"))
            self._sounds_loaded = True
        except Exception:
            # Sounds are optional; game still works without them
            self.snd_bounce = self.snd_goal = self.snd_timeout = None

    def _play(self, sound, cooldown_ms=0):
        if self._sounds_loaded and sound is not None:
            now = pygame.time.get_ticks()
            if cooldown_ms > 0:
                if now - self._last_bounce_time < cooldown_ms:
                    return
                self._last_bounce_time = now
            sound.play()

    # ── Maze construction ──────────────────────────────────────────
    def _build_maze(self):
        walls = []
        t = 16  # wall thickness

        # outer boundary
        walls.append(Wall(0, 0, self.width, t))
        walls.append(Wall(0, self.height - t, self.width, t))
        walls.append(Wall(0, 0, t, self.height))
        walls.append(Wall(self.width - t, 0, t, self.height))

        # a few internal walls forming a simple winding path
        walls.append(Wall(0, 140, self.width - 140, t))
        walls.append(Wall(140, 260, self.width - 140, t))
        walls.append(Wall(0, 380, self.width - 140, t))

        return walls

    # ── Event handling ─────────────────────────────────────────────
    def handle_event(self, event):
        if self.show_end_screen and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for rect, label, action in self._buttons:
                if rect.collidepoint(mx, my):
                    action()
                    return
        if self.show_end_screen and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._do_replay(self.difficulty)
            elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                self._do_quit()

    def handle_input(self):
        if self.game_over:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.width // 2
        dy = mouse_y - self.height // 2
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        ax = (dx / dist) * self.tilt_strength
        ay = (dy / dist) * self.tilt_strength
        self.marble.vx += ax
        self.marble.vy += ay

    # ── Physics update ─────────────────────────────────────────────
    def update(self):
        if self.game_over:
            return

        elapsed = pygame.time.get_ticks() - self.start_ticks
        if elapsed >= self.time_limit_ms:
            self.game_over = True
            self.result = "timeout"
            self.show_end_screen = True
            self._play(self.snd_timeout)       # Task 4
            return

        self.marble.vx *= (1 - self.friction)
        self.marble.vy *= (1 - self.friction)

        speed = (self.marble.vx ** 2 + self.marble.vy ** 2) ** 0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.marble.vx *= scale
            self.marble.vy *= scale

        self.marble.x += self.marble.vx
        self.marble.y += self.marble.vy

        self._resolve_wall_collisions()

        gx = self.goal_x - self.marble.x
        gy = self.goal_y - self.marble.y
        if (gx ** 2 + gy ** 2) ** 0.5 <= self.goal_radius:
            self.game_over = True
            self.result = "solved"
            self.finish_time_ms = elapsed
            self.show_end_screen = True
            self._play(self.snd_goal)          # Task 4

    # ── Task 1: Proper circle-vs-rectangle collision ───────────────
    def _resolve_wall_collisions(self):
        """True circle-vs-axis-aligned-rectangle collision detection.

        Instead of using the marble's bounding-box (which causes phantom
        bounces near wall corners), we find the closest point on each
        wall rectangle to the marble centre and compare the real
        distance to the marble's radius.
        """
        for wall in self.walls:
            wall_rect = wall.rect()

            # Closest point on the rectangle to the marble centre
            closest_x = max(wall_rect.left, min(self.marble.x, wall_rect.right))
            closest_y = max(wall_rect.top, min(self.marble.y, wall_rect.bottom))

            dx = self.marble.x - closest_x
            dy = self.marble.y - closest_y
            dist_sq = dx * dx + dy * dy

            if dist_sq < self.marble.radius ** 2:
                # There is a real collision
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.001
                # Normal vector pointing from wall to marble
                nx = dx / dist
                ny = dy / dist

                # Push marble out so it just touches
                penetration = self.marble.radius - dist
                self.marble.x += nx * penetration
                self.marble.y += ny * penetration

                # Reflect velocity along the normal, with damping
                dot = self.marble.vx * nx + self.marble.vy * ny
                if dot < 0:  # only bounce if moving toward the wall
                    self.marble.vx -= 2 * dot * nx
                    self.marble.vy -= 2 * dot * ny
                    # Dampen to simulate energy loss
                    self.marble.vx *= 0.5
                    self.marble.vy *= 0.5
                    self._play(self.snd_bounce, cooldown_ms=150)   # Task 4

    # ── Rendering ──────────────────────────────────────────────────
    def render(self, screen):
        screen.fill(DARK)

        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall.rect())

        pygame.draw.circle(screen, GOAL_COLOR, (self.goal_x, self.goal_y), self.goal_radius)
        pygame.draw.circle(screen, WHITE, (int(self.marble.x), int(self.marble.y)), self.marble.radius)

        elapsed = pygame.time.get_ticks() - self.start_ticks
        seconds_left = max(0, (self.time_limit_ms - elapsed) // 1000)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (10, 10))

        # Difficulty label in top-right corner
        diff_text = self.font_small.render(f"[{self.difficulty}]", True, HIGHLIGHT_COLOR)
        screen.blit(diff_text, (self.width - diff_text.get_width() - 12, 12))

        # ── Task 2 & 3: end screen overlay ─────────────────────────
        if self.show_end_screen:
            self._render_end_screen(screen)

    # ── Task 2: Game-over overlay  ─────────────────────────────────
    # ── Task 3: Replay / difficulty buttons ────────────────────────
    def _render_end_screen(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        screen.blit(overlay, (0, 0))

        self._buttons.clear()

        cx = self.width // 2
        y = 60

        # Title
        if self.result == "solved":
            title = self.font_large.render("🏆  You Win!", True, WIN_COLOR)
            sub = self.font.render(
                f"Finished in {self.finish_time_ms / 1000:.1f}s", True, TEXT_COLOR
            )
        else:
            title = self.font_large.render("⏰  Time's Up!", True, LOSE_COLOR)
            sub = self.font.render("Better luck next time!", True, TEXT_COLOR)

        screen.blit(title, (cx - title.get_width() // 2, y))
        y += title.get_height() + 10
        screen.blit(sub, (cx - sub.get_width() // 2, y))
        y += sub.get_height() + 40

        # Difficulty buttons
        prompt = self.font_small.render("Play Again — choose difficulty:", True, TITLE_COLOR)
        screen.blit(prompt, (cx - prompt.get_width() // 2, y))
        y += prompt.get_height() + 15

        btn_w, btn_h = 130, 40
        gap = 20
        total_w = 3 * btn_w + 2 * gap
        start_x = cx - total_w // 2

        mouse_pos = pygame.mouse.get_pos()

        for i, diff_name in enumerate(("Easy", "Medium", "Hard")):
            bx = start_x + i * (btn_w + gap)
            rect = pygame.Rect(bx, y, btn_w, btn_h)
            hovered = rect.collidepoint(mouse_pos)
            color = BUTTON_HOVER if hovered else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, width=2, border_radius=8)
            label = self.font_small.render(diff_name, True, BUTTON_TEXT)
            screen.blit(label, (rect.centerx - label.get_width() // 2,
                                rect.centery - label.get_height() // 2))
            self._buttons.append((rect, diff_name, lambda d=diff_name: self._do_replay(d)))

        y += btn_h + 20

        # Quit button
        quit_rect = pygame.Rect(cx - 65, y, 130, 40)
        hovered = quit_rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER if hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, quit_rect, border_radius=8)
        pygame.draw.rect(screen, LOSE_COLOR, quit_rect, width=2, border_radius=8)
        qlabel = self.font_small.render("Quit", True, BUTTON_TEXT)
        screen.blit(qlabel, (quit_rect.centerx - qlabel.get_width() // 2,
                             quit_rect.centery - qlabel.get_height() // 2))
        self._buttons.append((quit_rect, "Quit", self._do_quit))

        y += btn_h + 18
        hint = self.font_small.render("R = replay  •  Q = quit", True, (130, 130, 150))
        screen.blit(hint, (cx - hint.get_width() // 2, y))

    # ── Replay helpers ─────────────────────────────────────────────
    def _do_replay(self, difficulty):
        self.wants_replay = True
        self.replay_difficulty = difficulty

    def _do_quit(self):
        self.wants_quit = True
