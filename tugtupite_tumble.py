#!/usr/bin/env python3
"""Tugtupite Tumble — full-colour Python 3 boulder-run arcade for ElbowOS.

Steer a crimson tugtupite boulder down an ice stair. Scoop pearl shards.
Black spikes shatter the streak. Not a lighthouse, not a ROM.
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/TUGTUPITE_TUMBLE_ElbowOS.mp4")
TITLE, HANDLE = "TUGTUPITE TUMBLE", "x.com/ElbowOS"
NAVY = (8, 14, 36)
ICE = (168, 214, 236)
CRIMSON = (214, 42, 78)
PEARL = (255, 236, 220)
SPIKE = (18, 16, 28)
GOLD = (255, 196, 92)


def clamp(v, a, b):
    return a if v < a else b if v > b else v


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.canvas = pygame.Surface((W, H))
        self.font = pygame.font.Font(None, 78)
        self.mid = pygame.font.Font(None, 54)
        self.small = pygame.font.Font(None, 40)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.lives = 3
        self.x = 540.0
        self.vx = 0.0
        self.spin = 0.0
        self.flash = 0
        self.scroll = 0.0
        self.steps = []
        self.shards = []
        self.spikes = []
        self.pops = []
        y = 200
        left = True
        while y < 4200:
            width = random.randint(420, 640)
            x = 80 if left else W - 80 - width
            self.steps.append([x, y, width])
            if random.random() < 0.7:
                self.shards.append([x + width * 0.5, y - 28, False])
            if random.random() < 0.45:
                self.spikes.append([x + width * (0.25 if left else 0.75), y - 8])
            y += random.randint(168, 230)
            left = not left
        self.snow = [[random.randrange(W), random.randrange(H), random.uniform(1, 3)] for _ in range(80)]

    def step(self, keys):
        self.t += 1
        self.scroll += 6.2
        self.spin += 0.18
        if PLAY:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vx -= 1.4
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vx += 1.4
        else:
            by = 430 + self.scroll
            nxt = None
            for s in self.steps:
                if s[1] > by - 40:
                    nxt = s
                    break
            if nxt:
                target = nxt[0] + nxt[2] * 0.55
                self.vx += clamp(target - self.x, -2.2, 2.2)
            else:
                self.vx += math.sin(self.t * 0.07) * 0.4
        self.vx *= 0.86
        self.x = clamp(self.x + self.vx, 70, W - 70)
        by = 430
        world_y = by + self.scroll
        landed = False
        for s in self.steps:
            if abs(s[1] - world_y) < 36 and s[0] - 20 <= self.x <= s[0] + s[2] + 20:
                landed = True
                self.score += 1
                break
        if not landed and self.t % 8 == 0:
            self.score = max(0, self.score - 1)
            self.flash = 4
        for sh in self.shards:
            if not sh[2] and abs(sh[1] - world_y) < 40 and abs(sh[0] - self.x) < 48:
                sh[2] = True
                self.score += 50
                self.pops.append([self.x, by, 6])
        for sp in list(self.spikes):
            if abs(sp[1] - world_y) < 28 and abs(sp[0] - self.x) < 36:
                self.lives = max(0, self.lives - 1)
                self.flash = 10
                self.pops.append([self.x, by, 18])
                self.spikes.remove(sp)
                self.x += 80 if self.x < W / 2 else -80
        if self.lives == 0:
            self.lives = 3
        self.flash = max(0, self.flash - 1)
        self.pops = [[p[0], p[1], p[2] + 4] for p in self.pops if p[2] < 80]
        for s in self.snow:
            s[1] += s[2] + 4
            if s[1] > H:
                s[1] = 0
                s[0] = random.randrange(W)

    def draw_boulder(self, x, y):
        pts = []
        for i in range(6):
            a = self.spin + i * math.pi / 3
            pts.append((x + math.cos(a) * 46, y + math.sin(a) * 46))
        pygame.draw.polygon(self.canvas, CRIMSON, pts)
        pygame.draw.polygon(self.canvas, (255, 140, 160), pts, 5)
        pygame.draw.circle(self.canvas, GOLD, (int(x), int(y)), 10)

    def draw(self):
        self.canvas.fill(NAVY)
        for i in range(6):
            pygame.draw.polygon(self.canvas, (16, 28, 58), [
                (i * 200, 0), (i * 200 + 80, 0), (i * 200 + 40, H)
            ])
        for s in self.snow:
            pygame.draw.circle(self.canvas, (200, 220, 240), (int(s[0]), int(s[1])), 2)
        for step in self.steps:
            sy = step[1] - self.scroll
            if -80 < sy < H + 40:
                pygame.draw.rect(self.canvas, ICE, (step[0], sy, step[2], 28), border_radius=8)
                pygame.draw.rect(self.canvas, (90, 150, 190), (step[0], sy + 22, step[2], 10), border_radius=4)
        for sh in self.shards:
            if sh[2]:
                continue
            sy = sh[1] - self.scroll
            if -40 < sy < H:
                pygame.draw.polygon(self.canvas, PEARL, [
                    (sh[0], sy - 22), (sh[0] + 14, sy), (sh[0], sy + 22), (sh[0] - 14, sy)
                ])
        for sp in self.spikes:
            sy = sp[1] - self.scroll
            if -40 < sy < H:
                pygame.draw.polygon(self.canvas, SPIKE, [
                    (sp[0] - 16, sy + 8), (sp[0], sy - 36), (sp[0] + 16, sy + 8)
                ])
        self.draw_boulder(self.x, 430)
        for p in self.pops:
            pygame.draw.circle(self.canvas, GOLD, (int(p[0]), int(p[1])), p[2], 3)
        banner = pygame.Surface((W, 200), pygame.SRCALPHA)
        banner.fill((6, 10, 28, 180))
        self.canvas.blit(banner, (0, 0))
        title = self.font.render(TITLE, True, CRIMSON)
        self.canvas.blit(title, title.get_rect(center=(W // 2, 74)))
        score = self.mid.render(f"SCORE  {self.score}", True, PEARL)
        self.canvas.blit(score, score.get_rect(center=(W // 2, 146)))
        handle = self.small.render(HANDLE, True, ICE)
        self.canvas.blit(handle, handle.get_rect(center=(W // 2, 1860)))
        hearts = self.small.render("LIVES  " + "●" * self.lives + "○" * (3 - self.lives), True, GOLD)
        self.canvas.blit(hearts, (48, 188))
        if self.flash:
            wash = pygame.Surface((W, H), pygame.SRCALPHA)
            wash.fill((255, 60, 80, 60))
            self.canvas.blit(wash, (0, 0))
        self.screen.blit(self.canvas, (0, 0))
        pygame.display.flip()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", "-an", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.step(None)
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.canvas, "RGB"))
        finally:
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "replace")
            code = proc.wait()
        if code != 0 or not os.path.exists(OUT) or os.path.getsize(OUT) < 10000:
            raise SystemExit(f"ffmpeg failed ({code})\n{err[-1500:]}")
        mirror = "/home/workdir/artifacts/" + os.path.basename(OUT)
        if os.path.abspath(mirror) != os.path.abspath(OUT):
            os.makedirs("/home/workdir/artifacts", exist_ok=True)
            with open(OUT, "rb") as src, open(mirror, "wb") as dst:
                dst.write(src.read())
        print(OUT, os.path.getsize(OUT))

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset()
            self.step(keys)
            self.draw()
            clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    if PLAY and not RECORD:
        game.play()
    else:
        game.record()
