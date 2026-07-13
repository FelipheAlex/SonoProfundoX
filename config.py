# Configuração principal do Sono Profundo
# Tela cheia vertical para Android/Termux/Pydroid.
# O main.py também força estes valores antes de importar o jogo.

try:
    import pygame
    if not pygame.get_init():
        pygame.init()
    _info = pygame.display.Info()
    _w = int(getattr(_info, "current_w", 0) or 0)
    _h = int(getattr(_info, "current_h", 0) or 0)
except Exception:
    _w, _h = 720, 1280

if _w <= 0 or _h <= 0:
    _w, _h = 720, 1280

# Mantém retrato e aproveita toda a tela disponível.
LARGURA = min(_w, _h)
ALTURA = max(_w, _h)
FPS = 60

PRETO = (10, 10, 16)
BRANCO = (240, 240, 240)
CINZA = (90, 90, 95)
CINZA_ESCURO = (34, 34, 43)
CINZA_CLARO = (130, 130, 145)
MARROM = (126, 73, 34)
MARROM_ESCURO = (78, 45, 24)
AZUL = (50, 120, 220)
AZUL_CLARO = (85, 165, 255)
VERDE = (60, 205, 88)
VERDE_ESCURO = (28, 125, 58)
VERMELHO = (225, 58, 65)
VERMELHO_ESCURO = (145, 32, 38)
AMARELO = (238, 207, 48)
AMARELO_ESCURO = (164, 130, 30)
ROXO = (120, 42, 165)
ROXO_ESCURO = (70, 24, 106)
LARANJA = (236, 128, 40)
CIANO = (70, 210, 230)
PRETO_TEXTO = (16, 16, 20)
