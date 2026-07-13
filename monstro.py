import pygame
import math, random
from config import *
from interface import desenhar_barra

TIPOS_MONSTRO = {
    # v1.4.2: identificação visual por caretas, sem letras no corpo dos monstros.
    # Cada tipo mantém uma função clara para forçar estratégias diferentes.
    "normal": {"vida": 150, "dano": 4, "vel": 55, "cor": ROXO, "face": "zumbi", "recompensa": 0},
    "corredor": {"vida": 82, "dano": 3, "vel": 112, "cor": LARANJA, "face": "corredor", "recompensa": -4},
    "bruto": {"vida": 320, "dano": 8, "vel": 30, "cor": VERMELHO_ESCURO, "face": "bruto", "recompensa": 24},
    "explosivo": {"vida": 132, "dano": 4, "vel": 52, "cor": (230, 82, 35), "face": "explosivo", "recompensa": 18},
    "fantasma": {"vida": 96, "dano": 5, "vel": 86, "cor": (135, 150, 210), "face": "fantasma", "recompensa": 12},
    # Compatibilidade com versões anteriores.
    "rapido": {"vida": 82, "dano": 3, "vel": 112, "cor": LARANJA, "face": "corredor", "recompensa": -4},
    "tanque": {"vida": 320, "dano": 8, "vel": 30, "cor": VERMELHO_ESCURO, "face": "bruto", "recompensa": 24},
    "infectado": {"vida": 130, "dano": 5, "vel": 60, "cor": (80, 190, 75), "face": "zumbi", "recompensa": 10},
    "sombra": {"vida": 96, "dano": 5, "vel": 86, "cor": (135, 150, 210), "face": "fantasma", "recompensa": 12},
    "chefe": {"vida": 760, "dano": 14, "vel": 30, "cor": (90, 28, 135), "face": "chefe", "recompensa": 70},
    # v1.5.0: chefes inteligentes. Cada um tem função própria.
    "chefe_devorador": {"vida": 980, "dano": 16, "vel": 27, "cor": (92, 35, 145), "face": "chefe", "recompensa": 125},
    "chefe_fantasma": {"vida": 820, "dano": 14, "vel": 42, "cor": (115, 140, 220), "face": "fantasma", "recompensa": 145},
    "chefe_demolidor": {"vida": 1050, "dano": 18, "vel": 24, "cor": (210, 70, 38), "face": "explosivo", "recompensa": 165},
    "chefe_caos": {"vida": 930, "dano": 15, "vel": 36, "cor": (155, 75, 210), "face": "chefe", "recompensa": 190},
    # v1.13.0: chefe temático do Hospital Abandonado (Noite 20).
    "chefe_diretor": {"vida": 100000, "dano": 19, "vel": 28, "cor": (72, 38, 58), "face": "chefe", "recompensa": 260},
    # v1.16.0: chefe exclusivo da última noite da Ala Infantil.
    "chefe_baba": {"vida": 150000, "dano": 17, "vel": 34, "cor": (82, 54, 95), "face": "chefe", "recompensa": 300},
}

def desenhar_careta(tela, corpo, tipo_face):
    """Desenha uma expressão simples e leve no monstro.
    Usa só formas do pygame para funcionar bem no Pydroid e não depender de fonte/emoji.
    """
    cx = corpo.centerx
    y = corpo.y
    olho = (18, 15, 22)
    claro = (245, 245, 245)
    vermelho = (255, 65, 65)

    if tipo_face == "fantasma":
        olho = (18, 22, 42)
        pygame.draw.circle(tela, claro, (cx - 10, y + 23), 7)
        pygame.draw.circle(tela, claro, (cx + 10, y + 23), 7)
        pygame.draw.circle(tela, olho, (cx - 10, y + 23), 4)
        pygame.draw.circle(tela, olho, (cx + 10, y + 23), 4)
        pygame.draw.ellipse(tela, olho, (cx - 7, y + 36, 14, 16), 2)
        return

    if tipo_face == "explosivo":
        pygame.draw.circle(tela, claro, (cx - 10, y + 23), 7)
        pygame.draw.circle(tela, claro, (cx + 11, y + 20), 5)
        pygame.draw.circle(tela, olho, (cx - 8, y + 25), 3)
        pygame.draw.circle(tela, olho, (cx + 12, y + 19), 2)
        pygame.draw.arc(tela, olho, (cx - 10, y + 35, 20, 15), 0, math.pi, 3)
        return

    if tipo_face == "bruto":
        pygame.draw.line(tela, olho, (cx - 18, y + 16), (cx - 4, y + 22), 4)
        pygame.draw.line(tela, olho, (cx + 18, y + 16), (cx + 4, y + 22), 4)
        pygame.draw.circle(tela, claro, (cx - 10, y + 25), 5)
        pygame.draw.circle(tela, claro, (cx + 10, y + 25), 5)
        pygame.draw.circle(tela, olho, (cx - 9, y + 25), 3)
        pygame.draw.circle(tela, olho, (cx + 9, y + 25), 3)
        pygame.draw.line(tela, olho, (cx - 13, y + 43), (cx + 13, y + 39), 3)
        return

    if tipo_face == "corredor":
        pygame.draw.line(tela, olho, (cx - 17, y + 16), (cx - 3, y + 12), 3)
        pygame.draw.line(tela, olho, (cx + 17, y + 16), (cx + 3, y + 12), 3)
        pygame.draw.circle(tela, claro, (cx - 10, y + 24), 5)
        pygame.draw.circle(tela, claro, (cx + 10, y + 24), 5)
        pygame.draw.circle(tela, olho, (cx - 8, y + 24), 3)
        pygame.draw.circle(tela, olho, (cx + 8, y + 24), 3)
        pygame.draw.rect(tela, olho, (cx - 10, y + 39, 20, 7), border_radius=2)
        pygame.draw.line(tela, claro, (cx - 8, y + 42), (cx + 8, y + 42), 1)
        return

    if tipo_face == "chefe":
        pygame.draw.polygon(tela, AMARELO, [(cx - 18, y + 7), (cx - 10, y - 3), (cx, y + 7), (cx + 10, y - 3), (cx + 18, y + 7)])
        pygame.draw.line(tela, vermelho, (cx - 17, y + 24), (cx - 4, y + 20), 4)
        pygame.draw.line(tela, vermelho, (cx + 17, y + 24), (cx + 4, y + 20), 4)
        pygame.draw.circle(tela, vermelho, (cx - 10, y + 28), 4)
        pygame.draw.circle(tela, vermelho, (cx + 10, y + 28), 4)
        pygame.draw.arc(tela, olho, (cx - 14, y + 38, 28, 18), math.pi, math.pi*2, 3)
        return

    # Zumbi normal: rosto simples e morto-vivo.
    pygame.draw.circle(tela, claro, (cx - 10, y + 24), 5)
    pygame.draw.circle(tela, claro, (cx + 10, y + 24), 5)
    pygame.draw.circle(tela, olho, (cx - 10, y + 25), 2)
    pygame.draw.circle(tela, olho, (cx + 10, y + 25), 2)
    pygame.draw.line(tela, olho, (cx - 10, y + 42), (cx + 10, y + 42), 3)



