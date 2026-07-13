# Sono Profundo - main.py
# v1.24.36: Splash Screen, Menu finalizado, Game Over, Vitória, carregamento e prólogo.
# Use este arquivo como main.py na pasta do projeto.

import sys
import math
import random
import os
import json
import pygame

# APK/Pydroid: garante que arquivos como save.json, menu_config.json e assets
# sejam carregados a partir da pasta do jogo, mesmo quando o Android muda o diretório atual.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# Tela cheia vertical para Android.
# Usa a resolução real do aparelho e mantém orientação retrato.
pygame.init()
try:
    _info = pygame.display.Info()
    _w = int(getattr(_info, "current_w", 0) or 0)
    _h = int(getattr(_info, "current_h", 0) or 0)
except Exception:
    _w, _h = 0, 0

if _w <= 0 or _h <= 0:
    _w, _h = 720, 1280

# Se algum aparelho/report vier em paisagem, troca para retrato.
LARGURA = min(_w, _h)
ALTURA = max(_w, _h)
FPS = 60

# IMPORTANTE:
# O jogo.py usa valores importados do config.py.
# Por isso forçamos o config ANTES de importar Jogo.
# Assim o menu E a partida usam a mesma tela cheia vertical.
try:
    import config as cfg
    cfg.LARGURA = LARGURA
    cfg.ALTURA = ALTURA
    cfg.FPS = FPS
except Exception:
    cfg = None

# Importa o jogo real depois de travar a resolução.
# Deixe jogo.py na mesma pasta deste main.py.
from jogo import Jogo

# Paleta segura, sem depender do config.py.
BRANCO = (245, 245, 245)
PRETO = (0, 0, 0)
AMARELO = (245, 205, 70)
AMARELO_CLARO = (255, 232, 120)
AMARELO_ESCURO = (145, 105, 25)
VERMELHO = (220, 60, 70)
VERMELHO_ESCURO = (80, 18, 24)
VERDE = (80, 220, 120)
VERDE_ESCURO = (25, 90, 45)
ROXO = (120, 75, 190)
ROXO_CLARO = (190, 150, 255)
CINZA = (90, 90, 105)
CINZA_CLARO = (170, 170, 185)
FUNDO = (7, 7, 13)
MENU_CONFIG_ARQ = "menu_config.json"


def clamp(v, a, b):
    return max(a, min(b, v))


class BotaoMenu:
    def __init__(self, x, y, w, h, texto, acao, tipo="normal"):
        self.base_rect = pygame.Rect(x, y, w, h)
        self.rect = self.base_rect.copy()
        self.texto = texto
        self.acao = acao
        self.tipo = tipo
        self.pressionado = 0.0
        self.hover_t = 0.0

    def atualizar(self, dt):
        self.pressionado = max(0.0, self.pressionado - dt)
        mouse = pygame.mouse.get_pos()
        alvo = 1.0 if self.base_rect.collidepoint(mouse) else 0.0
        vel = 7.0 * dt
        if alvo > self.hover_t:
            self.hover_t = min(alvo, self.hover_t + vel)
        else:
            self.hover_t = max(alvo, self.hover_t - vel)
        extra = int(8 * self.hover_t + 4 * (self.pressionado > 0))
        self.rect = self.base_rect.inflate(extra, extra)

    def clicar(self, pos):
        if self.base_rect.collidepoint(pos):
            self.pressionado = 0.13
            return self.acao
        return None

    def desenhar_icone(self, tela, cx, cy, pronto=True):
        cor = AMARELO_CLARO if pronto else CINZA_CLARO
        escuro = (20, 20, 28)
        if self.acao in ("novo", "continuar"):
            pts = [(cx-6, cy-13), (cx-6, cy+13), (cx+13, cy)]
            pygame.draw.polygon(tela, cor, pts)
            pygame.draw.polygon(tela, escuro, pts, 2)
        elif self.acao == "conquistas":
            pygame.draw.rect(tela, cor, (cx-12, cy-6, 24, 18), border_radius=3)
            pygame.draw.rect(tela, escuro, (cx-7, cy+12, 14, 5), border_radius=2)
            pygame.draw.line(tela, cor, (cx-15, cy-2), (cx-24, cy-9), 3)
            pygame.draw.line(tela, cor, (cx+15, cy-2), (cx+24, cy-9), 3)
        elif self.acao == "config":
            pygame.draw.circle(tela, cor, (cx, cy), 13, 3)
            pygame.draw.circle(tela, escuro, (cx, cy), 4)
            for ang in range(0, 360, 60):
                ax = math.cos(math.radians(ang)); ay = math.sin(math.radians(ang))
                pygame.draw.line(tela, cor, (int(cx+ax*14), int(cy+ay*14)), (int(cx+ax*19), int(cy+ay*19)), 3)
        elif self.acao == "creditos":
            pygame.draw.circle(tela, cor, (cx, cy-7), 7)
            pygame.draw.rect(tela, cor, (cx-12, cy+2, 24, 18), border_radius=6)
        elif self.acao == "sair":
            pygame.draw.rect(tela, cor, (cx-12, cy-15, 20, 30), 3)
            pygame.draw.line(tela, cor, (cx-2, cy), (cx+17, cy), 3)
            pygame.draw.polygon(tela, cor, [(cx+17, cy), (cx+9, cy-7), (cx+9, cy+7)])
        elif self.acao == "voltar":
            pygame.draw.line(tela, cor, (cx+14, cy), (cx-12, cy), 4)
            pygame.draw.polygon(tela, cor, [(cx-12, cy), (cx-2, cy-10), (cx-2, cy+10)])
        else:
            pygame.draw.circle(tela, cor, (cx, cy), 12)

    def desenhar(self, tela, fonte):
        r = self.rect
        borda = VERMELHO if self.tipo == "perigo" else AMARELO
        brilho = AMARELO_CLARO if self.hover_t > 0.3 or self.pressionado > 0 else borda

        pygame.draw.rect(tela, (2, 2, 6), r.move(0, 7), border_radius=20)
        fundo1 = (33, 28, 43) if self.tipo != "perigo" else (42, 18, 24)
        fundo2 = (54, 45, 30) if self.pressionado > 0 else fundo1
        pygame.draw.rect(tela, fundo2, r, border_radius=20)
        pygame.draw.rect(tela, (15, 15, 22), r.inflate(-7, -7), 1, border_radius=16)
        pygame.draw.rect(tela, brilho, r, 3 if self.hover_t > 0.2 else 2, border_radius=20)

        # brilho lateral
        if self.hover_t > 0.05:
            pygame.draw.line(tela, AMARELO_CLARO, (r.x+20, r.y+7), (r.right-20, r.y+7), 2)

        self.desenhar_icone(tela, r.x + 48, r.centery)
        txt = fonte.render(self.texto, True, BRANCO)
        tela.blit(txt, txt.get_rect(midleft=(r.x + 86, r.centery)))


class Nevoa:
    def __init__(self):
        self.x = random.uniform(-120, LARGURA)
        self.y = random.uniform(160, ALTURA-160)
        self.w = random.randint(120, 260)
        self.h = random.randint(12, 28)
        self.vel = random.uniform(8, 24)
        self.cor = random.choice([(24, 24, 36), (30, 30, 44), (36, 34, 48)])

    def atualizar(self, dt):
        self.x += self.vel * dt
        if self.x > LARGURA + 140:
            self.x = -self.w - random.randint(20, 180)
            self.y = random.uniform(160, ALTURA-160)

    def desenhar(self, tela):
        # Sem alpha: elipses bem escuras, leves no Android.
        pygame.draw.ellipse(tela, self.cor, (int(self.x), int(self.y), self.w, self.h))
        pygame.draw.ellipse(tela, (15, 15, 24), (int(self.x+20), int(self.y+4), max(20, self.w-40), max(8, self.h-8)), 1)


