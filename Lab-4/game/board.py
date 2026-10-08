import math
import random
import pygame

GRID_SIZE = 8
TILE_SIZE = 60
POINTS_PER_GEM = 10
GEM_COLORS = [
    (220, 50, 50),   # Red
    (50, 200, 50),   # Green
    (50, 100, 240),  # Blue
    (240, 200, 40),  # Yellow
    (180, 50, 220),  # Purple
    (240, 130, 40),  # Orange
]


class Gem:
   
    def __init__(self, color, target_row, col):
        self.color = color
        self.bomb = None  # None, "row" (clears its row) or "col" (clears its column)
        self.target_row = target_row
        self.col = col
        self.current_y = (target_row - 2) * TILE_SIZE
        self.target_y = target_row * TILE_SIZE
        self.fall_speed = 12.0

    def update(self):
        if self.current_y < self.target_y:
            self.current_y += self.fall_speed
            if self.current_y > self.target_y:
                self.current_y = self.target_y

    def is_animating(self):
        return self.current_y < self.target_y


class Board:

    def __init__(self, offset_x, offset_y, target_score=500, max_moves=20):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.target_score = target_score
        self.max_moves = max_moves
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.score = 0
        self.moves_remaining = max_moves
        self.last_combo = 0
        self.hint = None  # ((row, col), (row, col)) of a swap that would match
        self.reset()

    def reset(self):
        self.score = 0
        self.moves_remaining = self.max_moves
        self.selected = None
        self.last_combo = 0
        self.hint = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = gem.target_y  
                self.grid[r][c] = gem

        self.resolve_matches(spawn_bombs=False)

    def is_animating(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] and self.grid[r][c].is_animating():
                    return True
        return False

    def swap_gems(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2

        g1, g2 = self.grid[r1][c1], self.grid[r2][c2]
        self.grid[r1][c1], self.grid[r2][c2] = g2, g1

        if self.grid[r1][c1]:
            self.grid[r1][c1].target_row = r1
            self.grid[r1][c1].target_y = r1 * TILE_SIZE
            self.grid[r1][c1].current_y = r1 * TILE_SIZE

        if self.grid[r2][c2]:
            self.grid[r2][c2].target_row = r2
            self.grid[r2][c2].target_y = r2 * TILE_SIZE
            self.grid[r2][c2].current_y = r2 * TILE_SIZE

    def is_adjacent(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def find_match_groups(self):
        """Return every run of 3+ same-colour gems as (cells, axis).

        axis is "row" for a horizontal run and "col" for a vertical run.
        """
        groups = []
        for axis in ("row", "col"):
            for line in range(GRID_SIZE):
                if axis == "row":
                    cells = [(line, k) for k in range(GRID_SIZE)]
                else:
                    cells = [(k, line) for k in range(GRID_SIZE)]
                start = 0
                while start < GRID_SIZE:
                    first = self.grid[cells[start][0]][cells[start][1]]
                    end = start + 1
                    if first:
                        while end < GRID_SIZE:
                            nxt = self.grid[cells[end][0]][cells[end][1]]
                            if not nxt or nxt.color != first.color:
                                break
                            end += 1
                        if end - start >= 3:
                            groups.append((cells[start:end], axis))
                    start = end
        return groups

    def find_matches(self):
        """Set of all (row, col) cells that are part of a 3+ run."""
        matched = set()
        for cells, _ in self.find_match_groups():
            matched.update(cells)
        return matched

    def find_hint(self):
        """Return a pair of adjacent cells whose swap would create a match, or None."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                for dr, dc in ((0, 1), (1, 0)):
                    r2, c2 = r + dr, c + dc
                    if r2 >= GRID_SIZE or c2 >= GRID_SIZE:
                        continue
                    g = self.grid
                    g[r][c], g[r2][c2] = g[r2][c2], g[r][c]
                    found = bool(self.find_matches())
                    g[r][c], g[r2][c2] = g[r2][c2], g[r][c]
                    if found:
                        return (r, c), (r2, c2)
        return None

    def find_bomb_spawns(self, groups, preferred=()):
        """Pick the cell that becomes a Bomb Gem for each run of 4 or more.

        Returns {(row, col): axis}. A horizontal run makes a "row" bomb and a
        vertical run makes a "col" bomb. The bomb appears on the gem the player
        just moved when it is part of the run, otherwise in the middle of it.
        """
        spawns = {}
        for cells, axis in groups:
            if len(cells) < 4:
                continue
            candidates = [p for p in cells if not self.grid[p[0]][p[1]].bomb and p not in spawns]
            if not candidates:
                continue
            chosen = next((p for p in preferred if p in candidates), None)
            if chosen is None:
                chosen = candidates[len(candidates) // 2]
            spawns[chosen] = axis
        return spawns

    def expand_with_blasts(self, cells):
        """Add the row/column cleared by every bomb in `cells` (chains included)."""
        cleared = set(cells)
        queue = [p for p in cleared if self.grid[p[0]][p[1]].bomb]
        detonated = set()
        while queue:
            r, c = queue.pop()
            if (r, c) in detonated:
                continue
            detonated.add((r, c))
            if self.grid[r][c].bomb == "row":
                blast = [(r, k) for k in range(GRID_SIZE)]
            else:
                blast = [(k, c) for k in range(GRID_SIZE)]
            for br, bc in blast:
                gem = self.grid[br][bc]
                if gem is None:
                    continue
                cleared.add((br, bc))
                if gem.bomb and (br, bc) not in detonated:
                    queue.append((br, bc))
        return cleared

    def drop_and_refill(self):
        for c in range(GRID_SIZE):
            empty_slots = 0
            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c] is None:
                    empty_slots += 1
                elif empty_slots > 0:
                    gem = self.grid[r][c]
                    gem.target_row = r + empty_slots
                    gem.target_y = (r + empty_slots) * TILE_SIZE
                    self.grid[r + empty_slots][c] = gem
                    self.grid[r][c] = None

            for r in range(empty_slots):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = -((empty_slots - r) * TILE_SIZE)
                self.grid[r][c] = gem

    def resolve_matches(self, preferred=(), spawn_bombs=True):
        """Clear matches until the board settles and return the points earned.

        Each successive drop reaction (cascade) raises the combo chain by one and
        multiplies its points: 1x for the initial match, 2x for the first
        cascade, 3x for the next, and so on.
        """
        total_points = 0
        combo = 0
        while True:
            groups = self.find_match_groups()
            if not groups:
                break
            combo += 1
            matches = set()
            for cells, _ in groups:
                matches.update(cells)
            spawns = {}
            if spawn_bombs:
                spawns = self.find_bomb_spawns(groups, preferred if combo == 1 else ())
            cleared = self.expand_with_blasts(matches) - set(spawns)
            total_points += len(cleared) * POINTS_PER_GEM * combo
            for r, c in cleared:
                self.grid[r][c] = None
            for (r, c), axis in spawns.items():
                self.grid[r][c].bomb = axis
            self.drop_and_refill()
        self.last_combo = combo
        return total_points

    def process_swap(self, pos1, pos2):
        if not self.is_adjacent(pos1, pos2) or self.is_game_over() or self.is_animating():
            return False

        self.swap_gems(pos1, pos2)
        matches = self.find_matches()

        if not matches:
            self.swap_gems(pos1, pos2)
            return False

        self.moves_remaining -= 1
        self.score += self.resolve_matches(preferred=(pos1, pos2))
        return True

    def is_game_over(self):
        return self.score >= self.target_score or self.moves_remaining <= 0

    def check_result(self):
        if self.score >= self.target_score:
            return "WIN"
        if self.moves_remaining <= 0:
            return "LOSS"
        return None

    def update(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]:
                    self.grid[r][c].update()

    def draw_hint_pulse(self, surface, r, c):
        """Soft pulsing gold outline plus shimmer over a hinted gem."""
        pulse = (math.sin(pygame.time.get_ticks() / 1000 * 5) + 1) / 2
        x = self.offset_x + c * TILE_SIZE
        y = self.offset_y + r * TILE_SIZE
        rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
        shimmer = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shimmer, (255, 255, 255, int(30 + 70 * pulse)), shimmer.get_rect(), border_radius=10)
        surface.blit(shimmer, rect.topleft)
        pygame.draw.rect(
            surface,
            (255, 230, 90),
            rect.inflate(int(2 + 4 * pulse), int(2 + 4 * pulse)),
            width=int(2 + 2 * pulse),
            border_radius=12,
        )

    def draw_bomb_overlay(self, surface, rect, axis):
        """Pulsing glow plus arrows showing which line the Bomb Gem will clear."""
        pulse = (math.sin(pygame.time.get_ticks() / 1000 * 6) + 1) / 2
        glow = pygame.Surface((rect.w + 16, rect.h + 16), pygame.SRCALPHA)
        for i, grow in enumerate((8, 5, 2)):
            ring = glow.get_rect().inflate(-(8 - grow) * 2, -(8 - grow) * 2)
            alpha = int((60 + 120 * pulse) / (i + 1))
            pygame.draw.rect(glow, (255, 240, 120, alpha), ring, width=3, border_radius=14)
        surface.blit(glow, (rect.x - 8, rect.y - 8))

        cx, cy = rect.center
        if axis == "row":
            arrows = [
                [(cx - 24, cy), (cx - 12, cy - 9), (cx - 12, cy + 9)],
                [(cx + 24, cy), (cx + 12, cy - 9), (cx + 12, cy + 9)],
            ]
        else:
            arrows = [
                [(cx, cy - 24), (cx - 9, cy - 12), (cx + 9, cy - 12)],
                [(cx, cy + 24), (cx - 9, cy + 12), (cx + 9, cy + 12)],
            ]
        for poly in arrows:
            pygame.draw.polygon(surface, (255, 255, 255), poly)
            pygame.draw.polygon(surface, (40, 40, 40), poly, width=1)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 8)
        pygame.draw.circle(surface, (40, 40, 40), (cx, cy), 8, width=2)

    def render(self, surface):
        board_rect = pygame.Rect(
            self.offset_x, self.offset_y, GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
        )
        pygame.draw.rect(surface, (20, 22, 28), board_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 65, 75), board_rect, width=3, border_radius=8)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = self.grid[r][c]
                if gem:
                    x = self.offset_x + c * TILE_SIZE
                    y = self.offset_y + gem.current_y
                    tile_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)

                    pygame.draw.rect(surface, gem.color, tile_rect, border_radius=10)
                    pygame.draw.rect(
                        surface, (255, 255, 255), tile_rect, width=1, border_radius=10
                    )
                    if gem.bomb:
                        self.draw_bomb_overlay(surface, tile_rect, gem.bomb)

                if self.hint and (r, c) in self.hint and gem:
                    self.draw_hint_pulse(surface, r, c)

                if self.selected == (r, c):
                    sel_x = self.offset_x + c * TILE_SIZE
                    sel_y = self.offset_y + r * TILE_SIZE
                    sel_rect = pygame.Rect(sel_x + 2, sel_y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(
                        surface, (255, 255, 255), sel_rect, width=4, border_radius=10
                    )
