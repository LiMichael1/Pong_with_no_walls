import random
import pygame
import sys
from pygame.locals import *
import time

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 1024

WINDOW_HEIGHT_EXTRA = 700

WINDOW_HEIGHT_DIFF = WINDOW_HEIGHT_EXTRA - WINDOW_HEIGHT

clock = pygame.time.Clock()

PADDLE_SPEED = 6

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 31)
RED = (255, 0, 0)

WIN_MESSAGE = 'OMG, YOU DID IT! GREAT GAME!'
LOSE_MESSAGE = 'WHAT A LOSER!'

pygame.init()

score_font = pygame.font.SysFont('Arial', 50)
winning_font = pygame.font.Font('Wingko.ttf', 70)
losing_font = pygame.font.SysFont('Arial', 120)

window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT_EXTRA), 0, 32)

winning_music = 'won.mp3'
losing_music = 'curb.mp3'
pygame.mixer.music.load('OOOOH.mp3')
bounce_sound = pygame.mixer.Sound('bounce.wav')


def game_won_sound(player_win):
    pygame.mixer.music.stop()
    if player_win:
        pygame.mixer.music.load('win_sound.mp3')
    else:
        pygame.mixer.music.load('lose_sound.mp3')
    pygame.mixer.music.play()
    time.sleep(2)
    pygame.mixer.music.stop()
    pygame.mixer.music.load('OOOOH.mp3')
    pygame.mixer.music.play(-1, 0.0)


def random_angle():
    while True:
        x, y = random.randint(-4, 4), random.randint(-4, 4)
        if x != 0 and y != 0:
            break
    direction = [x, y]

    return direction


class Paddle(pygame.sprite.Sprite):
    def __init__(self, side_paddle):
        pygame.sprite.Sprite.__init__(self)
        self.side_paddle = side_paddle
        if self.side_paddle:
            self.image = pygame.Surface([30, 100])
        else:
            self.image = pygame.Surface([100, 30])

        self.image.fill(GREEN)

        self.rect = self.image.get_rect()


class Paddles:
    def __init__(self, is_player):
        self.is_player = is_player
        self.speed = 6
        self.score = 0
        self.up, self.down, self.left, self.right = False, False, False, False
        self.group = [Paddle(side_paddle=True), Paddle(False), Paddle(False)]
        self.games_won = 0

        self.group[0].rect.centery = WINDOW_HEIGHT / 2
        self.group[1].rect.centery = WINDOW_HEIGHT_DIFF + 15
        self.group[2].rect.centery = window_surface.get_rect().bottom - 10

        if self.is_player:
            self.group[0].rect.centerx = window_surface.get_rect().left + 10
            self.group[1].rect.centerx = WINDOW_WIDTH / 4
            self.group[2].rect.centerx = WINDOW_WIDTH / 4  # AI
        else:
            self.group[0].rect.centerx = window_surface.get_rect().right - 10
            self.group[1].rect.centerx = (3 * WINDOW_WIDTH) / 4
            self.group[2].rect.centerx = (3 * WINDOW_WIDTH) / 4

    def move(self):
        if self.up and (self.group[0].rect.top > WINDOW_HEIGHT_DIFF):
            self.group[0].rect.y -= self.speed
        elif self.down and (self.group[0].rect.bottom < WINDOW_HEIGHT_EXTRA):
            self.group[0].rect.y += self.speed

        if self.is_player:
            if self.left and (self.group[1].rect.left > 0):
                self.group[1].rect.x -= self.speed
                self.group[2].rect.x -= self.speed
            elif self.right and (self.group[1].rect.right < WINDOW_WIDTH / 2):
                self.group[1].rect.x += self.speed
                self.group[2].rect.x += self.speed
        else:
            if self.left and (self.group[1].rect.left > WINDOW_WIDTH / 2):
                self.group[1].rect.x -= self.speed
                self.group[2].rect.x -= self.speed
            elif self.right and (self.group[1].rect.right < WINDOW_WIDTH):
                self.group[1].rect.x += self.speed
                self.group[2].rect.x += self.speed