class Poeira:
    def __init__(self):
        self.x = random.uniform(0, LARGURA)
        self.y = random.uniform(0, ALTURA)
        self.vel = random.uniform(6, 18)
        self.r = random.choice([1, 1, 2])
        self.osc = random.random() * 6.28

    def atualizar(self, dt):
        self.y -= self.vel * dt
        self.x += math.sin(pygame.time.get_ticks() * 0.001 + self.osc) * 0.15
        if self.y < -5:
            self.y = ALTURA + 5
            self.x = random.uniform(0, LARGURA)

    def desenhar(self, tela):
        pygame.draw.circle(tela, (70, 70, 88), (int(self.x), int(self.y)), self.r)


class OlhosSombra:
    def __init__(self):
        self.t = random.uniform(1.5, 5.0)
        self.visivel = 0.0
        self.x = random.choice([random.randint(30, 160), random.randint(LARGURA-160, LARGURA-30)])
        self.y = random.randint(290, 740)

    def atualizar(self, dt):
        self.t -= dt
        if self.t <= 0:
            self.visivel = 1.0
            self.t = random.uniform(4.0, 8.0)
            self.x = random.choice([random.randint(30, 160), random.randint(LARGURA-160, LARGURA-30)])
            self.y = random.randint(290, 720)
        else:
            self.visivel = max(0.0, self.visivel - dt * 0.7)

    def desenhar(self, tela):
        if self.visivel <= 0:
            return
        cor = (int(180*self.visivel), int(25*self.visivel), int(35*self.visivel))
        pygame.draw.ellipse(tela, cor, (self.x-16, self.y-5, 18, 10))
        pygame.draw.ellipse(tela, cor, (self.x+10, self.y-5, 18, 10))
        pygame.draw.circle(tela, (20, 0, 0), (self.x-7, self.y), 2)
        pygame.draw.circle(tela, (20, 0, 0), (self.x+19, self.y), 2)


class SombraMonstro:
    def __init__(self):
        self.reset(True)

    def reset(self, inicial=False):
        self.x = -80 if not inicial else random.randint(-400, -80)
        self.y = random.randint(650, 770)
        self.vel = random.uniform(18, 34)
        self.ativo = random.random() < 0.55
        self.espera = random.uniform(3.0, 9.0)

    def atualizar(self, dt):
        if not self.ativo:
            self.espera -= dt
            if self.espera <= 0:
                self.ativo = True
                self.x = -80
            return
        self.x += self.vel * dt
        if self.x > LARGURA + 80:
            self.reset(False)
            self.ativo = False

    def desenhar(self, tela):
        if not self.ativo:
            return
        x, y = int(self.x), int(self.y)
        cor = (18, 18, 24)
        pygame.draw.ellipse(tela, (0,0,0), (x-18, y+36, 44, 10))
        pygame.draw.rect(tela, cor, (x-10, y, 24, 40), border_radius=8)
        pygame.draw.circle(tela, cor, (x+2, y-10), 13)
        # braços e pernas simples
        pygame.draw.line(tela, cor, (x-8, y+12), (x-25, y+25), 5)
        pygame.draw.line(tela, cor, (x+13, y+13), (x+28, y+28), 5)
        passo = math.sin(pygame.time.get_ticks()*0.007)
        pygame.draw.line(tela, cor, (x-4, y+38), (x-14, y+58+int(passo*4)), 5)
        pygame.draw.line(tela, cor, (x+10, y+38), (x+22, y+58-int(passo*4)), 5)
        pygame.draw.circle(tela, (120, 18, 28), (x-3, y-12), 2)
        pygame.draw.circle(tela, (120, 18, 28), (x+8, y-12), 2)