def desenhar_zumbi_pixel_teste(tela, corpo, flash=False, hospital=False, animar=True):
    """Zumbi médico mais perturbador, ainda ultra leve.
    Só usa formas simples do pygame; não altera IA, colisão, vida ou dano.
    """
    pele = (112, 158, 84) if not flash else BRANCO
    pele_luz = (152, 190, 108) if not flash else BRANCO
    pele_sombra = (58, 94, 55)
    contorno = (20, 18, 23)
    olho = (238, 232, 58)
    boca = (20, 12, 15)
    sangue = (118, 24, 30)
    sangue_escuro = (74, 18, 24)
    jaleco = (218, 228, 224)
    jaleco_sombra = (150, 168, 164)
    mascara = (158, 216, 210)
    mascara_sombra = (64, 95, 96)
    calca = (42, 54, 84)
    calca_sombra = (28, 34, 52)
    sapato = (24, 26, 32)

    cx = corpo.centerx
    y = corpo.y
    # v1.24.6: animação sutil feita só por código.
    # Deixa o zumbi menos duro sem mudar IA, colisão, vida ou velocidade real.
    t = pygame.time.get_ticks()
    andando = (t // 210) % 2 if animar else 0
    balanco = 1 if andando else -1
    molejo = int(math.sin(t * 0.010) * 1)

    # Sombra mínima no chão.
    pygame.draw.ellipse(tela, (18, 16, 22), (cx - 17, y + 57, 34, 8))

    # v1.24.8: braços reabertos só alguns pixels, com cotovelo e balanço alternado.
    # O braço "de trás" fica atrás do jaleco; o da frente será desenhado depois do tronco
    # para não sumir quando o corpo balança.
    braco_y_esq = y + 33 + balanco + molejo
    braco_y_dir = y + 34 - balanco
    braco_frente_esq = andando == 0

    # Braço de trás: visível, mas parcialmente coberto pelo corpo.
    if braco_frente_esq:
        pygame.draw.rect(tela, contorno, (cx + 10, braco_y_dir - 1, 12, 10), border_radius=3)
        pygame.draw.rect(tela, pele, (cx + 12, braco_y_dir + 1, 8, 7), border_radius=3)
        pygame.draw.rect(tela, contorno, (cx + 16, braco_y_dir + 6, 8, 13), border_radius=3)
        pygame.draw.rect(tela, pele, (cx + 17, braco_y_dir + 8, 5, 10), border_radius=2)
        pygame.draw.rect(tela, pele_sombra, (cx + 17, braco_y_dir + 16, 4, 2))
    else:
        pygame.draw.rect(tela, contorno, (cx - 22, braco_y_esq - 2, 12, 10), border_radius=3)
        pygame.draw.rect(tela, pele, (cx - 20, braco_y_esq, 8, 7), border_radius=3)
        pygame.draw.rect(tela, contorno, (cx - 24, braco_y_esq + 6, 8, 13), border_radius=3)
        pygame.draw.rect(tela, pele, (cx - 22, braco_y_esq + 8, 5, 10), border_radius=2)
        pygame.draw.rect(tela, pele_sombra, (cx - 22, braco_y_esq + 16, 4, 2))

    # Pernas e calça, um pé mais adiantado para parecer manco.
    pygame.draw.rect(tela, contorno, (cx - 15, y + 43, 30, 19), border_radius=3)
    pygame.draw.rect(tela, calca, (cx - 13, y + 44, 26, 14), border_radius=2)
    pygame.draw.rect(tela, calca_sombra, (cx + 1, y + 45, 3, 13))
    pygame.draw.rect(tela, calca, (cx - 12, y + 55 + balanco, 9, 9), border_radius=2)
    pygame.draw.rect(tela, calca, (cx + 3, y + 55 - balanco, 9, 9), border_radius=2)
    pygame.draw.rect(tela, sapato, (cx - 15, y + 63 + balanco, 12, 4), border_radius=1)
    pygame.draw.rect(tela, sapato, (cx + 3, y + 63 - balanco, 12, 4), border_radius=1)

    # Tronco com jaleco hospitalar rasgado/sujo.
    tronco = pygame.Rect(cx - 15 + molejo, y + 27, 30, 23)
    pygame.draw.rect(tela, contorno, tronco.inflate(4, 4), border_radius=4)
    if hospital:
        pygame.draw.rect(tela, jaleco, tronco, border_radius=3)
        # Abertura irregular do jaleco.
        pygame.draw.line(tela, jaleco_sombra, (cx - 2, tronco.y + 2), (cx + 1, tronco.bottom - 2), 1)
        pygame.draw.line(tela, jaleco_sombra, (cx - 11, tronco.y + 6), (cx - 1, tronco.y + 14), 1)
        pygame.draw.line(tela, jaleco_sombra, (cx + 10, tronco.y + 5), (cx + 1, tronco.y + 13), 1)
        # Rasgos no rodapé do jaleco.
        pygame.draw.line(tela, contorno, (tronco.x + 5, tronco.bottom - 1), (tronco.x + 8, tronco.bottom - 6), 1)
        pygame.draw.line(tela, contorno, (tronco.right - 8, tronco.bottom - 1), (tronco.right - 5, tronco.bottom - 6), 1)
        pygame.draw.rect(tela, sangue, (cx + 5, tronco.y + 15, 7, 3))
        pygame.draw.rect(tela, sangue_escuro, (cx - 11, tronco.y + 19, 4, 2))
    else:
        pygame.draw.rect(tela, (100, 76, 58), tronco, border_radius=3)
        pygame.draw.rect(tela, (65, 50, 42), (cx - 14, y + 40, 28, 6), border_radius=2)
        pygame.draw.rect(tela, sangue, (cx + 6, y + 35, 6, 3))

    # Braço da frente: desenhado por cima do jaleco para não desaparecer.
    if braco_frente_esq:
        pygame.draw.rect(tela, contorno, (cx - 23, braco_y_esq - 2, 12, 10), border_radius=3)
        pygame.draw.rect(tela, pele, (cx - 21, braco_y_esq, 8, 7), border_radius=3)
        # Cotovelo levemente dobrado para dentro.
        pygame.draw.rect(tela, contorno, (cx - 25, braco_y_esq + 6, 8, 13), border_radius=3)
        pygame.draw.rect(tela, pele, (cx - 23, braco_y_esq + 8, 5, 10), border_radius=2)
        pygame.draw.rect(tela, pele_sombra, (cx - 23, braco_y_esq + 16, 4, 2))
    else:
        pygame.draw.rect(tela, contorno, (cx + 11, braco_y_dir - 1, 12, 10), border_radius=3)
        pygame.draw.rect(tela, pele, (cx + 13, braco_y_dir + 1, 8, 7), border_radius=3)
        # Cotovelo levemente dobrado para dentro.
        pygame.draw.rect(tela, contorno, (cx + 18, braco_y_dir + 6, 8, 13), border_radius=3)
        pygame.draw.rect(tela, pele, (cx + 19, braco_y_dir + 8, 5, 10), border_radius=2)
        pygame.draw.rect(tela, pele_sombra, (cx + 19, braco_y_dir + 16, 4, 2))


    # Cabeça "torta" em pixels: parte de baixo deslocada para um lado.
    hx = cx - 16 + balanco + molejo
    hy = y + 1 - (1 if andando else 0)
    pygame.draw.rect(tela, contorno, (hx - 2, hy + 4, 36, 24), border_radius=6)
    pygame.draw.rect(tela, contorno, (hx + 1, hy, 29, 31), border_radius=7)
    pygame.draw.rect(tela, pele, (hx + 1, hy + 2, 29, 27), border_radius=6)
    pygame.draw.rect(tela, pele_luz, (hx + 5, hy + 5, 7, 5), border_radius=2)
    pygame.draw.rect(tela, pele_sombra, (hx + 22, hy + 8, 5, 5), border_radius=1)
    pygame.draw.rect(tela, pele_sombra, (hx + 4, hy + 20, 5, 3), border_radius=1)

    # Corte na testa e sangue discreto.
    pygame.draw.rect(tela, sangue, (hx + 24, hy + 3, 4, 10))
    pygame.draw.rect(tela, sangue_escuro, (hx + 26, hy + 13, 2, 5))
    pygame.draw.rect(tela, sangue, (hx + 19, hy + 24, 3, 7))

    # Olhos desiguais: menos fofo, mais estranho.
    pygame.draw.rect(tela, contorno, (hx + 6, hy + 13, 8, 8), border_radius=1)
    pygame.draw.rect(tela, contorno, (hx + 19, hy + 12, 6, 9), border_radius=1)
    pygame.draw.rect(tela, olho, (hx + 8, hy + 15, 4, 4))
    pygame.draw.rect(tela, olho, (hx + 20, hy + 14, 3, 5))

    # Boca torta/gemendo.
    pygame.draw.rect(tela, boca, (hx + 9, hy + 23, 12, 6), border_radius=2)
    pygame.draw.rect(tela, sangue_escuro, (hx + 9, hy + 22, 5, 2))
    pygame.draw.rect(tela, sangue, (hx + 16, hy + 28, 2, 6))

    if hospital:
        # Máscara caída: aparece como acessório médico, mas não deixa o zumbi bonitinho.
        pygame.draw.rect(tela, mascara, (hx + 6, hy + 26, 18, 6), border_radius=2)
        pygame.draw.line(tela, mascara_sombra, (hx + 8, hy + 29), (hx + 22, hy + 28), 1)
        pygame.draw.line(tela, mascara_sombra, (hx + 5, hy + 27), (hx + 1, hy + 24), 1)
        pygame.draw.line(tela, mascara_sombra, (hx + 24, hy + 27), (hx + 29, hy + 24), 1)


def desenhar_corredor_pixel_teste(tela, corpo, flash=False, hospital=False, infantil=False, animar=True):
    """Corredor em perspectiva 3/4, mais virado para a direção da corrida.
    Visual ultra leve: só formas simples do pygame; não altera IA, dano, vida ou colisão.
    """
    pele = (78, 132, 68) if not flash else BRANCO
    pele_luz = (114, 166, 84) if not flash else BRANCO
    pele_sombra = (40, 78, 48)
    contorno = (18, 15, 22)
    olho = (245, 226, 54)
    boca = (18, 9, 12)
    osso = (205, 216, 190)
    sangue = (112, 22, 32)
    pano = (82, 61, 48)
    pano_sombra = (55, 42, 38)
    calca = (34, 45, 72)
    sapato = (22, 22, 28)
    mascara = (160, 216, 205)

    cx = corpo.centerx
    y = corpo.y

    # v1.24.13: perspectiva 3/4.
    # O peito, a cabeça e os ombros apontam mais para a direção da corrida,
    # evitando o efeito de "correndo de costas".
    t = pygame.time.get_ticks()
    andando = (t // 80) % 2 if animar else 0
    quique = 1 if andando else 0
    # Na Ala Infantil o visual antigo ficava "torto" porque todo o corpo
    # era empurrado demais para a direita. Mantemos a sensação de corrida,
    # mas com inclinação menor e acessórios alinhados à cabeça.
    inclina = (4 if infantil else 7) if animar else (3 if infantil else 5)

    # Sombra levemente para frente, sem alterar colisão.
    pygame.draw.ellipse(tela, (16, 14, 20), (cx - 20, y + 56, 42, 7))

    # Ombros em diagonal: o ombro da frente fica mais à direita e um pouco mais baixo.
    ombro_tras = (cx - 7 + inclina, y + 28 + quique)
    ombro_frente = (cx + 11 + inclina, y + 33 + quique)

    if andando:
        cot_tras, mao_tras = (cx - 15 + inclina, y + 24), (cx - 22 + inclina, y + 30)
        cot_frente, mao_frente = (cx + 17 + inclina, y + 40), (cx + 24 + inclina, y + 47)
    else:
        cot_tras, mao_tras = (cx - 13 + inclina, y + 40), (cx - 20 + inclina, y + 47)
        cot_frente, mao_frente = (cx + 18 + inclina, y + 27), (cx + 25 + inclina, y + 32)

    # Braço de trás primeiro, mais fechado e parcialmente escondido pelo corpo.
    pygame.draw.line(tela, contorno, ombro_tras, cot_tras, 5)
    pygame.draw.line(tela, contorno, cot_tras, mao_tras, 5)
    pygame.draw.line(tela, pele_sombra, ombro_tras, cot_tras, 3)
    pygame.draw.line(tela, pele_sombra, cot_tras, mao_tras, 3)

    # Tronco em 3/4: lado da frente maior, lado de trás mais estreito.
    tronco_contorno = [
        (cx - 10 + inclina, y + 23 + quique),
        (cx + 17 + inclina, y + 28 + quique),
        (cx + 8 + inclina, y + 49 + quique),
        (cx - 13 + inclina, y + 43 + quique),
    ]
    tronco = [
        (cx - 7 + inclina, y + 26 + quique),
        (cx + 14 + inclina, y + 30 + quique),
        (cx + 6 + inclina, y + 45 + quique),
        (cx - 10 + inclina, y + 41 + quique),
    ]
    pygame.draw.polygon(tela, contorno, tronco_contorno)
    pygame.draw.polygon(tela, pano, tronco)
    # Faixa lateral escura dá leitura de lado/costas.
    pygame.draw.polygon(tela, pano_sombra, [
        (cx - 7 + inclina, y + 27 + quique),
        (cx - 1 + inclina, y + 29 + quique),
        (cx - 4 + inclina, y + 42 + quique),
        (cx - 10 + inclina, y + 40 + quique),
    ])
    # Peito/sangue no lado da frente, apontando para a direita.
    pygame.draw.line(tela, sangue, (cx + 8 + inclina, y + 31), (cx + 12 + inclina, y + 40), 2)
    pygame.draw.line(tela, pele_sombra, (cx - 3 + inclina, y + 35), (cx + 10 + inclina, y + 38), 1)

    # Espinhos ficam mais atrás do corpo, reforçando a direção.
    costas_x = cx - 10 + inclina
    for yy in (y + 26, y + 32, y + 38):
        pygame.draw.polygon(tela, contorno, [(costas_x, yy), (costas_x - 8, yy - 3), (costas_x - 3, yy + 4)])
        pygame.draw.polygon(tela, osso, [(costas_x - 1, yy), (costas_x - 5, yy - 2), (costas_x - 2, yy + 2)])

    # v1.25.1: pernas do Zumbi Corredor mais juntas, no estilo do zumbi normal.
    # Antes elas abriam demais e formavam um triângulo duro, principalmente na Ala Infantil.
    # Agora a base fica mais fechada, mas com passada rápida para ele realmente parecer que corre.
    passo = 1 if andando else -1
    if infantil:
        # Mais fechado na Ala Infantil, onde o acessório da cabeça já chama bastante atenção.
        quadril_tras = (cx - 3 + inclina, y + 44 + quique)
        quadril_frente = (cx + 4 + inclina, y + 45 + quique)
        joelho_tras = (cx - 5 + inclina - passo * 2, y + 53)
        pe_tras = (cx - 7 + inclina - passo * 3, y + 62)
        joelho_frente = (cx + 6 + inclina + passo * 2, y + 52)
        pe_frente = (cx + 8 + inclina + passo * 3, y + 62)
    else:
        quadril_tras = (cx - 4 + inclina, y + 44 + quique)
        quadril_frente = (cx + 5 + inclina, y + 46 + quique)
        joelho_tras = (cx - 6 + inclina - passo * 3, y + 53)
        pe_tras = (cx - 9 + inclina - passo * 5, y + 62)
        joelho_frente = (cx + 7 + inclina + passo * 3, y + 52)
        pe_frente = (cx + 10 + inclina + passo * 5, y + 62)

    # Perna de trás: fechada no corpo, com passada curta e rápida.
    pygame.draw.line(tela, contorno, quadril_tras, joelho_tras, 5)
    pygame.draw.line(tela, contorno, joelho_tras, pe_tras, 5)
    pygame.draw.line(tela, calca, quadril_tras, joelho_tras, 3)
    pygame.draw.line(tela, calca, joelho_tras, pe_tras, 3)
    pygame.draw.rect(tela, sapato, (pe_tras[0] - 5, pe_tras[1] - 1, 12, 4), border_radius=1)

    # Perna da frente por cima, também próxima do eixo do corpo.
    pygame.draw.line(tela, contorno, quadril_frente, joelho_frente, 6)
    pygame.draw.line(tela, contorno, joelho_frente, pe_frente, 6)
    pygame.draw.line(tela, calca, quadril_frente, joelho_frente, 4)
    pygame.draw.line(tela, calca, joelho_frente, pe_frente, 4)
    pygame.draw.rect(tela, sapato, (pe_frente[0] - 4, pe_frente[1] - 1, 13, 4), border_radius=1)

    # Linhas de velocidade discretas atrás dele: dá leitura de corrida sem pesar no Android.
    if animar:
        vel_cor = (42, 38, 50) if infantil else (48, 44, 52)
        for off in (0, 8):
            yy = y + 31 + off + (1 if andando else 0)
            pygame.draw.line(tela, vel_cor, (cx - 24 + inclina, yy), (cx - 14 + inclina, yy + 1), 1)

    # Braço da frente por cima do tronco, mais fechado no corpo.
    pygame.draw.line(tela, contorno, ombro_frente, cot_frente, 6)
    pygame.draw.line(tela, contorno, cot_frente, mao_frente, 6)
    pygame.draw.line(tela, pele, ombro_frente, cot_frente, 4)
    pygame.draw.line(tela, pele, cot_frente, mao_frente, 4)
    for dx in (-2, 1, 4):
        pygame.draw.line(tela, osso, (mao_frente[0] + dx, mao_frente[1]), (mao_frente[0] + dx + 2, mao_frente[1] + 4), 1)

    # Cabeça 3/4: projetada para frente/direita, com rosto olhando na direção da corrida.
    hx = cx + 11 + inclina + (1 if andando else 0)
    hy = y + 2 + quique
    pygame.draw.rect(tela, contorno, (hx - 14, hy + 1, 27, 24), border_radius=5)
    pygame.draw.rect(tela, pele, (hx - 12, hy + 3, 23, 20), border_radius=5)
    # Sombra na parte de trás da cabeça.
    pygame.draw.rect(tela, pele_sombra, (hx - 11, hy + 5, 5, 15), border_radius=2)
    pygame.draw.rect(tela, pele_luz, (hx + 2, hy + 6, 5, 4), border_radius=1)

    # Rosto deslocado para a direita: deixa claro para onde ele está correndo.
    pygame.draw.rect(tela, contorno, (hx - 2, hy + 10, 6, 6), border_radius=1)
    pygame.draw.rect(tela, contorno, (hx + 7, hy + 9, 6, 6), border_radius=1)
    pygame.draw.rect(tela, olho, (hx, hy + 12, 3, 2))
    pygame.draw.rect(tela, olho, (hx + 9, hy + 11, 3, 2))
    pygame.draw.rect(tela, boca, (hx + 1, hy + 18, 10, 4), border_radius=1)
    pygame.draw.line(tela, sangue, (hx + 10, hy + 20), (hx + 13, hy + 24), 1)

    if hospital:
        # Touca/máscara acompanhando a cabeça 3/4.
        pygame.draw.rect(tela, mascara, (hx - 9, hy + 1, 18, 4), border_radius=2)
        pygame.draw.line(tela, (66, 94, 92), (hx - 4, hy + 4), (hx + 8, hy + 5), 1)

    if infantil:
        # v1.25: polimento do Zumbi Corredor na Ala Infantil.
        # O laço antigo era desenhado no centro do rect, enquanto a cabeça
        # do corredor fica deslocada pela perspectiva 3/4. Agora tudo acompanha
        # hx/hy, então o visual não parece torto/flutuando.
        laço = (154, 88, 160) if not flash else BRANCO
        laço_sombra = (78, 45, 90)
        mascara_velha = (205, 188, 150) if not flash else BRANCO
        risco = (42, 30, 44)

        # Laço rasgado preso no topo da cabeça.
        by = hy + 1
        pygame.draw.polygon(tela, laço_sombra, [(hx - 5, by + 1), (hx - 22, by - 6), (hx - 18, by + 9)])
        pygame.draw.polygon(tela, laço_sombra, [(hx + 2, by + 1), (hx + 20, by - 7), (hx + 15, by + 9)])
        pygame.draw.polygon(tela, laço, [(hx - 4, by), (hx - 20, by - 7), (hx - 16, by + 8)])
        pygame.draw.polygon(tela, laço, [(hx + 3, by), (hx + 18, by - 8), (hx + 14, by + 8)])
        pygame.draw.circle(tela, risco, (hx - 1, by + 1), 3)

        # Meia máscara infantil rachada, alinhada ao rosto 3/4.
        pygame.draw.arc(tela, mascara_velha, (hx - 7, hy + 8, 21, 15), 0.1, math.pi * 1.75, 1)
        pygame.draw.line(tela, risco, (hx + 2, hy + 10), (hx + 8, hy + 17), 1)
        pygame.draw.line(tela, risco, (hx + 8, hy + 17), (hx + 5, hy + 22), 1)

        # Costura/cadarço pendurado para dar leitura de brinquedo antigo.
        pygame.draw.line(tela, laço_sombra, (hx - 16, by + 8), (hx - 20, by + 16), 1)
        pygame.draw.line(tela, laço_sombra, (hx + 14, by + 8), (hx + 18, by + 15), 1)

def desenhar_roupa_medico(tela, corpo, tipo):
    """Roupa leve de hospital: só formas simples do pygame.
    Não muda colisão, vida, velocidade nem IA do monstro.
    """
    # Cores discretas para não esconder totalmente a identidade do monstro.
    jaleco = (232, 238, 235)
    jaleco_sombra = (188, 202, 198)
    mascara = (170, 225, 220)
    escuro = (35, 45, 48)
    sangue = (120, 24, 28)

    # Diretor do Hospital: visual próprio, ainda feito só com formas leves.
    if tipo == "chefe_diretor":
        sombra = (16, 12, 18)
        jaleco_dir = (218, 224, 220)
        jaleco_sujo = (156, 168, 164)
        mascara_escura = (42, 52, 55)
        vermelho_olho = (255, 55, 55)
        roupa = pygame.Rect(corpo.x + 6, corpo.y + 20, corpo.w - 12, corpo.h - 18)
        pygame.draw.rect(tela, sombra, roupa.move(2, 2), border_radius=7)
        pygame.draw.rect(tela, jaleco_dir, roupa, border_radius=7)
        pygame.draw.line(tela, jaleco_sujo, (roupa.centerx, roupa.y + 3), (roupa.centerx, roupa.bottom - 3), 2)
        pygame.draw.line(tela, sangue, (roupa.x + 8, roupa.y + 16), (roupa.x + 18, roupa.y + 28), 2)
        pygame.draw.rect(tela, mascara_escura, (corpo.centerx - 18, corpo.y + 36, 36, 12), border_radius=4)
        pygame.draw.circle(tela, vermelho_olho, (corpo.centerx - 11, corpo.y + 29), 4)
        pygame.draw.circle(tela, vermelho_olho, (corpo.centerx + 11, corpo.y + 29), 4)
        # Estetoscópio do diretor.
        pygame.draw.arc(tela, (25, 28, 32), (corpo.centerx - 22, roupa.y + 8, 44, 42), 0.15, math.pi - 0.15, 2)
        pygame.draw.circle(tela, (25, 28, 32), (corpo.centerx + 13, roupa.y + 46), 5, 2)
        # Bisturi simples na lateral direita.
        pygame.draw.line(tela, (210, 215, 218), (corpo.right - 6, corpo.y + 46), (corpo.right + 12, corpo.y + 66), 3)
        pygame.draw.line(tela, (90, 95, 100), (corpo.right + 11, corpo.y + 64), (corpo.right + 19, corpo.y + 72), 2)
        return

    # Jaleco no tronco, pequeno e barato de desenhar.
    margem_x = max(5, corpo.w // 8)
    topo = corpo.y + max(15, corpo.h // 4)
    altura = max(20, corpo.h // 2)
    roupa = pygame.Rect(corpo.x + margem_x, topo, corpo.w - margem_x * 2, altura)
    pygame.draw.rect(tela, jaleco, roupa, border_radius=5)
    pygame.draw.line(tela, jaleco_sombra, (roupa.centerx, roupa.y + 2), (roupa.centerx, roupa.bottom - 2), 1)
    pygame.draw.line(tela, jaleco_sombra, (roupa.x + 5, roupa.y + 6), (roupa.centerx, roupa.y + 15), 1)
    pygame.draw.line(tela, jaleco_sombra, (roupa.right - 5, roupa.y + 6), (roupa.centerx, roupa.y + 15), 1)

    # Máscara cirúrgica no rosto.
    mw = max(18, corpo.w // 2)
    mh = max(7, corpo.h // 9)
    mx = corpo.centerx - mw // 2
    my = corpo.y + max(31, corpo.h // 2 - 3)
    pygame.draw.rect(tela, mascara, (mx, my, mw, mh), border_radius=3)
    pygame.draw.line(tela, escuro, (mx + 3, my + mh // 2), (mx + mw - 3, my + mh // 2), 1)

    # Variações por tipo: mantém variedade sem usar random por frame.
    if tipo in ("normal", "infectado", "fantasma", "sombra"):
        # Estetoscópio simples.
        sx = roupa.centerx + roupa.w // 5
        pygame.draw.line(tela, escuro, (sx - 7, roupa.y + 4), (sx - 3, roupa.y + 17), 1)
        pygame.draw.line(tela, escuro, (sx + 7, roupa.y + 4), (sx + 3, roupa.y + 17), 1)
        pygame.draw.circle(tela, escuro, (sx, roupa.y + 20), 3, 1)
    elif tipo in ("corredor", "rapido"):
        # Touca rápida no topo.
        pygame.draw.rect(tela, mascara, (corpo.x + 7, corpo.y + 4, corpo.w - 14, 8), border_radius=4)
    elif tipo in ("bruto", "tanque", "chefe_devorador"):
        # Jaleco mais sujo/rasgado.
        pygame.draw.line(tela, sangue, (roupa.x + 5, roupa.y + 10), (roupa.x + 12, roupa.y + 18), 2)
    elif tipo in ("explosivo", "chefe_demolidor"):
        # Cruz médica quebrada no peito.
        cx, cy = roupa.centerx, roupa.y + 18
        pygame.draw.rect(tela, sangue, (cx - 2, cy - 8, 4, 16))
        pygame.draw.rect(tela, sangue, (cx - 8, cy - 2, 16, 4))

    # Pequena mancha fixa para reforçar terror sem exagerar.
    if tipo.startswith("chefe"):
        pygame.draw.circle(tela, sangue, (roupa.x + 8, roupa.bottom - 8), 3)


def desenhar_acessorio_infantil(tela, corpo, tipo):
    """Acessórios leves da Ala Infantil.
    Só aparência: não altera colisão, ataque, vida, velocidade nem IA.
    """
    escuro = (24, 18, 28)
    pano = (148, 96, 150)
    velho = (115, 84, 56)
    claro = (205, 188, 150)
    vermelho = (105, 30, 36)

    # Máscara infantil rachada em alguns tipos.
    if tipo in ("normal", "infectado", "fantasma", "sombra"):
        mx = corpo.centerx - max(10, corpo.w // 4)
        my = corpo.y + max(22, corpo.h // 3)
        pygame.draw.ellipse(tela, claro, (mx, my, max(20, corpo.w//2), max(12, corpo.h//5)), 1)
        pygame.draw.line(tela, escuro, (mx + 5, my + 3), (mx + 13, my + 10), 1)
    elif tipo in ("corredor", "rapido"):
        # Laço rasgado no topo para os rápidos.
        cy = corpo.y + 8
        pygame.draw.polygon(tela, pano, [(corpo.centerx-3, cy), (corpo.centerx-17, cy-6), (corpo.centerx-14, cy+7)])
        pygame.draw.polygon(tela, pano, [(corpo.centerx+3, cy), (corpo.centerx+17, cy-6), (corpo.centerx+14, cy+7)])
        pygame.draw.circle(tela, escuro, (corpo.centerx, cy), 3)
    elif tipo in ("bruto", "tanque", "chefe_devorador"):
        # Ursinho preso ao corpo, bem simples.
        tx, ty = corpo.x + 10, corpo.y + corpo.h // 2
        pygame.draw.circle(tela, velho, (tx, ty), 8)
        pygame.draw.circle(tela, velho, (tx-6, ty-6), 3)
        pygame.draw.circle(tela, velho, (tx+6, ty-6), 3)
        pygame.draw.line(tela, escuro, (tx-4, ty+3), (tx+4, ty+5), 1)
    elif tipo in ("explosivo", "chefe_demolidor"):
        # Babador/mancha em forma simples.
        pygame.draw.polygon(tela, claro, [(corpo.centerx-12, corpo.y+28), (corpo.centerx+12, corpo.y+28), (corpo.centerx, corpo.y+48)])
        pygame.draw.line(tela, vermelho, (corpo.centerx-3, corpo.y+35), (corpo.centerx+6, corpo.y+42), 2)
    elif tipo.startswith("chefe"):
        # Chefes recebem uma máscara mais evidente, mas ainda leve.
        pygame.draw.rect(tela, claro, (corpo.centerx-18, corpo.y+24, 36, 18), 1, border_radius=6)
        pygame.draw.line(tela, vermelho, (corpo.centerx-12, corpo.y+29), (corpo.centerx+12, corpo.y+39), 2)


def fantasma_materializado(monstro):
    """Fantasma só materializa quando chega na porta.
    Transparente = não recebe dano. Na porta = normal e vulnerável.
    """
    return getattr(monstro, "tipo", "") not in ("fantasma", "sombra") or getattr(monstro, "estado", "andando") == "atacando"

def desenhar_fantasma_pixel(tela, corpo, flash=False, materializado=False, animar=True):
    """Fantasma leve em pixel/Pygame.
    Antes da porta: transparente e invulnerável.
    Na porta: opaco e vulnerável.
    """
    alpha = 105 if not materializado else 235
    if flash:
        alpha = 255
    surf = pygame.Surface((corpo.w + 26, corpo.h + 24), pygame.SRCALPHA)
    ox, oy = 13, 10
    cx = ox + corpo.w // 2
    t = pygame.time.get_ticks()
    flutua = int(math.sin(t * 0.004) * 3) if animar else 0

    contorno = (22, 20, 30, alpha)
    pano = (196, 190, 145, alpha) if materializado else (186, 196, 215, alpha)
    sombra = (116, 112, 104, max(65, alpha - 55)) if materializado else (102, 116, 150, max(55, alpha - 45))
    olho = (255, 226, 45, min(255, alpha + 40))
    boca = (18, 12, 18, alpha)

    y = oy + flutua
    # sombra etérea mínima
    pygame.draw.ellipse(surf, (12, 10, 18, 55 if materializado else 30), (cx - 18, y + 55, 36, 8))

    # braços em trapo
    pygame.draw.polygon(surf, contorno, [(cx-16,y+25),(cx-38,y+32),(cx-42,y+44),(cx-30,y+40),(cx-22,y+45)])
    pygame.draw.polygon(surf, pano, [(cx-15,y+26),(cx-35,y+33),(cx-38,y+41),(cx-29,y+38),(cx-22,y+42)])
    pygame.draw.polygon(surf, contorno, [(cx+15,y+25),(cx+35,y+32),(cx+39,y+45),(cx+28,y+40),(cx+20,y+46)])
    pygame.draw.polygon(surf, pano, [(cx+14,y+26),(cx+32,y+33),(cx+35,y+42),(cx+27,y+38),(cx+20,y+42)])

    # corpo/capa rasgada
    pygame.draw.rect(surf, contorno, (cx-18, y+12, 36, 33), border_radius=8)
    pygame.draw.rect(surf, pano, (cx-16, y+14, 32, 30), border_radius=7)
    pygame.draw.polygon(surf, contorno, [(cx-18,y+39),(cx-12,y+63),(cx-5,y+45),(cx+1,y+66),(cx+8,y+45),(cx+16,y+61),(cx+18,y+38)])
    pygame.draw.polygon(surf, pano, [(cx-15,y+39),(cx-11,y+58),(cx-5,y+43),(cx+1,y+61),(cx+8,y+43),(cx+14,y+56),(cx+15,y+38)])

    # cabeça/capuz
    pygame.draw.rect(surf, contorno, (cx-18, y+0, 36, 29), border_radius=9)
    pygame.draw.rect(surf, pano, (cx-15, y+3, 30, 24), border_radius=8)
    pygame.draw.rect(surf, sombra, (cx+7, y+5, 5, 13), border_radius=2)
    pygame.draw.rect(surf, sombra, (cx-10, y+8, 4, 4), border_radius=1)

    # rosto assustado
    pygame.draw.rect(surf, contorno, (cx-11, y+12, 8, 9), border_radius=2)
    pygame.draw.rect(surf, contorno, (cx+4, y+12, 8, 9), border_radius=2)
    pygame.draw.rect(surf, olho, (cx-8, y+15, 4, 4))
    pygame.draw.rect(surf, olho, (cx+7, y+15, 4, 4))
    pygame.draw.rect(surf, boca, (cx-6, y+25, 13, 12), border_radius=3)
    pygame.draw.rect(surf, (235, 225, 175, alpha), (cx-4, y+25, 3, 5))
    pygame.draw.rect(surf, (235, 225, 175, alpha), (cx+2, y+25, 3, 5))

    if not materializado:
        # linhas leves para indicar transparência/invulnerável
        pygame.draw.line(surf, (210, 225, 255, 75), (cx-22, y+9), (cx+18, y+3), 1)
        pygame.draw.line(surf, (210, 225, 255, 65), (cx-20, y+42), (cx+15, y+52), 1)

    tela.blit(surf, (corpo.x - ox, corpo.y - oy))




def _linha_braco_dobrado(tela, contorno, cor, ombro, cotovelo, mao, grossura=6, grossura_interna=4):
    """Braço em bloco grosso, sem efeito de graveto.
    v1.24.18: usado em brutos e chefes para manter proporção pesada.
    """
    # Garante que chefes/brutos nunca fiquem com braço fino demais.
    grossura = max(grossura, 11)
    grossura_interna = max(grossura_interna, 7)

    # Desenha em duas partes, mas com espessura grande e juntas arredondadas.
    for a, b in ((ombro, cotovelo), (cotovelo, mao)):
        pygame.draw.line(tela, contorno, a, b, grossura)
        pygame.draw.circle(tela, contorno, a, grossura // 2)
        pygame.draw.circle(tela, contorno, b, grossura // 2)
        pygame.draw.line(tela, cor, a, b, grossura_interna)
        pygame.draw.circle(tela, cor, a, grossura_interna // 2)
        pygame.draw.circle(tela, cor, b, grossura_interna // 2)

    # Mão grande e pesada.
    r = max(6, grossura_interna // 2 + 2)
    pygame.draw.rect(tela, contorno, (mao[0] - r, mao[1] - r + 1, r * 2 + 2, r * 2), border_radius=4)
    pygame.draw.rect(tela, cor, (mao[0] - r + 2, mao[1] - r + 3, r * 2 - 2, r * 2 - 3), border_radius=3)


def _perna_dobrada(tela, contorno, cor, quadril, joelho, pe, grossura=6, grossura_interna=4, sapato_cor=None):
    """Perna em bloco curto e grosso, sem aparência de palito.
    v1.24.18: deixa brutos e chefes com peso visual real.
    """
    grossura = max(grossura, 11)
    grossura_interna = max(grossura_interna, 7)

    for a, b in ((quadril, joelho), (joelho, pe)):
        pygame.draw.line(tela, contorno, a, b, grossura)
        pygame.draw.circle(tela, contorno, a, grossura // 2)
        pygame.draw.circle(tela, contorno, b, grossura // 2)
        pygame.draw.line(tela, cor, a, b, grossura_interna)
        pygame.draw.circle(tela, cor, a, grossura_interna // 2)
        pygame.draw.circle(tela, cor, b, grossura_interna // 2)

    if sapato_cor is not None:
        pygame.draw.rect(tela, sapato_cor, (pe[0] - 10, pe[1] - 2, 20, 7), border_radius=3)


def _braco_bloco_tanque(tela, contorno, cor, x, y, lado=1, bal=0):
    """Braço quadrado/pesado para bruto: ombro, antebraço e mão em blocos."""
    # Ombro grudado no corpo, bem largo.
    pygame.draw.rect(tela, contorno, (x - 2 if lado < 0 else x - 5, y - 2, 17, 16), border_radius=5)
    pygame.draw.rect(tela, cor, (x + 1 if lado < 0 else x - 2, y + 1, 11, 10), border_radius=4)

    # Antebraço caído, grosso, sem linha fina.
    ax = x + (-3 if lado < 0 else 4)
    ay = y + 10 + bal
    pygame.draw.rect(tela, contorno, (ax - 4, ay, 15, 22), border_radius=5)
    pygame.draw.rect(tela, cor, (ax - 1, ay + 2, 9, 16), border_radius=4)

    # Mão pesada.
    pygame.draw.rect(tela, contorno, (ax - 5, ay + 18, 17, 10), border_radius=4)
    pygame.draw.rect(tela, cor, (ax - 2, ay + 19, 11, 7), border_radius=3)


def _perna_bloco_tanque(tela, contorno, cor, x, y, bal=0, sapato_cor=None):
    """Perna curta, grossa e fechada para bruto/chefes."""
    pygame.draw.rect(tela, contorno, (x - 7, y, 15, 17), border_radius=5)
    pygame.draw.rect(tela, cor, (x - 4, y + 2, 9, 12), border_radius=4)
    pygame.draw.rect(tela, contorno, (x - 8, y + 13 + bal, 17, 12), border_radius=4)
    pygame.draw.rect(tela, cor, (x - 5, y + 14 + bal, 11, 8), border_radius=3)
    if sapato_cor:
        pygame.draw.rect(tela, sapato_cor, (x - 12, y + 23 + bal, 24, 6), border_radius=2)


def desenhar_bruto_pixel(tela, corpo, flash=False, animar=True):
    """Bruto/tanque com silhueta pesada.
    v1.24.18: redesenhado em blocos. Sem porrete/graveto, braços e pernas grossos.
    """
    pele = (164, 148, 112) if not flash else BRANCO
    pele_luz = (194, 176, 132) if not flash else BRANCO
    pele_sombra = (94, 82, 66)
    contorno = (20, 17, 18)
    olho = (245, 205, 55)
    boca = (28, 14, 12)
    sangue = (110, 28, 25)
    pano = (76, 56, 42)
    sapato = (18, 16, 18)

    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 360 % 2) if animar else 0
    bal = 1 if t else -1

    # Sombra maior e baixa: sensação de peso.
    pygame.draw.ellipse(tela, (16, 14, 18), (cx - 33, y + 72, 66, 11))

    # Braços atrás/ao lado do tronco. Grossos e próximos do corpo.
    _braco_bloco_tanque(tela, contorno, pele, cx - 38, y + 34 + bal, lado=-1, bal=bal)
    _braco_bloco_tanque(tela, contorno, pele, cx + 26, y + 34 - bal, lado=1, bal=-bal)

    # Corpo mais quadrado e com ombros largos: deixa de parecer apenas gordo.
    pygame.draw.rect(tela, contorno, (cx - 34, y + 22, 68, 48), border_radius=12)
    pygame.draw.rect(tela, pele, (cx - 30, y + 25, 60, 41), border_radius=10)
    # Peito/abdômen em blocos, para parecer massa muscular/peso.
    pygame.draw.rect(tela, pele_luz, (cx - 23, y + 30, 17, 8), border_radius=3)
    pygame.draw.rect(tela, pele_sombra, (cx + 11, y + 34, 10, 13), border_radius=3)
    pygame.draw.line(tela, contorno, (cx - 1, y + 27), (cx - 1, y + 65), 2)
    pygame.draw.line(tela, sangue, (cx + 4, y + 42), (cx + 16, y + 53), 3)
    pygame.draw.line(tela, pele_sombra, (cx - 22, y + 51), (cx - 10, y + 47), 2)

    # Calça/saia rasgada curta.
    pygame.draw.rect(tela, pano, (cx - 27, y + 62, 54, 10), border_radius=2)
    for dx in (-20, -6, 9):
        pygame.draw.polygon(tela, pano, [(cx + dx, y + 70), (cx + dx + 12, y + 70), (cx + dx + 5, y + 79)])

    # Pernas curtas, grossas, quase embaixo do corpo. Nada de passada aberta.
    _perna_bloco_tanque(tela, contorno, pele, cx - 11, y + 67, bal=bal, sapato_cor=sapato)
    _perna_bloco_tanque(tela, contorno, pele, cx + 11, y + 67, bal=-bal, sapato_cor=sapato)

    # Cabeça pequena afundada entre os ombros.
    pygame.draw.rect(tela, contorno, (cx - 19, y + 1, 38, 31), border_radius=8)
    pygame.draw.rect(tela, pele, (cx - 16, y + 4, 32, 25), border_radius=7)
    pygame.draw.rect(tela, pele_sombra, (cx + 8, y + 7, 5, 7), border_radius=2)
    pygame.draw.rect(tela, sangue, (cx - 12, y + 7, 8, 3))
    pygame.draw.rect(tela, contorno, (cx - 11, y + 14, 8, 7), border_radius=1)
    pygame.draw.rect(tela, contorno, (cx + 4, y + 14, 8, 7), border_radius=1)
    pygame.draw.rect(tela, olho, (cx - 9, y + 16, 4, 3))
    pygame.draw.rect(tela, olho, (cx + 6, y + 16, 4, 3))
    pygame.draw.rect(tela, boca, (cx - 10, y + 23, 20, 7), border_radius=2)
    for tx in (-6, 0, 6):
        pygame.draw.rect(tela, (222, 205, 150), (cx + tx, y + 24, 2, 4))

def desenhar_explosivo_pixel(tela, corpo, flash=False, animar=True):
    """Explosivo ultra leve: corpo-bomba redondo, pavio e olhos quentes."""
    metal = (62, 58, 54) if not flash else BRANCO
    metal_luz = (92, 84, 72) if not flash else BRANCO
    metal_sombra = (30, 28, 30)
    pele = (93, 130, 78) if not flash else BRANCO
    contorno = (18, 15, 16)
    olho = (255, 178, 42)
    fogo = (255, 70, 30)
    fogo2 = (255, 210, 65)
    dinamite = (155, 42, 30)
    boca = (18, 10, 10)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 180 % 2) if animar else 0
    chama = 2 if t else 0

    pygame.draw.ellipse(tela, (15, 13, 18), (cx - 26, y + 58, 52, 8))

    # Pernas e braços curtos.
    pygame.draw.line(tela, contorno, (cx - 19, y + 34), (cx - 33, y + 45), 7)
    pygame.draw.line(tela, contorno, (cx + 19, y + 34), (cx + 33, y + 45), 7)
    pygame.draw.line(tela, pele, (cx - 19, y + 34), (cx - 32, y + 44), 5)
    pygame.draw.line(tela, pele, (cx + 19, y + 34), (cx + 32, y + 44), 5)
    pygame.draw.rect(tela, contorno, (cx - 18, y + 56, 12, 11), border_radius=3)
    pygame.draw.rect(tela, contorno, (cx + 6, y + 56, 12, 11), border_radius=3)
    pygame.draw.rect(tela, pele, (cx - 15, y + 57, 8, 8), border_radius=2)
    pygame.draw.rect(tela, pele, (cx + 8, y + 57, 8, 8), border_radius=2)

    # Corpo-bomba.
    pygame.draw.circle(tela, contorno, (cx, y + 30), 29)
    pygame.draw.circle(tela, metal, (cx, y + 30), 25)
    pygame.draw.rect(tela, metal_luz, (cx - 12, y + 11, 10, 5), border_radius=2)
    pygame.draw.rect(tela, metal_sombra, (cx + 12, y + 22, 6, 9), border_radius=2)
    pygame.draw.rect(tela, (206, 180, 118), (cx + 12, y + 32, 8, 10), border_radius=1)
    pygame.draw.circle(tela, metal_sombra, (cx - 12, y + 15), 3)

    # Dinamites simples amarradas.
    pygame.draw.rect(tela, dinamite, (cx - 24, y + 38, 8, 16), border_radius=2)
    pygame.draw.rect(tela, dinamite, (cx + 17, y + 38, 8, 16), border_radius=2)
    pygame.draw.line(tela, metal_sombra, (cx - 26, y + 37), (cx + 26, y + 37), 2)

    # Pavio e chama.
    pygame.draw.rect(tela, metal_sombra, (cx - 7, y + 1, 14, 6), border_radius=3)
    pygame.draw.line(tela, (120, 86, 54), (cx, y + 2), (cx + 8, y - 12), 3)
    pygame.draw.polygon(tela, fogo, [(cx+8,y-16-chama),(cx+3,y-8),(cx+13,y-8)])
    pygame.draw.polygon(tela, fogo2, [(cx+8,y-13-chama),(cx+6,y-8),(cx+11,y-8)])

    # Rosto furioso.
    pygame.draw.line(tela, contorno, (cx - 16, y + 20), (cx - 6, y + 16), 3)
    pygame.draw.line(tela, contorno, (cx + 16, y + 20), (cx + 6, y + 16), 3)
    pygame.draw.rect(tela, contorno, (cx - 14, y + 23, 9, 8), border_radius=2)
    pygame.draw.rect(tela, contorno, (cx + 5, y + 23, 9, 8), border_radius=2)
    pygame.draw.rect(tela, olho, (cx - 11, y + 25, 4, 4))
    pygame.draw.rect(tela, olho, (cx + 8, y + 25, 4, 4))
    pygame.draw.rect(tela, boca, (cx - 9, y + 38, 18, 9), border_radius=2)
    for tx in (-5, 1, 6):
        pygame.draw.rect(tela, (225, 205, 145), (cx + tx, y + 39, 2, 4))


def desenhar_venenoso_pixel(tela, corpo, flash=False, animar=True):
    """Infectado/venenoso ultra leve: barriga inchada, bolhas e fumacinha."""
    pele = (105, 145, 62) if not flash else BRANCO
    pele_luz = (148, 180, 72) if not flash else BRANCO
    pele_sombra = (54, 86, 42)
    contorno = (18, 16, 18)
    olho = (219, 236, 52)
    boca = (15, 8, 10)
    bolha = (112, 66, 86)
    veneno = (132, 214, 40)
    pano = (73, 55, 44)
    cx = corpo.centerx
    y = corpo.y
    t = pygame.time.get_ticks() if animar else 0
    gas = (t // 500) % 3

    pygame.draw.ellipse(tela, (15, 13, 18), (cx - 24, y + 62, 48, 8))

    # Gás verde simples nas costas.
    for i in range(3):
        gx = cx + 20 + i * 6
        gy = y + 6 + ((gas + i) % 3) * 4
        pygame.draw.circle(tela, (92, 145, 42), (gx, gy), 3 - (i == 2))

    # Braços pingando.
    pygame.draw.line(tela, contorno, (cx - 18, y + 35), (cx - 35, y + 50), 7)
    pygame.draw.line(tela, pele, (cx - 18, y + 35), (cx - 34, y + 49), 5)
    pygame.draw.line(tela, contorno, (cx + 18, y + 35), (cx + 32, y + 47), 7)
    pygame.draw.line(tela, pele, (cx + 18, y + 35), (cx + 31, y + 46), 5)
    pygame.draw.line(tela, veneno, (cx - 34, y + 50), (cx - 34, y + 58), 2)

    # Corpo e barriga tóxica.
    pygame.draw.rect(tela, contorno, (cx - 23, y + 24, 46, 39), border_radius=12)
    pygame.draw.rect(tela, pele, (cx - 20, y + 26, 40, 34), border_radius=11)
    pygame.draw.circle(tela, contorno, (cx, y + 48), 15)
    pygame.draw.circle(tela, veneno, (cx, y + 48), 12)
    pygame.draw.circle(tela, pele_luz, (cx - 4, y + 45), 4)
    pygame.draw.line(tela, veneno, (cx - 3, y + 58), (cx - 3, y + 66), 2)
    for bx, by in ((cx-14,y+33),(cx+14,y+34),(cx+9,y+25),(cx-10,y+55)):
        pygame.draw.circle(tela, bolha, (bx, by), 3)
        pygame.draw.circle(tela, contorno, (bx, by), 3, 1)

    # Pano e pernas.
    pygame.draw.rect(tela, pano, (cx - 18, y + 60, 36, 7), border_radius=2)
    pygame.draw.rect(tela, contorno, (cx - 16, y + 66, 11, 11), border_radius=3)
    pygame.draw.rect(tela, contorno, (cx + 5, y + 66, 11, 11), border_radius=3)
    pygame.draw.rect(tela, pele, (cx - 14, y + 67, 8, 8), border_radius=2)
    pygame.draw.rect(tela, pele, (cx + 7, y + 67, 8, 8), border_radius=2)

    # Cabeça.
    pygame.draw.rect(tela, contorno, (cx - 17, y + 2, 34, 27), border_radius=8)
    pygame.draw.rect(tela, pele, (cx - 14, y + 4, 28, 22), border_radius=7)
    pygame.draw.rect(tela, pele_sombra, (cx + 7, y + 7, 5, 6), border_radius=2)
    pygame.draw.rect(tela, contorno, (cx - 10, y + 13, 7, 6), border_radius=1)
    pygame.draw.rect(tela, contorno, (cx + 5, y + 13, 7, 6), border_radius=1)
    pygame.draw.rect(tela, olho, (cx - 8, y + 15, 3, 2))
    pygame.draw.rect(tela, olho, (cx + 7, y + 15, 3, 2))
    pygame.draw.rect(tela, boca, (cx - 8, y + 22, 16, 8), border_radius=2)
    pygame.draw.line(tela, veneno, (cx, y + 29), (cx, y + 39), 2)


def desenhar_devorador_pixel(tela, corpo, flash=False, animar=True):
    """Chefe Devorador ultra simplificado: boca gigante, olhos roxos e tentáculos curtos."""
    base = (94, 68, 82) if not flash else BRANCO
    luz = (124, 92, 104) if not flash else BRANCO
    sombra = (45, 34, 48)
    contorno = (15, 12, 18)
    roxo = (174, 85, 230)
    roxo_escuro = (82, 40, 110)
    dente = (220, 205, 160)
    boca = (18, 8, 18)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 300 % 2) if animar else 0
    bal = 2 if t else -1

    pygame.draw.ellipse(tela, (12, 10, 15), (cx - 45, y + 78, 90, 13))

    # Tentáculos curtos nas costas.
    for side in (-1, 1):
        pygame.draw.arc(tela, contorno, (cx + side*14 - 18, y + 1, 48, 34), 0.2, 2.7, 5)
        pygame.draw.arc(tela, roxo_escuro, (cx + side*14 - 16, y + 3, 44, 30), 0.2, 2.7, 3)
    pygame.draw.arc(tela, contorno, (cx - 8, y - 5, 44, 42), 4.1, 6.1, 5)
    pygame.draw.arc(tela, roxo_escuro, (cx - 6, y - 3, 40, 38), 4.1, 6.1, 3)

    # Braços enormes, mas com cotovelo como o zumbi normal.
    if t:
        _linha_braco_dobrado(tela, contorno, base, (cx - 32, y + 42), (cx - 37, y + 50), (cx - 39, y + 62), 12, 8)
        _linha_braco_dobrado(tela, contorno, base, (cx + 32, y + 41), (cx + 37, y + 49), (cx + 39, y + 61), 12, 8)
    else:
        _linha_braco_dobrado(tela, contorno, base, (cx - 32, y + 42), (cx - 36, y + 51), (cx - 38, y + 63), 12, 8)
        _linha_braco_dobrado(tela, contorno, base, (cx + 32, y + 41), (cx + 37, y + 48), (cx + 39, y + 59), 12, 8)

    # Corpo boss.
    pygame.draw.rect(tela, contorno, (cx - 42, y + 15, 84, 63), border_radius=20)
    pygame.draw.rect(tela, base, (cx - 38, y + 18, 76, 57), border_radius=18)
    pygame.draw.rect(tela, luz, (cx - 25, y + 24, 14, 8), border_radius=3)
    pygame.draw.rect(tela, sombra, (cx + 17, y + 30, 11, 18), border_radius=4)
    # Buracos/olhos no corpo.
    for bx, by, rr in ((cx-7,y+58,5),(cx+8,y+60,4),(cx+20,y+51,4),(cx-22,y+52,3)):
        pygame.draw.circle(tela, contorno, (bx, by), rr)
        pygame.draw.circle(tela, roxo_escuro, (bx, by), max(1, rr-2))

    # Cabeça/boca gigante integrada ao corpo.
    pygame.draw.rect(tela, contorno, (cx - 33, y + 2, 66, 45), border_radius=16)
    pygame.draw.rect(tela, base, (cx - 29, y + 5, 58, 38), border_radius=14)
    pygame.draw.rect(tela, boca, (cx - 21, y + 18, 42, 30), border_radius=8)
    # Dentes grandes, poucos.
    for dx in (-16, -6, 6, 16):
        pygame.draw.polygon(tela, dente, [(cx+dx-3,y+18),(cx+dx+3,y+18),(cx+dx,y+30)])
    for dx in (-13, -2, 10):
        pygame.draw.polygon(tela, dente, [(cx+dx-3,y+48),(cx+dx+3,y+48),(cx+dx,y+36)])
    # Olhos roxos.
    for ex, ey in ((cx-17,y+14),(cx-3,y+10),(cx+13,y+15)):
        pygame.draw.circle(tela, contorno, (ex, ey), 5)
        pygame.draw.circle(tela, roxo, (ex, ey), 3)
    # Espinhos simples.
    for sx, sy in ((cx-30,y+14),(cx+30,y+17),(cx-10,y+2),(cx+15,y+4)):
        pygame.draw.polygon(tela, contorno, [(sx,sy),(sx+5,sy-10),(sx+9,sy)])
        pygame.draw.polygon(tela, dente, [(sx+2,sy),(sx+5,sy-7),(sx+7,sy)])

    # Pernas curtas/pesadas com passo alternado, sem parecer bloco duro.
    if t:
        _perna_dobrada(tela, contorno, base, (cx - 15, y + 72), (cx - 17, y + 80), (cx - 18, y + 87), 10, 7, contorno)
        _perna_dobrada(tela, contorno, base, (cx + 15, y + 72), (cx + 17, y + 79), (cx + 18, y + 86), 10, 7, contorno)
    else:
        _perna_dobrada(tela, contorno, base, (cx - 15, y + 72), (cx - 16, y + 79), (cx - 17, y + 86), 10, 7, contorno)
        _perna_dobrada(tela, contorno, base, (cx + 15, y + 72), (cx + 18, y + 80), (cx + 19, y + 87), 10, 7, contorno)


def desenhar_rei_fantasma_boss(tela, corpo, flash=False, animar=True):
    """Rei Fantasma ultra leve: coroa, manto, cajado e flutuação simples."""
    ciano = (122, 207, 213) if not flash else BRANCO
    ciano_sombra = (62, 118, 132)
    manto = (58, 48, 86) if not flash else BRANCO
    manto_sombra = (32, 28, 52)
    contorno = (13, 12, 20)
    ouro = (214, 176, 68)
    ouro_sombra = (124, 92, 36)
    olho = (200, 245, 255)
    boca = (12, 10, 18)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 360 % 2) if animar else 0
    flut = 2 if t else 0
    y += flut

    pygame.draw.ellipse(tela, (13, 12, 18), (cx - 28, y + 76, 56, 8))

    # Cajado simples.
    sx = cx - 32
    pygame.draw.line(tela, contorno, (sx, y + 20), (sx, y + 75), 4)
    pygame.draw.line(tela, (70, 68, 76), (sx, y + 21), (sx, y + 74), 2)
    pygame.draw.rect(tela, ouro, (sx - 5, y + 12, 10, 9), border_radius=2)
    pygame.draw.circle(tela, (110, 80, 160), (sx, y + 16), 3)

    # Braços/mangas com cotovelo sutil, sem ficar rígido.
    _linha_braco_dobrado(tela, contorno, manto, (cx - 18, y + 33), (cx - 29, y + 39 + flut), (cx - 37, y + 49), 8, 5)
    _linha_braco_dobrado(tela, contorno, manto, (cx + 18, y + 34), (cx + 29, y + 41 - flut), (cx + 37, y + 50), 8, 5)
    pygame.draw.rect(tela, ciano, (cx + 33, y + 47, 9, 6), border_radius=2)

    # Corpo fantasma e manto.
    pygame.draw.rect(tela, contorno, (cx - 24, y + 22, 48, 44), border_radius=12)
    pygame.draw.rect(tela, manto, (cx - 21, y + 25, 42, 38), border_radius=10)
    pygame.draw.rect(tela, manto_sombra, (cx + 8, y + 31, 6, 24), border_radius=3)
    pygame.draw.circle(tela, ouro, (cx, y + 35), 4)
    pygame.draw.line(tela, ouro_sombra, (cx - 10, y + 38), (cx + 10, y + 38), 2)
    # cauda rasgada
    pts = [(cx-21,y+60),(cx-13,y+82),(cx-4,y+65),(cx+2,y+84),(cx+10,y+65),(cx+20,y+80),(cx+21,y+60)]
    pygame.draw.polygon(tela, contorno, pts)
    pygame.draw.polygon(tela, ciano_sombra, [(cx-17,y+61),(cx-11,y+77),(cx-4,y+63),(cx+2,y+78),(cx+9,y+63),(cx+16,y+75),(cx+17,y+61)])

    # Cabeça/rosto.
    pygame.draw.rect(tela, contorno, (cx - 18, y + 3, 36, 30), border_radius=9)
    pygame.draw.rect(tela, ciano, (cx - 15, y + 6, 30, 25), border_radius=8)
    pygame.draw.rect(tela, ciano_sombra, (cx + 7, y + 9, 5, 12), border_radius=2)
    pygame.draw.rect(tela, boca, (cx - 7, y + 18, 14, 13), border_radius=3)
    pygame.draw.rect(tela, olho, (cx - 9, y + 13, 4, 4))
    pygame.draw.rect(tela, olho, (cx + 5, y + 13, 4, 4))
    # coroa
    pygame.draw.rect(tela, ouro_sombra, (cx - 15, y - 3, 30, 6))
    for dx in (-12, 0, 12):
        pygame.draw.polygon(tela, ouro, [(cx+dx-4,y-3),(cx+dx,y-15),(cx+dx+4,y-3)])
    pygame.draw.rect(tela, ouro, (cx - 14, y + 0, 28, 4))


def desenhar_demolidor_boss(tela, corpo, flash=False, animar=True):
    """Demolidor ultra leve: capacete, armadura e bola de ferro simples."""
    pele = (158, 112, 88) if not flash else BRANCO
    pele_luz = (190, 140, 105) if not flash else BRANCO
    contorno = (15, 13, 15)
    metal = (54, 56, 60) if not flash else BRANCO
    metal_luz = (92, 94, 98) if not flash else BRANCO
    vermelho = (235, 40, 36)
    pano = (88, 42, 38)
    sangue = (100, 24, 24)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 300 % 2) if animar else 0
    bal = 2 if t else -1

    pygame.draw.ellipse(tela, (12, 11, 15), (cx - 43, y + 78, 86, 12))

    # Bola de ferro ultra simples.
    bx, by = cx - 42, y + 61 + bal
    pygame.draw.line(tela, contorno, (cx - 27, y + 46), (bx + 9, by - 8), 4)
    pygame.draw.circle(tela, contorno, (bx, by), 16)
    pygame.draw.circle(tela, metal, (bx, by), 13)
    for dx, dy in ((0,-15),(12,-4),(-12,3),(4,12)):
        pygame.draw.polygon(tela, metal_luz, [(bx+dx,by+dy),(bx+dx+4,by+dy+4),(bx+dx-4,by+dy+4)])

    # Corpo largo.
    pygame.draw.rect(tela, contorno, (cx - 34, y + 24, 68, 47), border_radius=13)
    pygame.draw.rect(tela, pele, (cx - 30, y + 27, 60, 40), border_radius=12)
    pygame.draw.rect(tela, pele_luz, (cx - 21, y + 31, 12, 6), border_radius=2)
    pygame.draw.line(tela, sangue, (cx + 8, y + 36), (cx + 20, y + 47), 3)
    # tiras simples no peito
    pygame.draw.line(tela, metal, (cx-23,y+28), (cx+20,y+66), 4)
    pygame.draw.line(tela, metal, (cx+23,y+28), (cx-20,y+66), 4)
    pygame.draw.circle(tela, metal_luz, (cx, y+47), 5)

    # Ombreira e braços com cotovelos, no estilo do zumbi normal.
    pygame.draw.circle(tela, contorno, (cx + 30, y + 30), 15)
    pygame.draw.circle(tela, metal, (cx + 30, y + 30), 12)
    _linha_braco_dobrado(tela, contorno, pele, (cx - 27, y + 39), (cx - 34, y + 48 + bal), (cx - 36, y + 61), 10, 7)
    _linha_braco_dobrado(tela, contorno, pele, (cx + 27, y + 40), (cx + 34, y + 48 - bal), (cx + 37, y + 60), 10, 7)

    # Pernas com joelho e passo alternado.
    pygame.draw.rect(tela, pano, (cx - 25, y + 66, 50, 10), border_radius=2)
    if t:
        _perna_dobrada(tela, contorno, metal, (cx - 13, y + 72), (cx - 16, y + 80), (cx - 19, y + 88), 8, 5, contorno)
        _perna_dobrada(tela, contorno, metal, (cx + 13, y + 72), (cx + 16, y + 79), (cx + 19, y + 87), 8, 5, contorno)
    else:
        _perna_dobrada(tela, contorno, metal, (cx - 13, y + 72), (cx - 15, y + 79), (cx - 17, y + 87), 8, 5, contorno)
        _perna_dobrada(tela, contorno, metal, (cx + 13, y + 72), (cx + 18, y + 80), (cx + 22, y + 88), 8, 5, contorno)

    # Cabeça com capacete.
    pygame.draw.rect(tela, contorno, (cx - 18, y + 2, 36, 31), border_radius=8)
    pygame.draw.rect(tela, metal, (cx - 15, y + 4, 30, 27), border_radius=7)
    pygame.draw.rect(tela, vermelho, (cx - 9, y + 14, 5, 4))
    pygame.draw.rect(tela, vermelho, (cx + 5, y + 14, 5, 4))
    for dx in (-8, 0, 8):
        pygame.draw.line(tela, contorno, (cx + dx, y + 21), (cx + dx, y + 31), 2)
    pygame.draw.polygon(tela, metal_luz, [(cx,y+0),(cx+4,y-10),(cx+8,y+0)])


def desenhar_caos_boss(tela, corpo, flash=False, animar=True):
    """Senhor do Caos ultra leve: manto roxo, capuz preto, cajado e poucos detalhes."""
    contorno = (12, 10, 18)
    manto = (48, 38, 74) if not flash else BRANCO
    manto_luz = (72, 54, 104) if not flash else BRANCO
    roxo = (180, 70, 230)
    ouro = (170, 135, 70)
    osso = (185, 170, 130)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 330 % 2) if animar else 0
    flut = 2 if t else 0
    y += flut

    pygame.draw.ellipse(tela, (11, 10, 15), (cx - 34, y + 80, 68, 10))

    # Cajado.
    sx = cx - 34
    pygame.draw.line(tela, contorno, (sx, y + 14), (sx, y + 79), 5)
    pygame.draw.line(tela, ouro, (sx, y + 15), (sx, y + 78), 2)
    pygame.draw.rect(tela, ouro, (sx - 6, y + 7, 12, 9), border_radius=2)
    pygame.draw.circle(tela, roxo, (sx, y + 11), 3)

    # Manto grande.
    pygame.draw.rect(tela, contorno, (cx - 30, y + 18, 60, 55), border_radius=14)
    pygame.draw.rect(tela, manto, (cx - 26, y + 21, 52, 49), border_radius=12)
    pygame.draw.rect(tela, manto_luz, (cx - 18, y + 27, 6, 31), border_radius=3)
    pygame.draw.polygon(tela, contorno, [(cx-30,y+65),(cx-20,y+90),(cx-8,y+70),(cx,y+93),(cx+8,y+70),(cx+22,y+88),(cx+30,y+65)])
    pygame.draw.polygon(tela, manto, [(cx-25,y+66),(cx-18,y+84),(cx-8,y+68),(cx,y+87),(cx+8,y+68),(cx+18,y+82),(cx+25,y+66)])

    # Braços com cotovelo, mais vivos e menos rígidos.
    _linha_braco_dobrado(tela, contorno, manto, (cx - 24, y + 35), (cx - 35, y + 43 + flut), (cx - 42, y + 55), 8, 5)
    _linha_braco_dobrado(tela, contorno, manto, (cx + 24, y + 35), (cx + 35, y + 42 - flut), (cx + 43, y + 53), 8, 5)
    pygame.draw.circle(tela, roxo, (cx + 44, y + 53), 4)

    # Capuz/rosto vazio.
    pygame.draw.rect(tela, contorno, (cx - 20, y + 0, 40, 36), border_radius=11)
    pygame.draw.rect(tela, (18, 14, 25), (cx - 16, y + 5, 32, 28), border_radius=9)
    pygame.draw.rect(tela, roxo, (cx - 7, y + 16, 4, 4))
    pygame.draw.rect(tela, roxo, (cx + 4, y + 16, 4, 4))
    # coroa/espinhos simples
    pygame.draw.rect(tela, ouro, (cx - 16, y + 0, 32, 4))
    for dx in (-13, 0, 13):
        pygame.draw.polygon(tela, ouro, [(cx+dx-3,y),(cx+dx,y-12),(cx+dx+3,y)])
    # caveiras simples no peito.
    pygame.draw.circle(tela, osso, (cx, y + 43), 6)
    pygame.draw.rect(tela, contorno, (cx - 3, y + 42, 2, 2))
    pygame.draw.rect(tela, contorno, (cx + 2, y + 42, 2, 2))


def desenhar_diretor_boss(tela, corpo, flash=False, animar=True):
    """Diretor do Hospital ultra leve: jaleco, máscara, prancheta e seringa."""
    contorno = (14, 12, 16)
    pele = (92, 135, 86) if not flash else BRANCO
    jaleco = (220, 225, 220) if not flash else BRANCO
    jaleco_sombra = (150, 160, 158)
    roupa = (38, 36, 42)
    vermelho = (230, 45, 45)
    metal = (85, 90, 95)
    papel = (220, 205, 170)
    tubo = (105, 42, 45)
    roxo = (95, 68, 92)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 300 % 2) if animar else 0
    bal = 1 if t else -1

    pygame.draw.ellipse(tela, (12, 10, 15), (cx - 38, y + 78, 76, 11))

    # Mochila/tubos nas costas, poucos detalhes.
    pygame.draw.rect(tela, contorno, (cx + 15, y + 15, 18, 42), border_radius=6)
    pygame.draw.rect(tela, (58, 45, 48), (cx + 18, y + 18, 12, 36), border_radius=4)
    pygame.draw.line(tela, tubo, (cx + 27, y + 17), (cx + 37, y + 31), 3)
    pygame.draw.line(tela, tubo, (cx + 29, y + 38), (cx + 39, y + 52), 3)

    # Braços com cotovelo, mantendo prancheta e seringa.
    cot_esq, mao_esq = (cx - 38, y + 43 + bal), (cx - 48, y + 55 + bal)
    cot_dir, mao_dir = (cx + 36, y + 43 - bal), (cx + 49, y + 48 - bal)
    _linha_braco_dobrado(tela, contorno, jaleco, (cx - 24, y + 35), cot_esq, mao_esq, 8, 5)
    _linha_braco_dobrado(tela, contorno, jaleco, (cx + 24, y + 36), cot_dir, mao_dir, 8, 5)
    # prancheta
    pygame.draw.rect(tela, contorno, (mao_esq[0] - 8, mao_esq[1] - 20, 17, 24), border_radius=2)
    pygame.draw.rect(tela, papel, (mao_esq[0] - 6, mao_esq[1] - 18, 13, 20), border_radius=1)
    pygame.draw.line(tela, (90,80,70), (mao_esq[0]-4,mao_esq[1]-13), (mao_esq[0]+4,mao_esq[1]-13), 1)
    pygame.draw.line(tela, (90,80,70), (mao_esq[0]-4,mao_esq[1]-8), (mao_esq[0]+3,mao_esq[1]-8), 1)
    # seringa
    pygame.draw.rect(tela, contorno, (mao_dir[0] - 4, mao_dir[1] - 5, 20, 10), border_radius=3)
    pygame.draw.rect(tela, roxo, (mao_dir[0] - 2, mao_dir[1] - 3, 14, 6), border_radius=2)
    pygame.draw.line(tela, metal, (mao_dir[0]+15,mao_dir[1]), (mao_dir[0]+24,mao_dir[1]), 2)

    # Corpo/jaleco.
    pygame.draw.rect(tela, contorno, (cx - 28, y + 22, 56, 54), border_radius=11)
    pygame.draw.rect(tela, jaleco, (cx - 25, y + 25, 50, 48), border_radius=9)
    pygame.draw.rect(tela, roupa, (cx - 10, y + 28, 20, 37), border_radius=4)
    pygame.draw.line(tela, jaleco_sombra, (cx - 1, y + 26), (cx - 2, y + 72), 2)
    pygame.draw.line(tela, vermelho, (cx + 10, y + 39), (cx + 17, y + 52), 2)
    pygame.draw.rect(tela, (100,25,28), (cx - 20, y + 61, 7, 3))

    # Pernas com movimento estilo zumbi normal.
    if t:
        _perna_dobrada(tela, contorno, roupa, (cx - 10, y + 70), (cx - 13, y + 78), (cx - 16, y + 86), 7, 4, contorno)
        _perna_dobrada(tela, contorno, roupa, (cx + 10, y + 70), (cx + 13, y + 77), (cx + 16, y + 85), 7, 4, contorno)
    else:
        _perna_dobrada(tela, contorno, roupa, (cx - 10, y + 70), (cx - 12, y + 77), (cx - 14, y + 85), 7, 4, contorno)
        _perna_dobrada(tela, contorno, roupa, (cx + 10, y + 70), (cx + 15, y + 78), (cx + 19, y + 86), 7, 4, contorno)

    # Cabeça/máscara.
    pygame.draw.rect(tela, contorno, (cx - 20, y + 1, 40, 32), border_radius=9)
    pygame.draw.rect(tela, pele, (cx - 17, y + 4, 34, 27), border_radius=8)
    pygame.draw.rect(tela, metal, (cx - 15, y + 19, 30, 10), border_radius=3)
    pygame.draw.circle(tela, vermelho, (cx - 9, y + 14), 4)
    pygame.draw.circle(tela, vermelho, (cx + 9, y + 14), 4)
    # disco de médico na testa
    pygame.draw.circle(tela, jaleco, (cx - 6, y + 3), 5)
    pygame.draw.circle(tela, metal, (cx - 6, y + 3), 2)
    # gravata
    pygame.draw.polygon(tela, vermelho, [(cx-3,y+31),(cx+3,y+31),(cx,y+47)])


def desenhar_baba_sombria_boss(tela, corpo, flash=False, animar=True):
    """Babá Sombria ultra leve: enfermeira fantasma da Ala Infantil.
    Visual feito só com formas simples do Pygame para manter o jogo liso.
    """
    contorno = (14, 12, 20)
    pele = (185, 190, 188) if not flash else BRANCO
    pele_sombra = (105, 115, 118)
    vestido = (62, 50, 78) if not flash else BRANCO
    vestido_luz = (90, 72, 108) if not flash else BRANCO
    touca = (222, 225, 218) if not flash else BRANCO
    cabelo = (18, 16, 23)
    vermelho = (240, 45, 65)
    urso = (136, 92, 64)
    urso_escuro = (66, 42, 35)
    cx = corpo.centerx
    y = corpo.y
    t = (pygame.time.get_ticks() // 360 % 2) if animar else 0
    flut = 2 if t else 0
    bal = 1 if t else -1
    y += flut

    # Sombra pequena no chão.
    pygame.draw.ellipse(tela, (12, 10, 16), (cx - 35, y + 80, 70, 10))

    # Ursinho amaldiçoado na mão: poucos círculos/retângulos.
    ux, uy = cx + 39, y + 51 + bal
    _linha_braco_dobrado(tela, contorno, vestido, (cx + 22, y + 38), (cx + 31, y + 44 - bal), (ux - 7, uy - 4), 7, 4)
    pygame.draw.circle(tela, contorno, (ux, uy), 10)
    pygame.draw.circle(tela, urso, (ux, uy), 8)
    pygame.draw.circle(tela, urso, (ux - 6, uy - 7), 4)
    pygame.draw.circle(tela, urso, (ux + 6, uy - 7), 4)
    pygame.draw.rect(tela, urso_escuro, (ux - 3, uy - 1, 2, 2))
    pygame.draw.rect(tela, vermelho, (ux + 3, uy - 2, 2, 2))
    pygame.draw.line(tela, contorno, (ux - 3, uy + 5), (ux + 4, uy + 5), 1)

    # Braço esquerdo fino, com cotovelo igual ao estilo do zumbi normal.
    _linha_braco_dobrado(tela, contorno, vestido, (cx - 20, y + 38), (cx - 31, y + 45 + bal), (cx - 39, y + 56 - bal), 7, 4)
    pygame.draw.circle(tela, pele, (cx - 40, y + 57 - bal), 4)

    # Corpo/vestido fantasma rasgado.
    pygame.draw.rect(tela, contorno, (cx - 28, y + 24, 56, 45), border_radius=13)
    pygame.draw.rect(tela, vestido, (cx - 24, y + 27, 48, 39), border_radius=11)
    pygame.draw.rect(tela, vestido_luz, (cx - 15, y + 31, 6, 24), border_radius=3)
    pygame.draw.line(tela, (110, 45, 65), (cx + 11, y + 38), (cx + 18, y + 50), 2)
    # Cauda/trapos, sem pernas.
    pygame.draw.polygon(tela, contorno, [(cx-27,y+62),(cx-18,y+88),(cx-7,y+68),(cx,y+91),(cx+8,y+68),(cx+20,y+86),(cx+27,y+62)])
    pygame.draw.polygon(tela, vestido, [(cx-23,y+63),(cx-16,y+82),(cx-7,y+66),(cx,y+84),(cx+8,y+66),(cx+17,y+80),(cx+23,y+63)])

    # Cabeça, cabelo e rosto.
    pygame.draw.rect(tela, contorno, (cx - 20, y + 2, 40, 33), border_radius=10)
    pygame.draw.rect(tela, pele, (cx - 17, y + 5, 34, 27), border_radius=8)
    # Cabelo cobrindo parte do rosto.
    pygame.draw.rect(tela, cabelo, (cx - 19, y + 4, 14, 30), border_radius=6)
    pygame.draw.rect(tela, cabelo, (cx + 8, y + 4, 10, 23), border_radius=5)
    pygame.draw.rect(tela, pele_sombra, (cx + 7, y + 21, 5, 6), border_radius=2)
    # Olhos vermelhos e boca pequena.
    pygame.draw.rect(tela, vermelho, (cx - 7, y + 16, 4, 4))
    pygame.draw.rect(tela, vermelho, (cx + 6, y + 16, 4, 4))
    pygame.draw.rect(tela, contorno, (cx - 3, y + 24, 9, 4), border_radius=1)

    # Touca de enfermeira e cruz.
    pygame.draw.rect(tela, contorno, (cx - 18, y - 4, 36, 10), border_radius=4)
    pygame.draw.rect(tela, touca, (cx - 15, y - 2, 30, 7), border_radius=3)
    pygame.draw.line(tela, vermelho, (cx, y - 1), (cx, y + 4), 2)
    pygame.draw.line(tela, vermelho, (cx - 3, y + 1), (cx + 3, y + 1), 2)


def _desenhar_particulas_impacto(tela, particulas):
    """Partículas pequenas de impacto nos pesadelos.
    Base v1.21.4: efeito leve, sem imagens e sem custo alto.
    """
    for p in particulas:
        vida = max(0, min(1, p.get("t", 0) / p.get("total", 0.18)))
        x = int(p["x"] + p["vx"] * (1 - vida) * 7)
        y = int(p["y"] + p["vy"] * (1 - vida) * 7)
        tam = 1 if vida < 0.55 else 2
        cor = (255, 230, 120) if vida > 0.35 else (160, 45, 55)
        pygame.draw.rect(tela, cor, (x, y, tam, tam))


def _desenhar_morte_pesadelo(tela, corpo, progresso, chefe=False, tipo="normal"):
    """Explosão simples ao morrer.
    progresso: 0 = acabou de morrer, 1 = efeito terminou.

    v1.21.5: troca o desaparecimento estranho por um círculo de explosão.
    O monstro explosivo usa raio maior para ficar fácil de identificar.
    Tudo é desenhado direto no Pygame, sem imagem, sem som e sem partículas caras.
    """
    progresso = max(0, min(1, progresso))
    cx, cy = corpo.center

    explosivo = tipo in ("explosivo", "chefe_demolidor")
    if chefe:
        # v1.21.7: derrota de chefe com explosão maior e mais marcante.
        raio_base = 28
        raio_extra = 46
        qtd = 14
    elif explosivo:
        raio_base = 16
        raio_extra = 24
        qtd = 9
    else:
        raio_base = 9
        raio_extra = 15
        qtd = 6

    raio = int(raio_base + progresso * raio_extra)
    nucleo = max(2, int(raio * (1.0 - progresso) * 0.55))

    # Sombra curta no chão para manter profundidade.
    sombra_w = max(8, int(raio * (1.15 - progresso * 0.45)))
    pygame.draw.ellipse(tela, (12, 10, 16), (cx - sombra_w, corpo.bottom - 4, sombra_w * 2, 5))

    # Anel principal da explosão.
    cor_anel = (255, 128, 45) if explosivo else (225, 88, 55)
    if chefe:
        cor_anel = (240, 95, 70)
    pygame.draw.circle(tela, cor_anel, (cx, cy), raio, 2)

    # Núcleo quente nos primeiros frames.
    if progresso < 0.65:
        pygame.draw.circle(tela, (255, 238, 165), (cx, cy), max(2, nucleo))
        pygame.draw.circle(tela, (255, 180, 70), (cx, cy), max(3, int(nucleo * 1.45)), 1)

    # Segundo anel para explosivos e chefes, deixando o estouro mais forte.
    if explosivo or chefe:
        pygame.draw.circle(tela, (255, 205, 95), (cx, cy), max(4, int(raio * 0.62)), 1)
    if chefe:
        # Terceiro anel só para chefes: impacto maior sem usar Surface/alpha.
        pygame.draw.circle(tela, (255, 225, 135), (cx, cy), max(5, int(raio * 0.38)), 1)

    # Pixels/fragmentos radiais bem leves.
    for i in range(qtd):
        ang = i * (math.pi * 2 / qtd) + progresso * 0.9
        dist = int(raio * (0.45 + progresso * 0.55))
        px = int(cx + math.cos(ang) * dist)
        py = int(cy + math.sin(ang) * dist)
        tam = 3 if (explosivo or chefe) and progresso < 0.55 else 2
        cor = (255, 226, 120) if i % 2 == 0 else (205, 55, 45)
        pygame.draw.rect(tela, cor, (px, py, tam, tam))


def _desenhar_presenca_chefe(tela, corpo, tipo, flash=False):
    """v1.21.7: presença visual dos chefes, leve e 100% Pygame.
    Aura, olhos e pequenas marcas dão identidade sem sprites novos.
    """
    ticks = pygame.time.get_ticks()
    cx, cy = corpo.center
    pulso = (ticks // 180) % 2
    cor_base = (105, 55, 145)
    if tipo == "chefe_fantasma":
        cor_base = (105, 145, 235)
    elif tipo == "chefe_demolidor":
        cor_base = (235, 95, 45)
    elif tipo == "chefe_caos":
        cor_base = (180, 85, 230)
    elif tipo == "chefe_diretor":
        cor_base = (120, 75, 92)
    elif tipo == "chefe_baba":
        cor_base = (155, 95, 180)

    # Sombra/aura no chão.
    pygame.draw.ellipse(tela, (18, 10, 28), (cx - 43, corpo.bottom - 4, 86, 12), 2)
    pygame.draw.ellipse(tela, cor_base, (cx - 40, corpo.bottom - 8, 80, 16), 1)

    # Aura lateral discreta, alternando 1px para parecer viva.
    r = 37 + pulso * 2
    pygame.draw.circle(tela, cor_base, (cx, cy), r, 1)
    if flash:
        pygame.draw.circle(tela, (255, 235, 160), (cx, cy), r + 4, 1)

    # Olhos brilhantes por cima do desenho do chefe.
    olho = (255, 72, 72)
    if tipo == "chefe_fantasma": olho = (210, 235, 255)
    elif tipo == "chefe_demolidor": olho = (255, 210, 80)
    elif tipo == "chefe_caos": olho = (230, 95, 255)
    pygame.draw.circle(tela, olho, (cx - 12, corpo.y + 28), 4 + pulso)
    pygame.draw.circle(tela, olho, (cx + 12, corpo.y + 28), 4 + pulso)


class Monstro:
    def __init__(self, x, y, noite=1, tipo="normal"):
        base = TIPOS_MONSTRO.get(tipo, TIPOS_MONSTRO["normal"])
        escala = 1 + (noite - 1) * 0.18
        w, h = (70, 86) if tipo.startswith("chefe") else ((44, 56) if tipo == "sombra" else (48, 60))
        self.rect = pygame.Rect(x, y, w, h)
        self.tipo = tipo
        # Audio: marcado pelo jogo.py depois que o som de surgimento tocar.
        self.som_aparecer_tocado = False
        self.canal_surgimento = None
        self.noite = noite
        self.vida_max = int(base["vida"] * escala)
        # v1.20.2: chefes especiais usam HP fixo de boss.
        # Evita que a escala por noite transforme Diretor/Babá em valores exagerados.
        if tipo == "chefe_diretor":
            self.vida_max = 100000
        elif tipo == "chefe_baba":
            self.vida_max = 150000
        self.vida = self.vida_max
        self.dano = int(base["dano"] + noite * 0.65)
        self.velocidade = base["vel"] + noite * 1.6
        self.cor = base["cor"]
        self.face = base.get("face", "zumbi")
        # v1.5.0: estados usados pelos chefes inteligentes.
        self.invisivel_tempo = 0
        self.habilidade_tick = random.uniform(1.0, 2.5) if tipo.startswith("chefe") else 0
        # Alvo inicial seguro. O jogo.py atualiza isso com a posição real da porta.
        self.alvo_x_base = LARGURA // 2 - w // 2
        self.alvo_x = self.alvo_x_base
        self.alvo_y = 334 - h + 4
        self.fila = 0
        self.estado = "andando"
        self.flash = 0
        self.recuo = 0
        self.passo = 0
        # v1.21.4: tempo um pouco maior para a morte aparecer sem pesar.
        self.morte_total = 0.20
        self.morte_tempo = self.morte_total
        self.hit_fx = []
        self.lentidao_tempo = 0
        self.lentidao_fator = 1
        self.queimadura_tempo = 0
        self.queimadura_dano = 0
        self.queimadura_tick = 0
        # v1.6.0: usado pela habilidade Congelar do jogador.
        self.congelado_tempo = 0
        self.recompensa = max(2, 8 + noite * 3 + base.get("recompensa", 0))

    def configurar_alvo_porta(self, porta):
        """Atualiza o alvo usando a posição REAL da porta.
        Assim, se o corredor/quarto/porta mudar de tamanho, o monstro
        continua andando até encostar na porta antes de atacar.
        """
        self.alvo_x_base = int(porta.centerx - self.rect.w // 2)
        # O monstro para com os pés encostando/sobrepondo levemente a porta.
        self.alvo_y = int(porta.y - self.rect.h + 8)
        self.alvo_x = self.alvo_x_base

    def definir_fila(self, indice):
        # Fila horizontal diante da porta. Evita monstros empilhados e mantém todos no corredor.
        self.fila = indice
        offsets = [0, -46, 46, -92, 92, -138, 138]
        off = offsets[indice % len(offsets)]
        self.alvo_x = self.alvo_x_base + off
        self.alvo_x = max(35, min(LARGURA - 35 - self.rect.w, self.alvo_x))

    def atualizar(self, dt):
        self.flash = max(0, self.flash - dt)
        self.invisivel_tempo = max(0, getattr(self, "invisivel_tempo", 0) - dt)
        self.congelado_tempo = max(0, getattr(self, "congelado_tempo", 0) - dt)
        self.recuo = max(0, self.recuo - dt * 35)
        self.lentidao_tempo = max(0, self.lentidao_tempo - dt)
        self.passo += dt * 10
        if self.hit_fx:
            for p in self.hit_fx:
                p["t"] -= dt
            self.hit_fx = [p for p in self.hit_fx if p["t"] > 0]
        if self.queimadura_tempo > 0 and self.vida > 0:
            self.queimadura_tempo = max(0, self.queimadura_tempo - dt)
            self.queimadura_tick += dt
            if self.queimadura_tick >= 0.35:
                self.queimadura_tick = 0
                self.sofrer_dano(self.queimadura_dano)
        if self.vida <= 0:
            self.morte_tempo -= dt
            return
        if getattr(self, "congelado_tempo", 0) > 0:
            self.estado = "andando"
            return
        fator = self.lentidao_fator if self.lentidao_tempo > 0 else 1
        # v1.22.0: fase de fúria dos chefes. Abaixo de 30% de vida,
        # ficam um pouco mais rápidos sem virar esponja de HP.
        if self.tipo.startswith("chefe") and self.vida <= self.vida_max * 0.30:
            fator *= 1.10
        passo = max(1, int(self.velocidade * fator * dt))

        # 1) Alinha com a porta no eixo X.
        if abs(self.rect.x - self.alvo_x) > 4:
            if self.rect.x < self.alvo_x:
                self.rect.x = min(self.alvo_x, self.rect.x + passo)
            else:
                self.rect.x = max(self.alvo_x, self.rect.x - passo)
            self.estado = "andando"
            return

        # 2) Depois de alinhado, desce até a porta.
        if self.rect.y < self.alvo_y:
            self.rect.y += passo
            if self.rect.y > self.alvo_y:
                self.rect.y = self.alvo_y
            self.estado = "andando"
        else:
            self.estado = "atacando"

    def sofrer_dano(self, dano, origem=None):
        # v1.14.8: Fantasma comum é invulnerável enquanto está transparente.
        # Ele só recebe dano depois que encosta na porta e materializa.
        if self.tipo in ("fantasma", "sombra") and self.estado != "atacando":
            return
        # Devorador: armadura enquanto está acima da metade da vida.
        if self.tipo == "chefe_devorador" and self.vida > self.vida_max * 0.5:
            dano = max(1, int(dano * 0.50))
        # v1.24.40: defesa contra ARMAS para chefes.
        # Chefes especiais recebem 50% menos dano de armas.
        # Chefes comuns recebem 25% menos dano de armas.
        # Habilidades do jogador continuam sem essa redução.
        if origem == "arma" and str(self.tipo).startswith("chefe"):
            if self.tipo in ("chefe_diretor", "chefe_baba"):
                dano = max(1, int(dano * 0.50))
                # Doutor Infectado: ao cair para 70% ou menos da vida,
                # ganha uma segunda camada de resistência contra armas.
                if self.tipo == "chefe_diretor" and self.vida <= self.vida_max * 0.70:
                    dano = max(1, int(dano * 0.50))
            else:
                dano = max(1, int(dano * 0.75))
        # Invisibilidade:
        # Babá Sombria fica realmente inalvejável por 5s após invocar.
        # Rei Fantasma mantém a regra antiga de dano mínimo.
        if getattr(self, "invisivel_tempo", 0) > 0:
            if self.tipo == "chefe_baba":
                return
            dano = max(1, int(dano * 0.25))
        self.vida -= dano
        if self.vida <= 0:
            self.vida = 0
        self.flash = 0.11
        self.recuo = 5
        # v1.21.4: faíscas leves no ponto de impacto.
        for _ in range(3):
            self.hit_fx.append({
                "x": self.rect.centerx + random.randint(-12, 12),
                "y": self.rect.centery + random.randint(-14, 12),
                "vx": random.uniform(-1.2, 1.2),
                "vy": random.uniform(-1.0, 0.8),
                "t": 0.16,
                "total": 0.16,
            })

    def aplicar_lentidao(self, fator, tempo):
        self.lentidao_fator = fator
        self.lentidao_tempo = max(self.lentidao_tempo, tempo)

    def aplicar_congelamento(self, tempo):
        self.congelado_tempo = max(getattr(self, "congelado_tempo", 0), tempo)

    def aplicar_queimadura(self, dano, tempo):
        self.queimadura_dano = max(self.queimadura_dano, int(dano))
        self.queimadura_tempo = max(self.queimadura_tempo, tempo)

    def pode_atacar(self):
        return (
            self.vida > 0
            and self.estado == "atacando"
            and abs(self.rect.x - self.alvo_x) <= 8
            and self.rect.y >= self.alvo_y - 2
        )

    def morto_pronto(self):
        return self.vida <= 0 and self.morte_tempo <= 0

    def desenhar(self, tela, fonte, hospital=False, infantil=False):
        if self.vida <= 0:
            progresso = 1 - max(0, self.morte_tempo) / max(0.01, getattr(self, "morte_total", 0.20))
            corpo_morte = self.rect.move(0, int(getattr(self, "recuo", 0)))
            _desenhar_morte_pesadelo(tela, corpo_morte, progresso, chefe=self.tipo.startswith("chefe"), tipo=self.tipo)
            return
        if getattr(self, "hit_fx", None):
            _desenhar_particulas_impacto(tela, self.hit_fx)
        # v1.7.4: barra de vida só quando faz diferença visual.
        # Monstros com vida cheia não redesenham barra todo frame; chefes continuam com barra grande no topo.
        if self.vida < self.vida_max and not self.tipo.startswith("chefe"):
            desenhar_barra(tela, self.rect.x - 10, self.rect.y - 10, self.rect.w + 20, 6, self.vida, self.vida_max, VERMELHO)
        cor = BRANCO if self.flash > 0 else self.cor
        if getattr(self, "invisivel_tempo", 0) > 0:
            cor = (80, 86, 125)
        if getattr(self, "congelado_tempo", 0) > 0:
            cor = CIANO
        # v1.21.4: respiração leve e passo mais vivo, sem mudar colisão/IA.
        animar_monstro = self.estado != 'atacando'
        respiro = int(math.sin(self.passo * 0.55) * (2 if self.tipo.startswith("chefe") else 1)) if animar_monstro else 0
        # v1.24.6: movimento visual mais suave; evita monstro parecendo bloco deslizando.
        offset = 2 if int(self.passo) % 2 == 0 and self.estado == "andando" else 0
        corpo = self.rect.move(0, -offset - int(self.recuo) + respiro)
        # v1.14.5: zumbi normal redesenhado, sem sombra grande e sem jaleco cobrindo o rosto.
        # Vida, dano, colisão e IA continuam iguais.
        if self.tipo == "normal":
            desenhar_zumbi_pixel_teste(tela, corpo, self.flash > 0, hospital=hospital, animar=animar_monstro)
            if infantil:
                desenhar_acessorio_infantil(tela, corpo, self.tipo)
            return
        # v1.14.7: corredor com visual próprio, magro e agressivo.
        # Mantém a mesma velocidade, vida, dano, IA e colisão.
        if self.tipo in ("corredor", "rapido"):
            desenhar_corredor_pixel_teste(tela, corpo, self.flash > 0, hospital=hospital, infantil=infantil, animar=animar_monstro)
            return
        # v1.14.8: fantasma próprio. Transparente/invulnerável até chegar na porta.
        if self.tipo in ("fantasma", "sombra"):
            desenhar_fantasma_pixel(tela, corpo, self.flash > 0, materializado=(self.estado == "atacando"), animar=animar_monstro)
            if infantil:
                desenhar_acessorio_infantil(tela, corpo, self.tipo)
            return

        # v1.15.0: todos os monstros principais ganharam visual pixel/Pygame ultra leve.
        if self.tipo in ("bruto", "tanque"):
            desenhar_bruto_pixel(tela, corpo, self.flash > 0, animar=animar_monstro)
            if infantil:
                desenhar_acessorio_infantil(tela, corpo, self.tipo)
            return
        if self.tipo in ("explosivo",):
            desenhar_explosivo_pixel(tela, corpo, self.flash > 0, animar=animar_monstro)
            if infantil:
                desenhar_acessorio_infantil(tela, corpo, self.tipo)
            return
        if self.tipo == "infectado":
            desenhar_venenoso_pixel(tela, corpo, self.flash > 0, animar=animar_monstro)
            if infantil:
                desenhar_acessorio_infantil(tela, corpo, self.tipo)
            return
        if self.tipo == "chefe_baba" and getattr(self, "invisivel_tempo", 0) > 0:
            # Babá Sombria invisível: caveira rabiscada, bem fraca e leve.
            # Sem Surface/alpha para evitar travamentos no Android/Pydroid.
            t = pygame.time.get_ticks()
            pulse = 1 + ((t // 190) % 3)
            cx, cy = corpo.center
            raio = max(corpo.w, corpo.h) // 2
            cor_fraca = (60, 55, 82)
            cor_linha = (86, 78, 118)
            cor_olho = (122, 118, 155)

            # Aura quase apagada ao redor da posição real dela.
            pygame.draw.circle(tela, cor_fraca, (cx, cy), raio + 9 + pulse, 1)
            pygame.draw.circle(tela, (45, 42, 64), (cx, cy), max(10, raio - 5), 1)

            # Caveira rabiscada: cabeça, queixo e rachaduras.
            cranio = pygame.Rect(cx - 22, cy - 31, 44, 42)
            pygame.draw.ellipse(tela, cor_linha, cranio, 1)
            pygame.draw.arc(tela, cor_linha, (cx - 18, cy - 5, 36, 30), 0, math.pi, 1)
            pygame.draw.line(tela, cor_linha, (cx - 15, cy + 8), (cx - 9, cy + 23), 1)
            pygame.draw.line(tela, cor_linha, (cx + 15, cy + 8), (cx + 9, cy + 23), 1)
            pygame.draw.line(tela, cor_linha, (cx - 9, cy + 23), (cx + 9, cy + 23), 1)

            # Olhos e nariz, pouco visíveis.
            pygame.draw.circle(tela, cor_olho, (cx - 10, cy - 11), 5, 1)
            pygame.draw.circle(tela, cor_olho, (cx + 10, cy - 11), 5, 1)
            pygame.draw.line(tela, cor_olho, (cx, cy - 3), (cx - 4, cy + 6), 1)
            pygame.draw.line(tela, cor_olho, (cx, cy - 3), (cx + 4, cy + 6), 1)
            pygame.draw.line(tela, cor_olho, (cx - 4, cy + 6), (cx + 4, cy + 6), 1)

            # Boca riscada e dentes tortos.
            pygame.draw.line(tela, cor_linha, (cx - 12, cy + 13), (cx + 12, cy + 12), 1)
            for dx in (-8, -3, 3, 8):
                pygame.draw.line(tela, cor_linha, (cx + dx, cy + 10), (cx + dx + (1 if dx < 0 else -1), cy + 17), 1)

            # Riscos externos dão aparência de desenho assombrado.
            for off in (-21, 0, 21):
                y = cy + off
                pygame.draw.line(tela, cor_fraca, (cx - raio + 6, y), (cx - 13, y + pulse), 1)
                pygame.draw.line(tela, cor_fraca, (cx + 13, y + pulse), (cx + raio - 6, y), 1)
            pygame.draw.line(tela, cor_fraca, (cx - 4, cy - 28), (cx + 6, cy - 16), 1)
            pygame.draw.line(tela, cor_fraca, (cx + 6, cy - 16), (cx + 1, cy - 6), 1)
            return
        if self.tipo.startswith("chefe"):
            _desenhar_presenca_chefe(tela, corpo, self.tipo, self.flash > 0)
            # v1.22.0: aura vermelha discreta quando o chefe entra em fúria.
            if self.vida <= self.vida_max * 0.30:
                pygame.draw.circle(tela, (255, 55, 55), corpo.center, max(corpo.w, corpo.h)//2 + 7, 1)
        if self.tipo == "chefe_baba":
            desenhar_baba_sombria_boss(tela, corpo, self.flash > 0, animar=animar_monstro)
            return
        if self.tipo == "chefe_devorador":
            desenhar_devorador_pixel(tela, corpo, self.flash > 0, animar=animar_monstro)
            return
        if self.tipo == "chefe_fantasma":
            desenhar_rei_fantasma_boss(tela, corpo, self.flash > 0, animar=animar_monstro)
            return
        if self.tipo == "chefe_demolidor":
            desenhar_demolidor_boss(tela, corpo, self.flash > 0, animar=animar_monstro)
            return
        if self.tipo == "chefe_caos":
            desenhar_caos_boss(tela, corpo, self.flash > 0, animar=animar_monstro)
            return
        if self.tipo == "chefe_diretor":
            desenhar_diretor_boss(tela, corpo, self.flash > 0, animar=animar_monstro)
            return
        if self.tipo == "chefe":
            desenhar_devorador_pixel(tela, corpo, self.flash > 0, animar=animar_monstro)
            return

        sombra = self.rect.move(0, 4).inflate(10, 8)
        pygame.draw.rect(tela, (20, 16, 28), sombra, border_radius=9)
        pygame.draw.rect(tela, cor, corpo, border_radius=9)
        if self.tipo in ("explosivo", "chefe_demolidor"):
            pygame.draw.circle(tela, LARANJA, corpo.center, max(8, corpo.w//3), 2)
        if self.tipo in ("fantasma", "sombra", "chefe_fantasma"):
            pygame.draw.rect(tela, (230, 235, 255), corpo.inflate(-12, -10), 1, border_radius=7)
            pygame.draw.circle(tela, (230, 235, 255), (corpo.centerx, corpo.y + 10), 5, 1)
        if self.tipo in ("corredor", "rapido"):
            pygame.draw.line(tela, AMARELO, (corpo.x + 8, corpo.y + 10), (corpo.x + 22, corpo.y + 4), 2)
            pygame.draw.line(tela, AMARELO, (corpo.right - 8, corpo.y + 10), (corpo.right - 22, corpo.y + 4), 2)
        if self.tipo in ("bruto", "tanque", "chefe_devorador"):
            pygame.draw.rect(tela, (60, 18, 22), corpo.inflate(-10, -4), 2, border_radius=8)
        if hospital:
            desenhar_roupa_medico(tela, corpo, self.tipo)
        elif infantil:
            desenhar_acessorio_infantil(tela, corpo, self.tipo)
        desenhar_careta(tela, corpo, self.face)
        perna_y = corpo.bottom - 4
        pygame.draw.line(tela, ROXO_ESCURO, (corpo.x + 14, perna_y), (corpo.x + 10 + (offset if animar_monstro else 0), perna_y + 10), 4)
        pygame.draw.line(tela, ROXO_ESCURO, (corpo.right - 14, perna_y), (corpo.right - 10 - (offset if animar_monstro else 0), perna_y + 10), 4)