class Ball:
    def __init__(self):
        self.image = pygame.image.load('ball.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = window_surface.get_rect().center
        self.direction = random_angle()
        # FASTER AFTER EVERY BOUNCE
        self.bounce_count = 0
        self.bounce_upgrade = 4
        # print('The angle is ' + str(self.direction))

    def move(self):
        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]

    def refresh(self):
        self.rect.center = window_surface.get_rect().center
        self.bounce_count = 0
        # new direction
        self.direction = random_angle()

        # print('The angle is ' + str(self.direction))

    def bounce(self, paddle, top_down):
        if paddle.rect.colliderect(self.rect):
            bounce_sound.play()
            self.bounce_count += 1
            if top_down:
                self.direction[1] = -(self.direction[1] + (self.bounce_count / self.bounce_upgrade)) \
                    if self.direction[1] > 0 else -(self.direction[1] - self.bounce_count / self.bounce_upgrade)
            else:
                self.direction[0] = -(self.direction[0] + (self.bounce_count / self.bounce_upgrade)) \
                    if self.direction[0] > 0 else -(self.direction[0] - (self.bounce_count / self.bounce_upgrade))

            self.move()
            return True

        return False

    def score(self, player, computer, player_colors, computer_colors):
        if self.rect.right > WINDOW_WIDTH or \
                (self.rect.top > WINDOW_HEIGHT_EXTRA and self.rect.centerx > WINDOW_WIDTH / 2) or \
                (self.rect.bottom < WINDOW_HEIGHT_DIFF and self.rect.centery > WINDOW_WIDTH / 2):
            player.score += 1
            if player.score >= 5:
                player.games_won += 1
                player.score = 0
                player_colors[player.games_won - 1] = RED
                game_won_sound(True)
        elif self.rect.left < 0 or \
                (self.rect.top > WINDOW_HEIGHT_EXTRA and self.rect.centerx < WINDOW_WIDTH / 2 + 1) or \
                (self.rect.bottom < WINDOW_HEIGHT_DIFF and self.rect.centery < WINDOW_WIDTH / 2 + 1):
            computer.score += 1
            if computer.score >= 5:
                computer.games_won += 1
                computer.score = 0
                computer_colors[computer.games_won - 1] = RED
                game_won_sound(False)

    def __str__(self):
        return f'The position is ({self.rect.x}, {self.rect.y})'


class Player(Paddles):
    def __init__(self):
        Paddles.__init__(self, True)

    def button_mash(self, event):
        if event.type == KEYDOWN:
            if event.key == K_LEFT or event.key == K_a:
                self.left, self.right = True, False
            elif event.key == K_RIGHT or event.key == K_d:
                self.right, self.left = True, False

            if event.key == K_UP or event.key == K_w:
                self.up, self.down = True, False
            elif event.key == K_DOWN or event.key == K_s:
                self.down, self.up = True, False

        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == K_LEFT or event.key == K_a:
                self.left = False
            elif event.key == K_RIGHT or event.key == K_d:
                self.right = False

            if event.key == K_UP or event.key == K_w:
                self.up = False
            elif event.key == K_DOWN or event.key == K_s:
                self.down = False


class Computer(Paddles):
    def __init__(self):
        Paddles.__init__(self, False)

    def follow_ball(self, ball):
        if ball.rect.centerx > self.group[1].rect.centerx:
            self.right, self.left = True, False
        elif ball.rect.centerx == self.group[1].rect.centerx:
            self.right, self.left = False, False
        else:
            self.right, self.left = False, True

        if ball.rect.centery > self.group[0].rect.centery:
            self.down, self.up = True, False
        elif ball.rect.centery == self.group[0].rect.centery:
            self.down, self.up = False, False
        else:
            self.down, self.up = False, True


def winner(player_win):
    if player_win:
        message = winning_font.render(WIN_MESSAGE, True, GREEN, YELLOW)
    else:
        message = winning_font.render(LOSE_MESSAGE, True, RED, YELLOW)

    message_rect = message.get_rect()
    message_rect.center = window_surface.get_rect().center
    return message, message_rect


