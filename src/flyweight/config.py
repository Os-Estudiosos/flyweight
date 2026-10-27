"""Constantes compartilhadas pelas duas versões do jogo."""

SCREEN_SIZE = (1280, 720)
WORLD_SIZE = (8000, 8000)
FPS = 60

DEFAULT_TREES = 10000
# Seed fixa: as duas versões plantam as mesmas árvores nas mesmas posições.
SEED = 42

PLAYER_SPEED = 400  # pixels por segundo
PLAYER_SIZE = 32

GRASS_COLOR = (86, 152, 74)
BORDER_COLOR = (40, 70, 35)
PLAYER_COLOR = (230, 80, 60)

# Intervalo (em segundos) entre os relatórios de FPS/RAM/CPU no terminal.
REPORT_INTERVAL = 2.0
