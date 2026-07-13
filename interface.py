import pygame
from config import PRETO_TEXTO, BRANCO, CINZA_CLARO, CINZA_ESCURO, VERDE, AMARELO, AMARELO_ESCURO, VERMELHO, AZUL, AZUL_CLARO, MARROM, MARROM_ESCURO, CIANO


# v1.7.4: cache simples de textos.
# No Pydroid, renderizar fonte muitas vezes por frame causa engasgos.
_TEXTO_CACHE = {}

def _render_texto_cache(msg, cor, fonte):
    key = (id(fonte), str(msg), tuple(cor))
    img = _TEXTO_CACHE.get(key)
    if img is None:
        img = fonte.render(str(msg), True, cor)
        if len(_TEXTO_CACHE) > 360:
            _TEXTO_CACHE.clear()
        _TEXTO_CACHE[key] = img
    return img

def desenhar_texto(tela, msg, x, y, cor, fonte):
    img = _render_texto_cache(msg, cor, fonte)
    tela.blit(img, (x, y))


def desenhar_texto_centralizado(tela, msg, rect, cor, fonte, desloc_y=0):
    """Desenha texto exatamente no centro de um retângulo."""
    img = _render_texto_cache(msg, cor, fonte)
    area = pygame.Rect(rect)
    pos = img.get_rect(center=(area.centerx, area.centery + desloc_y))
    tela.blit(img, pos)




def desenhar_texto_centralizado_ajustado(tela, msg, rect, cor, fonte, margem=8, desloc_y=0):
    """Centraliza texto e reduz levemente se ele passar da largura do retângulo.
    Evita cortar valores altos de upgrade no Android/Pydroid.
    """
    img = _render_texto_cache(msg, cor, fonte)
    area = pygame.Rect(rect)
    limite = max(8, area.w - margem * 2)
    if img.get_width() > limite:
        escala = limite / max(1, img.get_width())
        nova_larg = max(1, int(img.get_width() * escala))
        nova_alt = max(1, int(img.get_height() * escala))
        img = pygame.transform.smoothscale(img, (nova_larg, nova_alt))
    pos = img.get_rect(center=(area.centerx, area.centery + desloc_y))
    tela.blit(img, pos)

def desenhar_icone(tela, tipo, cx, cy, escala=1):
    """Ícones leves desenhados por código. Evita depender de emoji/fonte no Pydroid."""
    e = max(1, int(escala))
    if tipo == "moeda":
        pygame.draw.circle(tela, AMARELO, (cx, cy), 10*e)
        pygame.draw.circle(tela, AMARELO_ESCURO, (cx, cy), 10*e, 2*e)
        pygame.draw.circle(tela, (255, 235, 95), (cx-3*e, cy-3*e), 3*e)
    elif tipo == "cama":
        r = pygame.Rect(cx-13*e, cy-6*e, 26*e, 13*e)
        pygame.draw.rect(tela, AZUL, r, border_radius=3*e)
        pygame.draw.rect(tela, AZUL_CLARO, r, 2*e, border_radius=3*e)
        pygame.draw.rect(tela, (40, 90, 170), (cx-13*e, cy-11*e, 9*e, 10*e), border_radius=2*e)
        pygame.draw.line(tela, BRANCO, (cx-14*e, cy+8*e), (cx+14*e, cy+8*e), 2*e)
    elif tipo == "porta":
        r = pygame.Rect(cx-9*e, cy-13*e, 18*e, 26*e)
        pygame.draw.rect(tela, MARROM_ESCURO, r.inflate(5*e, 5*e), border_radius=3*e)
        pygame.draw.rect(tela, MARROM, r, border_radius=3*e)
        pygame.draw.line(tela, MARROM_ESCURO, (cx, cy-11*e), (cx, cy+12*e), e)
        pygame.draw.circle(tela, AMARELO, (cx+5*e, cy+1*e), 2*e)
    elif tipo == "restam":
        pygame.draw.circle(tela, VERMELHO, (cx, cy-2*e), 10*e)
        pygame.draw.circle(tela, (45, 10, 16), (cx-4*e, cy-4*e), 2*e)
        pygame.draw.circle(tela, (45, 10, 16), (cx+4*e, cy-4*e), 2*e)
        pygame.draw.rect(tela, (45, 10, 16), (cx-4*e, cy+3*e, 8*e, 2*e), border_radius=e)
    elif tipo == "loja":
        pygame.draw.rect(tela, CIANO, (cx-10*e, cy-7*e, 20*e, 15*e), 2*e, border_radius=3*e)
        pygame.draw.line(tela, CIANO, (cx-7*e, cy-7*e), (cx-4*e, cy-13*e), 2*e)
        pygame.draw.line(tela, CIANO, (cx+7*e, cy-7*e), (cx+4*e, cy-13*e), 2*e)
    elif tipo == "torre":
        pygame.draw.rect(tela, CINZA_CLARO, (cx-8*e, cy-10*e, 16*e, 20*e), border_radius=3*e)
        pygame.draw.rect(tela, (75,75,90), (cx-12*e, cy+7*e, 24*e, 5*e), border_radius=2*e)
    elif tipo == "vender":
        pygame.draw.circle(tela, VERMELHO, (cx, cy), 11*e)
        pygame.draw.line(tela, BRANCO, (cx-6*e, cy-6*e), (cx+6*e, cy+6*e), 2*e)
        pygame.draw.line(tela, BRANCO, (cx+6*e, cy-6*e), (cx-6*e, cy+6*e), 2*e)
    elif tipo == "pause":
        pygame.draw.rect(tela, BRANCO, (cx-6*e, cy-10*e, 4*e, 20*e), border_radius=e)
        pygame.draw.rect(tela, BRANCO, (cx+3*e, cy-10*e, 4*e, 20*e), border_radius=e)
    elif tipo == "speed":
        pts1=[(cx-10*e,cy-9*e),(cx-10*e,cy+9*e),(cx,cy)]
        pts2=[(cx,cy-9*e),(cx,cy+9*e),(cx+10*e,cy)]
        pygame.draw.polygon(tela, BRANCO, pts1)
        pygame.draw.polygon(tela, BRANCO, pts2)