class MenuPrincipal:
    def __init__(self, tela):
        self.tela = tela
        # v1.24.36: primeira tela exibida ao abrir o jogo.
        self.estado = "splash"
        self.splash_tempo = 0.0
        self.splash_duracao = 5.00
        self.aviso_tempo = 0.0
        self.aviso_duracao = 5.00
        self.jogo = None
        self.relogio = pygame.time.Clock()
        self.tempo = 0.0
        self.transicao = 0.0
        self.qualidade = "MÉDIA"
        self.vibracao = True
        self.auto_save = True
        # Histórias da campanha.
        self.historia_vista = False
        self.prologo_idx = 0
        self.prologo_tempo = 0.0
        self.prologo_apos = None
        self.prologo_modo = "inicio"
        self.prologo_titulo = "PRÓLOGO"
        self.prologo_paginas = self.paginas_historia("inicio")
        # v1.24.33: sistema de telas de carregamento/transição.
        self.carregando = False
        self.carregando_tempo = 0.0
        self.carregando_duracao = 1.05
        self.carregando_texto = "Carregando..."
        self.carregando_dica = "Melhore a porta antes dos chefes."
        self.carregando_destino = "menu"
        self.carregando_acao = None
        self.dicas_carregamento = [
            "Melhore a porta antes das noites de chefe.",
            "Itens lendários mudam completamente a partida.",
            "O Cofre Supremo ajuda muito em partidas longas.",
            "O Laser Supremo é excelente contra chefes.",
            "Use habilidades quando a porta estiver em perigo.",
            "Brutos resistem mais, mas podem ser controlados.",
        ]
        self.carregar_config_menu()

        self.fonte_titulo = pygame.font.SysFont("arial", 64, bold=True)
        self.fonte_zennick = pygame.font.SysFont("arial", 82, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("arial", 25, bold=True)
        self.fonte = pygame.font.SysFont("arial", 31, bold=True)
        self.fonte_pequena = pygame.font.SysFont("arial", 21)
        self.fonte_mini = pygame.font.SysFont("arial", 16)

        self.nevoas = [Nevoa() for _ in range(10)]
        self.poeiras = [Poeira() for _ in range(34)]
        self.olhos = [OlhosSombra() for _ in range(3)]
        self.sombra_monstro = SombraMonstro()
        self.criar_botoes()


    def carregar_config_menu(self):
        try:
            if os.path.exists(MENU_CONFIG_ARQ):
                with open(MENU_CONFIG_ARQ, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.qualidade = str(dados.get("qualidade", self.qualidade)).upper()
                self.vibracao = bool(dados.get("vibracao", self.vibracao))
                self.auto_save = bool(dados.get("auto_save", self.auto_save))
                self.historia_vista = bool(dados.get("historia_vista", self.historia_vista))
        except Exception:
            pass

    def salvar_config_menu(self):
        try:
            dados = {
                "qualidade": self.qualidade,
                "vibracao": self.vibracao,
                "auto_save": self.auto_save,
                "historia_vista": self.historia_vista,
            }
            with open(MENU_CONFIG_ARQ, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def carregar_save_resumo(self):
        try:
            from progresso import carregar_save
            save = carregar_save()
            if isinstance(save, dict):
                return save
        except Exception:
            pass
        return {}

    def criar_botoes(self):
        w = int(LARGURA * 0.84)
        h = 72
        x = (LARGURA - w) // 2
        y0 = 500
        gap = 18
        self.botoes_menu = [
            BotaoMenu(x, y0 + (h+gap)*0, w, h, "NOVO JOGO", "novo"),
            BotaoMenu(x, y0 + (h+gap)*1, w, h, "CONTINUAR", "continuar"),
            BotaoMenu(x, y0 + (h+gap)*2, w, h, "CONQUISTAS", "conquistas"),
            BotaoMenu(x, y0 + (h+gap)*3, w, h, "CONFIGURAÇÕES", "config"),
            BotaoMenu(x, y0 + (h+gap)*4, w, h, "CRÉDITOS", "creditos"),
            BotaoMenu(x, y0 + (h+gap)*5, w, h, "SAIR", "sair", "perigo"),
        ]
        self.botoes_config = [
            BotaoMenu(x, 455, w, h, "QUALIDADE: MÉDIA", "qualidade"),
            BotaoMenu(x, 545, w, h, "VIBRAÇÃO: ON", "vibracao"),
            BotaoMenu(x, 635, w, h, "AUTO SAVE: ON", "autosave"),
            BotaoMenu(x, 755, w, h, "VOLTAR", "voltar"),
        ]
        self.botao_voltar = BotaoMenu(x, 980, w, h, "VOLTAR", "voltar")
        self.botao_voltar_curto = BotaoMenu(x, 840, w, h, "VOLTAR", "voltar")
        # v1.24.31: botões da tela de Game Over.
        self.botoes_gameover = [
            BotaoMenu(x, 690, w, h, "TENTAR NOVAMENTE", "tentar_novamente"),
            BotaoMenu(x, 780, w, h, "VOLTAR AO MENU", "menu_gameover"),
            BotaoMenu(x, 870, w, h, "AD CONTINUA", "ad_continua"),
        ]
        # v1.24.32: botões da tela de Vitória.
        self.botoes_vitoria = [
            BotaoMenu(x, 760, w, h, "CONTINUAR CAMPANHA", "continuar_vitoria"),
            BotaoMenu(x, 850, w, h, "NOVA PARTIDA", "nova_vitoria"),
            BotaoMenu(x, 940, w, h, "VOLTAR AO MENU", "menu_vitoria"),
        ]
        # v1.24.34: botões do prólogo.
        self.botoes_prologo = [
            BotaoMenu(x, ALTURA - 380, w, h, "CONTINUAR", "prologo_proximo"),
            BotaoMenu(x, ALTURA - 290, w, h, "PULAR HISTÓRIA", "prologo_pular"),
        ]

    def iniciar_carregamento(self, texto, destino, acao=None, duracao=1.05):
        """v1.24.33: abre uma tela curta de carregamento antes de trocar de estado."""
        self.carregando = True
        self.carregando_tempo = 0.0
        self.carregando_duracao = max(0.35, float(duracao))
        self.carregando_texto = texto
        self.carregando_destino = destino
        self.carregando_acao = acao
        try:
            self.carregando_dica = random.choice(self.dicas_carregamento)
        except Exception:
            self.carregando_dica = "Prepare suas defesas antes da noite começar."
        self.estado = "carregamento"

    def executar_carregamento(self):
        """Executa a ação pesada só quando a barra termina."""
        acao = self.carregando_acao
        destino = self.carregando_destino
        self.carregando = False
        self.carregando_acao = None

        if callable(acao):
            acao()
        else:
            self.estado = destino

    def paginas_historia(self, modo="inicio"):
        if modo == "doutor":
            return [
                ["...o Doutor Infectado", "foi derrotado..."],
                ["Mas os gritos", "não pararam."],
                ["Uma criança chorava", "no andar acima."],
                ["As portas da Ala Infantil", "se abriram sozinhas..."],
                ["Seu pesadelo estava", "apenas começando."],
                ["ALA INFANTIL", "Capítulo 2"],
            ]
        if modo == "baba_final":
            return [
                ["A Babá Sombria desapareceu", "entre luzes brancas."],
                ["O silêncio tomou conta", "da Ala Infantil."],
                ["Mas outras portas ainda", "continuavam trancadas."],
                ["EM BREVE", "NOVOS ANDARES"],
            ]
        return [
            ["Era apenas mais uma noite..."],
            ["Você acordou preso em um corredor", "que parecia não ter fim."],
            ["A porta era a única coisa", "entre você e os pesadelos."],
            ["Algo estava vindo.", "E vinha cada vez mais rápido."],
            ["Cada noite...", "os pesadelos ficam mais fortes."],
            ["A única saída...", "é sobreviver."],
        ]

    def iniciar_prologo(self, depois=None, modo="inicio"):
        """Abre uma cena de história da campanha."""
        self.prologo_idx = 0
        self.prologo_tempo = 0.0
        self.prologo_apos = depois
        self.prologo_modo = modo
        self.prologo_paginas = self.paginas_historia(modo)
        self.prologo_titulo = "ALA INFANTIL" if modo == "doutor" else ("CAPÍTULO" if modo in ("baba_final",) else "PRÓLOGO")
        self.estado = "prologo"

    def finalizar_prologo(self):
        self.historia_vista = True
        self.salvar_config_menu()
        acao = self.prologo_apos
        self.prologo_apos = None
        if callable(acao):
            acao()
        else:
            self.estado = "menu"

    def avancar_prologo(self):
        if self.prologo_idx < len(self.prologo_paginas) - 1:
            self.prologo_idx += 1
            self.prologo_tempo = 0.0
        else:
            self.finalizar_prologo()

    def pular_prologo(self):
        self.finalizar_prologo()

    def iniciar_jogo_direto(self, novo=True):
        self.jogo = Jogo(self.tela)
        if novo:
            self.jogo.reiniciar()
        # Cada partida nova/continuada ganha 1 continuação por anúncio simulado.
        self.ad_continua_usado = False
        self.estado = "jogo"

    def iniciar_jogo(self, novo=True):
        texto = "Entrando no pesadelo..." if novo else "Carregando progresso..."
        self.iniciar_carregamento(texto, "jogo", lambda: self.iniciar_jogo_direto(novo), 1.10)

    def desenhar_corredor(self):
        self.tela.fill(FUNDO)

        # Vinheta/paredes laterais
        pygame.draw.rect(self.tela, (10, 9, 16), (0, 0, LARGURA, ALTURA))
        for y in range(0, ALTURA, 38):
            cor = (12, 12, 21) if (y // 38) % 2 == 0 else (8, 8, 15)
            pygame.draw.rect(self.tela, cor, (0, y, LARGURA, 38))

        # Corredor em perspectiva
        topo_y = 265
        fundo_y = 890
        centro = LARGURA // 2
        pygame.draw.polygon(self.tela, (18, 18, 27), [(110, topo_y), (LARGURA-110, topo_y), (LARGURA-15, fundo_y), (15, fundo_y)])
        pygame.draw.polygon(self.tela, (24, 22, 28), [(190, topo_y+45), (LARGURA-190, topo_y+45), (LARGURA-70, fundo_y), (70, fundo_y)])
        pygame.draw.line(self.tela, (64, 52, 78), (110, topo_y), (15, fundo_y), 3)
        pygame.draw.line(self.tela, (64, 52, 78), (LARGURA-110, topo_y), (LARGURA-15, fundo_y), 3)

        # Piso com linhas de profundidade
        for i in range(8):
            yy = topo_y + 80 + i * 72
            largura_linha = int(120 + i * 54)
            pygame.draw.line(self.tela, (38, 34, 44), (centro-largura_linha, yy), (centro+largura_linha, yy), 2)
        for xoff in (-220, -120, 120, 220):
            pygame.draw.line(self.tela, (28, 26, 36), (centro + xoff//3, topo_y+45), (centro + xoff, fundo_y), 2)

        # Porta distante/fundo
        pygame.draw.rect(self.tela, (8, 8, 12), (centro-82, topo_y+15, 164, 175), border_radius=8)
        pygame.draw.rect(self.tela, (54, 40, 68), (centro-72, topo_y+26, 144, 160), 3, border_radius=8)
        pygame.draw.circle(self.tela, (120, 80, 24), (centro+51, topo_y+106), 5)

        # Luz piscante
        luz = 40 + int((math.sin(self.tempo*2.2) + 1) * 15)
        pygame.draw.circle(self.tela, (luz, luz-12, 28), (centro, 225), 34, 2)
        pygame.draw.line(self.tela, (85, 70, 38), (centro, 150), (centro, 205), 3)

        # Bordas escuras
        pygame.draw.rect(self.tela, (4,4,8), (0,0,34,ALTURA))
        pygame.draw.rect(self.tela, (4,4,8), (LARGURA-34,0,34,ALTURA))
        pygame.draw.rect(self.tela, (0,0,0), (0,0,LARGURA,55))
        pygame.draw.rect(self.tela, (0,0,0), (0,ALTURA-70,LARGURA,70))

    def desenhar_logo(self):
        pulso = (math.sin(self.tempo * 2.4) + 1) * 0.5
        y = 180
        # Lua
        pygame.draw.circle(self.tela, (210, 195, 120), (LARGURA//2, 88), 42)
        pygame.draw.circle(self.tela, FUNDO, (LARGURA//2 + 18, 76), 40)

        # Título com sombra/brilho
        sombra = self.fonte_titulo.render("SONO PROFUNDO", True, (22, 15, 4))
        self.tela.blit(sombra, sombra.get_rect(center=(LARGURA//2+3, y+5)))
        brilho_cor = (245, 205 + int(35*pulso), 70 + int(45*pulso))
        titulo = self.fonte_titulo.render("SONO PROFUNDO", True, brilho_cor)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA//2, y)))
        pygame.draw.line(self.tela, AMARELO_ESCURO, (115, y+48), (LARGURA-115, y+48), 3)
        pygame.draw.line(self.tela, AMARELO_CLARO, (180, y+54), (LARGURA-180, y+54), 1)

        sub = self.fonte_subtitulo.render("PESADELOS NO CORREDOR", True, (192, 190, 210))
        self.tela.blit(sub, sub.get_rect(center=(LARGURA//2, y+86)))
        beta = self.fonte_pequena.render("BETA 0.1", True, AMARELO)
        self.tela.blit(beta, beta.get_rect(center=(LARGURA//2, y+122)))

        # Cama pixel art pequena
        cx, cy = LARGURA//2, 365
        pygame.draw.rect(self.tela, (10, 10, 16), (cx-95, cy+30, 190, 18), border_radius=8)
        pygame.draw.rect(self.tela, (42, 32, 54), (cx-88, cy-18, 176, 52), border_radius=10)
        pygame.draw.rect(self.tela, (94, 72, 126), (cx-72, cy-5, 145, 28), border_radius=7)
        pygame.draw.rect(self.tela, (220, 210, 185), (cx-72, cy-24, 48, 27), border_radius=6)
        pygame.draw.rect(self.tela, AMARELO, (cx-88, cy+25, 176, 8), border_radius=3)
        # Zzz sem emoji
        z = self.fonte_pequena.render("Z z z", True, (170, 150, 210))
        self.tela.blit(z, z.get_rect(center=(cx+65, cy-36)))

    def desenhar_fundo_vivo(self):
        self.desenhar_corredor()
        self.sombra_monstro.desenhar(self.tela)
        for n in self.nevoas:
            n.desenhar(self.tela)
        for p in self.poeiras:
            p.desenhar(self.tela)
        for o in self.olhos:
            o.desenhar(self.tela)

    def desenhar_menu(self):
        self.desenhar_fundo_vivo()
        self.desenhar_logo()
        for b in self.botoes_menu:
            b.desenhar(self.tela, self.fonte)
        txt = self.fonte_mini.render("TELA CHEIA • PIXEL ART NÍTIDA", True, (130, 130, 150))
        self.tela.blit(txt, txt.get_rect(center=(LARGURA//2, ALTURA-34)))

    def desenhar_config(self):
        self.desenhar_fundo_vivo()
        titulo = self.fonte_titulo.render("CONFIGURAÇÕES", True, AMARELO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA//2, 235)))
        desc = [
            "Menu final para a versão Beta.",
            "Tela cheia retrato, sem imagem borrada.",
            "Configurações salvas automaticamente.",
        ]
        y = 310
        for linha in desc:
            t = self.fonte_pequena.render(linha, True, CINZA_CLARO)
            self.tela.blit(t, t.get_rect(center=(LARGURA//2, y)))
            y += 32
        self.botoes_config[0].texto = f"QUALIDADE: {self.qualidade}"
        self.botoes_config[1].texto = "VIBRAÇÃO: ON" if self.vibracao else "VIBRAÇÃO: OFF"
        self.botoes_config[2].texto = "AUTO SAVE: ON" if self.auto_save else "AUTO SAVE: OFF"
        for b in self.botoes_config:
            b.desenhar(self.tela, self.fonte)

    def desenhar_creditos(self):
        self.desenhar_fundo_vivo()
        titulo = self.fonte_titulo.render("CRÉDITOS", True, AMARELO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA//2, 225)))
        painel = pygame.Rect(70, 320, LARGURA-140, 500)
        pygame.draw.rect(self.tela, (12, 12, 20), painel, border_radius=24)
        pygame.draw.rect(self.tela, AMARELO_ESCURO, painel, 2, border_radius=24)
        linhas = [
            "SONO PROFUNDO",
            "",
            "Criado por Feliphe Alex",
            "Desenvolvido em Python + Pygame",
            "Menu 9:16 fixo para Android",
            "Preparado para APK via Termux",
            "",
            "Obrigado por jogar!",
        ]
        y = painel.y + 55
        for linha in linhas:
            cor = AMARELO if linha == "SONO PROFUNDO" else BRANCO
            fonte = self.fonte if linha == "SONO PROFUNDO" else self.fonte_pequena
            txt = fonte.render(linha, True, cor)
            self.tela.blit(txt, txt.get_rect(center=(LARGURA//2, y)))
            y += 48 if linha else 24
        self.botao_voltar.desenhar(self.tela, self.fonte)

    def desenhar_conquistas(self):
        self.desenhar_fundo_vivo()
        titulo = self.fonte_titulo.render("CONQUISTAS", True, AMARELO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA//2, 210)))

        save = self.carregar_save_resumo()
        lendarios = save.get("lendarios_desbloqueados", [])
        if not isinstance(lendarios, (list, tuple, set)):
            lendarios = []

        painel = pygame.Rect(55, 300, LARGURA-110, 520)
        pygame.draw.rect(self.tela, (12, 12, 20), painel, border_radius=24)
        pygame.draw.rect(self.tela, AMARELO_ESCURO, painel, 2, border_radius=24)

        linhas = [
            ("RECORDE", f"Noite {int(save.get('recorde_noite', 0))}"),
            ("FRAGMENTOS", str(int(save.get('fragmentos', 0)))),
            ("FRAG. LENDÁRIOS", str(int(save.get('fragmentos_lendarios', 0)))),
            ("LENDÁRIOS", f"{len(lendarios)} / 4"),
            ("HABILIDADES USADAS", str(int(save.get('habilidades_usadas', 0)))),
        ]

        y = painel.y + 62
        for nome, valor in linhas:
            pygame.draw.rect(self.tela, (20, 20, 30), (painel.x+28, y-22, painel.w-56, 44), border_radius=12)
            n = self.fonte_pequena.render(nome, True, CINZA_CLARO)
            v = self.fonte_pequena.render(valor, True, AMARELO)
            self.tela.blit(n, n.get_rect(midleft=(painel.x+48, y)))
            self.tela.blit(v, v.get_rect(midright=(painel.right-48, y)))
            y += 72

        dica = self.fonte_mini.render("Os dados vêm do save atual do progresso.", True, (130, 130, 150))
        self.tela.blit(dica, dica.get_rect(center=(LARGURA//2, painel.bottom-30)))
        self.botao_voltar_curto.desenhar(self.tela, self.fonte)

    def preparar_game_over(self):
        """v1.24.31: congela a partida e abre a tela de Game Over."""
        if not self.jogo:
            self.estado = "menu"
            return
        self.estado = "gameover"
        try:
            self.jogo.pausado = True
        except Exception:
            pass

    def tentar_novamente_direto(self):
        """Reinicia uma partida limpa sem passar novamente pela tela de carregamento."""
        self.iniciar_jogo_direto(novo=True)

    def tentar_novamente(self):
        """Reinicia uma partida limpa."""
        self.iniciar_carregamento("Recriando o pesadelo...", "jogo", self.tentar_novamente_direto, 0.95)

    def voltar_menu_gameover_direto(self):
        """Sai da partida atual e volta ao menu sem nova transição."""
        self.jogo = None
        self.estado = "menu"

    def voltar_menu_gameover(self):
        """Sai da partida atual e volta ao menu."""
        self.iniciar_carregamento("Despertando...", "menu", self.voltar_menu_gameover_direto, 0.75)

    def ad_continua_direto(self):
        """Simulação do rewarded ad: revive uma vez e continua na mesma noite."""
        if not self.jogo:
            self.estado = "menu"
            return
        if getattr(self, "ad_continua_usado", False):
            return
        self.ad_continua_usado = True
        try:
            self.jogo.jogo_acabou = False
            self.jogo.vitoria = False
            self.jogo.pausado = False
            self.jogo.vida_porta = max(1, int(getattr(self.jogo, "vida_porta_max", 100) * 0.45))
            self.jogo.vida_porta_display = float(self.jogo.vida_porta)
            self.jogo.tremor_porta = 0
            self.jogo.porta_em_ataque = False
            self.jogo.mostrar_mensagem("AD CONTINUA: porta restaurada!", 1.8)
        except Exception:
            pass
        self.estado = "jogo"

    def ad_continua(self):
        if getattr(self, "ad_continua_usado", False):
            return
        self.iniciar_carregamento("Assistindo anúncio...", "jogo", self.ad_continua_direto, 1.20)

    def dados_game_over(self):
        if not self.jogo:
            return {"noite": 0, "derrotados": 0, "moedas": 0}
        return {
            "noite": int(getattr(self.jogo, "noite", 0)),
            "derrotados": int(getattr(self.jogo, "total_derrotados", getattr(self.jogo, "derrotados", 0))),
            "moedas": int(getattr(self.jogo, "moedas", 0)),
        }

    def preparar_vitoria(self):
        """v1.24.32: congela a partida e abre a tela de Vitória."""
        if not self.jogo:
            self.estado = "menu"
            return
        self.estado = "vitoria"
        try:
            self.jogo.pausado = True
        except Exception:
            pass

    def continuar_vitoria_direto(self):
        """Continua a campanha/salve atual após a vitória sem nova transição."""
        if not self.jogo:
            self.estado = "menu"
            return
        try:
            self.jogo.jogo_acabou = False
            self.jogo.vitoria = False
            self.jogo.pausado = False
            if hasattr(self.jogo, "preparar_noite"):
                self.jogo.preparar_noite()
            self.jogo.mostrar_mensagem("Campanha continuada!", 1.6)
        except Exception:
            pass
        self.estado = "jogo"

    def continuar_vitoria(self):
        """Continua a campanha/salve atual após a vitória."""
        self.iniciar_carregamento("Preparando próximo pesadelo...", "jogo", self.continuar_vitoria_direto, 0.95)

    def nova_vitoria(self):
        """Começa uma nova partida após vencer."""
        self.iniciar_carregamento("Começando nova campanha...", "jogo", lambda: self.iniciar_jogo_direto(True), 1.05)

    def voltar_menu_vitoria_direto(self):
        """Sai da tela de vitória e volta ao menu principal sem nova transição."""
        self.jogo = None
        self.estado = "menu"

    def voltar_menu_vitoria(self):
        """Sai da tela de vitória e volta ao menu principal."""
        self.iniciar_carregamento("Voltando ao menu...", "menu", self.voltar_menu_vitoria_direto, 0.75)

    def dados_vitoria(self):
        if not self.jogo:
            return {"noite": 0, "derrotados": 0, "moedas": 0, "fragmentos": 0, "fragmentos_lendarios": 0}
        return {
            "noite": int(getattr(self.jogo, "noite", 0)),
            "derrotados": int(getattr(self.jogo, "total_derrotados", getattr(self.jogo, "derrotados", 0))),
            "moedas": int(getattr(self.jogo, "moedas", 0)),
            "fragmentos": int(getattr(self.jogo, "fragmentos", 0)),
            "fragmentos_lendarios": int(getattr(self.jogo, "fragmentos_lendarios", 0)),
        }

    def processar_acao(self, acao):
        if acao == "novo":
            self.iniciar_prologo(lambda: self.iniciar_jogo(novo=True), "inicio")
        elif acao == "continuar":
            self.iniciar_jogo(novo=False)
        elif acao == "conquistas":
            self.estado = "conquistas"
        elif acao == "config":
            self.estado = "config"
        elif acao == "creditos":
            self.estado = "creditos"
        elif acao == "qualidade":
            ordem = ["BAIXA", "MÉDIA", "ALTA"]
            atual = self.qualidade if self.qualidade in ordem else "MÉDIA"
            self.qualidade = ordem[(ordem.index(atual) + 1) % len(ordem)]
            self.salvar_config_menu()
        elif acao == "vibracao":
            self.vibracao = not self.vibracao
            self.salvar_config_menu()
        elif acao == "autosave":
            self.auto_save = not self.auto_save
            self.salvar_config_menu()
        elif acao == "tentar_novamente":
            self.tentar_novamente()
        elif acao == "menu_gameover":
            self.voltar_menu_gameover()
        elif acao == "ad_continua":
            self.ad_continua()
        elif acao == "continuar_vitoria":
            self.continuar_vitoria()
        elif acao == "nova_vitoria":
            self.nova_vitoria()
        elif acao == "menu_vitoria":
            self.voltar_menu_vitoria()
        elif acao == "prologo_proximo":
            self.avancar_prologo()
        elif acao == "prologo_pular":
            self.pular_prologo()
        elif acao == "voltar":
            self.salvar_config_menu()
            self.estado = "menu"
        elif acao == "sair":
            pygame.quit()
            sys.exit()

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.estado == "splash":
                # Toque/tecla pula a logo para o aviso de ficção.
                if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self.estado = "aviso"
                    self.aviso_tempo = 0.0
                continue

            if self.estado == "aviso":
                # Toque/tecla pula o aviso para o menu.
                if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self.estado = "menu"
                continue

            if self.estado == "jogo":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.estado = "menu"
                    return
                if self.jogo:
                    self.jogo.eventos(evento)
                continue

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if self.estado == "prologo":
                    self.pular_prologo()
                else:
                    self.estado = "menu"

            if evento.type == pygame.KEYDOWN and self.estado == "prologo":
                if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.avancar_prologo()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                if self.estado == "menu":
                    botoes = self.botoes_menu
                elif self.estado == "config":
                    botoes = self.botoes_config
                elif self.estado == "creditos":
                    botoes = [self.botao_voltar]
                elif self.estado == "conquistas":
                    botoes = [self.botao_voltar_curto]
                elif self.estado == "gameover":
                    botoes = self.botoes_gameover
                elif self.estado == "vitoria":
                    botoes = self.botoes_vitoria
                elif self.estado == "carregamento":
                    botoes = []
                elif self.estado == "prologo":
                    botoes = self.botoes_prologo
                else:
                    botoes = []
                for b in botoes:
                    acao = b.clicar(pos)
                    if acao:
                        self.processar_acao(acao)
                        break

    def atualizar(self, dt):
        self.tempo += dt
        if self.estado == "splash":
            self.splash_tempo += dt
            for n in self.nevoas:
                n.atualizar(dt)
            for p in self.poeiras:
                p.atualizar(dt)
            if self.splash_tempo >= self.splash_duracao:
                self.estado = "aviso"
                self.aviso_tempo = 0.0
            return
        if self.estado == "aviso":
            self.aviso_tempo += dt
            if self.aviso_tempo >= self.aviso_duracao:
                self.estado = "menu"
            return
        if self.estado == "prologo":
            self.prologo_tempo += dt
            for n in self.nevoas:
                n.atualizar(dt)
            for p in self.poeiras:
                p.atualizar(dt)
            for o in self.olhos:
                o.atualizar(dt)
            self.sombra_monstro.atualizar(dt)
            todos_botoes = getattr(self, "botoes_prologo", [])
            for b in todos_botoes:
                b.atualizar(dt)
            return
        if self.estado == "carregamento":
            self.carregando_tempo += dt
            for n in self.nevoas:
                n.atualizar(dt)
            for p in self.poeiras:
                p.atualizar(dt)
            for o in self.olhos:
                o.atualizar(dt)
            self.sombra_monstro.atualizar(dt)
            if self.carregando_tempo >= self.carregando_duracao:
                self.executar_carregamento()
            return
        if self.estado == "jogo" and self.jogo:
            self.jogo.atualizar(dt)
            historia = getattr(self.jogo, "historia_pendente", None)
            if historia:
                self.jogo.historia_pendente = None
                try:
                    self.jogo.pausado = True
                except Exception:
                    pass
                if historia == "doutor":
                    def voltar_do_doutor():
                        if self.jogo:
                            # Depois da história, entra direto na Ala Infantil (2º andar).
                            try:
                                self.jogo.noite = max(int(getattr(self.jogo, "noite", 1)), 21)
                                self.jogo.ambiente_atual = "quarto_infantil"
                                self.jogo.save["ambiente_atual"] = "quarto_infantil"
                                info = self.jogo.campanha_info()
                                info["andar_atual"] = 2
                                desbloq = set(int(x) for x in info.get("andares_desbloqueados", [1]))
                                desbloq.add(2)
                                info["andares_desbloqueados"] = sorted(desbloq)
                                self.jogo.save["campanha"] = info
                                self.jogo.salvar_progresso()
                                self.jogo.preparar_noite()
                            except Exception:
                                pass
                            self.jogo.pausado = False
                            self.jogo.mostrar_mensagem("ALA INFANTIL - Capítulo 2", 3.0)
                        self.estado = "jogo"
                    self.iniciar_prologo(voltar_do_doutor, "doutor")
                elif historia == "baba_final":
                    def finalizar_baba():
                        if self.jogo:
                            self.jogo.jogo_acabou = True
                            self.jogo.vitoria = True
                        self.preparar_vitoria()
                    self.iniciar_prologo(finalizar_baba, "baba_final")
                return
            if getattr(self.jogo, "jogo_acabou", False):
                if getattr(self.jogo, "vitoria", False):
                    self.preparar_vitoria()
                else:
                    self.preparar_game_over()
            return
        for n in self.nevoas:
            n.atualizar(dt)
        for p in self.poeiras:
            p.atualizar(dt)
        for o in self.olhos:
            o.atualizar(dt)
        self.sombra_monstro.atualizar(dt)
        todos_botoes = self.botoes_menu + self.botoes_config + [self.botao_voltar, self.botao_voltar_curto] + getattr(self, "botoes_gameover", []) + getattr(self, "botoes_vitoria", []) + getattr(self, "botoes_prologo", [])
        for b in todos_botoes:
            b.atualizar(dt)

    def desenhar_splash(self):
        """Abertura ZENNICK antes do menu principal."""
        self.tela.fill((0, 0, 0))
        cx = LARGURA // 2
        cy = ALTURA // 2
        t = max(0.0, min(1.0, self.splash_tempo / max(0.01, self.splash_duracao)))

        if t < 0.25:
            fade = t / 0.25
        elif t > 0.78:
            fade = max(0.0, (1.0 - t) / 0.22)
        else:
            fade = 1.0
        brilho = int(255 * fade)
        cor = (brilho, brilho, min(255, brilho + 8))
        sombra = (20, 22, 34)
        dourado = (min(255, int(245 * fade)), min(255, int(205 * fade)), min(255, int(70 * fade)))

        pulso = (math.sin(self.splash_tempo * 7.0) + 1) * 0.5
        pygame.draw.circle(self.tela, (22, 22, 34), (cx, cy - 95), 16 + int(20 * pulso), 2)
        pygame.draw.circle(self.tela, dourado, (cx, cy - 95), 4 + int(3 * pulso))
        for i in range(26):
            ang = i * 0.83 + self.splash_tempo * 1.8
            dist = 55 + ((i * 19 + int(self.splash_tempo * 70)) % 145)
            x = int(cx + math.cos(ang) * dist)
            y = int(cy + math.sin(ang) * dist * 0.42)
            r = 1 if i % 4 else 2
            pygame.draw.circle(self.tela, (70, 70, 90), (x, y), r)

        tremor = 2 if 0.58 < t < 0.72 else 0
        ox = random.randint(-tremor, tremor) if tremor else 0
        oy = random.randint(-tremor, tremor) if tremor else 0
        txt_s = self.fonte_zennick.render("ZENNICK", True, sombra)
        txt = self.fonte_zennick.render("ZENNICK", True, cor)
        self.tela.blit(txt_s, txt_s.get_rect(center=(cx + 4 + ox, cy + 4 + oy)))
        self.tela.blit(txt, txt.get_rect(center=(cx + ox, cy + oy)))

        w = txt.get_width()
        y = cy + 66
        pygame.draw.line(self.tela, (55, 55, 75), (cx - w//2, y), (cx + w//2, y), 2)
        pygame.draw.line(self.tela, dourado, (cx - int(w*0.25), y), (cx + int(w*0.25), y), 2)

        dica = self.fonte_mini.render("Toque para pular", True, (90, 90, 105))
        self.tela.blit(dica, dica.get_rect(center=(cx, ALTURA - 105)))


    def desenhar_aviso_ficcao(self):
        """Aviso de ficção após a logo ZENNICK e antes do menu."""
        self.tela.fill((0, 0, 0))
        cx = LARGURA // 2
        cy = ALTURA // 2
        t = max(0.0, min(1.0, self.aviso_tempo / max(0.01, self.aviso_duracao)))
        if t < 0.22:
            fade = t / 0.22
        elif t > 0.78:
            fade = max(0.0, (1.0 - t) / 0.22)
        else:
            fade = 1.0
        brilho = int(235 * fade)
        fraco = int(165 * fade)
        dourado = (min(255, int(245 * fade)), min(255, int(205 * fade)), min(255, int(70 * fade)))

        # Partículas discretas, leves e sem transparência.
        for i in range(18):
            ang = i * 0.74 + self.aviso_tempo * 1.4
            dist = 70 + (i % 6) * 18
            x = int(cx + math.cos(ang) * dist)
            y = int(cy - 110 + math.sin(ang) * dist * 0.28)
            pygame.draw.circle(self.tela, (45, 45, 60), (x, y), 1 if i % 4 else 2)

        titulo = self.fonte.render("História Fictícia", True, (brilho, brilho, min(255, brilho + 8)))
        self.tela.blit(titulo, titulo.get_rect(center=(cx, cy - 120)))

        linha = self.fonte_pequena.render("Nada disso é real", True, (brilho, brilho, brilho))
        self.tela.blit(linha, linha.get_rect(center=(cx, cy - 62)))

        pygame.draw.line(self.tela, (55, 55, 75), (cx - 120, cy - 12), (cx + 120, cy - 12), 1)
        pygame.draw.line(self.tela, dourado, (cx - 55, cy - 12), (cx + 55, cy - 12), 2)

        nome = self.fonte_pequena.render("Felliphe Allex", True, dourado)
        self.tela.blit(nome, nome.get_rect(center=(cx, cy + 42)))
        ano = self.fonte_mini.render("© 2026", True, (fraco, fraco, fraco))
        self.tela.blit(ano, ano.get_rect(center=(cx, cy + 84)))

        dica = self.fonte_mini.render("Toque para pular", True, (80, 80, 95))
        self.tela.blit(dica, dica.get_rect(center=(cx, ALTURA - 105)))

    def desenhar_prologo(self):
        """Cenas de história da campanha."""
        self.desenhar_fundo_vivo()
        cx = LARGURA // 2
        painel = pygame.Rect(45, 230, LARGURA - 90, ALTURA - 440)
        pygame.draw.rect(self.tela, (6, 6, 12), painel, border_radius=28)
        pygame.draw.rect(self.tela, AMARELO_ESCURO, painel, 2, border_radius=28)
        pygame.draw.rect(self.tela, (24, 20, 32), painel.inflate(-18, -18), 1, border_radius=22)

        modo = getattr(self, "prologo_modo", "inicio")
        if modo in ("baba_final", "doutor"):
            # Transição cinematográfica: a tela escurece lentamente antes da próxima ala.
            escuro = pygame.Surface((LARGURA, ALTURA))
            escuro.fill((0, 0, 0))
            escuro.set_alpha(min(235, int(95 + self.prologo_idx * 26 + self.prologo_tempo * 42)))
            self.tela.blit(escuro, (0, 0))
        linhas = self.prologo_paginas[max(0, min(self.prologo_idx, len(self.prologo_paginas)-1))]
        primeira = linhas[0] if linhas else ""
        pulso = (math.sin(self.tempo * 2.2) + 1) * 0.5

        if modo == "inicio" and primeira == "ZENNICK":
            for i in range(18):
                ang = i * 0.95 + self.tempo
                dist = 70 + (i % 6) * 22
                pygame.draw.circle(self.tela, (82, 82, 110), (int(cx + math.cos(ang)*dist), int(painel.centery + math.sin(ang)*dist*0.36)), 1 if i % 3 else 2)
            txt_s = self.fonte_zennick.render("ZENNICK", True, (18, 18, 28))
            txt = self.fonte_zennick.render("ZENNICK", True, (235, 235, 245))
            self.tela.blit(txt_s, txt_s.get_rect(center=(cx+4, painel.centery+4)))
            self.tela.blit(txt, txt.get_rect(center=(cx, painel.centery)))
        elif modo == "inicio" and primeira == "FELLIPHE ALLEX":
            nome = self.fonte_titulo.render("FELLIPHE ALLEX", True, AMARELO)
            apr = self.fonte.render("APRESENTA", True, BRANCO)
            self.tela.blit(nome, nome.get_rect(center=(cx, painel.centery - 35)))
            self.tela.blit(apr, apr.get_rect(center=(cx, painel.centery + 45)))
        else:
            pygame.draw.circle(self.tela, (205, 190, 120), (cx, painel.y + 78), 38)
            pygame.draw.circle(self.tela, (6, 6, 12), (cx + 16, painel.y + 66), 37)
            porta_y = painel.y + 205
            pygame.draw.rect(self.tela, (12, 10, 14), (cx - 78, porta_y - 80, 156, 176), border_radius=8)
            pygame.draw.rect(self.tela, (54, 40, 68), (cx - 65, porta_y - 66, 130, 148), 3, border_radius=6)
            pygame.draw.circle(self.tela, (120, 80, 24), (cx + 44, porta_y + 12), 5)
            sombra_x = cx - 130 + int((self.prologo_idx % 5) * 38)
            pygame.draw.ellipse(self.tela, (0, 0, 0), (sombra_x - 18, porta_y + 104, 60, 12))
            pygame.draw.rect(self.tela, (15, 15, 22), (sombra_x, porta_y + 35, 26, 64), border_radius=8)
            pygame.draw.circle(self.tela, (15, 15, 22), (sombra_x + 13, porta_y + 24), 15)
            pygame.draw.circle(self.tela, (150 + int(60*pulso), 25, 35), (sombra_x + 7, porta_y + 21), 2)
            pygame.draw.circle(self.tela, (150 + int(60*pulso), 25, 35), (sombra_x + 18, porta_y + 21), 2)

            titulo = self.fonte.render(getattr(self, "prologo_titulo", "PRÓLOGO"), True, AMARELO)
            self.tela.blit(titulo, titulo.get_rect(center=(cx, painel.y + 330)))
            y = painel.y + 405
            brilho = int(120 + 125 * clamp(self.prologo_tempo / 0.65, 0.0, 1.0))
            cor_texto = (brilho, brilho, min(255, brilho + 10))
            destaque = ("EM BREVE" in linhas or "NOVOS ANDARES" in linhas)
            fonte_linha = self.fonte if destaque else self.fonte_pequena
            for linha in linhas:
                cor = AMARELO if linha in ("EM BREVE", "NOVOS ANDARES") else cor_texto
                txt = fonte_linha.render(linha, True, cor)
                self.tela.blit(txt, txt.get_rect(center=(cx, y)))
                y += 48 if destaque else 40

        etapa = self.fonte_mini.render(f"{self.prologo_idx + 1}/{len(self.prologo_paginas)}", True, (140, 140, 160))
        self.tela.blit(etapa, etapa.get_rect(center=(cx, painel.bottom - 42)))

        if self.prologo_idx >= len(self.prologo_paginas) - 1:
            self.botoes_prologo[0].texto = "ENTRAR NO PESADELO" if modo == "inicio" else "CONTINUAR"
        else:
            self.botoes_prologo[0].texto = "CONTINUAR"
        for b in self.botoes_prologo:
            b.desenhar(self.tela, self.fonte)

    def desenhar_carregamento(self):
        """v1.24.33: tela curta de carregamento com barra e dica."""
        self.desenhar_fundo_vivo()
        cx = LARGURA // 2
        progresso = 0.0
        if self.carregando_duracao > 0:
            progresso = clamp(self.carregando_tempo / self.carregando_duracao, 0.0, 1.0)

        painel = pygame.Rect(55, 340, LARGURA - 110, 470)
        pygame.draw.rect(self.tela, (8, 8, 14), painel, border_radius=28)
        pygame.draw.rect(self.tela, AMARELO_ESCURO, painel, 2, border_radius=28)
        pygame.draw.rect(self.tela, (28, 24, 36), painel.inflate(-18, -18), 1, border_radius=22)

        # Lua/cama pequena.
        pygame.draw.circle(self.tela, (210, 195, 120), (cx, painel.y + 70), 32)
        pygame.draw.circle(self.tela, (8, 8, 14), (cx + 14, painel.y + 60), 31)
        pygame.draw.rect(self.tela, (42, 32, 54), (cx-70, painel.y+130, 140, 38), border_radius=8)
        pygame.draw.rect(self.tela, (94, 72, 126), (cx-56, painel.y+142, 112, 18), border_radius=6)
        pygame.draw.rect(self.tela, (220, 210, 185), (cx-56, painel.y+122, 36, 24), border_radius=5)
        pygame.draw.rect(self.tela, AMARELO, (cx-70, painel.y+164, 140, 6), border_radius=3)

        titulo = self.fonte.render("SONO PROFUNDO", True, AMARELO)
        self.tela.blit(titulo, titulo.get_rect(center=(cx, painel.y + 215)))
        texto = self.fonte_pequena.render(self.carregando_texto, True, BRANCO)
        self.tela.blit(texto, texto.get_rect(center=(cx, painel.y + 260)))

        barra = pygame.Rect(painel.x + 55, painel.y + 305, painel.w - 110, 28)
        pygame.draw.rect(self.tela, (18, 18, 26), barra, border_radius=12)
        pygame.draw.rect(self.tela, (65, 55, 28), barra, 2, border_radius=12)
        preenchida = barra.copy()
        preenchida.w = max(8, int(barra.w * progresso))
        pygame.draw.rect(self.tela, AMARELO, preenchida, border_radius=12)
        pygame.draw.line(self.tela, AMARELO_CLARO, (preenchida.x+8, preenchida.y+7), (max(preenchida.x+8, preenchida.right-8), preenchida.y+7), 1)

        pct = self.fonte_mini.render(f"{int(progresso * 100)}%", True, CINZA_CLARO)
        self.tela.blit(pct, pct.get_rect(center=(cx, barra.bottom + 26)))

        dica_t = self.fonte_mini.render("DICA: " + self.carregando_dica, True, (145, 145, 165))
        self.tela.blit(dica_t, dica_t.get_rect(center=(cx, painel.bottom - 42)))

    def desenhar_game_over(self):
        """v1.24.31: tela final quando a porta cai."""
        self.desenhar_fundo_vivo()

        # Painel escuro central com clima de pesadelo.
        painel = pygame.Rect(50, 210, LARGURA - 100, 820)
        pygame.draw.rect(self.tela, (6, 6, 12), painel, border_radius=28)
        pygame.draw.rect(self.tela, VERMELHO, painel, 3, border_radius=28)
        pygame.draw.rect(self.tela, (40, 12, 18), painel.inflate(-18, -18), 2, border_radius=22)

        # Porta quebrada em pixel art simples.
        cx = LARGURA // 2
        py = 325
        pygame.draw.rect(self.tela, (16, 10, 12), (cx-80, py-86, 160, 180), border_radius=8)
        pygame.draw.rect(self.tela, (64, 38, 45), (cx-68, py-74, 136, 156), border_radius=6)
        pygame.draw.line(self.tela, (15, 8, 10), (cx-35, py-70), (cx-5, py+70), 7)
        pygame.draw.line(self.tela, (15, 8, 10), (cx+25, py-65), (cx+3, py+78), 6)
        pygame.draw.line(self.tela, (120, 52, 58), (cx-66, py-5), (cx+66, py+12), 4)
        pygame.draw.circle(self.tela, (150, 72, 45), (cx+43, py+8), 5)

        # Título.
        titulo_s = self.fonte_titulo.render("PESADELO", True, (30, 4, 8))
        titulo = self.fonte_titulo.render("PESADELO", True, VERMELHO)
        self.tela.blit(titulo_s, titulo_s.get_rect(center=(cx+3, 455+4)))
        self.tela.blit(titulo, titulo.get_rect(center=(cx, 455)))
        venceu = self.fonte.render("VENCEU", True, BRANCO)
        self.tela.blit(venceu, venceu.get_rect(center=(cx, 510)))

        dados = self.dados_game_over()
        linhas = [
            f"Noite alcançada: {dados['noite']}",
            f"Pesadelos derrotados: {dados['derrotados']}",
            f"Moedas finais: {dados['moedas']}",
        ]
        y = 565
        for linha in linhas:
            txt = self.fonte_pequena.render(linha, True, CINZA_CLARO)
            self.tela.blit(txt, txt.get_rect(center=(cx, y)))
            y += 34

        # Desativa visualmente o AD se já foi usado.
        if getattr(self, "ad_continua_usado", False):
            self.botoes_gameover[2].texto = "AD JÁ USADO"
            self.botoes_gameover[2].tipo = "perigo"
        else:
            self.botoes_gameover[2].texto = "AD CONTINUA"
            self.botoes_gameover[2].tipo = "normal"

        for b in self.botoes_gameover:
            b.desenhar(self.tela, self.fonte)

        aviso = self.fonte_mini.render("AD CONTINUA revive uma vez e restaura parte da porta", True, (135, 135, 150))
        self.tela.blit(aviso, aviso.get_rect(center=(cx, 985)))

    def desenhar_vitoria(self):
        """v1.24.32: tela final quando o jogador vence a campanha/noite especial."""
        self.desenhar_fundo_vivo()

        painel = pygame.Rect(50, 190, LARGURA - 100, 900)
        pygame.draw.rect(self.tela, (8, 10, 12), painel, border_radius=28)
        pygame.draw.rect(self.tela, AMARELO, painel, 3, border_radius=28)
        pygame.draw.rect(self.tela, (42, 35, 16), painel.inflate(-18, -18), 2, border_radius=22)

        cx = LARGURA // 2
        pulso = (math.sin(self.tempo * 2.6) + 1) * 0.5

        # Porta aberta com luz no fim do corredor.
        py = 320
        pygame.draw.rect(self.tela, (16, 14, 10), (cx-88, py-94, 176, 198), border_radius=9)
        luz_cor = (210 + int(35*pulso), 190 + int(45*pulso), 90)
        pygame.draw.rect(self.tela, luz_cor, (cx-62, py-70, 124, 150), border_radius=6)
        pygame.draw.line(self.tela, (255, 235, 150), (cx-44, py-55), (cx+44, py+70), 3)
        pygame.draw.line(self.tela, (255, 245, 180), (cx+36, py-50), (cx-34, py+76), 2)
        pygame.draw.rect(self.tela, (92, 64, 28), (cx-84, py-90, 28, 190), border_radius=5)
        pygame.draw.rect(self.tela, (92, 64, 28), (cx+56, py-90, 28, 190), border_radius=5)

        # Partículas douradas simples.
        for i in range(18):
            x = int((i * 43 + self.tempo * 28) % (painel.w - 80)) + painel.x + 40
            y = int((painel.bottom - 170 - (i * 37 + self.tempo * 45) % 520))
            pygame.draw.circle(self.tela, AMARELO_CLARO, (x, y), 2 if i % 3 else 3)

        titulo_s = self.fonte_titulo.render("VITÓRIA!", True, (30, 22, 4))
        titulo = self.fonte_titulo.render("VITÓRIA!", True, (245, 205 + int(35*pulso), 70))
        self.tela.blit(titulo_s, titulo_s.get_rect(center=(cx+3, 455+4)))
        self.tela.blit(titulo, titulo.get_rect(center=(cx, 455)))
        sub = self.fonte.render("VOCÊ SOBREVIVEU AO PESADELO", True, BRANCO)
        self.tela.blit(sub, sub.get_rect(center=(cx, 510)))

        dados = self.dados_vitoria()
        linhas = [
            f"Noite alcançada: {dados['noite']}",
            f"Pesadelos derrotados: {dados['derrotados']}",
            f"Moedas finais: {dados['moedas']}",
            f"Fragmentos: {dados['fragmentos']}",
            f"Frag. lendários: {dados['fragmentos_lendarios']}",
        ]
        y = 565
        for linha in linhas:
            txt = self.fonte_pequena.render(linha, True, CINZA_CLARO)
            self.tela.blit(txt, txt.get_rect(center=(cx, y)))
            y += 34

        for b in self.botoes_vitoria:
            b.desenhar(self.tela, self.fonte)

        aviso = self.fonte_mini.render("O pesadelo recuou... por enquanto.", True, (150, 150, 165))
        self.tela.blit(aviso, aviso.get_rect(center=(cx, 1045)))

    def desenhar(self):
        if self.estado == "jogo" and self.jogo:
            self.jogo.desenhar()
        elif self.estado == "splash":
            self.desenhar_splash()
        elif self.estado == "aviso":
            self.desenhar_aviso_ficcao()
        elif self.estado == "gameover":
            self.desenhar_game_over()
        elif self.estado == "vitoria":
            self.desenhar_vitoria()
        elif self.estado == "carregamento":
            self.desenhar_carregamento()
        elif self.estado == "prologo":
            self.desenhar_prologo()
        elif self.estado == "config":
            self.desenhar_config()
        elif self.estado == "creditos":
            self.desenhar_creditos()
        elif self.estado == "conquistas":
            self.desenhar_conquistas()
        else:
            self.desenhar_menu()

    def rodar(self):
        while True:
            dt = self.relogio.tick(FPS) / 1000.0
            self.eventos()
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()


def main():
    # Tela cheia real SEM pygame.SCALED.
    # O SCALED estica a pixel art e deixa tudo borrado em Android.
    # No APK/Buildozer, configure orientation = portrait.
    try:
        pygame.display.quit()
        pygame.display.init()
    except Exception:
        pass

    tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
    pygame.display.set_caption("Sono Profundo")

    # Garante que o jogo use exatamente o tamanho da tela criada.
    try:
        import config as cfg
        cfg.LARGURA = tela.get_width()
        cfg.ALTURA = tela.get_height()
        cfg.FPS = FPS
    except Exception:
        pass

    app = MenuPrincipal(tela)
    app.rodar()


if __name__ == "__main__":
    main()
