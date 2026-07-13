import pygame, random, math
from config import *
from interface import Botao, desenhar_texto, desenhar_texto_centralizado, desenhar_texto_centralizado_ajustado, desenhar_barra, desenhar_icone, desenhar_vinheta
from quarto import Quarto
from monstro import Monstro
from torres import Torre, TIPOS_TORRE, Impacto
from progresso import carregar_save, salvar_save, MELHORIAS_INFO, custo_melhoria, MAX_NIVEL_MELHORIA, CONQUISTAS_INFO, MISSOES_INFO, meta_concluida
try:
    from sons import Sons
except Exception:
    Sons = None
try:
    from ambientes import listar_ambientes, obter_ambiente, AMBIENTE_PADRAO, obter_andar_por_noite, obter_andar
except Exception:
    AMBIENTE_PADRAO = "hospital_abandonado"
    def obter_andar_por_noite(noite):
        return {"andar":1,"nome":"Hospital","ambiente":"hospital_abandonado","inicio":1,"fim":20,"chefe":"Doutor Infectado"}
    def obter_andar(numero):
        return obter_andar_por_noite(1)
    def listar_ambientes():
        return [{"id":"hospital_abandonado","nome":"Hospital","descricao":"Mapa padrao","desbloqueado":True}]
    def obter_ambiente(ambiente_id=None):
        return listar_ambientes()[0]

# v1.7.3: modo desempenho seguro para Android/Pydroid.
MAX_PROJETEIS_ATIVOS = 18
MAX_IMPACTOS_ATIVOS = 10
MAX_MOEDAS_ANIMADAS = 6

# v1.3.5: progressão mais longa e desafiadora.
# Cama/porta vão até o nível 15; o último upgrade custa acima de 30K.
MAX_NIVEL_CAMA = 15
MAX_NIVEL_PORTA = 15
MAX_NIVEL_ARMA = 15
CUSTOS_CAMA = [30, 75, 160, 350, 750, 1400, 2500, 4200, 6800, 10500, 14500, 19000, 24500, 32000]
CUSTOS_PORTA = [50, 110, 240, 520, 1050, 1900, 3300, 5400, 8500, 12500, 17000, 22500, 29000, 38000]
CUSTOS_ARMA = [120, 320, 780, 1650, 3400, 6200, 9800, 14500, 21000, 30000, 42000, 57000, 74000, 100000]
GANHOS_CAMA = [1, 2, 4, 7, 12, 20, 32, 50, 75, 110, 155, 215, 290, 380, 500]
VIDA_PORTA_NIVEIS = [145, 220, 300, 390, 500, 650, 830, 1050, 1320, 1650, 2050, 2550, 3150, 3900, 4800]

# v1.3.0: sistema de pesadelos leves.
# Só altera números de gameplay; não adiciona efeitos pesados.
EVENTOS_NOITE = {
    # v1.4.1: eventos renomeados para combinar com o tema de pesadelos.
    # Nada de FOME: agora a interface mostra eventos de terror/sonho.
    "normal": {"nome": "", "msg": "Prepare suas defesas", "moeda": 1.0, "vel": 1.0},
    "nevoa": {"nome": "NÉVOA", "msg": "NÉVOA: fantasmas surgem mais perto", "moeda": 1.12, "vel": 1.06},
    "frenesi": {"nome": "FRENESI", "msg": "FRENESI: monstros muito mais rápidos", "moeda": 1.18, "vel": 1.32},
    "maldicao": {"nome": "MALDIÇÃO", "msg": "MALDIÇÃO: a porta sofre mais dano", "moeda": 1.25, "vel": 1.0},
    "assombracao": {"nome": "ASSOMBRAÇÃO", "msg": "ASSOMBRAÇÃO: mais fantasmas aparecem", "moeda": 1.20, "vel": 1.08},
    "lua_sangue": {"nome": "LUA DE SANGUE", "msg": "LUA DE SANGUE: recompensas maiores, inimigos fortes", "moeda": 1.45, "vel": 1.12},
    "escuridao": {"nome": "ESCURIDÃO", "msg": "ESCURIDÃO: corredores dominam a noite", "moeda": 1.16, "vel": 1.18},
    "terror": {"nome": "TERROR", "msg": "TERROR: brutos aparecem em maior número", "moeda": 1.28, "vel": 0.96},
    "caos": {"nome": "CAOS", "msg": "CAOS: todos os pesadelos se misturam", "moeda": 1.35, "vel": 1.15},
}

# v1.4.0: plano de ondas. O jogador aprende um inimigo por vez.
# peso = chance relativa dentro da noite. O chefe ainda aparece no último spawn das noites múltiplas de 5.
PLANO_ONDAS = {
    1: [("normal", 100)],
    2: [("normal", 70), ("corredor", 30)],
    3: [("normal", 35), ("corredor", 65)],
    4: [("normal", 45), ("bruto", 55)],
    5: [("normal", 45), ("corredor", 35), ("bruto", 20)],
    6: [("normal", 35), ("corredor", 30), ("explosivo", 35)],
    7: [("normal", 30), ("corredor", 25), ("bruto", 20), ("explosivo", 25)],
    8: [("normal", 25), ("fantasma", 45), ("corredor", 30)],
    9: [("normal", 20), ("corredor", 25), ("bruto", 20), ("explosivo", 20), ("fantasma", 15)],
}

def escolher_por_peso(opcoes):
    total = sum(peso for _, peso in opcoes)
    sorte = random.uniform(0, total)
    acumulado = 0
    for tipo, peso in opcoes:
        acumulado += peso
        if sorte <= acumulado:
            return tipo
    return opcoes[-1][0]