def desenhar_barra(tela, x, y, largura, altura, atual, maximo, cor, cor_fundo=(30, 30, 40)):
    # Barra premium leve: sombra, fundo, preenchimento e brilho fino.
    rect = pygame.Rect(int(x), int(y), int(largura), int(altura))
    pygame.draw.rect(tela, (5, 5, 8), rect.move(0, 2), border_radius=max(3, altura//2))
    pygame.draw.rect(tela, cor_fundo, rect, border_radius=max(3, altura//2))
    pct = max(0, min(1, atual / maximo)) if maximo > 0 else 0
    if pct > 0:
        fill = pygame.Rect(rect.x+2, rect.y+2, max(1, int((rect.w-4) * pct)), max(1, rect.h-4))
        pygame.draw.rect(tela, cor, fill, border_radius=max(2, altura//2-1))
        brilho = pygame.Rect(fill.x+1, fill.y+1, max(1, fill.w-2), max(1, fill.h//3))
        pygame.draw.rect(tela, (255, 255, 255), brilho, border_radius=max(1, altura//4))
    pygame.draw.rect(tela, (160, 160, 178), rect, 1, border_radius=max(3, altura//2))


class Botao:
    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)
        self._cache = {}

    def _criar_surface(self, cor, texto, fonte, habilitado=True, icone=None):
        """Cria o desenho do botão uma vez e reutiliza.
        Isso é bem mais leve no Pydroid do que redesenhar texto, ícone, bordas e brilho 60x por segundo.
        """
        key = (self.rect.size, tuple(cor), str(texto), habilitado, icone, id(fonte))
        surf = self._cache.get(key)
        if surf is not None:
            return surf

        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        r = surf.get_rect()
        cor_final = cor if habilitado else (68, 68, 78)
        pygame.draw.rect(surf, cor_final, r.inflate(-2, -2), border_radius=12)
        # brilho superior muito simples: desenhado só no cache, não todo frame.
        pygame.draw.line(surf, (245, 245, 255) if habilitado else (120, 120, 130), (8, 6), (r.w - 8, 6), 1)
        pygame.draw.rect(surf, (245,245,255) if habilitado else (135,135,145), r.inflate(-2, -2), 2, border_radius=12)

        cx_text = r.centerx
        if icone:
            desenhar_icone(surf, icone, 24, r.centery, 1)
            cx_text += 12
        img = fonte.render(str(texto), True, PRETO_TEXTO if habilitado else (185, 185, 190))
        surf.blit(img, img.get_rect(center=(cx_text, r.centery)))

        # Limita o cache para evitar acúmulo se os textos mudarem muito.
        if len(self._cache) > 24:
            self._cache.clear()
        self._cache[key] = surf
        return surf

    def desenhar(self, tela, cor, texto, fonte, habilitado=True, icone=None, pressionado=False):
        """Botão otimizado: só blita uma imagem pronta."""
        desloc = 3 if pressionado and habilitado else 0
        sombra = self.rect.move(0, 4 if not pressionado else 2)
        pygame.draw.rect(tela, (6, 6, 10), sombra, border_radius=12)
        tela.blit(self._criar_surface(cor, texto, fonte, habilitado, icone), self.rect.move(0, desloc))


# Atmosfera v1.0.6 - vinheta mínima em cache
def desenhar_vinheta(tela):
    size = tela.get_size()
    cache = getattr(desenhar_vinheta, "_cache", None)
    if cache is None or cache[0] != size:
        s = pygame.Surface(size, pygame.SRCALPHA)
        w, h = size
        # Bordas escuras discretas, calculadas uma única vez
        pygame.draw.rect(s, (0, 0, 0, 14), (0, 0, w, h), 64)
        desenhar_vinheta._cache = (size, s)
    tela.blit(desenhar_vinheta._cache[1], (0, 0))