def scoreboard(player, computer):
    player_score = score_font.render(str(player.score), True, YELLOW, BLACK)
    computer_score = score_font.render(str(computer.score), True, YELLOW, BLACK)

    player_rect = player_score.get_rect()
    computer_rect = computer_score.get_rect()
    player_rect.centery = computer_rect.centery = WINDOW_HEIGHT_DIFF / 2
    player_rect.centerx = WINDOW_WIDTH / 4
    computer_rect.centerx = 3 * WINDOW_WIDTH / 4

    return player_score, player_rect, computer_score, computer_rect


def play():
    pygame.display.set_caption('PONG WITH NO WALLS')
    player = Player()
    computer = Computer()

    player_colors = [YELLOW for _ in range(3)]
    computer_colors = [YELLOW for _ in range(3)]

    ball = Ball()

    all_paddles = pygame.sprite.RenderPlain(player.group[0], player.group[1], player.group[2],
                                            computer.group[0], computer.group[1], computer.group[2])

    delta_y = int(WINDOW_HEIGHT / 40)
    k = int(WINDOW_WIDTH / 2)
    lines = [((k, y), (k, y + delta_y)) for y in range(WINDOW_HEIGHT_DIFF, WINDOW_HEIGHT_EXTRA, int(2 * delta_y))]

    pygame.mixer.music.play(-1, 0.0)

    gameOver = False
    while not gameOver:
        player_match_won = (player.games_won >= 3)
        computer_match_won = (computer.games_won >= 3)
        gameOver = player_match_won or computer_match_won

        if ball.rect.right > WINDOW_WIDTH or ball.rect.left < 0 \
                or ball.rect.top > WINDOW_HEIGHT_EXTRA or ball.rect.bottom < WINDOW_HEIGHT_DIFF:
            ball.refresh()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            player.button_mash(event)

        computer.follow_ball(ball)

        window_surface.fill(BLACK)

        player_score, player_rect, computer_score, computer_rect = scoreboard(player, computer)

        window_surface.blit(player_score, player_rect)
        window_surface.blit(computer_score, computer_rect)

        for i in range(len(lines)):
            el = lines[i]
            pygame.draw.line(window_surface, GREEN, el[0], el[1], 2)

        pygame.draw.line(window_surface, YELLOW, (0, WINDOW_HEIGHT_DIFF), (WINDOW_WIDTH, WINDOW_HEIGHT_DIFF))
        pygame.draw.line(window_surface, YELLOW, (WINDOW_WIDTH / 2, 0), (WINDOW_WIDTH / 2, WINDOW_HEIGHT_DIFF))
        # draw the paddles
        all_paddles.draw(window_surface)
        # draw the ball
        window_surface.blit(ball.image, ball.rect)

        player.move()
        computer.move()
        ball.move()

        ball.score(player, computer, player_colors, computer_colors)

        for i in range(3):
            pygame.draw.circle(window_surface, player_colors[i], (int(WINDOW_WIDTH / 4 + ((i - 1) * 30)),
                               WINDOW_HEIGHT_DIFF - 15), 10)
            pygame.draw.circle(window_surface, computer_colors[i], (int(3 * WINDOW_WIDTH / 4 + ((i - 1) * 30)),
                               WINDOW_HEIGHT_DIFF - 15), 10)

        if ball.bounce(player.group[0], top_down=False) or \
                ball.bounce(player.group[1], top_down=True) or \
                ball.bounce(player.group[2], top_down=True) or \
                ball.bounce(computer.group[0], top_down=False) or \
                ball.bounce(computer.group[1], top_down=True) or \
                ball.bounce(computer.group[2], top_down=True):
            pass

        pygame.display.update()
        clock.tick(120)
        # player music
    pygame.mixer.music.stop()

    player_won = True if player.games_won >= 3 else False
    game_over_music = winning_music if player_won else losing_music

    # Game over
    game_over_message, game_over_message_rect = winner(player_won)

    pygame.mixer.music.load(game_over_music)
    pygame.mixer.music.play(-1, 0.0)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        window_surface.fill(YELLOW)
        window_surface.blit(game_over_message, game_over_message_rect)
        pygame.display.update()
        clock.tick(120)


play()