def chefe_da_noite(noite, hospital=False, infantil=False):
    # v1.13.0: Noite 20 no Hospital vira evento especial do Diretor.
    if hospital and noite == 20:
        return "chefe_diretor"
    # v1.16.0: última noite da Ala Infantil vira evento da Babá Sombria.
    if infantil and noite == 40:
        return "chefe_baba"
    # v1.5.0: cada 5 noites entra um chefe diferente, em ciclo.
    ordem = ["chefe_devorador", "chefe_fantasma", "chefe_demolidor", "chefe_caos"]
    if noite < 5 or noite % 5 != 0:
        return None
    return ordem[((noite // 5) - 1) % len(ordem)]


# v1.6.1: habilidades do jogador com HUD em ícones e recarga visual.


# v1.23.0: base da Loja Lendária.
# Ainda não usa AdMob real: o botão de anúncio apenas simula +1 fragmento lendário.
LENDARIOS_INFO = {
    "laser_supremo": {
        "nome": "Laser Supremo", "icone": "L", "custo": 30,
        "cor": (255, 70, 70),
        "desc": "Libera arma: feixe que atravessa pesadelos."
    },
    "espingarda_suprema": {
        "nome": "Espingarda Suprema", "icone": "E", "custo": 30,
        "cor": (255, 135, 55),
        "desc": "Tiro espalhado supremo para limpar grupos."
    },
    "terremoto": {
        "nome": "Terremoto", "icone": "T", "custo": 25,
        "cor": (180, 120, 75),
        "desc": "O chão treme e atordoa os pesadelos."
    },
    "cofre_supremo": {
        "nome": "Cofre Supremo", "icone": "$", "custo": 25,
        "cor": (255, 215, 70),
        "desc": "Libera suporte lendário de economia suprema."
    },
}

HABILIDADES_JOGADOR = {
    "congelar": {"nome": "Gelo", "icone": "❄", "cooldown": 26, "cor": CIANO, "desc": "Congela todos por 4s"},
    "meteoro": {"nome": "Meteoro", "icone": "☄", "cooldown": 32, "cor": LARANJA, "desc": "Dano forte em todos"},
    "reparar": {"nome": "Reparar", "icone": "+", "cooldown": 38, "cor": VERDE, "desc": "Cura a porta"},
    "raio": {"nome": "Raio", "icone": "⚡", "cooldown": 28, "cor": (185,120,255), "desc": "Choque geral"},
    "ganancia": {"nome": "X2", "icone": "$", "cooldown": 44, "cor": AMARELO, "desc": "Moedas x2 por 10s"},
    # v1.23.6: habilidade lendária. Só aparece na HUD após desbloquear na Loja Lendária.
    "terremoto": {"nome": "Terremoto", "icone": "T", "cooldown": 42, "cor": (180, 120, 75), "desc": "Dano em área + atordoamento"},
}


# v1.7.2: suportes usam uma única linha acima da cama.
# As 2 primeiras linhas continuam exclusivas para armas/torres.
SUPORTES = {
    # v1.21.0: suportes refinados para jogo leve.
    # Cada um tem uma função clara, poucos cálculos por ciclo e sem usar imagens externas.
    "cofre": {"nome":"Cofre", "icone":"$", "custo":95, "cor":AMARELO, "desc":"Moedas extras melhores"},
    # v1.24.19: suporte lendário liberado pela Loja Lendária.
    # É uma evolução econômica do cofre comum, pensada para partidas longas.
    "cofre_supremo": {"nome":"Cofre Supremo", "icone":"$", "custo":420, "cor":(255,215,70), "desc":"LENDÁRIO: economia + jackpot supremo"},
    "gerador": {"nome":"Gerador", "icone":"G", "custo":140, "cor":CIANO, "desc":"Dano das armas + aura"},
    "reparador": {"nome":"Reparador", "icone":"+", "custo":165, "cor":VERDE, "desc":"Cura a porta em ciclos"},
    "congelador": {"nome":"Congelador", "icone":"F", "custo":190, "cor":(130,220,255), "desc":"Pulso de lentidão leve"},
}

class Suporte:
    def __init__(self, x, y, tipo):
        self.x=x; self.y=y; self.tipo=tipo; self.nivel=1
        cfg=SUPORTES[tipo]
        self.nome=cfg["nome"]; self.cor=cfg["cor"]; self.icone=cfg["icone"]
        self.rect=pygame.Rect(x, y, 44, 44)
        # Offset pequeno evita todos os suportes pulsarem no mesmo frame.
        # Isso mantém a sensação de vida sem pesar em celulares simples.
        self.tick=random.uniform(0.0, 0.45)
        self.pulso=0.0
        # v1.24.21: contadores leves do Cofre Supremo final.
        self.ciclo_lendario = 0
        self.mega_pulso = 0.0
    def custo_upgrade(self):
        if self.nivel >= 15:
            return 999999
        base=SUPORTES[self.tipo]["custo"]
        return int(base * (1.55 ** self.nivel) + self.nivel * 35)
    def melhorar(self):
        if self.nivel < 15:
            self.nivel += 1
    def atualizar_suporte(self, dt, jogo):
        self.tick += dt
        self.pulso = max(0.0, self.pulso - dt)
        self.mega_pulso = max(0.0, getattr(self, "mega_pulso", 0.0) - dt)
        eficiencia = jogo.bonus_engenharia_perm()

        if self.tipo == "cofre" and self.tick >= max(1.55, 2.05 - self.nivel * 0.025):
            self.tick = 0
            # v1.21.2: cofre recebeu um buff leve.
            # Gera um pouco mais e acelera suavemente com o nível, sem quebrar a economia.
            ganho = max(2, int((1.6 + self.nivel * 0.72) * eficiencia))
            if getattr(jogo, "evento_noite", "normal") == "lua_vermelha":
                ganho += 1
            # Bônus raro nos níveis altos: dá sensação de investimento, mas é barato de calcular.
            if self.nivel >= 6 and random.random() < min(0.12, 0.035 + self.nivel * 0.006):
                ganho += max(1, self.nivel // 3)
            jogo.moedas += ganho
            jogo.adicionar_moeda_animada(self.rect.centerx, self.rect.y, ganho)
            self.pulso = 0.50

        elif self.tipo == "cofre_supremo" and self.tick >= max(1.05, 2.55 - self.nivel * 0.065):
            self.tick = 0
            # v1.24.21 FINAL: economia lendária para partidas longas.
            # Forte, com jackpot memorável, mas ainda leve para Pydroid.
            self.ciclo_lendario = getattr(self, "ciclo_lendario", 0) + 1
            ganho_base = 10 + self.nivel * 4 + max(0, jogo.noite // 2)
            ganho = int(ganho_base * eficiencia)

            ganancia = getattr(jogo, "habilidade_ganancia_tempo", 0) > 0
            if ganancia:
                ganho *= 2

            # Jackpot comum: bom e frequente o bastante para o item parecer lendário.
            chance_jackpot = min(0.38, 0.10 + self.nivel * 0.016 + min(0.08, jogo.noite * 0.002))
            jackpot_garantido = self.ciclo_lendario >= max(4, 8 - min(4, self.nivel // 4))
            jackpot = jackpot_garantido or random.random() < chance_jackpot

            # Mega Jackpot: bem raro, mas cria momento especial.
            chance_mega = min(0.035, 0.010 + self.nivel * 0.0015)
            mega = random.random() < chance_mega

            if jackpot or mega:
                self.ciclo_lendario = 0
                if mega:
                    bonus = 55 + self.nivel * 9 + max(0, jogo.noite * 2)
                    ganho += bonus * (2 if ganancia else 1)
                    jogo.mostrar_mensagem("MEGA JACKPOT!!!", 1.75)
                    self.mega_pulso = 1.15
                    # Duas moedas animadas extras, respeitando o limite global.
                    jogo.adicionar_moeda_animada(self.rect.centerx - 12, self.rect.y - 3, max(1, ganho // 3))
                    jogo.adicionar_moeda_animada(self.rect.centerx + 12, self.rect.y - 3, max(1, ganho // 3))
                else:
                    ganho += (24 + self.nivel * 6 + max(0, jogo.noite)) * (2 if ganancia else 1)
                    jogo.mostrar_mensagem("JACKPOT LENDÁRIO!", 1.55)
                    self.mega_pulso = 0.70
                    jogo.adicionar_moeda_animada(self.rect.centerx, self.rect.y - 5, max(1, ganho // 4))

            jogo.moedas += max(1, ganho)
            jogo.adicionar_moeda_animada(self.rect.centerx, self.rect.y, ganho)
            self.pulso = 1.05 if (jackpot or mega) else 0.65

        elif self.tipo == "reparador" and self.tick >= 2.9:
            self.tick = 0
            if jogo.vida_porta < jogo.vida_porta_max:
                cura = max(1, int((2 + self.nivel * 1.15) * eficiencia))
                # Quando a porta está crítica, o suporte ganha importância sem criar nova mecânica pesada.
                if jogo.vida_porta <= jogo.vida_porta_max * 0.30:
                    cura = int(cura * 1.35)
                jogo.vida_porta = min(jogo.vida_porta_max, jogo.vida_porta + cura)
                jogo.flash_reparo = 0.28
                self.pulso = 0.50

        elif self.tipo == "congelador" and self.tick >= 2.55:
            self.tick = 0
            fator = 0.86 - min(0.30, self.nivel * 0.011 * eficiencia)
            duracao = 1.2 + min(0.65, self.nivel * 0.027)
            afetados = 0
            # Limite pequeno para evitar varrer uma horda inteira com efeito forte.
            # Ainda percorre a lista uma vez, mas aplica só nos primeiros vivos do corredor.
            for m in jogo.monstros:
                if m.vida > 0 and hasattr(m, "aplicar_lentidao"):
                    m.aplicar_lentidao(fator, duracao)
                    afetados += 1
                    if afetados >= 7:
                        break
            if afetados:
                self.pulso = 0.45
    def desenhar(self, tela, fonte, selecionada=False):
        r = self.rect
        cx, cy = r.center
        ativo = self.pulso > 0
        t = pygame.time.get_ticks() // 220

        # sombra e base geral
        pygame.draw.rect(tela, (5, 5, 8), r.move(0, 3), border_radius=9)
        pygame.draw.rect(tela, (18, 22, 30), r, border_radius=9)
        pygame.draw.rect(tela, (52, 58, 70), (r.x+3, r.y+3, r.w-6, r.h-6), 1, border_radius=7)

        # pulso de ativação
        if ativo:
            raio = 18 + int(self.pulso * 18)
            pygame.draw.circle(tela, self.cor, r.center, raio, 1)
            pygame.draw.rect(tela, self.cor, r.inflate(4, 4), 1, border_radius=10)

        # desenhos próprios, todos feitos por código e bem leves
        if self.tipo == "cofre":
            # Cofre metálico com porta, trava e moedas.
            pygame.draw.rect(tela, (74, 78, 86), (r.x+8, r.y+10, 28, 25), border_radius=4)
            pygame.draw.rect(tela, (34, 38, 46), (r.x+11, r.y+13, 22, 19), border_radius=3)
            pygame.draw.circle(tela, (235, 190, 55), (cx, cy+1), 6)
            pygame.draw.circle(tela, (45, 38, 30), (cx, cy+1), 3, 1)
            pygame.draw.rect(tela, (235, 190, 55), (r.x+14, r.y+6, 6, 3), border_radius=1)
            pygame.draw.rect(tela, (235, 190, 55), (r.x+24, r.y+6, 6, 3), border_radius=1)
            if ativo or t % 2 == 0:
                pygame.draw.circle(tela, (255, 220, 85), (r.right-9, r.y+9), 3)
                pygame.draw.circle(tela, (180, 130, 35), (r.right-9, r.y+9), 3, 1)

        elif self.tipo == "cofre_supremo":
            # Cofre lendário final: dourado, vivo e fácil de reconhecer na tela.
            mega_pulso = getattr(self, "mega_pulso", 0.0)
            brilho = ativo or mega_pulso > 0 or (t % 2 == 0)
            pygame.draw.circle(tela, (95, 70, 22), r.center, 24, 1)
            pygame.draw.circle(tela, (255, 215, 70), r.center, 22 if brilho else 19, 1)
            if mega_pulso > 0:
                pygame.draw.circle(tela, (255, 245, 150), r.center, 24 + int(mega_pulso * 14), 2)
            pygame.draw.rect(tela, (74, 55, 22), (r.x+5, r.y+8, 34, 29), border_radius=6)
            pygame.draw.rect(tela, (168, 122, 30), (r.x+8, r.y+11, 28, 23), border_radius=5)
            pygame.draw.rect(tela, (255, 224, 95), (r.x+10, r.y+13, 24, 19), 2, border_radius=4)
            pygame.draw.circle(tela, (255, 245, 160), (cx, cy+1), 8)
            pygame.draw.circle(tela, (90, 58, 18), (cx, cy+1), 3, 1)
            pygame.draw.rect(tela, (255, 238, 130), (r.x+12, r.y+5, 8, 4), border_radius=1)
            pygame.draw.rect(tela, (255, 238, 130), (r.x+24, r.y+5, 8, 4), border_radius=1)
            pygame.draw.line(tela, (255, 250, 190), (r.x+11, r.y+13), (r.x+27, r.y+13), 1)
            # pequenas estrelas fixas, sem partículas reais para não pesar.
            if brilho:
                for sx, sy in ((r.right-8, r.y+8), (r.x+8, r.bottom-9), (r.x+10, r.y+8), (r.right-10, r.bottom-10)):
                    pygame.draw.line(tela, (255, 245, 170), (sx-3, sy), (sx+3, sy), 1)
                    pygame.draw.line(tela, (255, 245, 170), (sx, sy-3), (sx, sy+3), 1)
                pygame.draw.circle(tela, (255, 235, 110), r.center, 18, 1)
            # selo minúsculo no próprio item para reforçar raridade sem poluir.
            pygame.draw.rect(tela, (90, 58, 18), (r.x+6, r.bottom-13, 32, 7), border_radius=2)
            pygame.draw.rect(tela, (255, 225, 95), (r.x+6, r.bottom-13, 32, 7), 1, border_radius=2)
            try:
                txt_l = fonte.render("L", True, (255, 245, 170))
                tela.blit(txt_l, (r.x+19, r.bottom-18))
            except Exception:
                pass

        elif self.tipo == "gerador":
            # Gerador com bobina, raio e LED.
            pygame.draw.rect(tela, (55, 68, 76), (r.x+8, r.y+12, 28, 22), border_radius=4)
            pygame.draw.rect(tela, (25, 30, 38), (r.x+11, r.y+16, 22, 12), border_radius=3)
            for ox in (15, 21, 27):
                pygame.draw.line(tela, (130, 225, 255), (r.x+ox, r.y+15), (r.x+ox-3, r.y+29), 2)
            raio_pts = [(cx-2, r.y+8), (cx+5, cy-2), (cx+1, cy-1), (cx+6, r.y+35), (cx-5, cy+3), (cx, cy+3)]
            pygame.draw.polygon(tela, (245, 230, 80), raio_pts)
            led = (75, 255, 125) if (ativo or t % 2 == 0) else (35, 105, 60)
            pygame.draw.circle(tela, led, (r.x+12, r.y+10), 2)

        elif self.tipo == "reparador":
            # Caixa de ferramentas com chave simples.
            pygame.draw.rect(tela, (105, 42, 42), (r.x+8, r.y+13, 28, 22), border_radius=4)
            pygame.draw.rect(tela, (170, 68, 58), (r.x+13, r.y+9, 18, 7), border_radius=3)
            pygame.draw.line(tela, (215, 220, 215), (r.x+15, r.y+30), (r.x+30, r.y+16), 3)
            pygame.draw.circle(tela, (215, 220, 215), (r.x+31, r.y+15), 4, 2)
            pygame.draw.rect(tela, (85, 255, 120), (r.x+11, r.y+18, 5, 5), border_radius=1)
            if ativo:
                pygame.draw.line(tela, (110, 255, 140), (r.x+10, r.y+8), (r.x+16, r.y+4), 1)
                pygame.draw.line(tela, (110, 255, 140), (r.right-10, r.y+8), (r.right-16, r.y+4), 1)

        elif self.tipo == "congelador":
            # Mini freezer com ventoinha e floco central.
            pygame.draw.rect(tela, (45, 86, 108), (r.x+8, r.y+9, 28, 27), border_radius=4)
            pygame.draw.rect(tela, (115, 210, 245), (r.x+11, r.y+12, 22, 19), 2, border_radius=3)
            pygame.draw.circle(tela, (22, 45, 62), (cx, cy+1), 8)
            pygame.draw.line(tela, (180, 245, 255), (cx-8, cy+1), (cx+8, cy+1), 1)
            pygame.draw.line(tela, (180, 245, 255), (cx, cy-7), (cx, cy+9), 1)
            pygame.draw.line(tela, (180, 245, 255), (cx-6, cy-5), (cx+6, cy+7), 1)
            pygame.draw.line(tela, (180, 245, 255), (cx+6, cy-5), (cx-6, cy+7), 1)
            if ativo:
                pygame.draw.circle(tela, (190, 245, 255), r.center, 16, 1)

        # Contorno de seleção/tipo
        pygame.draw.rect(tela, self.cor, r, 3 if selecionada else 2, border_radius=9)

        # Pips de evolução no lugar de número grande: limpo e legível.
        pips = min(5, max(1, (self.nivel + 2) // 3))
        px0 = r.x + 8
        py = r.bottom - 6
        for i in range(pips):
            pygame.draw.rect(tela, self.cor, (px0 + i*6, py, 4, 3), border_radius=1)

def nome_chefe(tipo):
    nomes = {
        "chefe_devorador": "DEVORADOR",
        "chefe_fantasma": "REI FANTASMA",
        "chefe_demolidor": "DEMOLIDOR",
        "chefe_caos": "SENHOR DO CAOS",
        "chefe_diretor": "DOUTOR INFECTADO",
        "chefe_baba": "BABÁ SOMBRIA",
        "chefe": "CHEFE",
    }
    return nomes.get(tipo, "CHEFE")

class ParticulaPoeira:
    def __init__(self, area=None):
        area = area or pygame.Rect(25, 205, LARGURA-50, 625)
        self.x = random.uniform(area.x, area.right)
        self.y = random.uniform(area.y, area.bottom)
        self.r = random.choice([1, 1, 2])
        self.vel = random.uniform(5, 13)
        self.onda = random.uniform(0, math.pi * 2)
        self.alpha = random.randint(22, 48)
    def atualizar(self, dt):
        self.y -= self.vel * dt
        self.x += math.sin(pygame.time.get_ticks() * 0.0015 + self.onda) * 0.18
        if self.y < 205:
            self.y = 830
            self.x = random.uniform(25, LARGURA-25)
    def desenhar(self, tela):
        # Sem Surface com alpha por partícula: mais leve no celular.
        cor = (95, 100, 125) if self.alpha < 35 else (120, 125, 150)
        pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), self.r)

class MoedaAnimada:
    def __init__(self, x, y, valor):
        # v1.1.2: moeda animada restaurada e mais visível, sem usar alpha/transparência.
        self.x=float(x)
        self.y=float(y)
        self.valor=valor
        self.tempo=1.05
        self.tempo_total=1.05
    def atualizar(self, dt):
        self.tempo-=dt
        self.y-=34*dt
        self.x+=math.sin((self.tempo_total-self.tempo)*12)*0.45
    def desenhar(self,tela,fonte):
        if self.tempo <= 0:
            return
        # Some nos últimos instantes apenas parando de desenhar, evitando Surface com alpha.
        if self.tempo < 0.12:
            return
        x=int(self.x); y=int(self.y)
        # Sombra + moeda com contorno para aparecer bem em cima da cama/quarto escuro.
        pygame.draw.circle(tela, (20, 16, 8), (x+1,y+2), 11)
        pygame.draw.circle(tela, AMARELO, (x,y), 10)
        pygame.draw.circle(tela, (255, 238, 115), (x-3,y-3), 4)
        pygame.draw.circle(tela, AMARELO_ESCURO, (x,y), 10, 2)
        txt=fonte.render(f"+{self.valor}", True, AMARELO)
        # Contorno simples no texto, barato e legível.
        sombra=fonte.render(f"+{self.valor}", True, (20,16,8))
        tela.blit(sombra, (x+14,y-11+1))
        tela.blit(txt, (x+14,y-11))

class Jogo:
    def __init__(self,tela):
        self.tela=tela
        self.fonte=pygame.font.SysFont("arial",22)
        self.fonte_pequena=pygame.font.SysFont("arial",17)
        self.fonte_grande=pygame.font.SysFont("arial",36)
        # v1.9.1: progresso permanente carregado antes da partida.
        self.save = carregar_save()
        self.sons = Sons() if Sons else None
        if self.sons:
            self.sons.iniciar_ambiente()
        self.arvore_aberta = False
        self.ambientes_aberto = False
        self.reiniciar()

    def reiniciar(self):
        self.fragmentos = int(self.save.get("fragmentos", 0))
        # v1.23.0: fragmentos lendários são separados dos Fragmentos do Sono.
        self.fragmentos_lendarios = int(self.save.get("fragmentos_lendarios", 0))
        self.lendarios_desbloqueados = set(self.save.get("lendarios_desbloqueados", []))
        self.lendarios_anuncios = dict(self.save.get("lendarios_anuncios", {}))
        self.loja_aba = "normal"
        self.ambiente_atual = self.save.get("ambiente_atual", AMBIENTE_PADRAO)
        self.campanha = self.save.setdefault("campanha", {"andar_atual": 1, "andares_desbloqueados": [1], "chefes_campanha_derrotados": [], "modo_pesadelo": False, "campanha_concluida": False})
        self.moedas=80; self.moedas_display=float(self.moedas); self.nivel_cama=1; self.nivel_arma=1
        self.nivel_porta=1; self.vida_porta_max=int(VIDA_PORTA_NIVEIS[0] * self.bonus_resistencia_perm()); self.vida_porta=self.vida_porta_max; self.vida_porta_display=float(self.vida_porta)
        self.cama_max_msg=False; self.porta_max_msg=False  # v1.2.1: mensagens MAX uma vez
        self.noite=1; self.derrotados=0; self.meta_noite=5; self.total_derrotados=0
        self.quarto=Quarto(); self.monstros=[]; self.torres=[None]*len(self.quarto.pontos_torre); self.projeteis=[]; self.impactos=[]; self.moedas_animadas=[]
        # Audio: cada monstro controla seu próprio som de surgimento com o atributo
        # som_aparecer_tocado. Evitamos guardar id(monstro) em set permanente,
        # porque o Python pode reutilizar IDs em noites futuras e silenciar monstros novos.
        self.custo_cama=20; self.custo_porta=35; self.custo_arma=45
        self.tempo_moeda=0; self.tempo_spawn=0; self.tempo_ataque=0; self.spawnados=0; self.intervalo_spawn=2.4
        self.fase="preparacao"; self.tempo_preparacao=15.0; self.max_simultaneos=1; self.noite_bonus=0; self.pausado=False; self.velocidade_jogo=1
        self.pulso_cama=0; self.tremor_porta=0; self.porta_em_ataque=False; self.jogo_acabou=False; self.vitoria=False; self.selecionada=None; self.loja_aberta=False; self.menu_construcao=None
        self.historia_pendente = None
        self.historia_doutor_mostrada = False
        self.historia_baba_mostrada = False
        self.mensagem=""; self.mensagem_tempo=0; self.mensagem_tempo_max=1; self.pesadelo=False; self.evento_noite="normal"; self.torre_para_comprar=None
        self.evento_diretor_tempo=0
        self.arvore_aberta=False
        self.tela_info=None
        # v1.10.1: inicializa contadores de estatísticas para não travar ao abrir/atualizar no Pydroid.
        self.tempo_jogado_acum = 0
        self.tempo_estatisticas = 0
        self.tempestade_tick=0; self.evento_moeda_mult=1.0; self.evento_vel_mult=1.0
        self.habilidades_cd = {k: 0 for k in HABILIDADES_JOGADOR}
        self.habilidade_ganancia_tempo = 0
        self.habilidade_efeitos = []
        # v1.23.9: tremor curtinho e leve para o Terremoto Lendário.
        self.tremor_terremoto = 0
        self.chefe_invocacao_tick=0; self.chefe_fantasma_tick=0
        # v1.20.3: fala curta do chefe antes da invocacao.
        self.chefe_invocacao_pendente=None
        self.chefe_fala_tempo=0
        # Símbolos/rúnas de invocação antes dos monstros aparecerem.
        self.invocacoes_simbolos=[]
        # v1.20.4 FUNCIONAL: efeito simples e leve para chefes.
        # Sem fade, fumaça, tremor, partículas ou Surface com alpha.
        self.efeito_alerta_chefe = True
        self.barra_chefe_alerta = True
        self.botao_chefe_especial_toggle = 0
        self.botao_chefe_especial = pygame.Rect(0, 0, 1, 1)
        self.botao_feedback=""; self.botao_feedback_tempo=0
        # v1.21.6: poucas partículas de poeira. Limite baixo para manter leve no Android.
        self.particulas=[ParticulaPoeira(pygame.Rect(25, 205, LARGURA-50, ALTURA-255)) for _ in range(7)]
        self.preparar_cache_atmosfera()
        self.transicao_noite=0
        self.flash_porta=0
        self.flash_reparo=0
        self.pulso_hud=0
        # v1.21.7: efeitos leves de entrada/derrota dos chefes.
        self.efeitos_chefe=[]
        self.tremor_chefe=0
        # v1.25.0: morte cinematográfica dos chefes especiais.
        self.morte_chefe_cinematica = None
        self.luzes_morte_chefe = []
        y=ALTURA-112
        margem_btn = 16
        gap = 18
        largura_btn = (LARGURA - margem_btn*2 - gap*2) // 3
        self.botao_loja=Botao(margem_btn,y,largura_btn,44)
        self.botao_cama=Botao(margem_btn+largura_btn+gap,y,largura_btn,44)
        self.botao_porta=Botao(margem_btn+(largura_btn+gap)*2,y,largura_btn,44)
        self.botao_upgrade=Botao(margem_btn,y+52,largura_btn,40)
        self.botao_vender=Botao(margem_btn+largura_btn+gap,y+52,largura_btn,40)
        self.botao_pause=Botao(margem_btn+(largura_btn+gap)*2,y+52,(largura_btn-gap)//2,40)
        self.botao_speed=Botao(self.botao_pause.rect.right+gap,y+52,largura_btn-(largura_btn-gap)//2-gap,40)
        self.atualizar_botoes_laterais()
        self.modo_upgrade_hint = 0
        self.painel_objeto = None
        self.painel_objeto_tempo = 0
        self.preparar_noite()


    def salvar_progresso(self):
        """Salva Fragmentos, melhorias e estatisticas permanentes."""
        self.save["fragmentos"] = int(getattr(self, "fragmentos", self.save.get("fragmentos", 0)))
        self.save["fragmentos_lendarios"] = int(getattr(self, "fragmentos_lendarios", self.save.get("fragmentos_lendarios", 0)))
        self.save["lendarios_desbloqueados"] = sorted(list(getattr(self, "lendarios_desbloqueados", set(self.save.get("lendarios_desbloqueados", [])))))
        self.save["lendarios_anuncios"] = dict(getattr(self, "lendarios_anuncios", self.save.get("lendarios_anuncios", {})))
        self.save.setdefault("melhorias", {})
        self.save.setdefault("marcos_noite", [])
        self.save.setdefault("ambiente_atual", getattr(self, "ambiente_atual", AMBIENTE_PADRAO))
        self.save["campanha"] = getattr(self, "campanha", self.save.get("campanha", {}))
        salvar_save(self.save)

    # v1.11.3: leitura segura do ambiente atual.
    # Mantém a jogabilidade antiga quando o ambiente não existir no save.
    def ambiente_cfg(self):
        try:
            return obter_ambiente(getattr(self, "ambiente_atual", AMBIENTE_PADRAO))
        except Exception:
            return obter_ambiente(AMBIENTE_PADRAO)

    def ambiente_id(self):
        return self.ambiente_cfg().get("id", AMBIENTE_PADRAO)

    def tocar_som(self, nome, volume=None, intervalo=0.0):
        if getattr(self, "sons", None):
            canal = self.sons.tocar(nome, volume=volume, intervalo=intervalo)
            # Compatibilidade: algumas rotas antigas de sons.py tocavam o áudio,
            # mas não retornavam o canal. Pegamos o último canal tocado para que
            # o monstro possa parar o próprio som ao morrer.
            if canal is None:
                canal = getattr(self.sons, "ultimo_canal_tocado", None)
            return canal
        return None

    def parar_todos_sons_monstro(self, monstro):
        """Para todos os canais ligados a um monstro morto.

        Antes só o canal_surgimento era limpo. Agora também varremos qualquer
        atributo canal_* guardado na instância, evitando vestígio de áudio quando
        o monstro morre muito rápido ou quando futuros sons forem adicionados.
        """
        for attr in list(vars(monstro).keys()):
            if not attr.startswith("canal_"):
                continue
            canal = getattr(monstro, attr, None)
            if canal is not None:
                try:
                    if canal.get_busy():
                        canal.stop()
                except Exception:
                    pass
            try:
                setattr(monstro, attr, None)
            except Exception:
                pass

    def tocar_som_porta_impacto(self):
        """Toca som da porta só quando há batida/golpe direto.
        Explosões não chamam esta função, para não parecer batida na porta.
        """
        # Porta 1-6: madeira/reforçada. Porta 7+: metal/ferro/blindada.
        if getattr(self, "nivel_porta", 1) >= 7:
            return self.tocar_som("porta_metal_hit", volume=0.82, intervalo=0.18)
        return self.tocar_som("porta_madeira_hit", volume=0.82, intervalo=0.18)

    def parar_som_monstro_surgimento(self, monstro):
        # Mantido por compatibilidade com chamadas antigas.
        self.parar_todos_sons_monstro(monstro)

    def bonus_moedas_ambiente(self):
        try:
            return float(self.ambiente_cfg().get("bonus_moedas", 1.0))
        except Exception:
            return 1.0

    def hospital_ativo(self):
        return self.ambiente_id() == "hospital_abandonado"

    def campanha_info(self):
        if not isinstance(getattr(self, "campanha", None), dict):
            self.campanha = self.save.setdefault("campanha", {"andar_atual": 1, "andares_desbloqueados": [1], "chefes_campanha_derrotados": [], "modo_pesadelo": False, "campanha_concluida": False})
        self.campanha.setdefault("andar_atual", 1)
        self.campanha.setdefault("andares_desbloqueados", [1])
        self.campanha.setdefault("chefes_campanha_derrotados", [])
        self.campanha.setdefault("modo_pesadelo", False)
        self.campanha.setdefault("campanha_concluida", False)
        return self.campanha

    def andar_cfg(self):
        if self.campanha_info().get("modo_pesadelo", False):
            return obter_andar_por_noite(self.noite)
        return obter_andar_por_noite(self.noite)

    def atualizar_andar_pela_noite(self):
        # v1.14.0: campanha por andares, leve e baseada apenas no numero da noite.
        info = self.campanha_info()
        andar = self.andar_cfg()
        n = int(andar.get("andar", 1))
        info["andar_atual"] = n
        desbloq = set(int(x) for x in info.get("andares_desbloqueados", [1]))
        if n not in desbloq and not info.get("modo_pesadelo", False):
            # Segurança: se o save antigo cair direto em uma noite alta, não trava.
            desbloq.add(n)
            info["andares_desbloqueados"] = sorted(desbloq)
        amb = andar.get("ambiente", AMBIENTE_PADRAO)
        if amb in [a.get("id") for a in listar_ambientes()]:
            self.ambiente_atual = amb
            self.save["ambiente_atual"] = amb
            self.save.setdefault("ambientes_desbloqueados", [])
            if amb not in self.save["ambientes_desbloqueados"]:
                self.save["ambientes_desbloqueados"].append(amb)
        self.save["campanha"] = info

    def desbloquear_andar(self, numero, motivo=""):
        info = self.campanha_info()
        desbloq = set(int(x) for x in info.get("andares_desbloqueados", [1]))
        numero = int(numero)
        novo = numero not in desbloq
        desbloq.add(numero)
        info["andares_desbloqueados"] = sorted(desbloq)
        try:
            amb = obter_andar(numero).get("ambiente")
            if amb in [a.get("id") for a in listar_ambientes()]:
                self.save.setdefault("ambientes_desbloqueados", [])
                if amb not in self.save["ambientes_desbloqueados"]:
                    self.save["ambientes_desbloqueados"].append(amb)
        except Exception:
            pass
        self.save["campanha"] = info
        self.salvar_progresso()
        if novo:
            nome = obter_andar(numero).get("nome", f"Andar {numero}")
            self.mostrar_mensagem(f"Elevador liberado: {nome}", 2.8)

    def texto_andar(self):
        a = self.andar_cfg()
        return f"{int(a.get('andar', 1))}º Andar - {a.get('nome', 'Hospital')}"

    def nivel_perm(self, nome):
        return int(self.save.get("melhorias", {}).get(nome, 0))

    def bonus_prosperidade(self):
        return 1.0 + self.nivel_perm("prosperidade") * 0.05

    def bonus_poder_perm(self):
        return 1.0 + self.nivel_perm("poder") * 0.05

    def bonus_resistencia_perm(self):
        return 1.0 + self.nivel_perm("resistencia") * 0.10

    def bonus_reflexos_perm(self):
        return 1.0 + self.nivel_perm("reflexos") * 0.05

    def bonus_engenharia_perm(self):
        return 1.0 + self.nivel_perm("engenharia") * 0.08

    def dar_fragmentos(self, qtd, motivo=""):
        qtd = int(max(0, qtd))
        if qtd <= 0:
            return
        self.fragmentos += qtd
        self.save["fragmentos"] = self.fragmentos
        self.salvar_progresso()
        extra = f" ({motivo})" if motivo else ""
        self.mostrar_mensagem(f"+{qtd} Fragmentos do Sono{extra}", 2.0)

    def dar_fragmentos_lendarios(self, qtd, motivo=""):
        # v1.23.0: moeda rara para a Loja Lendária.
        # Fonte principal: chefes especiais. Anúncios recompensados entram depois no APK.
        qtd = int(max(0, qtd))
        if qtd <= 0:
            return
        self.fragmentos_lendarios += qtd
        self.save["fragmentos_lendarios"] = self.fragmentos_lendarios
        self.salvar_progresso()
        extra = f" ({motivo})" if motivo else ""
        self.mostrar_mensagem(f"+{qtd} Fragmento Lendário{extra}", 2.1)

    def item_lendario_desbloqueado(self, chave):
        return chave in getattr(self, "lendarios_desbloqueados", set())

    def garantir_habilidade_lendaria_ativa(self, chave):
        """
        v1.23.8: liga itens lendários que são habilidades ao sistema de uso.
        O Terremoto não é arma nem suporte: após comprar na Loja Lendária,
        ele deve aparecer e funcionar na HUD de habilidades imediatamente.
        """
        if chave == "terremoto":
            self.habilidades_cd.setdefault("terremoto", 0)

    def desbloquear_lendario(self, chave):
        info = LENDARIOS_INFO.get(chave)
        if not info:
            return
        if self.item_lendario_desbloqueado(chave):
            self.mostrar_mensagem("Lendário já desbloqueado", 1.3)
            return
        custo = int(info.get("custo", 999))
        if self.fragmentos_lendarios < custo:
            self.mostrar_mensagem("Fragmentos lendários insuficientes", 1.6)
            return
        self.fragmentos_lendarios -= custo
        self.lendarios_desbloqueados.add(chave)
        self.save["fragmentos_lendarios"] = self.fragmentos_lendarios
        self.save["lendarios_desbloqueados"] = sorted(list(self.lendarios_desbloqueados))
        self.garantir_habilidade_lendaria_ativa(chave)
        self.salvar_progresso()
        if chave == "terremoto":
            self.mostrar_mensagem("Terremoto liberado nas habilidades!", 2.2)
        else:
            self.mostrar_mensagem(f"{info['nome']} desbloqueado!", 2.2)

    def simular_anuncio_lendario(self, chave):
        # Base para AdMob: futuramente este método será chamado após o rewarded ad terminar.
        if self.item_lendario_desbloqueado(chave):
            self.mostrar_mensagem("Esse lendário já está liberado", 1.3)
            return
        self.lendarios_anuncios[chave] = int(self.lendarios_anuncios.get(chave, 0)) + 1
        self.save["lendarios_anuncios"] = dict(self.lendarios_anuncios)
        self.dar_fragmentos_lendarios(1, "Anúncio teste")

    def registrar_recorde_e_marco(self):
        mudou = False
        if self.noite > int(self.save.get("recorde_noite", 0)):
            self.save["recorde_noite"] = int(self.noite)
            mudou = True
        # Marco unico a cada 10 noites alcançadas.
        if self.noite >= 10 and self.noite % 10 == 0:
            marcos = set(self.save.get("marcos_noite", []))
            chave = str(self.noite)
            if chave not in marcos:
                self.save.setdefault("marcos_noite", []).append(chave)
                self.dar_fragmentos(max(2, self.noite // 5), f"Noite {self.noite}")
                return
        if mudou:
            self.salvar_progresso()

    def custo_upgrade_permanente(self, nome):
        return custo_melhoria(self.nivel_perm(nome))

    def comprar_upgrade_permanente(self, nome):
        if nome not in MELHORIAS_INFO:
            return
        nivel = self.nivel_perm(nome)
        custo = custo_melhoria(nivel)
        if custo is None:
            self.mostrar_mensagem("Melhoria no nivel maximo", 1.5)
            return
        if self.fragmentos < custo:
            self.mostrar_mensagem("Fragmentos insuficientes", 1.5)
            return
        self.fragmentos -= custo
        self.save["fragmentos"] = self.fragmentos
        self.save.setdefault("melhorias", {})[nome] = nivel + 1
        # Aplica resistência imediatamente na porta atual.
        if nome == "resistencia":
            self.vida_porta_max = int(self.vida_porta_por_nivel() * self.bonus_resistencia_perm())
            self.vida_porta = min(self.vida_porta_max, self.vida_porta + int(self.vida_porta_max * 0.10))
        self.salvar_progresso()
        self.mostrar_mensagem(f"{MELHORIAS_INFO[nome]['nome']} {nivel+1}", 1.7)

    # v1.10.0: missões, conquistas, perfil e bestiário.
    def tela_info_aberta(self):
        return getattr(self, "tela_info", None) in ("missoes", "conquistas", "perfil", "bestiario")

    def progresso_meta(self, info):
        valor = int(info.get("valor", 1))
        atual = int(self.save.get(info.get("tipo", ""), 0))
        return atual, valor, min(1.0, atual / max(1, valor))

    def verificar_conquistas(self):
        ganhas = set(self.save.get("conquistas", []))
        novas = []
        for chave, info in CONQUISTAS_INFO.items():
            if chave not in ganhas and meta_concluida(self.save, info):
                ganhas.add(chave)
                novas.append((chave, info))
        if novas:
            self.save["conquistas"] = list(ganhas)
            total = sum(int(info.get("fragmentos", 0)) for _, info in novas)
            if total > 0:
                self.fragmentos += total
                self.save["fragmentos"] = self.fragmentos
            self.salvar_progresso()
            if len(novas) == 1:
                self.mostrar_mensagem(f"Conquista: {novas[0][1]['nome']}  +{novas[0][1]['fragmentos']} Fragmentos", 2.2)
            else:
                self.mostrar_mensagem(f"{len(novas)} conquistas desbloqueadas! +{total} Fragmentos", 2.2)

    def coletar_missao(self, chave):
        if chave not in MISSOES_INFO:
            return
        coletadas = set(self.save.get("missoes_coletadas", []))
        info = MISSOES_INFO[chave]
        if chave in coletadas:
            self.mostrar_mensagem("Missão já coletada", 1.2)
            return
        if not meta_concluida(self.save, info):
            self.mostrar_mensagem("Missão ainda não concluída", 1.2)
            return
        coletadas.add(chave)
        self.save["missoes_coletadas"] = list(coletadas)
        self.fragmentos += int(info.get("fragmentos", 0))
        self.save["fragmentos"] = self.fragmentos
        self.salvar_progresso()
        self.mostrar_mensagem(f"Missão concluída: +{info['fragmentos']} Fragmentos", 1.7)

    def registrar_inimigo_visto(self, tipo):
        vistos = set(self.save.get("inimigos_vistos", []))
        if tipo not in vistos:
            vistos.add(tipo)
            self.save["inimigos_vistos"] = list(vistos)
            self.salvar_progresso()

    def rects_tela_info(self):
        return pygame.Rect(30, 185, LARGURA-60, min(500, ALTURA-230))

    def preparar_cache_atmosfera(self):
        # v1.0.7: modo desempenho. Nada de Surface transparente grande.
        # Mantemos só valores simples para efeitos por desenho direto.
        self.hud_moeda_cache = None

    def mostrar_mensagem(self, texto, tempo=1.6):
        self.mensagem = texto
        self.mensagem_tempo = tempo
        self.mensagem_tempo_max = tempo

    def feedback_botao(self, nome):
        self.botao_feedback = nome
        self.botao_feedback_tempo = 0.13

    def botao_pressionado(self, nome):
        return self.botao_feedback == nome and self.botao_feedback_tempo > 0

    def adicionar_moeda_animada(self, x, y, valor):
        # Limite visual: muitas moedas animadas derrubam FPS no Pydroid.
        if len(self.moedas_animadas) < MAX_MOEDAS_ANIMADAS:
            self.moedas_animadas.append(MoedaAnimada(x, y, valor))

    def adicionar_impacto(self, impacto):
        if impacto and len(self.impactos) < MAX_IMPACTOS_ATIVOS:
            self.impactos.append(impacto)


    def atualizar_botoes_laterais(self):
        """v1.3.3: apenas o botão de Loja fica fixo na tela.
        Upgrades são feitos tocando diretamente na cama, porta ou torre.
        """
        r = 31
        cy = self.quarto.cama.centery - 4
        # Botão Loja mais afastado da cama e perto da parede direita do quarto.
        loja_x = min(self.quarto.rect.right - r*2 - 24, self.quarto.cama.right + 78)
        self.botao_loja_lateral = pygame.Rect(int(loja_x), int(cy-r), r*2, r*2)


    def opcoes_suportes_disponiveis(self):
        # v1.24.19: o Cofre Supremo só aparece nos suportes após ser desbloqueado
        # na Loja Lendária. Mantém o item lendário com sensação de prêmio real.
        opcoes = {}
        for chave, cfg in SUPORTES.items():
            if chave == "cofre_supremo" and not self.item_lendario_desbloqueado("cofre_supremo"):
                continue
            opcoes[chave] = cfg
        return opcoes

    def slot_e_suporte(self, idx):
        # Com 9 espaços atuais: linhas 1 e 2 (0..5) são armas; linha 3 (6..8) é suporte.
        return idx >= 6

    def objeto_e_torre(self, obj):
        return isinstance(obj, Torre)

    def objeto_e_suporte(self, obj):
        return isinstance(obj, Suporte)

    def bonus_suportes_dano(self):
        bonus = 0.0
        engenharia = self.bonus_engenharia_perm()
        for obj in self.torres:
            if isinstance(obj, Suporte) and obj.tipo == "gerador":
                # Gerador continua simples: bônus global calculado uma vez por frame.
                # Escala melhor nos níveis baixos e tem teto saudável com 3 slots.
                bonus += (0.10 + obj.nivel * 0.022) * engenharia
        return 1.0 + bonus

    def rects_menu_torre(self):
        """Retorna os botões flutuantes Upgrade/Vender do objeto selecionado."""
        if self.selecionada is None or self.selecionada >= len(self.torres) or not self.torres[self.selecionada]:
            return None, None
        t = self.torres[self.selecionada]
        # v1.19.8: botão de upgrade um pouco mais largo para valores altos
        # sem mudar o layout/corredor.
        w, h = 100, 34
        x = t.rect.right + 6
        y = t.rect.y - 4
        if x + w > self.quarto.rect.right - 8:
            x = t.rect.x - w - 10
        x = max(self.quarto.rect.x + 8, min(x, self.quarto.rect.right - w - 8))
        y = max(self.quarto.rect.y + 8, min(y, self.quarto.rect.bottom - h*2 - 10))
        return pygame.Rect(x, y, w, h), pygame.Rect(x, y + h + 6, w, h)

    def rects_habilidades(self):
        # Barra de poderes abaixo da cama, sem ocupar corredor.
        # v1.23.6: Terremoto entra junto das outras habilidades apenas quando liberado.
        y = self.quarto.cama.bottom + 10
        w = 52
        h = 44
        gap = 10
        ordem = ["congelar", "meteoro", "reparar", "raio", "ganancia"]
        if self.item_lendario_desbloqueado("terremoto"):
            self.garantir_habilidade_lendaria_ativa("terremoto")
            ordem.append("terremoto")
        total = len(ordem) * w + (len(ordem) - 1) * gap
        x0 = (LARGURA - total) // 2
        return [(k, pygame.Rect(x0 + i * (w + gap), y, w, h)) for i, k in enumerate(ordem)]

    def habilidade_pronta(self, nome):
        return self.habilidades_cd.get(nome, 0) <= 0

    def criar_efeito_habilidade(self, tipo, x=None, y=None):
        """Base visual leve das habilidades: só dados simples e desenho em Pygame."""
        if len(self.habilidade_efeitos) >= 10:
            self.habilidade_efeitos.pop(0)
        cx = int(x if x is not None else LARGURA // 2)
        cy = int(y if y is not None else self.quarto.rect.centery)
        duracoes = {
            "congelar": 0.48,
            # v1.24.26: meteoro mais longo para mostrar queda + explosão no corredor.
            "meteoro": 0.82,
            "reparar": 0.70,
            "raio": 0.42,
            "ganancia": 0.80,
            "terremoto": 0.70,
        }
        self.habilidade_efeitos.append({"tipo": tipo, "x": cx, "y": cy, "t": duracoes.get(tipo, 0.45), "max": duracoes.get(tipo, 0.45)})

    def usar_habilidade(self, nome):
        if nome not in HABILIDADES_JOGADOR:
            return
        if not self.habilidade_pronta(nome):
            self.mostrar_mensagem(f"{HABILIDADES_JOGADOR[nome]['nome']} recarregando", 1.1)
            return
        if nome != "reparar" and not any(m.vida > 0 for m in self.monstros):
            self.mostrar_mensagem("Espere os pesadelos chegarem", 1.1)
            return

        self.habilidades_cd[nome] = HABILIDADES_JOGADOR[nome]["cooldown"] / self.bonus_reflexos_perm()
        # Áudio: cada habilidade toca seu próprio som no momento da ativação.
        self.tocar_som(nome, intervalo=0.12)
        self.save["habilidades_usadas"] = int(self.save.get("habilidades_usadas", 0)) + 1
        if nome == "congelar":
            for m in self.monstros:
                if m.vida > 0 and hasattr(m, "aplicar_congelamento"):
                    m.aplicar_congelamento(4.0)
            self.criar_efeito_habilidade("congelar", self.quarto.rect.centerx, self.quarto.rect.centery)
            self.mostrar_mensagem("Pesadelos congelados!", 1.4)
        elif nome == "meteoro":
            # v1.24.26: Meteoro agora mira o CORREDOR, não o centro da tela.
            # O impacto cai no grupo de pesadelos; se houver só um, cai nele.
            vivos = [m for m in self.monstros if m.vida > 0]
            corredor = getattr(self.quarto, "corredor", pygame.Rect(25, 145, LARGURA-50, 190))
            if vivos:
                alvo_x = int(sum(m.rect.centerx for m in vivos) / len(vivos))
                alvo_y = int(sum(m.rect.centery for m in vivos) / len(vivos))
                alvo_x = max(corredor.left + 30, min(corredor.right - 30, alvo_x))
                alvo_y = max(corredor.top + 25, min(corredor.bottom - 25, alvo_y))
            else:
                alvo_x, alvo_y = corredor.center

            dano = int((70 + self.noite * 10 + self.nivel_arma * 6) * 1.14)
            raio_explosao = 128
            for m in vivos:
                dist = math.hypot(m.rect.centerx - alvo_x, m.rect.centery - alvo_y)
                if dist <= raio_explosao:
                    fator = 1.0 - min(0.45, dist / max(1, raio_explosao) * 0.45)
                    m.sofrer_dano(max(1, int(dano * fator)))
                    self.adicionar_impacto(Impacto(m.rect.centerx, m.rect.centery, LARANJA, 38))
                elif m.rect.colliderect(corredor.inflate(40, 40)):
                    # Ondas de calor ainda acertam de leve quem está no corredor.
                    m.sofrer_dano(max(1, int(dano * 0.35)))
                    self.adicionar_impacto(Impacto(m.rect.centerx, m.rect.centery, LARANJA, 26))

            self.criar_efeito_habilidade("meteoro", alvo_x, alvo_y)
            self.tremor_chefe = max(getattr(self, "tremor_chefe", 0), 0.22)
            self.mostrar_mensagem("Chuva de meteoros!", 1.4)
        elif nome == "reparar":
            cura = int(self.vida_porta_max * 0.42)
            antes = self.vida_porta
            self.vida_porta = min(self.vida_porta_max, self.vida_porta + cura)
            self.flash_reparo = 0.35
            self.criar_efeito_habilidade("reparar", self.quarto.porta.centerx, self.quarto.porta.centery)
            self.mostrar_mensagem(f"Porta reparada +{int(self.vida_porta-antes)}", 1.4)
        elif nome == "raio":
            dano = int((46 + self.noite * 7 + self.nivel_arma * 5) * 1.05)
            for m in self.monstros:
                if m.vida > 0:
                    m.sofrer_dano(dano)
                    if hasattr(m, "aplicar_lentidao"):
                        m.aplicar_lentidao(0.60, 1.6)
            self.criar_efeito_habilidade("raio", self.quarto.rect.centerx, self.quarto.rect.y + 80)
            self.mostrar_mensagem("Descarga elétrica!", 1.4)
        elif nome == "terremoto":
            # v1.24.25: Terremoto agora acontece no CORREDOR.
            # Dano com buff leve e efeito visual concentrado onde os pesadelos passam.
            dano = int((58 + self.noite * 8 + self.nivel_arma * 7) * 1.32)
            for m in self.monstros:
                if m.vida > 0:
                    m.sofrer_dano(dano)
                    if hasattr(m, "aplicar_lentidao"):
                        # Mantém o controle forte, mas sem congelar para sempre.
                        m.aplicar_lentidao(0.18, 2.75)
                    self.adicionar_impacto(Impacto(m.rect.centerx, m.rect.centery, (180, 120, 75), 38))
            self.criar_efeito_habilidade("terremoto", self.quarto.corredor.centerx, self.quarto.corredor.centery)
            # Tremor um pouco mais longo para combinar com as rachaduras no corredor.
            self.tremor_terremoto = 0.62
            self.mostrar_mensagem("Terremoto lendário!", 1.4)
        elif nome == "ganancia":
            self.habilidade_ganancia_tempo = 10.0
            self.criar_efeito_habilidade("ganancia", self.quarto.cama.centerx, self.quarto.cama.centery)
            self.mostrar_mensagem("Ganância: moedas dobradas!", 1.4)

    def atualizar_habilidades_jogador(self, dt):
        for k in list(self.habilidades_cd):
            self.habilidades_cd[k] = max(0, self.habilidades_cd[k] - dt)
        self.habilidade_ganancia_tempo = max(0, self.habilidade_ganancia_tempo - dt)
        self.tremor_terremoto = max(0, getattr(self, "tremor_terremoto", 0) - dt)
        for e in self.habilidade_efeitos:
            e["t"] -= dt
        self.habilidade_efeitos = [e for e in self.habilidade_efeitos if e["t"] > 0]

    def desenhar_icone_habilidade(self, nome, rect, pronto):
        """Ícones desenhados por código para não depender de emoji/fonte no Android."""
        cx, cy = rect.centerx, rect.centery
        cor_base = HABILIDADES_JOGADOR[nome]["cor"] if pronto else (135, 135, 145)
        claro = BRANCO if pronto else (170, 170, 180)
        escuro = (25, 25, 34)

        if nome == "congelar":
            # Floco de gelo simples.
            for ang in (0, math.pi/3, -math.pi/3):
                dx = int(math.cos(ang) * 15)
                dy = int(math.sin(ang) * 15)
                pygame.draw.line(self.tela, cor_base, (cx-dx, cy-dy), (cx+dx, cy+dy), 3)
            pygame.draw.circle(self.tela, claro, (cx, cy), 4)
        elif nome == "meteoro":
            # Meteoro com cauda.
            pygame.draw.line(self.tela, LARANJA, (cx-17, cy-13), (cx+2, cy+6), 5)
            pygame.draw.line(self.tela, AMARELO, (cx-21, cy-8), (cx-2, cy+11), 3)
            pygame.draw.circle(self.tela, cor_base, (cx+7, cy+8), 11)
            pygame.draw.circle(self.tela, AMARELO, (cx+4, cy+5), 4)
        elif nome == "reparar":
            # Cruz de reparo.
            pygame.draw.rect(self.tela, cor_base, (cx-5, cy-17, 10, 34), border_radius=3)
            pygame.draw.rect(self.tela, cor_base, (cx-17, cy-5, 34, 10), border_radius=3)
            pygame.draw.rect(self.tela, claro, (cx-3, cy-14, 6, 28), border_radius=2)
        elif nome == "raio":
            pts = [(cx+4, cy-18), (cx-10, cy+1), (cx, cy+1), (cx-5, cy+18), (cx+13, cy-5), (cx+2, cy-5)]
            pygame.draw.polygon(self.tela, cor_base, pts)
            pygame.draw.polygon(self.tela, claro, pts, 2)
        elif nome == "ganancia":
            # Moeda x2.
            pygame.draw.circle(self.tela, cor_base, (cx, cy), 15)
            pygame.draw.circle(self.tela, (170, 120, 25), (cx, cy), 15, 3)
            desenhar_texto_centralizado(self.tela, "2x", pygame.Rect(cx-17, cy-10, 34, 20), escuro, self.fonte_pequena)
        elif nome == "terremoto":
            # Rachadura lendária.
            pygame.draw.line(self.tela, (80, 52, 32), (cx-18, cy+13), (cx+18, cy+13), 3)
            pts = [(cx-12, cy-12), (cx-4, cy-2), (cx-9, cy+1), (cx+2, cy+14), (cx-1, cy+3), (cx+9, cy+1), (cx+3, cy-12)]
            pygame.draw.lines(self.tela, claro, False, pts, 3)
            pygame.draw.circle(self.tela, cor_base, (cx, cy), 18, 2)

    def desenhar_habilidades(self):
        rects = self.rects_habilidades()
        if not rects:
            return

        # Moldura única da barra: parece HUD, não botões soltos.
        xs = [r.x for _, r in rects]
        xe = [r.right for _, r in rects]
        barra = pygame.Rect(min(xs)-12, rects[0][1].y-10, max(xe)-min(xs)+24, rects[0][1].h+20)
        pygame.draw.rect(self.tela, (6, 6, 11), barra.move(0, 4), border_radius=15)
        pygame.draw.rect(self.tela, (24, 24, 34), barra, border_radius=15)
        pygame.draw.rect(self.tela, (210, 190, 70), barra, 2, border_radius=15)

        for nome, rect in rects:
            cfg = HABILIDADES_JOGADOR[nome]
            pronto = self.habilidade_pronta(nome)
            cooldown_total = max(1, cfg["cooldown"])
            cd = max(0, self.habilidades_cd.get(nome, 0))
            pct_pronto = 1 - min(1, cd / cooldown_total)

            # Botão quadrado com brilho quando pronto.
            sombra = rect.move(0, 3)
            pygame.draw.rect(self.tela, (4, 4, 8), sombra, border_radius=12)
            fundo = (38, 38, 50) if pronto else (54, 54, 64)
            pygame.draw.rect(self.tela, fundo, rect, border_radius=12)
            pygame.draw.rect(self.tela, cfg["cor"] if pronto else (115, 115, 126), rect, 2, border_radius=12)
            if pronto:
                pygame.draw.rect(self.tela, (245, 245, 255), rect.inflate(-8, -8), 1, border_radius=8)

            self.desenhar_icone_habilidade(nome, rect, pronto)

            if not pronto:
                # Camada escura simples sem Surface/alpha novo por frame.
                pygame.draw.rect(self.tela, (18, 18, 25), rect.inflate(-4, -4), border_radius=10)
                segundos = str(int(cd) + 1)
                bolha = pygame.Rect(rect.centerx-15, rect.centery-15, 30, 30)
                pygame.draw.circle(self.tela, (12, 12, 18), bolha.center, 16)
                pygame.draw.circle(self.tela, CINZA_CLARO, bolha.center, 16, 2)
                desenhar_texto_centralizado(self.tela, segundos, bolha, BRANCO, self.fonte_pequena)

                # Barra de recarga na base do quadrado.
                prog = pygame.Rect(rect.x+6, rect.bottom-7, int((rect.w-12) * pct_pronto), 4)
                pygame.draw.rect(self.tela, (20, 20, 28), (rect.x+6, rect.bottom-7, rect.w-12, 4), border_radius=2)
                if prog.w > 0:
                    pygame.draw.rect(self.tela, cfg["cor"], prog, border_radius=2)

        if self.habilidade_ganancia_tempo > 0:
            r = pygame.Rect(160, 270, 200, 25)
            pygame.draw.rect(self.tela, (28, 24, 12), r, border_radius=8)
            pygame.draw.rect(self.tela, AMARELO, r, 1, border_radius=8)
            desenhar_texto_centralizado(self.tela, f"GANÂNCIA {int(self.habilidade_ganancia_tempo)+1}s", r, AMARELO, self.fonte_pequena)
        self.desenhar_efeitos_habilidades()

    def desenhar_efeitos_habilidades(self):
        """Efeitos de base das habilidades. Sem imagens, sem alpha, sem custo alto."""
        for e in self.habilidade_efeitos:
            tipo = e.get("tipo", "")
            max_t = max(0.01, e.get("max", 0.45))
            p = 1.0 - max(0.0, min(1.0, e.get("t", 0) / max_t))
            x, y = int(e.get("x", LARGURA//2)), int(e.get("y", ALTURA//2))
            if tipo == "congelar":
                raio = int(35 + p * 260)
                pygame.draw.circle(self.tela, CIANO, (x, y), raio, 3)
                pygame.draw.circle(self.tela, (170, 240, 255), (x, y), max(8, raio//2), 1)
                for m in self.monstros:
                    if m.vida > 0:
                        pygame.draw.circle(self.tela, CIANO, m.rect.center, 16, 2)
            elif tipo == "meteoro":
                # v1.24.26: meteoros caem no corredor, no ponto real de impacto.
                corredor = getattr(self.quarto, "corredor", pygame.Rect(25, 145, LARGURA-50, 190))
                area = corredor.inflate(-24, -18)
                impacto_x = max(area.left + 20, min(area.right - 20, x))
                impacto_y = max(area.top + 18, min(area.bottom - 18, y))

                # Primeiro metade: queda. Segunda metade: explosão/onda no chão.
                queda = min(1.0, p * 1.65)
                expl = max(0.0, (p - 0.46) / 0.54)
                meteoros = [
                    (impacto_x, impacto_y, 0),
                    (max(area.left+25, impacto_x-76), min(area.bottom-18, impacto_y+28), 1),
                    (min(area.right-25, impacto_x+72), max(area.top+18, impacto_y-22), 2),
                ]
                for mx, my, i in meteoros:
                    start_x = mx - 165 + i * 22
                    start_y = area.top - 135 - i * 22
                    sx = int(start_x + (mx - start_x) * queda)
                    sy = int(start_y + (my - start_y) * queda)
                    # Cauda de fogo diagonal, feita só com linhas/círculos.
                    pygame.draw.line(self.tela, (135, 38, 18), (sx-36, sy-38), (sx+8, sy+8), 7)
                    pygame.draw.line(self.tela, LARANJA, (sx-30, sy-32), (sx+8, sy+8), 4)
                    pygame.draw.line(self.tela, AMARELO, (sx-18, sy-20), (sx+6, sy+6), 2)
                    pygame.draw.circle(self.tela, (255, 210, 80), (sx+9, sy+9), 8 if i == 0 else 6)

                    if expl > 0:
                        raio = int((34 if i == 0 else 22) + expl * (68 if i == 0 else 42))
                        pygame.draw.circle(self.tela, (85, 38, 20), (mx, my), raio, 3)
                        pygame.draw.circle(self.tela, LARANJA, (mx, my), max(8, raio-10), 2)
                        pygame.draw.circle(self.tela, AMARELO, (mx, my), max(4, raio//3), 1)
                        # Pequenas rachaduras queimadas no chão do corredor.
                        for off in (-1, 1):
                            pygame.draw.line(self.tela, (95, 48, 26), (mx, my), (mx + off * (24 + i*8), my + 12 + i*4), 3)
                            pygame.draw.line(self.tela, (225, 120, 55), (mx, my), (mx + off * (18 + i*6), my + 9 + i*3), 1)

                if expl > 0:
                    pygame.draw.rect(self.tela, LARANJA, area.inflate(6, 6), 2, border_radius=5)
            elif tipo == "reparar":
                for i in range(6):
                    px = x - 45 + i * 18
                    py = y + 28 - int(p * 55) - (i % 2) * 8
                    pygame.draw.line(self.tela, VERDE, (px-5, py), (px+5, py), 3)
                    pygame.draw.line(self.tela, VERDE, (px, py-5), (px, py+5), 3)
                pygame.draw.rect(self.tela, VERDE, self.quarto.porta.inflate(12, 12), 3, border_radius=6)
            elif tipo == "raio":
                alvos = [m for m in self.monstros if m.vida > 0][:5]
                if not alvos:
                    alvos = []
                for m in alvos:
                    mx, my = m.rect.center
                    meio = ((x + mx)//2 + random.randint(-14, 14), (y + my)//2 + random.randint(-14, 14))
                    pygame.draw.line(self.tela, (210, 170, 255), (x, y), meio, 3)
                    pygame.draw.line(self.tela, (210, 170, 255), meio, (mx, my), 3)
                    pygame.draw.circle(self.tela, (230, 210, 255), (mx, my), 18, 2)
            elif tipo == "terremoto":
                # v1.24.25: terremoto desenhado no corredor, não no quarto inteiro.
                # Usa apenas linhas e círculos simples para continuar leve no Android/Pydroid.
                cor_terra = (180, 120, 75)
                cor_clara = (225, 178, 112)
                cor_escura = (58, 38, 28)
                corredor = getattr(self.quarto, "corredor", pygame.Rect(25, 145, LARGURA-50, 190))

                tremor = 3 if getattr(self, "tremor_terremoto", 0) > 0 else 0
                ox = random.randint(-tremor, tremor) if tremor else 0
                oy = random.randint(-tremor, tremor) if tremor else 0
                area = corredor.inflate(-22, -24).move(ox, oy)

                # Onda principal correndo pelo corredor.
                onda_x = int(area.right - p * area.w)
                pygame.draw.line(self.tela, cor_clara, (onda_x, area.y), (onda_x, area.bottom), 3)
                pygame.draw.circle(self.tela, cor_terra, (onda_x, area.centery), int(18 + p * 42), 2)

                # Rachaduras grandes atravessando o piso do corredor.
                rachaduras = [
                    [(area.right-18, area.centery-34), (area.right-70, area.centery-16), (area.right-118, area.centery-29), (area.right-170, area.centery-4), (area.right-230, area.centery-12)],
                    [(area.right-8, area.centery+28), (area.right-58, area.centery+12), (area.right-112, area.centery+25), (area.right-166, area.centery+7), (area.right-222, area.centery+20)],
                    [(area.centerx+120, area.y+20), (area.centerx+72, area.y+48), (area.centerx+20, area.y+41), (area.centerx-35, area.y+66), (area.centerx-92, area.y+55)],
                    [(area.centerx+98, area.bottom-22), (area.centerx+42, area.bottom-48), (area.centerx-12, area.bottom-39), (area.centerx-70, area.bottom-66), (area.centerx-130, area.bottom-54)],
                    [(area.x+24, area.centery-18), (area.x+78, area.centery-34), (area.x+132, area.centery-17), (area.x+188, area.centery-38)],
                    [(area.x+42, area.centery+31), (area.x+96, area.centery+12), (area.x+152, area.centery+29), (area.x+214, area.centery+9)],
                ]

                # No começo aparecem menores; depois abrem até o tamanho total.
                progresso = min(1.0, p * 1.35)
                for pts in rachaduras:
                    if len(pts) < 2:
                        continue
                    n = max(2, int(2 + (len(pts)-1) * progresso))
                    pts2 = pts[:n]
                    pygame.draw.lines(self.tela, cor_escura, False, pts2, 5)
                    pygame.draw.lines(self.tela, cor_clara, False, pts2, 2)
                    # Pequenos galhos laterais, fixos e baratos.
                    if progresso > 0.45 and len(pts2) >= 3:
                        bx, by = pts2[len(pts2)//2]
                        pygame.draw.line(self.tela, cor_escura, (bx, by), (bx+16, by-13), 3)
                        pygame.draw.line(self.tela, cor_clara, (bx, by), (bx+11, by-9), 1)

                # Contorno do corredor tremendo para vender o impacto.
                pygame.draw.rect(self.tela, cor_terra, area.inflate(8, 8), 3, border_radius=5)

                # Monstros atingidos recebem anel de impacto no corredor.
                for m in [m for m in self.monstros if m.vida > 0][:9]:
                    pygame.draw.circle(self.tela, cor_terra, m.rect.center, 23, 2)
                    pygame.draw.line(self.tela, cor_clara, (m.rect.centerx-14, m.rect.bottom+2), (m.rect.centerx+14, m.rect.bottom+2), 2)
            elif tipo == "ganancia":
                raio = int(24 + p * 46)
                pygame.draw.circle(self.tela, AMARELO, (x, y), raio, 3)
                for i in range(5):
                    ang = p * 6.28 + i * 1.25
                    px = x + int(math.cos(ang) * (35 + i*5))
                    py = y + int(math.sin(ang) * (18 + i*3))
                    pygame.draw.circle(self.tela, AMARELO, (px, py), 6)
                    pygame.draw.circle(self.tela, AMARELO_ESCURO, (px, py), 6, 1)

    def abrir_painel_objeto(self, tipo, tempo=3.0):
        self.painel_objeto = tipo
        self.painel_objeto_tempo = tempo

    def melhorar_cama(self):
        self.abrir_painel_objeto("cama")
        if self.nivel_cama >= MAX_NIVEL_CAMA:
            self.mostrar_mensagem("Cama no nível máximo!", 1.6)
            return
        custo = self.custo_cama_atual()
        if self.moedas >= custo:
            self.moedas -= custo
            self.nivel_cama += 1
            self.tocar_som("upgrade", intervalo=0.12)
            self.mostrar_mensagem("Cama melhorada!", 1.4)
            self.mensagem_max_se_preciso("cama")
        else:
            self.mostrar_mensagem("Moedas insuficientes", 1.4)

    def melhorar_porta(self):
        self.abrir_painel_objeto("porta")
        if self.nivel_porta >= MAX_NIVEL_PORTA:
            self.mostrar_mensagem("Porta totalmente reforçada!", 1.6)
            return
        custo = self.custo_porta_atual()
        if self.moedas >= custo:
            self.moedas -= custo
            self.nivel_porta += 1
            self.vida_porta_max = int(self.vida_porta_por_nivel() * self.bonus_resistencia_perm())
            self.vida_porta = self.vida_porta_max
            self.tocar_som("upgrade", intervalo=0.12)
            self.mostrar_mensagem("Porta reforçada!", 1.4)
            self.mensagem_max_se_preciso("porta")
        else:
            self.mostrar_mensagem("Moedas insuficientes", 1.4)

    def ganho_moedas(self):
        idx = max(0, min(MAX_NIVEL_CAMA, self.nivel_cama) - 1)
        ganho = GANHOS_CAMA[idx]
        # v1.22.0: economia mais confortável no começo e levemente mais apertada no fim.
        mult_noite = 1.10 if self.noite <= 5 else (0.95 if self.noite >= 16 else 1.0)
        # v1.4.1: eventos de pesadelo não reduzem mais a cama de forma confusa.
        # A dificuldade agora vem dos inimigos, velocidade e dano na porta.
        return max(1, int(ganho * self.bonus_prosperidade() * mult_noite))

    def texto_nivel_cama(self):
        return "MAX" if self.nivel_cama >= MAX_NIVEL_CAMA else f"{self.nivel_cama}"

    def texto_nivel_porta(self):
        return "MAX" if self.nivel_porta >= MAX_NIVEL_PORTA else f"{self.nivel_porta}"

    def mensagem_max_se_preciso(self, tipo):
        if tipo == "cama" and self.nivel_cama >= MAX_NIVEL_CAMA and not self.cama_max_msg:
            self.cama_max_msg = True
            self.mostrar_mensagem("Cama no nível máximo!", 2.0)
        elif tipo == "porta" and self.nivel_porta >= MAX_NIVEL_PORTA and not self.porta_max_msg:
            self.porta_max_msg = True
            self.mostrar_mensagem("Porta totalmente reforçada!", 2.0)

    def nome_evento_noite(self):
        evento = getattr(self, "evento_noite", "normal")
        return EVENTOS_NOITE.get(evento, EVENTOS_NOITE["normal"])["nome"]

    def sortear_evento_noite(self):
        # v1.4.1: eventos só começam na Noite 5 para o jogador aprender primeiro.
        if self.noite < 5:
            return "normal"
        # Hospital Abandonado: a Névoa é mais comum, mas sem forçar toda noite.
        if self.hospital_ativo() and random.random() < 0.30:
            return "nevoa"
        if self.noite % 10 == 0:
            return "lua_sangue"
        if self.noite % 7 == 0:
            return "caos"
        if self.noite % 5 == 0:
            return random.choice(["nevoa", "frenesi", "maldicao", "assombracao", "escuridao", "terror"])
        chance = min(0.48, 0.12 + (self.noite - 4) * 0.035)
        if random.random() > chance:
            return "normal"
        return random.choice(["nevoa", "frenesi", "maldicao", "assombracao", "escuridao", "terror", "caos"])

    def aplicar_regras_evento_noite(self):
        evento = getattr(self, "evento_noite", "normal")
        cfg = EVENTOS_NOITE.get(evento, EVENTOS_NOITE["normal"])
        self.evento_moeda_mult = cfg.get("moeda", 1.0)
        self.evento_vel_mult = cfg.get("vel", 1.0)
        self.evento_dano_porta_mult = 1.0
        self.pesadelo = evento not in ("normal",)
        self.tempestade_tick = 0

        if evento == "nevoa":
            self.meta_noite = max(4, int(self.meta_noite * 0.88))
            self.intervalo_spawn = max(0.85, self.intervalo_spawn - 0.18)
        elif evento == "frenesi":
            self.intervalo_spawn = max(0.70, self.intervalo_spawn - 0.28)
            self.max_simultaneos += 1
        elif evento == "maldicao":
            self.evento_dano_porta_mult = 1.25
            self.meta_noite += 1
        elif evento == "assombracao":
            self.intervalo_spawn = max(0.85, self.intervalo_spawn - 0.12)
            self.max_simultaneos += 1
        elif evento == "lua_sangue":
            self.meta_noite = int(self.meta_noite * 1.35)
            self.max_simultaneos += 2
            self.intervalo_spawn = max(0.75, self.intervalo_spawn - 0.22)
            self.evento_dano_porta_mult = 1.15
        elif evento == "escuridao":
            self.intervalo_spawn = max(0.75, self.intervalo_spawn - 0.25)
            self.max_simultaneos += 1
        elif evento == "terror":
            self.meta_noite += 2
        elif evento == "caos":
            self.meta_noite = int(self.meta_noite * 1.22)
            self.max_simultaneos += 2
            self.intervalo_spawn = max(0.70, self.intervalo_spawn - 0.25)

        self.mostrar_mensagem(cfg.get("msg", "Prepare suas defesas"), 3.0 if evento != "normal" else 2.0)

    def custo_cama_atual(self):
        if self.nivel_cama >= MAX_NIVEL_CAMA:
            return 999999
        return CUSTOS_CAMA[self.nivel_cama - 1]

    def custo_porta_atual(self):
        if self.nivel_porta >= MAX_NIVEL_PORTA:
            return 999999
        return CUSTOS_PORTA[self.nivel_porta - 1]

    def vida_porta_por_nivel(self, nivel=None):
        nivel = self.nivel_porta if nivel is None else nivel
        idx = max(0, min(MAX_NIVEL_PORTA, nivel) - 1)
        return VIDA_PORTA_NIVEIS[idx]

    def custo_arma_atual(self):
        if self.nivel_arma >= MAX_NIVEL_ARMA:
            return 999999
        return CUSTOS_ARMA[self.nivel_arma - 1]

    def bonus_arma(self):
        return (1.0 + (self.nivel_arma - 1) * 0.16) * self.bonus_poder_perm()

    def preparar_noite(self):
        self.atualizar_andar_pela_noite()
        self.fase="preparacao"
        self.tempo_preparacao=15.0
        self.monstros.clear(); self.projeteis.clear(); self.impactos.clear()
        self.derrotados=0; self.spawnados=0; self.tempo_spawn=0
        self.chefe_invocacao_tick=0; self.chefe_fantasma_tick=0
        # Balanceamento justo por noite: poucos no começo, aumentando aos poucos.
        if self.noite == 1: self.meta_noite = 5
        elif self.noite == 2: self.meta_noite = 8
        elif self.noite == 3: self.meta_noite = 10
        else: self.meta_noite = 10 + (self.noite - 3) * 3
        self.max_simultaneos = 1 if self.noite < 3 else (2 if self.noite < 5 else 3 + (self.noite // 4))
        self.intervalo_spawn=max(1.0,3.2-self.noite*.18)

        # v1.3.0: pesadelos sorteados. Sem efeitos pesados: só muda regras de gameplay.
        self.evento_noite = self.sortear_evento_noite()
        self.aplicar_regras_evento_noite()

    def iniciar_noite(self):
        self.fase="noite"
        self.tempo_spawn=self.intervalo_spawn  # primeiro monstro sai na hora
        self.transicao_noite=0.55
        self.tocar_som("noite", intervalo=0.5)
        if self.hospital_ativo() and self.noite == 20:
            # Evento leve: só mensagem e piscada visual, sem tocar na lógica pesada.
            self.evento_diretor_tempo = 3.2
            self.mostrar_mensagem("Algo despertou nos corredores...", 2.4)
        else:
            self.mostrar_mensagem("A NOITE COMEÇOU", 2.0)

    def tipo_monstro(self):
        # v1.5.0: sistema de ondas com chefes inteligentes no último spawn de noites múltiplas de 5.
        chefe = chefe_da_noite(self.noite, self.hospital_ativo(), getattr(self, "ambiente_atual", "") == "quarto_infantil")
        if chefe and self.spawnados == self.meta_noite-1:
            return chefe

        evento = getattr(self, "evento_noite", "normal")
        if self.noite in PLANO_ONDAS:
            opcoes = list(PLANO_ONDAS[self.noite])
        else:
            # Depois da noite 9, mistura progressiva de todos os inimigos.
            opcoes = [("normal", 20), ("corredor", 22), ("bruto", 20), ("explosivo", 20), ("fantasma", 18)]
            if self.noite >= 14:
                opcoes = [("normal", 15), ("corredor", 22), ("bruto", 23), ("explosivo", 22), ("fantasma", 18)]

        # Eventos de pesadelo puxam certos tipos de inimigo.
        if evento == "nevoa":
            opcoes += [("fantasma", 38), ("corredor", 12)]
        elif evento == "frenesi":
            opcoes += [("corredor", 45), ("explosivo", 12)]
        elif evento == "maldicao":
            opcoes += [("bruto", 25), ("explosivo", 25)]
        elif evento == "assombracao":
            opcoes += [("fantasma", 55)]
        elif evento == "lua_sangue":
            opcoes += [("corredor", 25), ("bruto", 25), ("explosivo", 25), ("fantasma", 25)]
        elif evento == "escuridao":
            opcoes += [("corredor", 38), ("fantasma", 18)]
        elif evento == "terror":
            opcoes += [("bruto", 45), ("explosivo", 15)]
        elif evento == "caos":
            opcoes += [("corredor", 30), ("bruto", 30), ("explosivo", 30), ("fantasma", 30)]

        # v1.11.3: Hospital Abandonado favorece fantasmas sem mudar o caminho do mapa.
        # Isso evita mexer na IA e mantém a versão estável no Android.
        if self.hospital_ativo():
            opcoes += [("fantasma", 42), ("corredor", 8)]

        return escolher_por_peso(opcoes)

    def tocar_som_monstro_aparece(self, tipo, monstro=None):
        """Toca o som de surgimento uma única vez por monstro.

        Regra definitiva:
        - O som de aparecer só toca no nascimento/criação do monstro.
        - Se esta função for chamada por engano de novo para a mesma instância, ela ignora.
        - Cada tipo de monstro usa seu próprio som de surgimento.
        """
        if monstro is not None and getattr(monstro, "som_aparecer_tocado", False):
            return

        mapa_sons = {
            "normal": ("zumbi_normal_aparece", 0.72),
            "infectado": ("zumbi_normal_aparece", 0.72),
            "corredor": ("corredor_aparece", 0.72),
            "rapido": ("corredor_aparece", 0.72),
            "explosivo": ("explosivo_aparece", 0.82),
            "fantasma": ("fantasma_aparece", 0.80),
            "sombra": ("fantasma_aparece", 0.80),
            "bruto": ("bruto_aparece", 0.88),
            "tanque": ("bruto_aparece", 0.88),
            "chefe_devorador": ("devorador_aparece", 0.90),
            "chefe_fantasma": ("chefe_fantasma_aparece", 0.90),
            "chefe_demolidor": ("chefe_demolidor_aparece", 0.92),
            "chefe_diretor": ("chefe_diretor_aparece", 0.92),
            "chefe_baba": ("chefe_baba_aparece", 0.90),
        }
        info = mapa_sons.get(tipo)
        canal_tocado = None
        if info:
            nome_som, volume = info
            canal_tocado = self.tocar_som(nome_som, volume=volume, intervalo=0.0)

        if monstro is not None:
            monstro.som_aparecer_tocado = True
            # Guarda o canal para cortar o som se o monstro morrer antes do áudio terminar.
            monstro.canal_surgimento = canal_tocado

    def criar_monstro(self):
        # v0.8.1: spawn no corredor superior. O monstro desce até a porta.
        x=random.randint(self.quarto.corredor.x + 35, self.quarto.corredor.right - 70)
        if getattr(self, "evento_noite", "normal") == "nevoa":
            y=random.choice([218,238,258])
        elif self.hospital_ativo():
            y=random.choice([184,214,240])
        else:
            y=random.choice([178,205,232])
        tipo = self.tipo_monstro()
        monstro = Monstro(x,y,self.noite,tipo)
        monstro.velocidade = int(monstro.velocidade * getattr(self, "evento_vel_mult", 1.0))
        mult_economia = 1.10 if self.noite <= 5 else (0.95 if self.noite >= 16 else 1.0)
        monstro.recompensa = max(1, int(monstro.recompensa * getattr(self, "evento_moeda_mult", 1.0) * self.bonus_moedas_ambiente() * mult_economia))
        self.monstros.append(monstro)
        self.tocar_som_monstro_aparece(tipo, monstro)
        if tipo.startswith("chefe"):
            self.adicionar_efeito_chefe(monstro.rect.centerx, monstro.rect.centery, "entrada")
        self.registrar_inimigo_visto(tipo)
        self.spawnados+=1
        if tipo == "chefe_diretor":
            self.evento_diretor_tempo = 2.4
            self.mostrar_mensagem("O Diretor encontrou você.", 2.8)
        elif tipo == "chefe_baba":
            self.mostrar_mensagem("A Babá Sombria despertou.", 2.8)
        elif tipo.startswith("chefe"):
            self.mostrar_mensagem(f"[BOSS] {nome_chefe(tipo)} APARECEU!", 2.6)
        elif tipo == "corredor" and self.noite <= 3:
            self.mostrar_mensagem("Corredores são muito rápidos!", 1.6)
        elif tipo == "bruto" and self.noite <= 4:
            self.mostrar_mensagem("Bruto: muita vida e boa recompensa!", 1.6)
        elif tipo == "explosivo" and self.noite <= 6:
            self.mostrar_mensagem("Cuidado: monstro explosivo!", 1.6)
        elif tipo == "fantasma" and self.noite <= 8:
            self.mostrar_mensagem("Fantasma resiste a tiros físicos!", 1.6)

    def eventos(self,evento):
        if evento.type==pygame.KEYDOWN and evento.key==pygame.K_r: self.reiniciar()
        if evento.type==pygame.KEYDOWN and evento.key==pygame.K_SPACE: self.pausado = not self.pausado
        if evento.type!=pygame.MOUSEBUTTONDOWN or self.jogo_acabou: return
        mx,my=evento.pos


        if self.ambientes_aberto:
            self.clique_ambientes(mx,my); return
        if self.arvore_aberta:
            self.clique_arvore(mx,my); return
        if self.tela_info_aberta():
            self.clique_tela_info(mx,my); return
        if self.loja_aberta:
            self.clique_loja(mx,my); return
        if self.menu_construcao is not None:
            self.clique_construcao(mx,my); return

        for nome, rect in self.rects_habilidades():
            if rect.collidepoint(mx, my):
                self.feedback_botao(nome)
                self.usar_habilidade(nome)
                return

        # v1.3.2: botões flutuantes da torre aparecem somente ao selecionar uma torre.
        up_rect, vender_rect = self.rects_menu_torre()
        if up_rect and up_rect.collidepoint(mx,my):
            self.feedback_botao("upgrade")
            t=self.torres[self.selecionada]; custo=t.custo_upgrade()
            if self.moedas>=custo and t.nivel < 15:
                self.moedas-=custo; t.melhorar(); self.mostrar_mensagem(f"{t.nome} melhorada!", 1.4)
            else:
                self.mostrar_mensagem("Moedas insuficientes ou nível máximo", 1.4)
            return
        if vender_rect and vender_rect.collidepoint(mx,my):
            self.feedback_botao("vender")
            t=self.torres[self.selecionada]
            base = TIPOS_TORRE[t.tipo]["custo"] if isinstance(t, Torre) else SUPORTES[t.tipo]["custo"]
            reembolso=max(10, int(base * 0.55 + (t.nivel-1)*18))
            self.moedas += reembolso; self.torres[self.selecionada]=None; self.selecionada=None
            self.mostrar_mensagem(f"Vendido +${reembolso}", 1.4)
            return


        # Botão redondo lateral: abre a oficina/loja.
        if self.botao_loja_lateral.collidepoint(mx,my):
            self.feedback_botao("loja")
            self.loja_aberta=True
            return

        # Upgrade direto tocando no próprio objeto.
        if self.quarto.cama.collidepoint(mx,my):
            self.feedback_botao("cama")
            self.melhorar_cama()
            return
        if self.quarto.porta.inflate(10, 18).collidepoint(mx,my):
            self.feedback_botao("porta")
            self.melhorar_porta()
            return

        # Seleciona torre existente; o menu Upgrade/Vender aparece ao lado dela.
        for i,t in enumerate(self.torres):
            if t and t.rect.collidepoint(mx,my):
                self.selecionada=i
                self.mostrar_mensagem(f"{t.nome} selecionada", 1.0)
                return

        # Tocar em um + abre construção. 2 linhas de cima = armas; linha de suporte = suportes.
        for i,(x,y) in enumerate(self.quarto.pontos_torre):
            if pygame.Rect(x,y,44,44).collidepoint(mx,my):
                if self.torres[i] is None:
                    self.menu_construcao=i
                else:
                    self.selecionada=i
                    self.mostrar_mensagem(f"{self.torres[i].nome} selecionado", 1.0)
                return

        self.selecionada=None

    def opcoes_armas_disponiveis(self):
        # v1.23.3: armas lendárias só aparecem para construir depois de liberadas na Loja Lendária.
        opcoes = dict(TIPOS_TORRE)
        if not self.item_lendario_desbloqueado("laser_supremo"):
            opcoes.pop("laser_supremo", None)
        if not self.item_lendario_desbloqueado("espingarda_suprema"):
            opcoes.pop("espingarda_suprema", None)
        return opcoes

    def construir_torre(self, idx, tipo):
        if self.slot_e_suporte(idx):
            self.mostrar_mensagem("Este espaço é só para suporte", 1.4)
            self.menu_construcao=None
            return
        cfg=TIPOS_TORRE[tipo]
        if self.torres[idx] is None and self.moedas>=cfg["custo"]:
            self.moedas-=cfg["custo"]
            x,y=self.quarto.pontos_torre[idx]
            self.torres[idx]=Torre(x,y,tipo)
            self.selecionada=idx
            self.mostrar_mensagem(f"{cfg['nome']} construída!", 1.4)
        else:
            self.mostrar_mensagem("Moedas insuficientes!", 1.4)
        self.menu_construcao=None

    def construir_suporte(self, idx, tipo):
        if not self.slot_e_suporte(idx):
            self.mostrar_mensagem("Este espaço é só para armas", 1.4)
            self.menu_construcao=None
            return
        if tipo == "cofre_supremo" and not self.item_lendario_desbloqueado("cofre_supremo"):
            self.mostrar_mensagem("Cofre Supremo bloqueado", 1.4)
            self.menu_construcao=None
            return
        cfg=SUPORTES[tipo]
        if self.torres[idx] is None and self.moedas>=cfg["custo"]:
            self.moedas-=cfg["custo"]
            x,y=self.quarto.pontos_torre[idx]
            self.torres[idx]=Suporte(x,y,tipo)
            self.selecionada=idx
            self.mostrar_mensagem(f"{cfg['nome']} construído!", 1.4)
        else:
            self.mostrar_mensagem("Moedas insuficientes!", 1.4)
        self.menu_construcao=None

    def clique_construcao(self,mx,my):
        opcoes = self.opcoes_suportes_disponiveis() if self.slot_e_suporte(self.menu_construcao) else self.opcoes_armas_disponiveis()
        caixa = pygame.Rect(30, 145, LARGURA - 60, 720)
        botao_x = pygame.Rect(caixa.right - 46, caixa.y + 18, 34, 34)
        if botao_x.collidepoint(mx,my):
            self.menu_construcao=None; return
        if not caixa.collidepoint(mx,my):
            self.menu_construcao=None; return

        y = caixa.y + 72
        passo = 64 if len(opcoes) > 5 else 70
        altura_item = 56 if len(opcoes) > 5 else 60
        item_x = caixa.x + 30
        item_w = caixa.w - 60

        for tipo,cfg in opcoes.items():
            r=pygame.Rect(item_x,y,item_w,altura_item)
            if r.collidepoint(mx,my):
                if self.slot_e_suporte(self.menu_construcao):
                    self.construir_suporte(self.menu_construcao,tipo)
                else:
                    self.construir_torre(self.menu_construcao,tipo)
                return
            y+=passo

    def clique_loja(self,mx,my):
        if pygame.Rect(630,190,40,40).collidepoint(mx,my):
            self.loja_aberta=False; return

        # v1.23.2: abas e cards lendários maiores para evitar textos cortados.
        if pygame.Rect(60,260,285,36).collidepoint(mx,my):
            self.loja_aba = "normal"
            return
        if pygame.Rect(375,260,285,36).collidepoint(mx,my):
            self.loja_aba = "lendarios"
            return

        if getattr(self, "loja_aba", "normal") == "lendarios":
            y = 315
            for chave, info in LENDARIOS_INFO.items():
                card = pygame.Rect(60, y, 600, 100)
                btn_ad = pygame.Rect(525, y+28, 48, 44)
                btn_unlock = pygame.Rect(580, y+28, 70, 44)
                if btn_ad.collidepoint(mx, my):
                    self.simular_anuncio_lendario(chave)
                    return
                if btn_unlock.collidepoint(mx, my):
                    self.desbloquear_lendario(chave)
                    return
                y += 110
            return

        # A oficina normal cuida das armas e telas de progresso.
        if pygame.Rect(60,310,390,58).collidepoint(mx,my):
            custo=self.custo_arma_atual()
            if self.nivel_arma >= MAX_NIVEL_ARMA:
                self.mostrar_mensagem("Armas no nível máximo!", 1.6)
            elif self.moedas>=custo:
                self.moedas-=custo; self.nivel_arma+=1; self.mostrar_mensagem("Arma aprimorada!", 1.4)
            else:
                self.mostrar_mensagem("Moedas insuficientes", 1.4)
        if pygame.Rect(60,378,390,40).collidepoint(mx,my):
            self.loja_aberta=False
            self.arvore_aberta=True
            return
        botoes_info = [
            ("missoes", pygame.Rect(60,426,186,38)),
            ("conquistas", pygame.Rect(264,426,186,38)),
            ("perfil", pygame.Rect(60,472,186,38)),
            ("bestiario", pygame.Rect(264,472,186,38)),
        ]
        for nome, r in botoes_info:
            if r.collidepoint(mx,my):
                self.loja_aberta=False
                self.tela_info=nome
                self.verificar_conquistas()
                return
        if pygame.Rect(60,520,390,34).collidepoint(mx,my):
            self.loja_aberta=False
            self.ambientes_aberto=True
            return
        # Cama e porta são melhoradas tocando diretamente nelas.
        # Torres são compradas somente tocando nos espaços "+".

    def invocar_chefe_especial_teste(self, tipo):
        # Remove chefe ativo para o teste ficar limpo e evita empilhar chefes.
        self.monstros = [m for m in self.monstros if not getattr(m, "tipo", "").startswith("chefe")]
        self.chefe_invocacao_tick = 0
        self.chefe_fantasma_tick = 0
        self.chefe_invocacao_pendente = None
        x = self.quarto.corredor.right - 80
        y = 215
        chefe = Monstro(x, y, self.noite, tipo)
        self.monstros.append(chefe)
        self.fase = "noite"

    def chefe_ativo(self):
        chefes = [m for m in self.monstros if m.vida > 0 and getattr(m, "tipo", "").startswith("chefe")]
        return chefes[0] if chefes else None

    def adicionar_efeito_chefe(self, x, y, tipo="entrada"):
        # Efeito curto: anel circular + poucos pixels. Sem Surface com alpha.
        self.efeitos_chefe.append({"x": int(x), "y": int(y), "tipo": tipo, "t": 0.0, "total": 0.55 if tipo == "entrada" else 0.75})
        self.tremor_chefe = max(getattr(self, "tremor_chefe", 0), 7 if tipo == "entrada" else 10)

    def criar_invocado_chefe(self, tipo, dono="chefe", x=None, y=None):
        # Invocações de chefes especiais.
        # Não contam na meta da onda e não dão recompensa para evitar farm de moedas.
        if x is None:
            x=random.randint(self.quarto.corredor.x + 35, self.quarto.corredor.right - 70)
        if y is None:
            y=random.choice([188,215,242])
        monstro = Monstro(int(x), int(y), self.noite, tipo)
        monstro.invocado_por = dono
        monstro.vida = max(12, int(monstro.vida * 0.85))
        monstro.vida_max = monstro.vida
        monstro.recompensa = 0
        self.monstros.append(monstro)
        self.tocar_som_monstro_aparece(tipo, monstro)
        if tipo.startswith("chefe"):
            self.adicionar_efeito_chefe(monstro.rect.centerx, monstro.rect.centery, "entrada")
        self.registrar_inimigo_visto(tipo)

    def agendar_invocado_chefe(self, tipo, dono="chefe"):
        # Primeiro aparece um símbolo no corredor; depois o monstro nasce no centro dele.
        x=random.randint(self.quarto.corredor.x + 35, self.quarto.corredor.right - 70)
        y=random.choice([188,215,242])
        self.invocacoes_simbolos.append({
            "tipo": tipo, "dono": dono, "x": int(x), "y": int(y),
            "tempo": 0.95, "total": 0.95
        })

    def atualizar_simbolos_invocacao(self, dt):
        novos=[]
        for s in self.invocacoes_simbolos:
            s["tempo"] -= dt
            if s["tempo"] <= 0:
                self.criar_invocado_chefe(s["tipo"], s["dono"], s["x"], s["y"])
            else:
                novos.append(s)
        self.invocacoes_simbolos = novos

    def desenhar_simbolos_invocacao(self):
        for s in getattr(self, "invocacoes_simbolos", []):
            total=max(0.01, s.get("total", 0.95))
            prog=1.0 - max(0.0, s.get("tempo", 0.0)) / total
            cx=int(s["x"] + 24); cy=int(s["y"] + 30)
            cor=(130, 220, 255) if s.get("tipo") == "fantasma" else (110, 230, 130)
            raio=16 + int(prog * 18)
            pygame.draw.circle(self.tela, (18, 18, 26), (cx, cy), raio + 5, 2)
            pygame.draw.circle(self.tela, cor, (cx, cy), raio, 2)
            pygame.draw.circle(self.tela, cor, (cx, cy), max(6, raio // 2), 1)
            pygame.draw.line(self.tela, cor, (cx-raio, cy), (cx+raio, cy), 1)
            pygame.draw.line(self.tela, cor, (cx, cy-raio), (cx, cy+raio), 1)
            if int(pygame.time.get_ticks()/120) % 2 == 0:
                pygame.draw.circle(self.tela, (245, 245, 180), (cx, cy), 3)

    def contar_invocados_chefe(self, dono):
        vivos = sum(1 for m in self.monstros if m.vida > 0 and getattr(m, "invocado_por", "") == dono)
        pendentes = sum(1 for s in getattr(self, "invocacoes_simbolos", []) if s.get("dono") == dono)
        return vivos + pendentes

    def invocar_grupo_chefe(self, tipo, quantidade, dono):
        for _ in range(quantidade):
            self.agendar_invocado_chefe(tipo, dono)

    def preparar_invocacao_chefe(self, chefe_tipo, fala, tipo_invocado, quantidade, dono):
        # v1.20.3: o chefe fala primeiro; a invocacao acontece 1 segundo depois.
        # Isso deixa a habilidade legivel sem travar a partida.
        if getattr(self, "chefe_invocacao_pendente", None):
            return
        self.chefe_invocacao_pendente = {
            "chefe_tipo": chefe_tipo,
            "tipo_invocado": tipo_invocado,
            "quantidade": quantidade,
            "dono": dono,
            "tempo": 1.0,
            "fala": fala,
        }
        self.chefe_fala_tempo = 1.0
        # Fala do chefe agora aparece em balão acima dele, não na HUD.

    def atualizar_invocacao_pendente_chefe(self, dt):
        pendente = getattr(self, "chefe_invocacao_pendente", None)
        if not pendente:
            return
        pendente["tempo"] -= dt
        self.chefe_fala_tempo = max(0, pendente["tempo"])
        if pendente["tempo"] > 0:
            return
        chefe = self.chefe_ativo()
        if chefe and chefe.tipo == pendente["chefe_tipo"]:
            quantidade = int(pendente.get("quantidade", 0))

            # Habilidade especial do Doutor Infectado:
            # cada zumbi invocado restaura vida. Quando ele fica crítico
            # (20% ou menos), a cura dobra para deixar a fase final mais tensa.
            if chefe.tipo == "chefe_diretor" and pendente.get("dono") == "diretor":
                cura_por_zumbi = 2000 if chefe.vida <= chefe.vida_max * 0.20 else 1000
                cura_total = max(0, quantidade) * cura_por_zumbi
                if cura_total > 0:
                    vida_antes = chefe.vida
                    chefe.vida = min(chefe.vida_max, chefe.vida + cura_total)
                    curado = int(chefe.vida - vida_antes)
                    if curado > 0:
                        self.adicionar_impacto(Impacto(chefe.rect.centerx, chefe.rect.centery, VERDE, 42))
                        self.mostrar_mensagem(f"Doutor Infectado recuperou +{curado} HP", 1.45)

            self.invocar_grupo_chefe(pendente["tipo_invocado"], quantidade, pendente["dono"])

            # Habilidade especial da Babá Sombria:
            # após invocar fantasmas, ela some por 5 segundos.
            if chefe.tipo == "chefe_baba" and pendente.get("dono") == "baba":
                chefe.invisivel_tempo = 5.0
                self.adicionar_impacto(Impacto(chefe.rect.centerx, chefe.rect.centery, (135, 150, 210), 48))
        self.chefe_invocacao_pendente = None
        self.chefe_fala_tempo = 0

    def atualizar_habilidades_chefes(self, dt):
        self.atualizar_invocacao_pendente_chefe(dt)
        chefe = self.chefe_ativo()
        if not chefe:
            return
        if chefe.tipo == "chefe_fantasma":
            self.chefe_fantasma_tick += dt
            if self.chefe_fantasma_tick >= 4.8:
                self.chefe_fantasma_tick = 0
                chefe.invisivel_tempo = 1.6
                self.mostrar_mensagem("Rei Fantasma ficou invisível!", 1.4)
        elif chefe.tipo == "chefe_diretor":
            # Doutor Infectado: HP alto, dano igual ao antigo, invocação de zumbis e cura por invocação.
            self.chefe_invocacao_tick += dt
            em_furia = chefe.vida <= chefe.vida_max * 0.5
            intervalo = 8.5 if em_furia else 10.0
            quantidade = 3 if em_furia else 2
            limite = 6
            if self.chefe_invocacao_tick >= intervalo and self.contar_invocados_chefe("diretor") < limite and not getattr(self, "chefe_invocacao_pendente", None):
                self.chefe_invocacao_tick = 0
                disponivel = max(0, limite - self.contar_invocados_chefe("diretor"))
                self.preparar_invocacao_chefe(
                    "chefe_diretor",
                    "Zumbis... levantem-se!",
                    "normal",
                    min(quantidade, disponivel),
                    "diretor",
                )
        elif chefe.tipo == "chefe_baba":
            # Babá Sombria: HP 15K, dano igual ao antigo e invocação de fantasmas.
            self.chefe_invocacao_tick += dt
            em_furia = chefe.vida <= chefe.vida_max * 0.5
            intervalo = 8.5 if em_furia else 10.0
            quantidade = 3 if em_furia else 2
            limite = 8
            if self.chefe_invocacao_tick >= intervalo and self.contar_invocados_chefe("baba") < limite and not getattr(self, "chefe_invocacao_pendente", None):
                self.chefe_invocacao_tick = 0
                disponivel = max(0, limite - self.contar_invocados_chefe("baba"))
                self.preparar_invocacao_chefe(
                    "chefe_baba",
                    "Venham brincar...",
                    "fantasma",
                    min(quantidade, disponivel),
                    "baba",
                )
        elif chefe.tipo == "chefe_caos":
            self.chefe_invocacao_tick += dt
            if self.chefe_invocacao_tick >= 5.2 and len(self.monstros) < self.max_simultaneos + 4:
                self.chefe_invocacao_tick = 0
                self.criar_invocado_chefe(random.choice(["corredor", "fantasma"]), "caos")
                self.mostrar_mensagem("Senhor do Caos invocou pesadelos!", 1.3)

    def iniciar_morte_chefe_especial(self, chefe):
        """Pausa curta e luzes brancas quando Doutor/Babá são derrotados."""
        if getattr(self, "morte_chefe_cinematica", None):
            return
        if getattr(chefe, "tipo", "") not in ("chefe_diretor", "chefe_baba"):
            return
        chefe.morte_total = 2.20
        chefe.morte_tempo = 2.20
        self.morte_chefe_cinematica = {"tempo": 2.20, "total": 2.20, "chefe": chefe}
        self.luzes_morte_chefe = []
        cx, cy = chefe.rect.centerx, chefe.rect.centery
        for _ in range(34):
            ang = random.uniform(0, math.pi * 2)
            vel = random.uniform(30, 95)
            self.luzes_morte_chefe.append({
                "x": float(cx + random.randint(-12, 12)),
                "y": float(cy + random.randint(-18, 18)),
                "vx": math.cos(ang) * vel * 0.38,
                "vy": math.sin(ang) * vel * 0.28 - random.uniform(35, 80),
                "r": random.choice([2, 2, 3, 4, 5]),
                "t": random.uniform(1.25, 2.05),
                "max": 2.05,
            })
        self.tremor_chefe = max(getattr(self, "tremor_chefe", 0), 12)

    def atualizar_morte_chefe_cinematica(self, dt):
        estado = getattr(self, "morte_chefe_cinematica", None)
        if not estado:
            return False
        dt = min(dt, 1/24)
        estado["tempo"] -= dt
        chefe = estado.get("chefe")
        if chefe is not None:
            chefe.morte_tempo = max(0, getattr(chefe, "morte_tempo", 0) - dt)
        self.tremor_chefe = max(0, getattr(self, "tremor_chefe", 0) - dt * 18)
        novas=[]
        for p in getattr(self, "luzes_morte_chefe", []):
            p["t"] -= dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 18 * dt
            if p["t"] > 0:
                novas.append(p)
        self.luzes_morte_chefe = novas
        # A mensagem e o brilho visual continuam sumindo, mas gameplay fica congelado.
        self.mensagem_tempo = max(0, getattr(self, "mensagem_tempo", 0) - dt)
        for e in getattr(self, "efeitos_chefe", []):
            e["t"] += dt
        self.efeitos_chefe=[e for e in getattr(self,"efeitos_chefe",[]) if e["t"] < e.get("total",0.6)]
        if estado["tempo"] <= 0:
            self.morte_chefe_cinematica = None
            self.luzes_morte_chefe = []
        return True

    def desenhar_luzes_morte_chefe(self):
        for p in getattr(self, "luzes_morte_chefe", []):
            frac = max(0.0, min(1.0, p.get("t", 0) / max(0.01, p.get("max", 1))))
            r = max(1, int(p.get("r", 2) * (0.65 + frac)))
            x, y = int(p["x"]), int(p["y"])
            pygame.draw.circle(self.tela, (255, 255, 255), (x, y), r)
            if r >= 3:
                pygame.draw.circle(self.tela, (210, 230, 255), (x, y), r + 2, 1)

    def atualizar(self,dt):
        if getattr(self, "sons", None):
            self.sons.atualizar_ambiente(min(dt, 1/24))
        if self.jogo_acabou or self.pausado: return
        if self.atualizar_morte_chefe_cinematica(dt):
            return
        # Evita travadas em cascata: quando um frame atrasa no Android,
        # não tentamos simular um dt gigante no frame seguinte.
        dt = min(dt, 1/24)
        dt *= self.velocidade_jogo
        self.tempo_jogado_acum += dt
        if self.tempo_jogado_acum >= 1:
            segundos = int(self.tempo_jogado_acum)
            self.tempo_jogado_acum -= segundos
            self.save["tempo_jogado"] = int(self.save.get("tempo_jogado", 0)) + segundos
        self.tempo_estatisticas += dt
        if self.tempo_estatisticas >= 12:
            self.tempo_estatisticas = 0
            self.salvar_progresso()
        self.mensagem_tempo=max(0,self.mensagem_tempo-dt)
        self.botao_feedback_tempo=max(0,self.botao_feedback_tempo-dt)
        self.transicao_noite=max(0,self.transicao_noite-dt)
        self.evento_diretor_tempo=max(0,getattr(self,"evento_diretor_tempo",0)-dt)
        self.flash_porta=max(0,self.flash_porta-dt)
        self.flash_reparo=max(0,getattr(self,"flash_reparo",0)-dt)
        self.pulso_hud=max(0,self.pulso_hud-dt)
        self.modo_upgrade_hint=max(0,getattr(self,"modo_upgrade_hint",0)-dt)
        self.painel_objeto_tempo=max(0,getattr(self,"painel_objeto_tempo",0)-dt)
        self.atualizar_habilidades_jogador(dt)
        if self.painel_objeto_tempo <= 0:
            self.painel_objeto = None
        # Poeira leve do ambiente.
        for p in getattr(self, "particulas", []):
            p.atualizar(dt)
        # Atualiza efeitos de chefe com lista pequena.
        self.tremor_chefe=max(0,getattr(self,"tremor_chefe",0)-dt*32)
        for e in getattr(self, "efeitos_chefe", []):
            e["t"] += dt
        self.efeitos_chefe=[e for e in getattr(self,"efeitos_chefe",[]) if e["t"] < e.get("total",0.6)]
        # contadores visuais suavizados, sem alterar o valor real usado na jogabilidade
        self.moedas_display += (self.moedas - self.moedas_display) * min(1, dt * 9)
        self.vida_porta_display += (self.vida_porta - self.vida_porta_display) * min(1, dt * 10)
        self.tempo_moeda+=dt
        if self.fase == "preparacao":
            self.tempo_preparacao -= dt
            if self.tempo_preparacao <= 0:
                self.iniciar_noite()
        else:
            self.tempo_spawn+=dt
        self.pulso_cama=max(0,self.pulso_cama-dt*2.8); self.tremor_porta=max(0,self.tremor_porta-dt*42)
        if self.tempo_moeda>=1:
            self.tempo_moeda=0; ganho=self.ganho_moedas(); self.moedas+=ganho; self.save["moedas_totais"] = int(self.save.get("moedas_totais", 0)) + ganho
            self.adicionar_moeda_animada(self.quarto.cama.centerx,self.quarto.cama.y-18,ganho)
        vivos_em_jogo = sum(1 for m in self.monstros if m.vida > 0)
        if self.fase == "noite" and self.spawnados<self.meta_noite and vivos_em_jogo < self.max_simultaneos and self.tempo_spawn>=self.intervalo_spawn:
            self.tempo_spawn=0; self.criar_monstro()
        # Tempestade: dano leve e espaçado na porta. Não usa efeitos pesados.
        if False and self.fase == "noite" and getattr(self, "evento_noite", "normal") == "tempestade":
            self.tempestade_tick += dt
            if self.tempestade_tick >= 5.0:
                self.tempestade_tick = 0
                self.vida_porta -= max(1, 2 + self.noite // 3)
                self.flash_porta = 0.18
                self.tremor_porta = 5
                self.mostrar_mensagem("A tempestade abalou a porta!", 1.2)
        # v0.8.0: organiza fila antes de mover. Os mais próximos da porta têm prioridade.
        fila = [m for m in self.monstros if m.vida > 0]
        fila.sort(key=lambda m: -m.rect.y)
        for i, m in enumerate(fila):
            if hasattr(m, "configurar_alvo_porta"):
                m.configurar_alvo_porta(self.quarto.porta)
            if hasattr(m, "definir_fila"):
                m.definir_fila(i)
        for m in self.monstros:
            if hasattr(m, "configurar_alvo_porta"):
                m.configurar_alvo_porta(self.quarto.porta)
            m.atualizar(dt)
        self.atualizar_habilidades_chefes(dt)
        self.atualizar_simbolos_invocacao(dt)
        atacantes=[m for m in self.monstros if m.pode_atacar()]
        # Só alguns conseguem bater ao mesmo tempo. Os outros ficam na fila.
        limite_ataque = 1 if self.noite < 3 else (2 if self.noite < 6 else 3)
        atacantes = atacantes[:limite_ataque]
        self.porta_em_ataque = bool(atacantes)
        if atacantes:
            self.tempo_ataque+=dt
            if self.tempo_ataque>=.62:
                self.tempo_ataque=0; dano=sum(m.dano for m in atacantes)
                if any(getattr(m,"tipo","")=="infectado" for m in atacantes): dano += max(1, self.noite//2)
                if any(getattr(m,"tipo","") in ("fantasma", "sombra") for m in atacantes): dano += 1
                dano = max(1, int(dano * getattr(self, "evento_dano_porta_mult", 1.0)))
                self.vida_porta-=dano; self.tremor_porta=9; self.flash_porta=0.22
                self.tocar_som_porta_impacto()
        # Calcula bônus de suportes uma vez por frame, não uma vez para cada torre.
        bonus_total_torres = self.bonus_arma()*self.bonus_suportes_dano()
        dt_torres = dt * self.bonus_reflexos_perm()
        for t in self.torres:
            if isinstance(t, Torre):
                t.atualizar(dt_torres,self.monstros,self.projeteis,bonus_total_torres)
                som_disparo = getattr(t, "som_disparo_pendente", None)
                if som_disparo:
                    # Som das armas toca somente quando a torre realmente dispara.
                    # Cada arma usa o nome enviado pela Torre e o gerenciador de áudio escolhe o canal de armas.
                    volumes_armas = {
                        "metralhadora_disparo": 0.82,
                        "canhao_disparo": 0.88,
                        "veneno_disparo": 0.84,
                        "gelo_disparo": 0.84,
                        "lanca_chamas_disparo": 0.78,
                        "sniper_disparo": 0.68,
                        "tesla_disparo": 0.82,
                        "laser_disparo": 0.82,
                        "espingarda_disparo": 0.88,
                    }
                    intervalos_armas = {
                        "metralhadora_disparo": 0.035,
                        "lanca_chamas_disparo": 0.045,
                        "tesla_disparo": 0.05,
                        "laser_disparo": 0.08,
                        "espingarda_disparo": 0.08,
                    }
                    self.tocar_som(
                        som_disparo,
                        volume=volumes_armas.get(som_disparo, 0.82),
                        intervalo=intervalos_armas.get(som_disparo, 0.02),
                    )
                    t.som_disparo_pendente = None
            elif isinstance(t, Suporte):
                t.atualizar_suporte(dt, self)
        for p in self.projeteis:
            p.atualizar(dt,self.monstros)
            if p.impactou: self.adicionar_impacto(p.impactou)
        self.projeteis=[p for p in self.projeteis if p.vivo]
        if len(self.projeteis) > MAX_PROJETEIS_ATIVOS:
            self.projeteis = self.projeteis[-MAX_PROJETEIS_ATIVOS:]
        for i in self.impactos: i.atualizar(dt)
        self.impactos=[i for i in self.impactos if i.t>0]
        if len(self.impactos) > MAX_IMPACTOS_ATIVOS:
            self.impactos = self.impactos[-MAX_IMPACTOS_ATIVOS:]
        for a in self.moedas_animadas: a.atualizar(dt)
        self.moedas_animadas=[a for a in self.moedas_animadas if a.tempo>0]
        if len(self.moedas_animadas) > MAX_MOEDAS_ANIMADAS:
            self.moedas_animadas = self.moedas_animadas[-MAX_MOEDAS_ANIMADAS:]
        vivos=[]
        for m in self.monstros:
            if m.vida<=0 and not hasattr(m,"contou"):
                self.parar_todos_sons_monstro(m)
                m.contou=True
                invocado = bool(getattr(m, "invocado_por", None))

                if invocado:
                    # Zumbis do Diretor e fantasmas da Babá morrem corretamente ao zerar a vida,
                    # mas não contam a onda e não dão moedas para evitar farm no chefe.
                    if getattr(m, "tipo", "") == "explosivo":
                        self.tocar_som("explosivo_morte", volume=0.80, intervalo=0.05)
                else:
                    self.derrotados+=1; self.total_derrotados+=1
                    if getattr(m, "tipo", "") == "explosivo":
                        self.tocar_som("explosivo_morte", volume=1.0, intervalo=0.05)
                    else:
                        # Correção: não tocar som de zumbi ao morrer/finalizar a noite.
                        pass

                    if getattr(m, "tipo", "").startswith("chefe"):
                        if getattr(m, "tipo", "") in ("chefe_diretor", "chefe_baba"):
                            self.iniciar_morte_chefe_especial(m)
                        self.adicionar_efeito_chefe(m.rect.centerx, m.rect.centery, "derrota")
                    self.save["monstros_derrotados"] = int(self.save.get("monstros_derrotados", 0)) + 1
                    recompensa = int(m.recompensa * (2 if self.habilidade_ganancia_tempo > 0 else 1))
                    self.moedas+=recompensa
                    self.save["moedas_totais"] = int(self.save.get("moedas_totais", 0)) + recompensa
                    self.adicionar_moeda_animada(m.rect.centerx, m.rect.y, recompensa)
                    self.tocar_som("moeda", volume=0.45, intervalo=0.08)

                    # Explosivo: se morrer muito perto da porta, causa dano leve.
                    if getattr(m, "tipo", "") == "explosivo" and abs(m.rect.centery - self.quarto.porta.centery) < 120:
                        self.vida_porta -= max(1, int((14 + self.noite * 2) * getattr(self, "evento_dano_porta_mult", 1.0)))
                        self.flash_porta = 0.22
                        self.tremor_porta = 8
                        # Explosão não conta como batida na porta: sem som de impacto de porta.
                        self.mostrar_mensagem("Explosão atingiu a porta!", 1.4)
                    elif getattr(m, "tipo", "") == "chefe_demolidor":
                        dano = max(20, int((45 + self.noite * 4) * getattr(self, "evento_dano_porta_mult", 1.0)))
                        if abs(m.rect.centery - self.quarto.porta.centery) < 150:
                            self.vida_porta -= dano
                            self.flash_porta = 0.35
                            self.tremor_porta = 13
                            # Explosão do Demolidor não conta como batida na porta.
                            self.mostrar_mensagem("Demolidor explodiu perto da porta!", 1.8)
                        else:
                            self.mostrar_mensagem("[BOSS] Demolidor derrotado!", 1.8)
                        self.save["chefes_derrotados"] = int(self.save.get("chefes_derrotados", 0)) + 1
                        self.dar_fragmentos(1 + self.noite // 10, "Chefe")
                        self.dar_fragmentos_lendarios(1, "Boss Especial")
                    elif getattr(m, "tipo", "").startswith("chefe"):
                        bonus = (220 + self.noite * 14) if getattr(m, "tipo", "") == "chefe_diretor" else (80 + self.noite * 12)
                        self.moedas += bonus
                        self.save["moedas_totais"] = int(self.save.get("moedas_totais", 0)) + bonus
                        self.adicionar_moeda_animada(m.rect.centerx, m.rect.y - 18, bonus)
                        self.save["chefes_derrotados"] = int(self.save.get("chefes_derrotados", 0)) + 1
                        self.dar_fragmentos(1 + self.noite // 10, "Chefe")
                        qtd_lendario = 2 if getattr(m, "tipo", "") in ("chefe_diretor", "chefe_baba") else 1
                        self.dar_fragmentos_lendarios(qtd_lendario, "Boss Especial")
                        if getattr(m, "tipo", "") == "chefe_diretor":
                            self.evento_diretor_tempo = 0
                            self.campanha_info().setdefault("chefes_campanha_derrotados", [])
                            if "doutor_infectado" not in self.campanha_info()["chefes_campanha_derrotados"]:
                                self.campanha_info()["chefes_campanha_derrotados"].append("doutor_infectado")
                            self.desbloquear_andar(2, "Doutor Infectado")
                            self.mostrar_mensagem("O Doutor Infectado foi derrotado. Elevador liberado.", 3.0)
                            if not getattr(self, "historia_doutor_mostrada", False):
                                self.historia_doutor_mostrada = True
                                self.historia_pendente = "doutor"
                                # Limpa a tela para a transição ficar limpa depois da morte do chefe.
                                self.monstros = []
                                self.projeteis = []
                                self.invocacoes_simbolos = []
                        elif getattr(m, "tipo", "") == "chefe_baba":
                            self.campanha_info().setdefault("chefes_campanha_derrotados", [])
                            if "baba_sombria" not in self.campanha_info()["chefes_campanha_derrotados"]:
                                self.campanha_info()["chefes_campanha_derrotados"].append("baba_sombria")
                            self.desbloquear_andar(3, "Babá Sombria")
                            self.mostrar_mensagem("A Babá Sombria foi derrotada.", 3.0)
                            if not getattr(self, "historia_baba_mostrada", False):
                                self.historia_baba_mostrada = True
                                self.historia_pendente = "baba_final"
                                self.monstros = []
                                self.projeteis = []
                                self.invocacoes_simbolos = []
                        else:
                            self.mostrar_mensagem(f"[BOSS] {nome_chefe(m.tipo)} derrotado!", 2.0)
            if not m.morto_pronto(): vivos.append(m)
        self.monstros=vivos
        if self.vida_porta<=0:
            self.vida_porta=0; self.jogo_acabou=True; self.vitoria=False; self.tocar_som("game_over", intervalo=2.0); self.registrar_recorde_e_marco(); self.salvar_progresso()
        if self.derrotados>=self.meta_noite and self.spawnados>=self.meta_noite and not self.monstros:
            self.noite+=1
            self.registrar_recorde_e_marco()
            bonus_noite = int((18 + self.noite * 4) * self.bonus_prosperidade() * self.bonus_moedas_ambiente() * (0.95 if self.noite >= 16 else 1.0))
            self.moedas += bonus_noite
            self.save["moedas_totais"] = int(self.save.get("moedas_totais", 0)) + bonus_noite
            self.verificar_conquistas()
            self.vida_porta=min(self.vida_porta_max,self.vida_porta+35+self.nivel_porta*8)
            self.tocar_som("vitoria", intervalo=1.0)
            self.preparar_noite()
            self.mostrar_mensagem("Amanheceu. Prepare-se para a próxima noite.", 2.6)

    def desenhar_atmosfera(self):
        # v1.1.1: modo ultra leve.
        # Sem brilho/pulso da cama e sem pisca-pisca da HUD.
        # Mantém apenas sinais baratos que não criam Surface transparente.
        # v1.11.3: Hospital recebe sinais visuais baratos, sem Surface com alpha.
        if self.hospital_ativo():
            # v1.11.6: detalhes estáticos foram para o cache do quarto.
            # Aqui ficam só efeitos dinâmicos muito leves.
            pygame.draw.rect(self.tela, (58, 105, 92), self.quarto.corredor.inflate(-7, -7), 1, border_radius=4)
            pygame.draw.rect(self.tela, (50, 95, 84), self.quarto.rect.inflate(-8, -8), 1, border_radius=4)

            ticks = pygame.time.get_ticks()
            if getattr(self, "evento_diretor_tempo", 0) > 0:
                # Piscada do evento do Doutor Infectado: retângulos simples, sem Surface/alpha.
                if (ticks // 120) % 2 == 0:
                    pygame.draw.rect(self.tela, (95, 22, 28), self.quarto.rect.inflate(-14, -14), 3, border_radius=8)
                    pygame.draw.rect(self.tela, (115, 25, 30), self.quarto.corredor.inflate(-12, -12), 2, border_radius=5)

            # Luz fluorescente piscando ocasionalmente. Sem alpha e sem Surface extra.
            ciclo = (ticks // 170) % 32
            if ciclo in (0, 1, 2, 12):
                pygame.draw.rect(self.tela, (205, 240, 225), (self.quarto.rect.x + 72, self.quarto.rect.y + 22, self.quarto.rect.w - 144, 4), border_radius=2)

            # Luzes de emergência discretas nos cantos.
            if (ticks // 900) % 2 == 0:
                pygame.draw.circle(self.tela, (95, 170, 140), (self.quarto.rect.x + 42, self.quarto.rect.y + 42), 5)
                pygame.draw.circle(self.tela, (95, 170, 140), (self.quarto.rect.right - 42, self.quarto.rect.y + 42), 5)

            # Relâmpago raro na janela, só um traço rápido.
            if (ticks // 1200) % 18 == 7:
                pygame.draw.line(self.tela, (225, 245, 255), (self.quarto.corredor.x + 54, self.quarto.corredor.y + 28), (self.quarto.corredor.x + 42, self.quarto.corredor.y + 46), 2)
                pygame.draw.line(self.tela, (225, 245, 255), (self.quarto.corredor.x + 42, self.quarto.corredor.y + 46), (self.quarto.corredor.x + 62, self.quarto.corredor.y + 54), 2)

        # Poeira/brilhos ocasionais do cenário: 7 pontos pequenos, custo mínimo.
        for p in getattr(self, "particulas", []):
            p.desenhar(self.tela)

        # Porta em ataque usa vermelho; reparo agora usa verde dentro do desenho da porta.
        if self.flash_porta > 0:
            pygame.draw.rect(self.tela, (120, 35, 35), self.quarto.porta.inflate(10, 8), 2, border_radius=8)

        if self.transicao_noite > 0:
            pygame.draw.rect(self.tela, (0, 0, 0), (0, 0, LARGURA, 22))
            pygame.draw.rect(self.tela, (0, 0, 0), (0, ALTURA-22, LARGURA, 22))

    def desenhar_efeitos_chefe(self):
        # v1.21.7: anéis de entrada/derrota dos chefes.
        for e in getattr(self, "efeitos_chefe", []):
            total = max(0.01, e.get("total", 0.6))
            p = max(0, min(1, e.get("t", 0) / total))
            x, y = e["x"], e["y"]
            derrota = e.get("tipo") == "derrota"
            raio = int((18 if not derrota else 30) + p * (64 if derrota else 46))
            cor = (255, 92, 70) if derrota else (185, 85, 235)
            cor2 = (255, 220, 120) if derrota else (255, 210, 90)
            pygame.draw.circle(self.tela, cor, (x, y), raio, 2)
            pygame.draw.circle(self.tela, cor2, (x, y), max(6, int(raio * 0.55)), 1)
            if p < 0.45:
                pygame.draw.circle(self.tela, (255, 235, 160), (x, y), max(3, int(14 * (1 - p))), 0)
            qtd = 8 if derrota else 6
            for i in range(qtd):
                ang = i * (math.pi * 2 / qtd) + p
                dist = int(raio * (0.45 + p * 0.45))
                px = int(x + math.cos(ang) * dist)
                py = int(y + math.sin(ang) * dist)
                pygame.draw.rect(self.tela, cor2 if i % 2 == 0 else cor, (px, py, 3 if derrota else 2, 3 if derrota else 2))

    def desenhar_brilho_hud_moeda(self):
        # v1.1.1: removido o pisca-pisca do cartão de moedas para máxima leveza.
        return

    def desenhar_barra_chefe(self):
        chefe = self.chefe_ativo()
        if not chefe:
            return
        caixa = pygame.Rect(42, 150, LARGURA - 84, 42)
        pygame.draw.rect(self.tela, (8, 8, 14), caixa.move(0, 3), border_radius=13)
        pygame.draw.rect(self.tela, (26, 20, 34), caixa, border_radius=13)
        pygame.draw.rect(self.tela, VERMELHO_ESCURO, caixa, 2, border_radius=13)
        nome = nome_chefe(chefe.tipo)
        if getattr(chefe, "invisivel_tempo", 0) > 0:
            nome += "  •  INVISÍVEL"
        desenhar_texto_centralizado_ajustado(self.tela, f"CHEFE: {nome}", pygame.Rect(caixa.x, caixa.y + 3, caixa.w, 18), AMARELO, self.fonte_pequena, margem=8)
        barra = pygame.Rect(caixa.x + 16, caixa.y + 24, caixa.w - 32, 10)
        cor_barra = VERMELHO
        if chefe.vida <= chefe.vida_max * 0.25 and (pygame.time.get_ticks() // 180) % 2 == 0:
            cor_barra = (255, 205, 80)
            pygame.draw.rect(self.tela, (90, 25, 25), barra.inflate(8, 6), 1, border_radius=5)
        if getattr(self, "barra_chefe_alerta", False) and getattr(self, "chefe_invocacao_pendente", None):
            cor_barra = LARANJA
        desenhar_barra(self.tela, barra.x, barra.y, barra.w, barra.h, chefe.vida, chefe.vida_max, cor_barra)

    def desenhar_alerta_chefe_simples(self):
        # Balão de fala acima do chefe antes da invocação.
        # Evita texto na HUD e funciona sem emojis no Android.
        if not getattr(self, "efeito_alerta_chefe", True):
            return
        pendente = getattr(self, "chefe_invocacao_pendente", None)
        if not pendente:
            return
        chefe = self.chefe_ativo()
        if not chefe:
            return
        fala = str(pendente.get("fala", "...")).strip() or "..."
        cx = chefe.rect.centerx
        cy = max(36, chefe.rect.y - 42)
        w = min(LARGURA - 40, max(150, len(fala) * 8 + 26))
        h = 34
        caixa = pygame.Rect(0, 0, w, h)
        caixa.center = (cx, cy)
        caixa.x = max(12, min(caixa.x, LARGURA - caixa.w - 12))
        pygame.draw.rect(self.tela, (9, 9, 15), caixa.move(0, 3), border_radius=13)
        pygame.draw.rect(self.tela, (235, 232, 214), caixa, border_radius=13)
        pygame.draw.rect(self.tela, (70, 56, 74), caixa, 2, border_radius=13)
        ponta = [(cx - 8, caixa.bottom - 1), (cx + 8, caixa.bottom - 1), (cx, caixa.bottom + 11)]
        pygame.draw.polygon(self.tela, (235, 232, 214), ponta)
        pygame.draw.polygon(self.tela, (70, 56, 74), ponta, 2)
        desenhar_texto_centralizado_ajustado(self.tela, fala, caixa.inflate(-10, -6), (34, 26, 40), self.fonte_pequena, margem=4)

    def desenhar_hud(self):
        # HUD v1.0.1: cartões premium com ícones desenhados por código.
        hud = pygame.Rect(14, 12, LARGURA - 28, 134)
        pygame.draw.rect(self.tela, (5, 5, 9), hud.move(0, 5), border_radius=18)
        pygame.draw.rect(self.tela, (18, 18, 28), hud, border_radius=18)
        pygame.draw.rect(self.tela, (70, 66, 86), hud.inflate(-4, -4), 1, border_radius=16)
        pygame.draw.rect(self.tela, AMARELO_ESCURO, hud, 2, border_radius=18)

        # v1.11.4: topo mais organizado para caber melhor no Android.
        # O nome do jogo fica limpo, e o ambiente/fragmentos aparecem em uma linha menor.
        amb_nome = self.ambiente_cfg().get("nome", "Quarto Infantil")
        desenhar_texto_centralizado(self.tela, "SONO PROFUNDO", pygame.Rect(hud.x, hud.y + 6, hud.w, 23), AMARELO, self.fonte)
        subtitulo = f"{self.texto_andar()}  •  Fragmentos: {int(self.fragmentos)}"
        desenhar_texto_centralizado(self.tela, subtitulo, pygame.Rect(hud.x, hud.y + 30, hud.w, 16), CIANO if self.hospital_ativo() else CINZA_CLARO, self.fonte_pequena)

        fase_txt = f"Preparar {max(0,int(self.tempo_preparacao)+1)}s" if self.fase == "preparacao" else f"Onda {self.derrotados}/{self.meta_noite}"
        evento_nome = self.nome_evento_noite()
        if evento_nome:
            fase_txt += f"  •  {evento_nome}"
        topo = pygame.Rect(hud.x + 18, hud.y + 52, hud.w - 36, 20)
        pygame.draw.rect(self.tela, (12, 12, 19), topo, border_radius=8)
        desenhar_texto_centralizado(self.tela, f"Noite {self.noite}  •  {fase_txt}", topo, VERMELHO if self.pesadelo else BRANCO, self.fonte_pequena)

        card_y = hud.y + 82
        card_h = 42
        gap = 10
        card_w = (hud.w - 34 - gap * 3) // 4
        cards = [
            ("moeda", "MOEDAS", f"{int(self.moedas_display)}", AMARELO),
            ("cama", "CAMA", ("MAX" if self.nivel_cama >= MAX_NIVEL_CAMA else f"Nível {self.nivel_cama}") + f"  +{self.ganho_moedas()}/s", VERDE),
            ("porta", "PORTA", "MAX" if self.nivel_porta >= MAX_NIVEL_PORTA else f"Nível {self.nivel_porta}", AMARELO),
            ("restam", "RESTAM", f"{max(0,self.meta_noite-self.derrotados)}", VERMELHO),
        ]
        for i, (icone, rotulo, valor, cor) in enumerate(cards):
            r = pygame.Rect(hud.x + 17 + (card_w + gap) * i, card_y, card_w, card_h)
            pygame.draw.rect(self.tela, (8, 8, 13), r.move(0, 3), border_radius=12)
            pygame.draw.rect(self.tela, (30, 30, 43), r, border_radius=12)
            pygame.draw.rect(self.tela, cor, r, 1, border_radius=12)
            desenhar_icone(self.tela, icone, r.x + 24, r.centery, 1)
            desenhar_texto(self.tela, rotulo, r.x + 45, r.y + 5, cor, self.fonte_pequena)
            desenhar_texto(self.tela, valor, r.x + 45, r.y + 24, BRANCO, self.fonte_pequena)

        self.desenhar_brilho_hud_moeda()
        if self.selecionada is not None and self.selecionada < len(self.torres):
            t=self.torres[self.selecionada]
            if t:
                prox = "MAX" if t.nivel >= 15 else f"Up ${t.custo_upgrade()}"
                painel = pygame.Rect(24, 150, LARGURA - 48, 30)
                pygame.draw.rect(self.tela,(8,8,13),painel.move(0,3),border_radius=10)
                pygame.draw.rect(self.tela,(22,22,32),painel,border_radius=10)
                pygame.draw.rect(self.tela,AMARELO,painel,1,border_radius=10)
                if isinstance(t, Torre):
                    info = f"{t.nome} {t.nivel}  Dano {t.dano}  Alc. {t.alcance}  {prox}"
                else:
                    desc = SUPORTES.get(t.tipo, {}).get("desc", "Suporte")
                    info = f"{t.nome} {t.nivel}  {desc}  {prox}"
                    if getattr(t, "tipo", "") == "cofre_supremo":
                        info = f"LENDÁRIO ✦ {t.nome} {t.nivel}  {desc}  {prox}"
                desenhar_texto_centralizado_ajustado(self.tela,info,painel,AMARELO,self.fonte_pequena, margem=10)

    def desenhar_menu_construcao(self):
        pygame.draw.rect(self.tela,(12,12,18),(0,0,LARGURA,ALTURA))

        # v1.23.6: menu ainda maior para caber armas normais + lendárias com leitura melhor.
        caixa = pygame.Rect(30, 145, LARGURA - 60, 720)
        pygame.draw.rect(self.tela,(24,24,32),caixa,border_radius=16)
        pygame.draw.rect(self.tela,AMARELO,caixa,2,border_radius=16)

        suporte = self.slot_e_suporte(self.menu_construcao)
        titulo = "Escolha o suporte" if suporte else "Escolha a arma"
        opcoes = self.opcoes_suportes_disponiveis() if suporte else self.opcoes_armas_disponiveis()

        desenhar_texto(self.tela,titulo,caixa.x + 42,caixa.y + 24,AMARELO,self.fonte)
        botao_x = pygame.Rect(caixa.right - 46, caixa.y + 18, 34, 34)
        pygame.draw.rect(self.tela,VERMELHO,botao_x,border_radius=8)
        desenhar_texto(self.tela,"X",botao_x.x + 11,botao_x.y + 6,BRANCO,self.fonte_pequena)

        y = caixa.y + 72
        passo = 64 if len(opcoes) > 5 else 70
        altura_item = 56 if len(opcoes) > 5 else 60
        item_x = caixa.x + 30
        item_w = caixa.w - 60

        for tipo,cfg in opcoes.items():
            r=pygame.Rect(item_x,y,item_w,altura_item)
            ok=self.moedas>=cfg["custo"]
            lendario_item = tipo in ("laser_supremo", "espingarda_suprema", "cofre_supremo")
            fundo_item = cfg["cor"] if ok else CINZA
            if lendario_item:
                fundo_item = (55, 42, 18) if tipo == "cofre_supremo" and ok else ((62, 52, 35) if tipo == "cofre_supremo" else ((42, 26, 58) if ok else (58, 50, 66)))
            pygame.draw.rect(self.tela, fundo_item, r, border_radius=10)
            pygame.draw.rect(self.tela, ROXO if lendario_item else BRANCO, r, 3 if lendario_item else 2, border_radius=10)
            if lendario_item:
                selo = pygame.Rect(r.right - 118, r.y + 8, 96, 20)
                pygame.draw.rect(self.tela, AMARELO, selo, border_radius=7)
                rotulo = "★ LENDÁRIO ★" if tipo == "cofre_supremo" else "LENDÁRIA"
                desenhar_texto_centralizado(self.tela, rotulo, selo, PRETO_TEXTO, self.fonte_pequena)
                pygame.draw.rect(self.tela, AMARELO, r.inflate(-8, -8), 1, border_radius=8)
                if tipo == "cofre_supremo":
                    pygame.draw.rect(self.tela, (255, 245, 170), r.inflate(-14, -14), 1, border_radius=7)
            nome = cfg['nome']
            cor_txt = BRANCO if lendario_item else (PRETO_TEXTO if ok else BRANCO)
            desenhar_texto(self.tela,f"{cfg['icone']} {nome}   ${cfg['custo']}",r.x + 16,y + 8,cor_txt,self.fonte_pequena)
            if suporte:
                desenhar_texto(self.tela,cfg.get('desc',''),r.x + 16,y + 31,AMARELO if tipo == 'cofre_supremo' else cor_txt,self.fonte_pequena)
            else:
                papel = {"sniper":"prioriza vida alta", "veneno":"dano contínuo", "eletrica":"raio em cadeia", "chamas":"cone curto", "metralhadora":"alta cadência", "canhao":"dano em área", "gelo":"controle de velocidade", "laser_supremo":"feixe atravessador", "espingarda_suprema":"cone espalhado"}.get(tipo, "")
                if papel:
                    desenhar_texto(self.tela,papel,r.x + 16,y + 31,AMARELO if lendario_item else cor_txt,self.fonte_pequena)
            y+=passo

        desenhar_texto(self.tela,"Toque fora da janela para cancelar",caixa.x + 56,caixa.bottom - 34,CINZA_CLARO,self.fonte_pequena)

    def desenhar_icone_fragmento(self, x, y, r=7):
        pts = [(x, y-r), (x+r, y-1), (x+4, y+r), (x-4, y+r), (x-r, y-1)]
        pygame.draw.polygon(self.tela, (160, 80, 230), pts)
        pygame.draw.polygon(self.tela, CIANO, pts, 1)
        pygame.draw.line(self.tela, (230, 210, 255), (x-2, y-r+2), (x+3, y-1), 1)

    def desenhar_icone_coroa(self, x, y, escala=1):
        s = max(1, int(escala))
        pts = [(x-11*s,y+6*s),(x-8*s,y-6*s),(x-3*s,y+1*s),(x,y-8*s),(x+3*s,y+1*s),(x+8*s,y-6*s),(x+11*s,y+6*s)]
        pygame.draw.polygon(self.tela, AMARELO, pts)
        pygame.draw.line(self.tela, AMARELO_ESCURO, (x-11*s,y+6*s), (x+11*s,y+6*s), 2)

    def desenhar_icone_video(self, x, y):
        corpo = pygame.Rect(x-10, y-8, 18, 14)
        pygame.draw.rect(self.tela, (35,35,45), corpo, border_radius=3)
        pygame.draw.rect(self.tela, BRANCO, corpo, 1, border_radius=3)
        pygame.draw.polygon(self.tela, BRANCO, [(x-3,y-5),(x-3,y+3),(x+4,y-1)])
        pygame.draw.polygon(self.tela, BRANCO, [(x+8,y-4),(x+14,y-7),(x+14,y+5),(x+8,y+2)])

    def desenhar_icone_lendario(self, chave, x, y, cor):
        # Ícones pixelados simples para não depender de emojis ou imagens externas.
        if chave == "laser_supremo":
            pygame.draw.line(self.tela, (255,245,245), (x-10,y), (x+10,y), 3)
            pygame.draw.line(self.tela, (255,60,60), (x-10,y), (x+10,y), 1)
            pygame.draw.circle(self.tela, (255,245,245), (x-11,y), 3)
            pygame.draw.circle(self.tela, (255,60,60), (x+11,y), 3)
        elif chave == "espingarda_suprema":
            pygame.draw.line(self.tela, (70,45,30), (x-10,y+5), (x-2,y+1), 4)
            pygame.draw.line(self.tela, (60,60,70), (x-2,y), (x+11,y-5), 4)
            pygame.draw.line(self.tela, (230,230,230), (x+1,y-2), (x+12,y-7), 1)
            for dy in (-5, 0, 5):
                pygame.draw.line(self.tela, (255,170,70), (x+8,y-4), (x+14,y+dy), 1)
        elif chave == "terremoto":
            pygame.draw.line(self.tela, (70,45,30), (x-11,y+6), (x+11,y+6), 2)
            pygame.draw.line(self.tela, (255,230,130), (x-8,y-4), (x-2,y+2), 2)
            pygame.draw.line(self.tela, (255,230,130), (x-2,y+2), (x+3,y-3), 2)
            pygame.draw.line(self.tela, (255,230,130), (x+3,y-3), (x+8,y+4), 2)
            pygame.draw.circle(self.tela, (255,230,130), (x,y), 12, 1)
        elif chave == "cofre_supremo":
            r = pygame.Rect(x-10, y-8, 20, 16)
            pygame.draw.rect(self.tela, (55,55,62), r, border_radius=3)
            pygame.draw.rect(self.tela, AMARELO, r, 2, border_radius=3)
            pygame.draw.circle(self.tela, AMARELO, (x,y), 4)
            pygame.draw.line(self.tela, PRETO_TEXTO, (x,y-3), (x,y+3), 1)
            pygame.draw.line(self.tela, PRETO_TEXTO, (x-3,y), (x+3,y), 1)
        else:
            pygame.draw.circle(self.tela, cor, (x,y), 10)

    def desenhar_loja(self):
        pygame.draw.rect(self.tela,(10,10,16),(0,0,LARGURA,ALTURA))
        # v1.23.2: janela da loja maior e mais respirável.
        caixa=pygame.Rect(35,170,650,735)
        pygame.draw.rect(self.tela,(23,23,31),caixa,border_radius=15)
        pygame.draw.rect(self.tela,CIANO,caixa,2,border_radius=15)
        desenhar_texto(self.tela,"OFICINA - SONO PROFUNDO",185,195,AMARELO,self.fonte)
        desenhar_texto(self.tela,f"Moedas: {int(self.moedas)}   Frag: {int(self.fragmentos)}",65,235,AMARELO,self.fonte_pequena)
        self.desenhar_icone_fragmento(300, 242, 7)
        desenhar_texto(self.tela, f"{int(getattr(self,'fragmentos_lendarios',0))}", 314, 235, CIANO, self.fonte_pequena)
        pygame.draw.rect(self.tela,VERMELHO,(630,190,40,40),border_radius=7)
        desenhar_texto(self.tela,"X",643,199,BRANCO,self.fonte)

        aba = getattr(self, "loja_aba", "normal")
        normal = pygame.Rect(60,260,285,36)
        lend = pygame.Rect(375,260,285,36)
        pygame.draw.rect(self.tela, CIANO if aba == "normal" else (35,35,45), normal, border_radius=8)
        pygame.draw.rect(self.tela, BRANCO, normal, 1, border_radius=8)
        desenhar_texto_centralizado(self.tela, "Oficina", normal, PRETO_TEXTO if aba == "normal" else BRANCO, self.fonte_pequena)
        pygame.draw.rect(self.tela, AMARELO if aba == "lendarios" else (35,35,45), lend, border_radius=8)
        pygame.draw.rect(self.tela, BRANCO, lend, 1, border_radius=8)
        self.desenhar_icone_coroa(lend.x + 36, lend.y + 19, 1)
        desenhar_texto_centralizado(self.tela, "Lendarios", pygame.Rect(lend.x+35, lend.y, lend.w-35, lend.h), PRETO_TEXTO if aba == "lendarios" else BRANCO, self.fonte_pequena)

        if aba == "lendarios":
            y = 315
            for chave, info in LENDARIOS_INFO.items():
                desbloq = self.item_lendario_desbloqueado(chave)
                custo = int(info.get("custo", 0))
                cor = info.get("cor", AMARELO)
                card = pygame.Rect(60, y, 600, 100)
                pygame.draw.rect(self.tela, (36,31,24) if not desbloq else (30,45,35), card, border_radius=10)
                pygame.draw.rect(self.tela, cor, card, 2, border_radius=10)
                # Ícones desenhados por código, sem depender de emoji/fonte do Android.
                pygame.draw.circle(self.tela, cor, (95, y+50), 23)
                pygame.draw.circle(self.tela, (255,245,185), (88, y+40), 5)
                self.desenhar_icone_lendario(chave, 95, y+50, cor)
                nome = info.get("nome", chave)
                atual = int(getattr(self,'fragmentos_lendarios',0))
                progresso = min(1.0, atual / max(1, custo))
                desenhar_texto(self.tela, nome, 130, y+12, AMARELO if not desbloq else VERDE, self.fonte_pequena)
                desenhar_texto(self.tela, info.get("desc",""), 130, y+36, CINZA_CLARO, self.fonte_pequena)
                if desbloq:
                    desenhar_texto(self.tela, "DESBLOQUEADO", 130, y+66, VERDE, self.fonte_pequena)
                    destino = "Na HUD de habilidades" if chave == "terremoto" else "Disponível na construção"
                    if chave == "cofre_supremo":
                        destino = "Disponível nos suportes"
                    desenhar_texto(self.tela, destino, 405, y+40, VERDE, self.fonte_pequena)
                else:
                    # Barra de progresso lendário com mais espaço.
                    barra = pygame.Rect(130, y+68, 245, 10)
                    pygame.draw.rect(self.tela, (18,18,24), barra, border_radius=5)
                    pygame.draw.rect(self.tela, ROXO, (barra.x, barra.y, int(barra.w*progresso), barra.h), border_radius=5)
                    pygame.draw.rect(self.tela, CIANO, barra, 1, border_radius=5)
                    self.desenhar_icone_fragmento(392, y+73, 6)
                    desenhar_texto(self.tela, f"{atual}/{custo}", 405, y+62, CIANO, self.fonte_pequena)
                    btn_ad = pygame.Rect(525, y+28, 48, 44)
                    btn_unlock = pygame.Rect(580, y+28, 70, 44)
                    pygame.draw.rect(self.tela, ROXO, btn_ad, border_radius=8)
                    pygame.draw.rect(self.tela, BRANCO, btn_ad, 1, border_radius=8)
                    self.desenhar_icone_video(btn_ad.centerx, btn_ad.centery-4)
                    desenhar_texto_centralizado(self.tela, "+1", pygame.Rect(btn_ad.x, btn_ad.y+25, btn_ad.w, 15), BRANCO, self.fonte_pequena)
                    ok = atual >= custo
                    pygame.draw.rect(self.tela, VERDE if ok else CINZA, btn_unlock, border_radius=8)
                    pygame.draw.rect(self.tela, BRANCO, btn_unlock, 1, border_radius=8)
                    desenhar_texto_centralizado(self.tela, "OK" if ok else "BLOQ", btn_unlock, PRETO_TEXTO if ok else BRANCO, self.fonte_pequena)
                y += 110
            self.desenhar_icone_fragmento(78,830,6)
            desenhar_texto(self.tela,"Anúncios são teste. Boss especial dá fragmentos.",92,820,CINZA_CLARO,self.fonte_pequena)
            return

        custo_arma = self.custo_arma_atual()
        max_arma = self.nivel_arma >= MAX_NIVEL_ARMA
        preco = "MAX" if max_arma else f"${custo_arma}"
        ok = self.moedas >= custo_arma and not max_arma
        r = pygame.Rect(60,310,390,58)
        pygame.draw.rect(self.tela, CIANO if ok else CINZA, r, border_radius=9)
        pygame.draw.rect(self.tela, BRANCO, r, 2, border_radius=9)
        cor_txt = PRETO_TEXTO if ok else BRANCO
        desenhar_texto(self.tela, f"Armas  Melhorar {preco}", 78, 319, cor_txt, self.fonte_pequena)
        desenhar_texto(self.tela, f"{self.nivel_arma}/{MAX_NIVEL_ARMA}  dano +{int((self.bonus_arma()-1)*100)}%", 78, 342, cor_txt, self.fonte_pequena)

        arv = pygame.Rect(60, 378, 390, 40)
        pygame.draw.rect(self.tela, ROXO, arv, border_radius=9)
        pygame.draw.rect(self.tela, BRANCO, arv, 2, border_radius=9)
        desenhar_texto_centralizado(self.tela, f"Arvore do Sono  |  Fragmentos: {int(self.fragmentos)}", arv, BRANCO, self.fonte_pequena)

        botoes = [
            ("Missões", pygame.Rect(60,426,186,38), VERDE),
            ("Conquistas", pygame.Rect(264,426,186,38), AMARELO),
            ("Perfil", pygame.Rect(60,472,186,38), CIANO),
            ("Bestiário", pygame.Rect(264,472,186,38), ROXO),
        ]
        for texto_btn, rb, cor_btn in botoes:
            pygame.draw.rect(self.tela, cor_btn, rb, border_radius=9)
            pygame.draw.rect(self.tela, BRANCO, rb, 2, border_radius=9)
            desenhar_texto_centralizado(self.tela, texto_btn, rb, PRETO_TEXTO if texto_btn != "Bestiário" else BRANCO, self.fonte_pequena)

        amb = pygame.Rect(60, 520, 390, 34)
        pygame.draw.rect(self.tela, (31,31,42), amb, border_radius=8)
        pygame.draw.rect(self.tela, VERDE, amb, 2, border_radius=8)
        nome_amb = obter_ambiente(getattr(self, "ambiente_atual", AMBIENTE_PADRAO)).get("nome", "Quarto Infantil")
        desenhar_texto_centralizado(self.tela, "Ambientes  |  " + nome_amb, amb, BRANCO, self.fonte_pequena)
    def clique_tela_info(self, mx, my):
        if pygame.Rect(LARGURA-86, 204, 48, 40).collidepoint(mx, my):
            self.tela_info = None
            return
        if self.tela_info == "missoes":
            y = 292
            for chave, info in MISSOES_INFO.items():
                r = pygame.Rect(54, y, LARGURA-108, 58)
                if r.collidepoint(mx, my):
                    self.coletar_missao(chave)
                    return
                y += 68
        if not pygame.Rect(30, 185, LARGURA-60, min(500, ALTURA-230)).collidepoint(mx, my):
            self.tela_info = None

    def desenhar_progresso_meta(self, r, atual, valor, pct, cor):
        barra = pygame.Rect(r.x + 14, r.bottom - 15, r.w - 28, 8)
        pygame.draw.rect(self.tela, (10,10,16), barra, border_radius=4)
        if barra.w > 0:
            preench = pygame.Rect(barra.x, barra.y, int(barra.w * pct), barra.h)
            pygame.draw.rect(self.tela, cor, preench, border_radius=4)
        pygame.draw.rect(self.tela, CINZA_CLARO, barra, 1, border_radius=4)

    def desenhar_tela_info(self):
        pygame.draw.rect(self.tela, (9, 9, 15), (0, 0, LARGURA, ALTURA))
        caixa = self.rects_tela_info()
        pygame.draw.rect(self.tela, (22, 22, 32), caixa, border_radius=15)
        pygame.draw.rect(self.tela, AMARELO, caixa, 2, border_radius=15)
        titulos = {
            "missoes": "MISSOES",
            "conquistas": "CONQUISTAS",
            "perfil": "PERFIL",
            "bestiario": "BESTIARIO",
        }
        desenhar_texto(self.tela, titulos.get(self.tela_info, ""), caixa.x + 24, caixa.y + 20, AMARELO, self.fonte)
        pygame.draw.rect(self.tela, VERMELHO, (LARGURA-86, 204, 48, 40), border_radius=8)
        desenhar_texto_centralizado(self.tela, "X", pygame.Rect(LARGURA-86,204,48,40), BRANCO, self.fonte)
        desenhar_texto(self.tela, f"Fragmentos: {int(self.fragmentos)}", caixa.x + 24, caixa.y + 52, CIANO, self.fonte_pequena)

        if self.tela_info == "missoes":
            coletadas = set(self.save.get("missoes_coletadas", []))
            y = caixa.y + 96
            for chave, info in MISSOES_INFO.items():
                r = pygame.Rect(caixa.x + 24, y, caixa.w - 48, 58)
                feita = meta_concluida(self.save, info)
                coletada = chave in coletadas
                cor = VERDE if feita and not coletada else (AMARELO if feita else (70,70,86))
                pygame.draw.rect(self.tela, (8,8,14), r.move(0,3), border_radius=10)
                pygame.draw.rect(self.tela, cor, r, border_radius=10)
                pygame.draw.rect(self.tela, BRANCO, r, 1, border_radius=10)
                txt_cor = PRETO_TEXTO if feita else BRANCO
                status = "COLETADO" if coletada else ("TOQUE PARA COLETAR" if feita else "EM ANDAMENTO")
                desenhar_texto(self.tela, f"{info['nome']}  +{info['fragmentos']} Fragmentos", r.x+14, r.y+6, txt_cor, self.fonte_pequena)
                desenhar_texto(self.tela, f"{info['desc']}  |  {status}", r.x+14, r.y+27, txt_cor, self.fonte_pequena)
                atual, valor, pct = self.progresso_meta(info)
                self.desenhar_progresso_meta(r, atual, valor, pct, VERDE if feita else CIANO)
                y += 68

        elif self.tela_info == "conquistas":
            ganhas = set(self.save.get("conquistas", []))
            self.verificar_conquistas()
            y = caixa.y + 88
            for i, (chave, info) in enumerate(CONQUISTAS_INFO.items()):
                if y > caixa.bottom - 48:
                    break
                r = pygame.Rect(caixa.x + 22, y, caixa.w - 44, 46)
                ganha = chave in ganhas or meta_concluida(self.save, info)
                cor = AMARELO if ganha else (56,56,70)
                pygame.draw.rect(self.tela, (8,8,14), r.move(0,3), border_radius=9)
                pygame.draw.rect(self.tela, (36,36,49), r, border_radius=9)
                pygame.draw.rect(self.tela, cor, r, 1, border_radius=9)
                selo = "OK" if ganha else "--"
                desenhar_texto(self.tela, f"{selo} {info['nome']}  +{info['fragmentos']}", r.x+12, r.y+5, cor, self.fonte_pequena)
                desenhar_texto(self.tela, info["desc"], r.x+12, r.y+25, BRANCO, self.fonte_pequena)
                y += 52

        elif self.tela_info == "perfil":
            dados = [
                ("Maior noite", self.save.get("recorde_noite", 0)),
                ("Chefes derrotados", self.save.get("chefes_derrotados", 0)),
                ("Monstros eliminados", self.save.get("monstros_derrotados", 0)),
                ("Moedas totais", self.save.get("moedas_totais", 0)),
                ("Habilidades usadas", self.save.get("habilidades_usadas", 0)),
                ("Conquistas", f"{len(self.save.get('conquistas', []))}/{len(CONQUISTAS_INFO)}"),
            ]
            y = caixa.y + 96
            for nome, valor in dados:
                r = pygame.Rect(caixa.x + 26, y, caixa.w - 52, 42)
                pygame.draw.rect(self.tela, (31,31,43), r, border_radius=9)
                pygame.draw.rect(self.tela, CIANO, r, 1, border_radius=9)
                desenhar_texto(self.tela, nome, r.x+14, r.y+10, CIANO, self.fonte_pequena)
                desenhar_texto(self.tela, str(valor), r.right-150, r.y+10, BRANCO, self.fonte_pequena)
                y += 49

        elif self.tela_info == "bestiario":
            vistos = set(self.save.get("inimigos_vistos", []))
            lista = ["normal", "corredor", "bruto", "explosivo", "fantasma", "chefe_devorador", "chefe_fantasma", "chefe_demolidor", "chefe_caos"]
            nomes = {
                "normal": "Zumbi", "corredor": "Corredor", "bruto": "Bruto", "explosivo": "Explosivo", "fantasma": "Fantasma",
                "chefe_devorador": "Devorador", "chefe_fantasma": "Rei Fantasma", "chefe_demolidor": "Demolidor", "chefe_caos": "Senhor do Caos",
            }
            y = caixa.y + 92
            for tipo in lista:
                if y > caixa.bottom - 44:
                    break
                r = pygame.Rect(caixa.x + 24, y, caixa.w - 48, 42)
                visto = tipo in vistos
                pygame.draw.rect(self.tela, (31,31,43), r, border_radius=9)
                pygame.draw.rect(self.tela, VERDE if visto else (70,70,82), r, 1, border_radius=9)
                nome = nomes[tipo] if visto else "???"
                desc = "Encontrado" if visto else "Ainda não apareceu"
                desenhar_texto(self.tela, nome, r.x+14, r.y+7, VERDE if visto else CINZA_CLARO, self.fonte_pequena)
                desenhar_texto(self.tela, desc, r.x+210, r.y+7, BRANCO, self.fonte_pequena)
                y += 48


    # v1.11.2: seleção segura de ambientes.
    # Nesta etapa a escolha é salva, mas ainda não muda a jogabilidade.
    def rects_ambientes(self):
        rects = []
        y = 292
        for amb in listar_ambientes():
            rects.append((amb, pygame.Rect(54, y, LARGURA - 108, 72)))
            y += 82
        return rects

    def ambiente_desbloqueado(self, amb):
        desbloqueados = set(self.save.get("ambientes_desbloqueados", ["quarto_infantil", "hospital_abandonado"]))
        return amb.get("desbloqueado", False) or amb.get("id") in desbloqueados

    def selecionar_ambiente(self, ambiente_id):
        self.ambiente_atual = ambiente_id
        self.save["ambiente_atual"] = ambiente_id
        self.salvar_progresso()
        nome = obter_ambiente(ambiente_id).get("nome", "Ambiente")
        self.mostrar_mensagem("Ambiente: " + nome, 1.6)

    def clique_ambientes(self, mx, my):
        if pygame.Rect(LARGURA-86, 204, 48, 40).collidepoint(mx, my):
            self.ambientes_aberto = False
            return
        for amb, r in self.rects_ambientes():
            if r.collidepoint(mx, my):
                if self.ambiente_desbloqueado(amb):
                    self.selecionar_ambiente(amb.get("id", AMBIENTE_PADRAO))
                    self.ambientes_aberto = False
                else:
                    self.mostrar_mensagem("Ambiente bloqueado", 1.3)
                return
        if not pygame.Rect(30, 185, LARGURA-60, min(500, ALTURA-230)).collidepoint(mx, my):
            self.ambientes_aberto = False

    def desenhar_ambientes(self):
        pygame.draw.rect(self.tela, (9, 9, 15), (0, 0, LARGURA, ALTURA))
        caixa = pygame.Rect(30, 185, LARGURA-60, min(500, ALTURA-230))
        pygame.draw.rect(self.tela, (22, 22, 32), caixa, border_radius=15)
        pygame.draw.rect(self.tela, VERDE, caixa, 2, border_radius=15)
        desenhar_texto(self.tela, "ANDARES / AMBIENTES", caixa.x + 24, caixa.y + 20, AMARELO, self.fonte)
        desenhar_texto(self.tela, "Campanha salva por andares. O elevador libera novos locais.", caixa.x + 24, caixa.y + 52, CINZA_CLARO, self.fonte_pequena)
        pygame.draw.rect(self.tela, VERMELHO, (LARGURA-86, 204, 48, 40), border_radius=8)
        desenhar_texto_centralizado(self.tela, "X", pygame.Rect(LARGURA-86,204,48,40), BRANCO, self.fonte)

        atual = getattr(self, "ambiente_atual", AMBIENTE_PADRAO)
        for amb, r in self.rects_ambientes():
            aberto = self.ambiente_desbloqueado(amb)
            escolhido = amb.get("id") == atual
            cor = VERDE if escolhido else (CIANO if aberto else (70,70,82))
            pygame.draw.rect(self.tela, (8,8,14), r.move(0,3), border_radius=10)
            pygame.draw.rect(self.tela, (36,36,49), r, border_radius=10)
            pygame.draw.rect(self.tela, cor, r, 2 if escolhido else 1, border_radius=10)
            status = "SELECIONADO" if escolhido else ("DISPONIVEL" if aberto else "BLOQUEADO")
            titulo = amb.get("nome", "Ambiente") + "  |  " + status
            desenhar_texto(self.tela, titulo, r.x + 14, r.y + 8, cor, self.fonte_pequena)
            desenhar_texto(self.tela, amb.get("descricao", ""), r.x + 14, r.y + 34, BRANCO if aberto else CINZA_CLARO, self.fonte_pequena)

    def rects_arvore(self):
        rects = []
        y = 288
        for nome in MELHORIAS_INFO.keys():
            rects.append((nome, pygame.Rect(58, y, LARGURA - 116, 54)))
            y += 62
        return rects

    def clique_arvore(self, mx, my):
        if pygame.Rect(LARGURA-86, 204, 48, 40).collidepoint(mx, my):
            self.arvore_aberta = False
            return
        for nome, r in self.rects_arvore():
            if r.collidepoint(mx, my):
                self.comprar_upgrade_permanente(nome)
                return
        # toque fora da janela fecha para manter simples no celular
        if not pygame.Rect(30, 185, LARGURA-60, 455).collidepoint(mx, my):
            self.arvore_aberta = False

    def desenhar_arvore(self):
        pygame.draw.rect(self.tela, (9, 9, 15), (0, 0, LARGURA, ALTURA))
        caixa = pygame.Rect(30, 185, LARGURA-60, 455)
        pygame.draw.rect(self.tela, (22, 22, 32), caixa, border_radius=15)
        pygame.draw.rect(self.tela, ROXO, caixa, 2, border_radius=15)
        desenhar_texto(self.tela, "ARVORE DO SONO", caixa.x + 24, caixa.y + 20, AMARELO, self.fonte)
        desenhar_texto(self.tela, f"Fragmentos: {int(self.fragmentos)}", caixa.x + 24, caixa.y + 53, CIANO, self.fonte_pequena)
        pygame.draw.rect(self.tela, VERMELHO, (LARGURA-86, 204, 48, 40), border_radius=8)
        desenhar_texto_centralizado(self.tela, "X", pygame.Rect(LARGURA-86,204,48,40), BRANCO, self.fonte)

        for nome, r in self.rects_arvore():
            info = MELHORIAS_INFO[nome]
            nivel = self.nivel_perm(nome)
            custo = custo_melhoria(nivel)
            maximo = custo is None
            ok = (not maximo) and self.fragmentos >= custo
            cor = VERDE if ok else (ROXO if not maximo else AMARELO)
            pygame.draw.rect(self.tela, (8,8,14), r.move(0,3), border_radius=10)
            pygame.draw.rect(self.tela, cor if ok else (44,44,58), r, border_radius=10)
            pygame.draw.rect(self.tela, BRANCO if ok else CINZA_CLARO, r, 1, border_radius=10)
            txt_cor = PRETO_TEXTO if ok else BRANCO
            titulo = f"{info['icone']}  {info['nome']}  {nivel}/{MAX_NIVEL_MELHORIA}"
            preco = "MAX" if maximo else f"Custo: {custo}"
            desenhar_texto(self.tela, titulo, r.x + 14, r.y + 7, txt_cor, self.fonte_pequena)
            desenhar_texto(self.tela, f"{info['desc']}   |   {preco}", r.x + 14, r.y + 30, txt_cor, self.fonte_pequena)

        rodape = pygame.Rect(caixa.x + 18, caixa.bottom - 42, caixa.w - 36, 28)
        pygame.draw.rect(self.tela, (32,32,44), rodape, border_radius=8)
        desenhar_texto_centralizado(self.tela, "Chefes e marcos de noite dão Fragmentos.", rodape, CINZA_CLARO, self.fonte_pequena)

    def desenhar_painel_objeto(self):
        if not getattr(self, "painel_objeto", None) or getattr(self, "painel_objeto_tempo", 0) <= 0:
            return
        tipo = self.painel_objeto
        if tipo == "cama":
            base = self.quarto.cama
            w, h = 260, 92
            x = max(self.quarto.rect.x + 10, min(base.centerx - w//2, self.quarto.rect.right - w - 10))
            y = max(self.quarto.rect.y + 10, base.y - h - 12)
            titulo = "CAMA"
            icon = "cama"
            if self.nivel_cama >= MAX_NIVEL_CAMA:
                linhas = ["MAX", f"+{self.ganho_moedas()}/s"]
                cor = VERDE
            else:
                custo = self.custo_cama_atual()
                falta = max(0, custo - int(self.moedas))
                linhas = [f"Nível {self.nivel_cama}  +{self.ganho_moedas()}/s", f"Upgrade: ${custo}"]
                cor = VERDE if self.moedas >= custo else AMARELO
        elif tipo == "porta":
            base = self.quarto.porta
            w, h = 280, 98
            x = max(self.quarto.rect.x + 10, min(base.centerx - w//2, self.quarto.rect.right - w - 10))
            y = min(self.quarto.rect.bottom - h - 10, base.bottom + 12)
            titulo = "PORTA"
            icon = "porta"
            hp = f"Vida: {int(self.vida_porta)}/{int(self.vida_porta_max)}"
            if self.nivel_porta >= MAX_NIVEL_PORTA:
                linhas = ["MAX", hp]
                cor = AMARELO
            else:
                custo = self.custo_porta_atual()
                falta = max(0, custo - int(self.moedas))
                linhas = [f"Nível {self.nivel_porta}  {hp}", f"Upgrade: ${custo}"]
                cor = AMARELO if self.moedas >= custo else (230,150,70)
        else:
            return

        caixa = pygame.Rect(int(x), int(y), w, h)
        pygame.draw.rect(self.tela, (15,15,22), caixa, border_radius=12)
        pygame.draw.rect(self.tela, cor, caixa, 2, border_radius=12)
        desenhar_icone(self.tela, icon, caixa.x + 24, caixa.y + 24, 1)
        desenhar_texto(self.tela, titulo, caixa.x + 48, caixa.y + 13, cor, self.fonte_pequena)
        desenhar_texto(self.tela, linhas[0], caixa.x + 18, caixa.y + 43, BRANCO, self.fonte_pequena)
        desenhar_texto(self.tela, linhas[1], caixa.x + 18, caixa.y + 66, BRANCO, self.fonte_pequena)

    def desenhar_botao_redondo(self, rect, cor, icone, texto=None, pressionado=False):
        """Botão redondo direto, leve e sem Surface transparente grande."""
        cx, cy = rect.center
        raio = rect.w // 2
        if pressionado:
            cy += 2
        pygame.draw.circle(self.tela, (5,5,8), (cx, cy+4), raio)
        pygame.draw.circle(self.tela, cor, (cx, cy), raio)
        pygame.draw.circle(self.tela, BRANCO, (cx, cy), raio, 2)
        if texto:
            # Texto dentro do botão para economizar espaço e manter a tela limpa.
            img = self.fonte_pequena.render(str(texto), True, PRETO_TEXTO)
            self.tela.blit(img, img.get_rect(center=(cx, cy)))
        else:
            desenhar_icone(self.tela, icone, cx, cy-1, 1)

    def desenhar_botao_pequeno(self, rect, cor, texto, icone=None, habilitado=True, pressionado=False):
        desloc = 2 if pressionado and habilitado else 0
        r = rect.move(0, desloc)
        cor_final = cor if habilitado else (65,65,76)
        pygame.draw.rect(self.tela, (5,5,8), r.move(0,3), border_radius=10)
        pygame.draw.rect(self.tela, cor_final, r, border_radius=10)
        pygame.draw.rect(self.tela, BRANCO, r, 2, border_radius=10)
        cor_txt = PRETO_TEXTO if habilitado else (185,185,190)
        if icone:
            desenhar_icone(self.tela, icone, r.x+18, r.centery, 1)
            # Texto ocupa só a área livre à direita do ícone.
            # Se o preço for grande, reduz levemente para não cortar o último número.
            area_txt = pygame.Rect(r.x+34, r.y, max(20, r.w-38), r.h)
            desenhar_texto_centralizado_ajustado(self.tela, texto, area_txt, cor_txt, self.fonte_pequena, margem=2)
        else:
            desenhar_texto_centralizado_ajustado(self.tela, texto, r, cor_txt, self.fonte_pequena, margem=4)

    def desenhar_controles_minimos(self):
        # v1.3.3: somente Loja fixa. Upgrades aparecem pelo toque nos objetos.
        self.desenhar_botao_redondo(self.botao_loja_lateral, LARANJA, "loja", "Loja", self.botao_pressionado("loja"))

        # Menu flutuante da torre selecionada.
        up_rect, vender_rect = self.rects_menu_torre()
        if up_rect:
            t = self.torres[self.selecionada]
            custo = t.custo_upgrade()
            txt_up = "MAX" if t.nivel >= 15 else f"Up ${custo}"
            self.desenhar_botao_pequeno(up_rect, CIANO, txt_up, "torre", self.moedas>=custo and t.nivel<15, self.botao_pressionado("upgrade"))
            self.desenhar_botao_pequeno(vender_rect, VERMELHO, "Vender", "vender", True, self.botao_pressionado("vender"))


    def desenhar_icone_cofre_supremo_mensagem(self, rect):
        """Ícone pequeno do Cofre Supremo para mensagens.
        Usa desenho por código, igual ao sprite do suporte, sem emoji/fonte externa.
        """
        r = rect
        cx, cy = r.center
        pygame.draw.circle(self.tela, (95, 70, 22), (cx, cy), 15, 1)
        pygame.draw.rect(self.tela, (74, 55, 22), (r.x+2, r.y+6, r.w-4, r.h-8), border_radius=5)
        pygame.draw.rect(self.tela, (168, 122, 30), (r.x+5, r.y+9, r.w-10, r.h-14), border_radius=4)
        pygame.draw.rect(self.tela, (255, 224, 95), (r.x+7, r.y+11, r.w-14, r.h-18), 2, border_radius=3)
        pygame.draw.circle(self.tela, (255, 245, 160), (cx, cy+1), 5)
        pygame.draw.circle(self.tela, (90, 58, 18), (cx, cy+1), 2, 1)
        pygame.draw.rect(self.tela, (255, 238, 130), (r.x+7, r.y+4, 5, 3), border_radius=1)
        pygame.draw.rect(self.tela, (255, 238, 130), (r.right-12, r.y+4, 5, 3), border_radius=1)
        for sx, sy in ((r.right-4, r.y+5), (r.x+4, r.bottom-6)):
            pygame.draw.line(self.tela, (255, 245, 170), (sx-2, sy), (sx+2, sy), 1)
            pygame.draw.line(self.tela, (255, 245, 170), (sx, sy-2), (sx, sy+2), 1)

    def desenhar_flash_relampago(self):
        """Flash branco rápido quando o trovão toca. Leve para Android/Pydroid."""
        if not getattr(self, "sons", None):
            return
        try:
            intensidade = self.sons.obter_flash_relampago()
        except Exception:
            intensidade = 0
        if intensidade <= 0:
            return
        # Sem Surface com alpha: desenha poucas linhas claras para simular clarão.
        cor = (min(255, int(80 + 120 * intensidade)), min(255, int(80 + 120 * intensidade)), min(255, int(95 + 135 * intensidade)))
        for y in range(0, ALTURA, 34):
            pygame.draw.line(self.tela, cor, (0, y), (LARGURA, y + 10), 1)
        pygame.draw.rect(self.tela, cor, pygame.Rect(0, 0, LARGURA, ALTURA), 2)


    def info_icone_mensagem(self, texto):
        """Retorna o tipo de ícone da mensagem sem depender de emoji.
        Corrige o quadradinho que aparecia em avisos de habilidades no Android.
        """
        msg = str(texto).lower()
        if "jackpot" in msg or "cofre supremo" in msg:
            return "suporte", "cofre_supremo"
        if "congel" in msg:
            return "habilidade", "congelar"
        if "meteoro" in msg:
            return "habilidade", "meteoro"
        if "reparad" in msg:
            return "habilidade", "reparar"
        if "descarga" in msg or "elétrica" in msg or "eletrica" in msg:
            return "habilidade", "raio"
        if "terremoto" in msg:
            return "habilidade", "terremoto"
        if "ganância" in msg or "ganancia" in msg:
            return "habilidade", "ganancia"
        if "cama" in msg:
            return "padrao", "cama"
        if "porta" in msg:
            return "padrao", "porta"
        if "moeda" in msg or "$" in msg:
            return "padrao", "moeda"
        if "defesa" in msg or "constru" in msg:
            return "padrao", "torre"
        if "amanheceu" in msg or "prepare" in msg:
            return "padrao", "cama"
        return "padrao", "restam"

    def desenhar(self):
        # O próprio cenário desenha o fundo inteiro.
        self.quarto.ambiente_id = self.ambiente_id()
        self.quarto.desenhar(self.tela,self.fonte,self.vida_porta_display,self.vida_porta_max,self.torres,self.pulso_cama,self.tremor_porta,self.nivel_cama,self.nivel_porta,getattr(self,"porta_em_ataque",False),getattr(self,"flash_reparo",0))
        self.desenhar_atmosfera()
        self.desenhar_flash_relampago()
        self.desenhar_efeitos_chefe()
        for i,t in enumerate(self.torres):
            if t: t.desenhar(self.tela,self.fonte_pequena, self.selecionada == i)
        # Limita visualmente os projéteis à área jogável.
        # Assim as balas não passam por cima da HUD/título nem ultrapassam
        # a linha superior do corredor. A bala continua existindo normalmente,
        # só deixa de ser desenhada fora do corredor/quarto.
        clip_anterior = self.tela.get_clip()
        area_jogo = self.quarto.corredor.union(self.quarto.rect)
        self.tela.set_clip(area_jogo)
        for p in self.projeteis:
            p.desenhar(self.tela)
        self.tela.set_clip(clip_anterior)
        for i in self.impactos: i.desenhar(self.tela)
        self.desenhar_simbolos_invocacao()
        ambiente_atual = self.ambiente_id()
        hospital = ambiente_atual == "hospital_abandonado"
        infantil = ambiente_atual == "quarto_infantil"
        for m in self.monstros: m.desenhar(self.tela,self.fonte,hospital,infantil)
        self.desenhar_luzes_morte_chefe()
        self.desenhar_alerta_chefe_simples()
        for a in self.moedas_animadas: a.desenhar(self.tela,self.fonte_pequena)
        self.desenhar_hud()
        self.desenhar_barra_chefe()
        self.desenhar_habilidades()
        self.desenhar_controles_minimos()
        self.desenhar_painel_objeto()
        if self.mensagem_tempo > 0:
            # Mensagem sem Surface com alpha. Mais leve no Pydroid.
            caixa_msg = pygame.Rect(34,158,LARGURA-68,36)
            pygame.draw.rect(self.tela,(16,16,23),caixa_msg,border_radius=9)
            pygame.draw.rect(self.tela,AMARELO,caixa_msg,2,border_radius=9)
            tipo_icone, icone_msg = self.info_icone_mensagem(self.mensagem)
            r_icon = pygame.Rect(caixa_msg.x + 10, caixa_msg.y + 4, 28, 28)
            if tipo_icone == "habilidade":
                # Ícone limpo, sem fundo quadrado e sem emoji.
                self.desenhar_icone_habilidade(icone_msg, r_icon, True)
            elif tipo_icone == "suporte" and icone_msg == "cofre_supremo":
                self.desenhar_icone_cofre_supremo_mensagem(r_icon)
            else:
                desenhar_icone(self.tela, icone_msg, caixa_msg.x + 24, caixa_msg.centery, 1)
            desenhar_texto_centralizado_ajustado(self.tela, str(self.mensagem), pygame.Rect(caixa_msg.x + 50, caixa_msg.y, caixa_msg.w - 58, caixa_msg.h), AMARELO, self.fonte_pequena, margem=4)
        # v1.7.2: 2 linhas de cima = armas; 1 linha acima da cama = suporte.
        if self.fase == "preparacao" and not self.jogo_acabou:
            caixa_prep = pygame.Rect(34, min(790, ALTURA-174), LARGURA-68, 52)
            pygame.draw.rect(self.tela,(16,16,23),caixa_prep,border_radius=11)
            pygame.draw.rect(self.tela,AMARELO,caixa_prep,2,border_radius=11)
            desenhar_texto_centralizado(self.tela,"PREPARE SUAS DEFESAS",pygame.Rect(caixa_prep.x, caixa_prep.y+3, caixa_prep.w, 24),AMARELO,self.fonte)
            desenhar_texto_centralizado(self.tela,f"A noite começa em {max(0,int(self.tempo_preparacao)+1)} segundos",pygame.Rect(caixa_prep.x, caixa_prep.y+27, caixa_prep.w, 20),BRANCO,self.fonte_pequena)

        if self.menu_construcao is not None:
            self.desenhar_menu_construcao()
        if self.loja_aberta:
            self.desenhar_loja()
        if self.arvore_aberta:
            self.desenhar_arvore()
        if self.ambientes_aberto:
            self.desenhar_ambientes()
        if self.tela_info_aberta():
            self.desenhar_tela_info()
        if self.jogo_acabou:
            caixa=pygame.Rect(55,390,410,130); pygame.draw.rect(self.tela,(24,24,31),caixa,border_radius=12); pygame.draw.rect(self.tela,BRANCO,caixa,2,border_radius=12)
            msg="VOCÊ VENCEU!" if self.vitoria else "VOCÊ PERDEU!"; cor=VERDE if self.vitoria else VERMELHO
            desenhar_texto(self.tela,msg,105,413,cor,self.fonte_grande)
            desenhar_texto(self.tela,"Aperte R para reiniciar",138,470,BRANCO,self.fonte)
