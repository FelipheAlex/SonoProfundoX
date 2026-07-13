import pygame
import math
from config import *
from interface import desenhar_barra

class Quarto:
    def __init__(self):
        # v0.9.8 teste: aumenta apenas a largura útil do jogo.
        # A altura e a barra inferior continuam no mesmo lugar.
        margem = 18
        painel_botoes = 126
        self.corredor = pygame.Rect(margem, 146, LARGURA - margem*2, 280)
        self.rect = pygame.Rect(margem, 470, LARGURA - margem*2, ALTURA - 470 - painel_botoes)
        porta_w = 130
        porta_h = 34
        self.porta = pygame.Rect((LARGURA - porta_w)//2, self.rect.y - 30, porta_w, porta_h)
        self.cama = pygame.Rect((LARGURA - 160)//2, self.rect.y + int(self.rect.h*0.54), 160, 140)

        # 9 espaços em grade, distribuídos proporcionalmente na largura nova.
        colunas = [self.rect.x + int(self.rect.w * 0.16),
                   self.rect.x + int(self.rect.w * 0.50) - 22,
                   self.rect.x + int(self.rect.w * 0.84) - 44]
        # v1.7.2 estável: 2 linhas de armas + 1 linha de suporte acima da cama.
        # Isso evita que o layout ultrapasse a parte inferior da tela e reduz elementos úteis fora de alcance.
        linha_armas_1 = self.rect.y + 48
        linha_armas_2 = self.rect.y + 142
        linha_suporte = self.cama.y - 58
        linhas = [linha_armas_1, linha_armas_2, linha_suporte]
        self.pontos_torre = [(x, y) for y in linhas for x in colunas]

        # v1.7.3: cache do cenário estático.
        # Antes o jogo redesenhava centenas de quadrados do fundo a cada frame;
        # no Pydroid isso causa lag. Agora o fundo é renderizado uma vez e só é copiado.
        self._cache_base = None
        self._cache_tamanho = None
        self._cache_ambiente = None
        self.fonte_slot = pygame.font.SysFont("arial", 17)

    def desenhar_grade(self, tela, area, tam, cor1, cor2):
        for y in range(area.y, area.bottom, tam):
            for x in range(area.x, area.right, tam):
                pygame.draw.rect(tela, cor1 if ((x//tam)+(y//tam)) % 2 == 0 else cor2, (x, y, tam, tam))

    def desenhar_slots(self, tela, torres, selecionada_idx=None):
        ambiente_id = getattr(self, "ambiente_id", "quarto_infantil")
        hospital = ambiente_id == "hospital_abandonado"
        infantil = ambiente_id == "quarto_infantil"
        for i, (x, y) in enumerate(self.pontos_torre):
            r = pygame.Rect(x, y, 44, 44)
            vazio = i >= len(torres) or torres[i] is None
            if vazio:
                suporte = i >= 6
                if hospital:
                    # Slots vazios com visual de equipamento médico.
                    # Continua sendo o mesmo slot clicável; muda só o desenho.
                    borda = (80, 185, 235) if suporte else (90, 105, 118)
                    pygame.draw.rect(tela, (42, 43, 53), r, border_radius=8)
                    pygame.draw.rect(tela, borda, r, 2, border_radius=8)
                    pygame.draw.rect(tela, (55, 58, 68), r.inflate(-8, -8), 1, border_radius=5)
                    if suporte:
                        img = self.fonte_slot.render("S", True, borda)
                        tela.blit(img, img.get_rect(center=r.center))
                    elif i % 3 == 0:
                        # Cruz médica discreta.
                        pygame.draw.line(tela, borda, (r.centerx-9, r.centery), (r.centerx+9, r.centery), 2)
                        pygame.draw.line(tela, borda, (r.centerx, r.centery-9), (r.centerx, r.centery+9), 2)
                    elif i % 3 == 1:
                        # Suporte de soro simples.
                        pygame.draw.line(tela, borda, (r.centerx, r.y+10), (r.centerx, r.bottom-9), 2)
                        pygame.draw.line(tela, borda, (r.centerx-8, r.y+12), (r.centerx+8, r.y+12), 2)
                        pygame.draw.rect(tela, borda, (r.centerx+5, r.y+15, 6, 10), 1, border_radius=2)
                    else:
                        # Monitor pequeno.
                        pygame.draw.rect(tela, borda, (r.x+10, r.y+13, 24, 15), 1, border_radius=3)
                        pygame.draw.line(tela, borda, (r.x+14, r.y+21), (r.x+20, r.y+21), 1)
                        pygame.draw.line(tela, borda, (r.x+20, r.y+21), (r.x+24, r.y+17), 1)
                        pygame.draw.line(tela, borda, (r.x+24, r.y+17), (r.x+31, r.y+24), 1)
                elif infantil:
                    # Slots da Ala Infantil: visual de brinquedos antigos.
                    # Continua sendo o mesmo slot clicável; só muda o desenho.
                    borda = (120, 175, 235) if suporte else (170, 130, 190)
                    pygame.draw.rect(tela, (43, 38, 50), r, border_radius=8)
                    pygame.draw.rect(tela, borda, r, 2, border_radius=8)
                    pygame.draw.rect(tela, (55, 48, 62), r.inflate(-8, -8), 1, border_radius=5)
                    if suporte:
                        img = self.fonte_slot.render("S", True, borda)
                        tela.blit(img, img.get_rect(center=r.center))
                    elif i % 3 == 0:
                        # Bloquinho infantil.
                        pygame.draw.rect(tela, borda, (r.x+12, r.y+13, 20, 20), 2, border_radius=3)
                        pygame.draw.line(tela, borda, (r.x+17, r.y+20), (r.x+27, r.y+20), 1)
                        pygame.draw.line(tela, borda, (r.x+22, r.y+16), (r.x+22, r.y+29), 1)
                    elif i % 3 == 1:
                        # Ursinho simples.
                        pygame.draw.circle(tela, borda, (r.centerx, r.centery+2), 10, 2)
                        pygame.draw.circle(tela, borda, (r.centerx-8, r.centery-7), 4, 1)
                        pygame.draw.circle(tela, borda, (r.centerx+8, r.centery-7), 4, 1)
                    else:
                        # Carrinho pequeno.
                        pygame.draw.rect(tela, borda, (r.x+10, r.y+20, 24, 9), 2, border_radius=3)
                        pygame.draw.circle(tela, borda, (r.x+15, r.y+31), 3, 1)
                        pygame.draw.circle(tela, borda, (r.x+29, r.y+31), 3, 1)
                else:
                    borda = (80, 185, 235) if suporte else (95, 95, 110)
                    simbolo = "S" if suporte else "+"
                    pygame.draw.rect(tela, (46, 46, 56), r, border_radius=8)
                    pygame.draw.rect(tela, borda, r, 2, border_radius=8)
                    if suporte:
                        img = self.fonte_slot.render(simbolo, True, borda)
                        tela.blit(img, img.get_rect(center=r.center))
                    else:
                        pygame.draw.line(tela, borda, (r.centerx-9, r.centery), (r.centerx+9, r.centery), 2)
                        pygame.draw.line(tela, borda, (r.centerx, r.centery-9), (r.centerx, r.centery+9), 2)

    def _criar_cache_base(self, tamanho):
        cache = pygame.Surface(tamanho).convert()
        ambiente_id = getattr(self, "ambiente_id", "quarto_infantil")
        hospital = ambiente_id == "hospital_abandonado"

        # Fundo contínuo do jogo. Ele cobre a tela inteira para não sobrar faixa preta.
        cache.fill((17, 17, 24))
        tela_rect = pygame.Rect(0, 0, LARGURA, ALTURA)
        if hospital:
            # Hospital: piso e corredor brancos, com azulejo claro.
            # Mantém desenho em cache para não pesar no Android.
            self.desenhar_grade(cache, tela_rect, 32, (16, 24, 25), (18, 28, 29))
            pygame.draw.circle(cache, (28, 48, 48), (LARGURA//2, ALTURA//2+70), 420, 2)

            pygame.draw.rect(cache, (218, 224, 220), self.corredor, border_radius=4)
            self.desenhar_grade(cache, self.corredor.inflate(-8, -8), 28, (238, 242, 238), (220, 228, 224))
            pygame.draw.rect(cache, (120, 150, 145), self.corredor, 4, border_radius=4)

            pygame.draw.rect(cache, (218, 224, 220), self.rect, border_radius=4)
            self.desenhar_grade(cache, self.rect.inflate(-9, -9), 31, (240, 243, 240), (222, 230, 226))
            pygame.draw.rect(cache, (72, 95, 92), self.rect.move(4, 6), 7, border_radius=4)
            pygame.draw.rect(cache, (148, 170, 165), self.rect, 7, border_radius=4)

            pygame.draw.rect(cache, (240, 243, 240), (self.porta.x - 8, self.rect.y - 9, self.porta.w + 16, 18))

            # v1.11.6: detalhes estáticos do Hospital no cache.
            # Desenhados uma vez só, para dar vida ao mapa sem causar lag.
            # Placa EXIT no corredor
            placa = pygame.Rect(self.corredor.right - 62, self.corredor.y + 2, 54, 18)
            pygame.draw.rect(cache, (18, 55, 48), placa, border_radius=3)
            pygame.draw.rect(cache, (88, 170, 145), placa, 1, border_radius=3)
            fonte_exit = pygame.font.SysFont("arial", 13, bold=True)
            txt_exit = fonte_exit.render("EXIT", True, (120, 220, 185))
            cache.blit(txt_exit, txt_exit.get_rect(center=placa.center))

            # Janela com chuva no corredor
            janela = pygame.Rect(self.corredor.x + 28, self.corredor.y + 22, 58, 34)
            pygame.draw.rect(cache, (35, 54, 62), janela, border_radius=4)
            pygame.draw.rect(cache, (110, 145, 150), janela, 2, border_radius=4)
            pygame.draw.line(cache, (95, 125, 130), janela.midtop, janela.midbottom, 1)
            pygame.draw.line(cache, (95, 125, 130), janela.midleft, janela.midright, 1)
            for dx in (10, 22, 36, 49):
                pygame.draw.line(cache, (150, 180, 185), (janela.x+dx, janela.y+5), (janela.x+dx-5, janela.y+18), 1)

            # v1.11.7: rodapés e desgaste leve para tirar o aspecto de hospital novo.
            rodape_cor = (115, 135, 132)
            pygame.draw.line(cache, rodape_cor, (self.rect.x + 10, self.rect.y + 8), (self.rect.right - 10, self.rect.y + 8), 3)
            pygame.draw.line(cache, rodape_cor, (self.rect.x + 9, self.rect.y + 8), (self.rect.x + 9, self.rect.bottom - 12), 3)
            pygame.draw.line(cache, rodape_cor, (self.rect.right - 10, self.rect.y + 8), (self.rect.right - 10, self.rect.bottom - 12), 3)
            pygame.draw.line(cache, (128, 148, 144), (self.corredor.x + 8, self.corredor.bottom - 10), (self.corredor.right - 8, self.corredor.bottom - 10), 3)

            # Maca encostada na parede esquerda, sem ficar no meio da sala.
            maca = pygame.Rect(self.rect.x + 18, self.rect.y + 250, 76, 22)
            pygame.draw.rect(cache, (42, 78, 72), maca, border_radius=5)
            pygame.draw.rect(cache, (92, 150, 135), maca, 2, border_radius=5)
            pygame.draw.line(cache, (72, 105, 100), (maca.x + 8, maca.y + 5), (maca.right - 8, maca.bottom - 5), 1)
            pygame.draw.circle(cache, (70, 75, 82), (maca.x + 12, maca.bottom + 5), 4)
            pygame.draw.circle(cache, (70, 75, 82), (maca.right - 12, maca.bottom + 5), 4)

            # Armário de remédios preso na parede direita.
            arm = pygame.Rect(self.rect.right - 76, self.rect.y + 220, 48, 58)
            pygame.draw.rect(cache, (35, 63, 60), arm, border_radius=5)
            pygame.draw.rect(cache, (83, 145, 130), arm, 2, border_radius=5)
            pygame.draw.line(cache, (150, 215, 190), (arm.centerx, arm.y + 14), (arm.centerx, arm.y + 36), 3)
            pygame.draw.line(cache, (150, 215, 190), (arm.centerx - 10, arm.y + 25), (arm.centerx + 10, arm.y + 25), 3)

            # Monitor hospitalar encostado na parede esquerda.
            monitor = pygame.Rect(self.rect.x + 22, self.rect.y + 330, 52, 30)
            pygame.draw.rect(cache, (20, 36, 36), monitor, border_radius=4)
            pygame.draw.rect(cache, (70, 130, 120), monitor, 1, border_radius=4)
            pygame.draw.line(cache, (90, 180, 145), (monitor.x+7, monitor.centery), (monitor.x+16, monitor.centery), 1)
            pygame.draw.line(cache, (90, 180, 145), (monitor.x+16, monitor.centery), (monitor.x+22, monitor.y+9), 1)
            pygame.draw.line(cache, (90, 180, 145), (monitor.x+22, monitor.y+9), (monitor.x+30, monitor.y+22), 1)
            pygame.draw.line(cache, (90, 180, 145), (monitor.x+30, monitor.y+22), (monitor.right-7, monitor.centery), 1)

            # v1.11.9: polimento leve do hospital. Tudo fica no cache, então não pesa por frame.
            # Mesa de recepção com papéis, monitor e luminária.
            recep = pygame.Rect(self.porta.x + 6, self.porta.y + 8, self.porta.w - 12, 30)
            pygame.draw.rect(cache, (96, 55, 32), recep.move(0, 4), border_radius=3)
            pygame.draw.rect(cache, (125, 72, 40), recep, border_radius=3)
            pygame.draw.rect(cache, (80, 45, 27), (recep.x, recep.bottom-7, recep.w, 7), border_radius=2)
            pygame.draw.rect(cache, (208, 214, 205), (recep.x+12, recep.y+6, 22, 12), border_radius=2)
            pygame.draw.rect(cache, (35, 44, 48), (recep.right-38, recep.y+5, 22, 13), border_radius=2)
            pygame.draw.line(cache, (70, 190, 150), (recep.right-34, recep.y+12), (recep.right-20, recep.y+12), 1)
            pygame.draw.line(cache, (180, 135, 70), (recep.centerx, recep.y+14), (recep.centerx-4, recep.y+23), 2)
            pygame.draw.circle(cache, (190, 150, 70), (recep.centerx, recep.y+13), 3)

            # Carrinho/item antigo removido para não aparecer atrás do armário.

            # Placas/tubos de parede quebrados para dar cara de abandono.
            painel = pygame.Rect(self.rect.x + 18, self.rect.y + 102, 72, 18)
            pygame.draw.rect(cache, (38, 70, 66), painel, border_radius=3)
            pygame.draw.line(cache, (106, 150, 142), (painel.x+8, painel.centery), (painel.right-8, painel.centery), 1)
            pygame.draw.line(cache, (106, 150, 142), (painel.x+18, painel.y+4), (painel.x+18, painel.bottom-4), 1)
            pygame.draw.rect(cache, (40, 58, 60), (self.rect.right-82, self.rect.y+150, 48, 12), border_radius=3)
            pygame.draw.line(cache, (86, 125, 120), (self.rect.right-78, self.rect.y+156), (self.rect.right-42, self.rect.y+156), 1)

            # Pequenos papéis no chão em grupos, menos espalhados e mais naturais.
            papel_cor = (218, 222, 214)
            for px, py, ang in [
                (self.rect.x+88, self.rect.y+160, 0), (self.rect.x+99, self.rect.y+168, 1),
                (self.rect.right-136, self.rect.y+312, 0), (self.rect.right-124, self.rect.y+320, 1),
                (self.rect.x+184, self.rect.y+68, 1),
            ]:
                rr = pygame.Rect(px, py, 10, 6)
                pygame.draw.rect(cache, papel_cor, rr, border_radius=1)
                pygame.draw.line(cache, (170, 178, 170), (rr.x+2, rr.y+3), (rr.right-2, rr.y+3), 1)

            # Rachaduras, sujeira e manchas discretas espalhadas no piso.
            desgaste = (176, 184, 180)
            for x, y, pts in [
                (self.rect.x+85, self.rect.y+110, [(0,0),(20,15),(15,28),(34,42)]),
                (self.rect.right-150, self.rect.y+120, [(0,0),(18,22),(12,34)]),
                (self.rect.x+210, self.rect.y+345, [(0,0),(-15,18),(-5,36),(-22,55)]),
            ]:
                last = (x, y)
                for dx, dy in pts[1:]:
                    nxt = (x+dx, y+dy)
                    pygame.draw.line(cache, desgaste, last, nxt, 1)
                    last = nxt
            for cx, cy, raio in [
                (self.rect.x + 125, self.rect.y + 205, 4),
                (self.rect.right - 150, self.rect.y + 250, 3),
                (self.rect.x + 92, self.rect.y + 370, 3),
                (self.rect.right - 82, self.rect.y + 392, 4),
            ]:
                pygame.draw.circle(cache, (92, 55, 60), (cx, cy), raio)
                pygame.draw.circle(cache, (135, 118, 112), (cx + 7, cy + 3), max(2, raio-1))


            # v1.22.0: preenchimento do hospital com objetos leves em Pygame.
            self.desenhar_itens_hospital_pygame(cache)

            # Leve névoa no corredor, feita com poucas linhas estáticas.
            for yy in (self.corredor.y + 70, self.corredor.y + 104, self.corredor.y + 136):
                pygame.draw.line(cache, (230, 238, 235), (self.corredor.x + 36, yy), (self.corredor.right - 36, yy), 1)
        else:
            self.desenhar_grade(cache, tela_rect, 32, (18, 18, 25), (22, 22, 30))
            pygame.draw.circle(cache, (30, 30, 40), (LARGURA//2, ALTURA//2+70), 420, 2)

            # corredor superior
            pygame.draw.rect(cache, (21, 19, 25), self.corredor, border_radius=4)
            self.desenhar_grade(cache, self.corredor.inflate(-8, -8), 28, (33, 30, 37), (42, 38, 46))
            pygame.draw.rect(cache, (80, 76, 92), self.corredor, 4, border_radius=4)

            # quarto inferior
            pygame.draw.rect(cache, CINZA_ESCURO, self.rect, border_radius=4)
            self.desenhar_grade(cache, self.rect.inflate(-9, -9), 31, (27, 27, 35), (35, 35, 45))
            pygame.draw.rect(cache, (14, 14, 20), self.rect.move(4, 6), 7, border_radius=4)
            pygame.draw.rect(cache, CINZA_CLARO, self.rect, 7, border_radius=4)

            # abertura da porta entre corredor e quarto
            pygame.draw.rect(cache, (27, 27, 35), (self.porta.x - 8, self.rect.y - 9, self.porta.w + 16, 18))

            # v1.12.0: Polimento da Ala Infantil.
            # Detalhes estáticos no cache: aparecem só neste mapa e não pesam por frame.
            # Tapete de EVA desgastado, encostado no canto inferior esquerdo.
            tapete = pygame.Rect(self.rect.x + 18, self.rect.y + 235, 104, 58)
            cores_eva = [(70, 86, 135), (110, 65, 120), (120, 92, 48), (55, 110, 95)]
            p = 0
            for yy in range(tapete.y, tapete.bottom, 29):
                for xx in range(tapete.x, tapete.right, 26):
                    pygame.draw.rect(cache, cores_eva[p % len(cores_eva)], (xx, yy, 25, 28), border_radius=3)
                    pygame.draw.rect(cache, (31, 28, 38), (xx, yy, 25, 28), 1, border_radius=3)
                    p += 1
            pygame.draw.line(cache, (44, 40, 52), (tapete.x + 8, tapete.y + 12), (tapete.right - 12, tapete.bottom - 8), 2)

            # Berço antigo no lado direito, fora do caminho principal.
            berco = pygame.Rect(self.rect.right - 115, self.rect.y + 230, 86, 42)
            pygame.draw.rect(cache, (72, 55, 52), berco, border_radius=5)
            pygame.draw.rect(cache, (132, 104, 96), berco, 2, border_radius=5)
            for bx in range(berco.x + 10, berco.right - 8, 12):
                pygame.draw.line(cache, (138, 112, 105), (bx, berco.y + 6), (bx, berco.bottom - 7), 2)
            pygame.draw.rect(cache, (48, 42, 56), (berco.x + 8, berco.bottom - 6, berco.w - 16, 5), border_radius=2)

            # Prateleira com brinquedos na parede.
            prateleira = pygame.Rect(self.rect.x + 28, self.rect.y + 34, 95, 11)
            pygame.draw.rect(cache, (80, 55, 52), prateleira, border_radius=3)
            pygame.draw.circle(cache, (120, 88, 48), (prateleira.x + 18, prateleira.y - 7), 7)
            pygame.draw.circle(cache, (95, 120, 165), (prateleira.x + 45, prateleira.y - 7), 6)
            pygame.draw.rect(cache, (135, 80, 120), (prateleira.x + 66, prateleira.y - 16, 14, 14), border_radius=3)

            # Desenhos infantis tortos na parede do corredor.
            papel1 = pygame.Rect(self.corredor.x + 120, self.corredor.y + 18, 34, 25)
            papel2 = pygame.Rect(self.corredor.right - 170, self.corredor.y + 27, 38, 27)
            for papel in (papel1, papel2):
                pygame.draw.rect(cache, (215, 205, 180), papel, border_radius=2)
                pygame.draw.rect(cache, (70, 62, 70), papel, 1, border_radius=2)
            pygame.draw.circle(cache, (115, 80, 130), (papel1.x + 13, papel1.y + 12), 6, 1)
            pygame.draw.line(cache, (150, 70, 70), (papel1.x + 22, papel1.y + 18), (papel1.x + 29, papel1.y + 8), 1)
            pygame.draw.line(cache, (75, 120, 95), (papel2.x + 8, papel2.y + 19), (papel2.x + 18, papel2.y + 8), 1)
            pygame.draw.line(cache, (75, 120, 95), (papel2.x + 18, papel2.y + 8), (papel2.x + 30, papel2.y + 20), 1)

            # Brinquedos abandonados, poucos e bem espalhados.
            # Carrinho quebrado.
            pygame.draw.rect(cache, (125, 48, 58), (self.rect.x + 145, self.rect.y + 318, 32, 14), border_radius=4)
            pygame.draw.circle(cache, (20, 18, 24), (self.rect.x + 152, self.rect.y + 335), 4)
            pygame.draw.circle(cache, (20, 18, 24), (self.rect.x + 171, self.rect.y + 335), 4)
            # Ursinho caído.
            ux, uy = self.rect.right - 154, self.rect.y + 315
            pygame.draw.circle(cache, (118, 82, 50), (ux, uy), 12)
            pygame.draw.circle(cache, (118, 82, 50), (ux - 9, uy - 9), 5)
            pygame.draw.circle(cache, (118, 82, 50), (ux + 8, uy - 9), 5)
            pygame.draw.line(cache, (45, 28, 28), (ux - 6, uy + 5), (ux + 7, uy + 8), 2)
            # Cubos.
            for bx, by, c in [(self.rect.x+204, self.rect.y+252, (100,85,150)), (self.rect.right-210, self.rect.y+365, (120,95,45))]:
                pygame.draw.rect(cache, c, (bx, by, 20, 20), border_radius=3)
                pygame.draw.rect(cache, (35, 30, 40), (bx, by, 20, 20), 1, border_radius=3)
                pygame.draw.line(cache, (210, 190, 150), (bx+6, by+10), (bx+14, by+10), 1)

            # Luz noturna fraca na parede direita.
            luz = pygame.Rect(self.rect.right - 58, self.rect.y + 90, 22, 30)
            pygame.draw.rect(cache, (75, 62, 78), luz, border_radius=8)
            pygame.draw.circle(cache, (135, 125, 95), luz.center, 7)
            pygame.draw.circle(cache, (70, 65, 50), luz.center, 18, 1)

            # Manchas e rachaduras agrupadas, menos repetitivas.
            for x, y in [(self.rect.x+58, self.rect.y+155), (self.rect.right-96, self.rect.y+155), (self.rect.x+255, self.rect.y+410)]:
                pygame.draw.circle(cache, (45, 38, 48), (x, y), 9, 1)
                pygame.draw.circle(cache, (38, 33, 42), (x+12, y+7), 5, 1)
            for x, y in [(self.corredor.x+230, self.corredor.y+105), (self.rect.x+300, self.rect.y+70)]:
                pygame.draw.line(cache, (70, 65, 78), (x, y), (x+16, y+9), 2)
                pygame.draw.line(cache, (70, 65, 78), (x+9, y+5), (x+4, y+18), 1)

            # Névoa baixa bem leve para dar clima sem usar transparência por frame.
            for yy in (self.corredor.y + 74, self.corredor.y + 126, self.rect.y + 116):
                pygame.draw.line(cache, (45, 42, 54), (self.rect.x + 40, yy), (self.rect.right - 40, yy), 1)
        return cache



    def desenhar_itens_hospital_pygame(self, cache):
        """Objetos hospitalares decorativos feitos 100% com pygame.
        Tudo é desenhado no cache estático do cenário, então não adiciona custo por frame.
        """
        # Paleta compacta para manter pixel art leve.
        metal=(150,158,158); metal2=(92,104,108); esc=(36,43,46)
        verde=(50,130,112); verde2=(32,82,72); azul=(45,72,120)
        branco=(222,226,222); sombra=(18,22,24); vermelho=(165,45,38)

        # --- CORREDOR: objetos encostados nas paredes ---
        # Placa Ala Infantil
        placa=pygame.Rect(self.corredor.centerx-54, self.corredor.y+2,108,42)
        pygame.draw.rect(cache,(28,90,76),placa,border_radius=3)
        pygame.draw.rect(cache,(205,220,210),placa,2,border_radius=3)
        f=pygame.font.SysFont('arial',14,bold=True)
        for n,txt in enumerate(('ALA','INFANTIL')):
            img=f.render(txt,True,(232,238,228)); cache.blit(img,(placa.x+10,placa.y+6+n*14))
        pygame.draw.line(cache,(232,238,228),(placa.right-35,placa.centery),(placa.right-10,placa.centery),3)
        pygame.draw.polygon(cache,(232,238,228),[(placa.right-10,placa.centery),(placa.right-22,placa.centery-7),(placa.right-22,placa.centery+7)])

        # Raio-X na parede esquerda do corredor
        rx=pygame.Rect(self.corredor.x+105,self.corredor.y+2,48,48)
        pygame.draw.rect(cache,(12,22,24),rx,border_radius=3); pygame.draw.rect(cache,(95,125,128),rx,2,border_radius=3)
        pygame.draw.line(cache,(175,220,215),(rx.centerx,rx.y+8),(rx.centerx,rx.bottom-9),2)
        pygame.draw.arc(cache,(175,220,215),(rx.x+12,rx.y+12,24,18),3.3,6.1,2)
        pygame.draw.arc(cache,(175,220,215),(rx.x+12,rx.y+20,24,18),0.2,2.9,2)
        for off in (-8,-4,4,8):
            pygame.draw.line(cache,(175,220,215),(rx.centerx,rx.centery),(rx.centerx+off,rx.y+13),1)
            pygame.draw.line(cache,(175,220,215),(rx.centerx,rx.centery),(rx.centerx+off,rx.bottom-13),1)

        # Extintor no corredor direito
        ex=pygame.Rect(self.corredor.right-46,self.corredor.y+28,22,48)
        pygame.draw.rect(cache,(90,25,25),ex.move(2,2),border_radius=5)
        pygame.draw.rect(cache,vermelho,ex,border_radius=5); pygame.draw.rect(cache,(230,110,90),ex,2,border_radius=5)
        pygame.draw.rect(cache,branco,(ex.x+5,ex.y+17,12,14),border_radius=2)
        pygame.draw.line(cache,(80,30,25),(ex.centerx,ex.y-8),(ex.right+10,ex.y-14),3)
        pygame.draw.rect(cache,(45,45,45),(ex.x+6,ex.y-5,10,7),border_radius=2)

        # Cadeira de rodas quebrada no canto do corredor
        cx=self.corredor.x+36; cy=self.corredor.bottom-68
        pygame.draw.circle(cache,(25,28,32),(cx+38,cy+35),17,2); pygame.draw.circle(cache,(25,28,32),(cx+38,cy+35),9,1)
        pygame.draw.circle(cache,(25,28,32),(cx+6,cy+40),1)
        pygame.draw.rect(cache,azul,(cx+10,cy+12,36,18),border_radius=4)
        pygame.draw.rect(cache,(32,54,86),(cx+14,cy-8,30,24),border_radius=4)
        pygame.draw.line(cache,metal,(cx+12,cy+30),(cx+5,cy+45),2); pygame.draw.line(cache,metal,(cx+45,cy+30),(cx+55,cy+45),2)
        pygame.draw.line(cache,metal2,(cx+8,cy+13),(cx,cy+13),3); pygame.draw.line(cache,metal2,(cx+47,cy+12),(cx+60,cy+8),3)

        # --- QUARTO: objetos em volta, sem cobrir cama/slots principais ---
        # Suporte de soro perto da cama
        sx=self.cama.x-42; sy=self.cama.y+8
        pygame.draw.line(cache,metal,(sx,sy),(sx,sy+98),3)
        pygame.draw.line(cache,metal,(sx-13,sy+8),(sx+13,sy+8),3)
        pygame.draw.line(cache,metal,(sx-18,sy+98),(sx+18,sy+98),3)
        pygame.draw.circle(cache,(35,38,42),(sx-16,sy+102),4); pygame.draw.circle(cache,(35,38,42),(sx+16,sy+102),4)
        bolsa=pygame.Rect(sx+10,sy+18,16,29)
        pygame.draw.rect(cache,(160,218,224),bolsa,border_radius=4); pygame.draw.rect(cache,(80,145,150),bolsa,1,border_radius=4)
        pygame.draw.line(cache,(110,190,190),(bolsa.centerx,bolsa.bottom),(sx+2,sy+74),1)

        # Mesa de cabeceira com remédio
        mesa=pygame.Rect(self.cama.x-112,self.cama.y+32,48,56)
        pygame.draw.rect(cache,sombra,mesa.move(3,4),border_radius=3)
        pygame.draw.rect(cache,(190,190,184),mesa,border_radius=3); pygame.draw.rect(cache,(95,100,102),mesa,2,border_radius=3)
        pygame.draw.rect(cache,(150,154,154),(mesa.x+10,mesa.y+23,28,14),border_radius=2); pygame.draw.rect(cache,(45,52,55),(mesa.x+20,mesa.y+29,8,3))
        pygame.draw.rect(cache,(80,150,135),(mesa.centerx-5,mesa.y-10,10,15),border_radius=2); pygame.draw.rect(cache,(190,225,210),(mesa.centerx-2,mesa.y-7,4,7))

        # Lixeira hospitalar vermelha
        lix=pygame.Rect(self.rect.right-72,self.rect.bottom-112,38,52)
        pygame.draw.rect(cache,(85,25,22),lix.move(2,3),border_radius=5)
        pygame.draw.rect(cache,(170,50,42),lix,border_radius=5); pygame.draw.rect(cache,(95,30,28),lix,2,border_radius=5)
        pygame.draw.rect(cache,(145,42,36),(lix.x-3,lix.y-8,lix.w+6,10),border_radius=4)
        pygame.draw.line(cache,branco,(lix.centerx-9,lix.centery),(lix.centerx+9,lix.centery),2)
        pygame.draw.circle(cache,branco,(lix.centerx,lix.centery),9,1)

        # Bebedouro no canto inferior esquerdo
        bx=self.rect.x+38; by=self.rect.bottom-120
        pygame.draw.rect(cache,(165,172,172),(bx,by+30,32,58),border_radius=4); pygame.draw.rect(cache,(72,88,92),(bx,by+30,32,58),2,border_radius=4)
        pygame.draw.ellipse(cache,(75,145,185),(bx+1,by+2,30,15)); pygame.draw.rect(cache,(55,125,170),(bx+1,by+9,30,31),border_radius=8); pygame.draw.ellipse(cache,(75,145,185),(bx+1,by+28,30,15))
        pygame.draw.rect(cache,(38,50,55),(bx+8,by+49,16,18),border_radius=2); pygame.draw.circle(cache,(200,55,45),(bx+13,by+58),3); pygame.draw.circle(cache,(45,115,170),(bx+21,by+58),3)

        # Planta para quebrar o cenário frio
        px=self.rect.right-128; py=self.rect.bottom-95
        pygame.draw.rect(cache,(178,170,146),(px,py+48,32,28),border_radius=4); pygame.draw.rect(cache,(92,84,70),(px,py+48,32,28),2,border_radius=4)
        for dx,dy in [(-16,26),(-9,14),(0,4),(9,15),(17,27),(-20,38),(18,39)]:
            pygame.draw.line(cache,(55,120,55),(px+16,py+50),(px+16+dx,py+dy),3)
            pygame.draw.ellipse(cache,(70,150,65),(px+12+dx,py+dy-5,14,10))
        # Computador removido

        # Armário/arquivo pequeno na parede direita superior
        arq=pygame.Rect(self.rect.right-72,self.rect.y+24,42,74)
        pygame.draw.rect(cache,(65,70,72),arq,border_radius=4); pygame.draw.rect(cache,(155,160,158),arq,2,border_radius=4)
        for yy in (arq.y+9, arq.y+31, arq.y+53):
            pygame.draw.rect(cache,(85,90,92),(arq.x+7,yy,28,16),border_radius=2)
            pygame.draw.rect(cache,(170,174,170),(arq.x+17,yy+5,8,3),border_radius=1)

    def desenhar_corpo_cama_meio(self, tela, cama, fonte, nivel_cama=1, alerta_porta=False):
        """Pessoa dormindo na cama central, simples e leve.
        Visual inspirado em cama pixel art: travesseiro, cabeça e cobertor azul.
        Não altera colisão, moedas nem mecânica; é apenas desenho por formas.
        """
        # Travesseiro atrás da cabeça.
        trav = pygame.Rect(cama.centerx - 47, cama.y + 21, 94, 28)
        pygame.draw.rect(tela, (225, 228, 232), trav, border_radius=8)
        pygame.draw.rect(tela, (174, 182, 194), trav, 2, border_radius=8)
        pygame.draw.line(tela, (200, 205, 214), (trav.x + 8, trav.centery), (trav.x + 20, trav.centery + 8), 2)
        pygame.draw.line(tela, (200, 205, 214), (trav.right - 8, trav.centery), (trav.right - 20, trav.centery + 8), 2)

        # Cabeça simples aparecendo acima do cobertor.
        pele = (235, 160, 108)
        cabelo = (80, 43, 22)
        rosto = pygame.Rect(cama.centerx - 19, cama.y + 29, 38, 27)
        pygame.draw.rect(tela, pele, rosto, border_radius=9)
        pygame.draw.rect(tela, cabelo, (rosto.x - 2, rosto.y - 9, rosto.w + 4, 18), border_radius=8)
        pygame.draw.rect(tela, cabelo, (rosto.x - 3, rosto.y + 3, 8, 13), border_radius=4)
        pygame.draw.rect(tela, cabelo, (rosto.right - 5, rosto.y + 2, 7, 13), border_radius=4)
        olho = (25, 22, 26)
        if alerta_porta:
            # Monstro batendo na porta: paciente acorda/abre os olhos.
            pygame.draw.rect(tela, (245, 245, 235), (rosto.x + 8, rosto.y + 13, 8, 6), border_radius=2)
            pygame.draw.rect(tela, (245, 245, 235), (rosto.right - 16, rosto.y + 13, 8, 6), border_radius=2)
            pygame.draw.rect(tela, olho, (rosto.x + 11, rosto.y + 14, 3, 4), border_radius=1)
            pygame.draw.rect(tela, olho, (rosto.right - 13, rosto.y + 14, 3, 4), border_radius=1)
            pygame.draw.line(tela, olho, (rosto.x + 12, rosto.y + 22), (rosto.right - 12, rosto.y + 22), 2)
        else:
            # Dormindo: olhos fechados em linhas simples.
            pygame.draw.line(tela, olho, (rosto.x + 8, rosto.y + 16), (rosto.x + 16, rosto.y + 16), 2)
            pygame.draw.line(tela, olho, (rosto.right - 16, rosto.y + 16), (rosto.right - 8, rosto.y + 16), 2)

        # Cobertor evolutivo por cor, bem leve: só troca tuplas RGB.
        #  1-4 normal, 5-9 verde, 10-14 vermelho, 15/MAX dourado.
        if nivel_cama >= 15:
            cob = (218, 178, 48)
            cob_esc = (142, 105, 24)
            cob_luz = (255, 226, 94)
        elif nivel_cama >= 10:
            cob = (194, 54, 60)
            cob_esc = (126, 30, 38)
            cob_luz = (234, 92, 98)
        elif nivel_cama >= 5:
            cob = (62, 172, 92)
            cob_esc = (32, 104, 56)
            cob_luz = (104, 216, 126)
        else:
            cob = (55, 95, 190)
            cob_esc = (36, 66, 145)
            cob_luz = (78, 128, 220)
        cobertor = pygame.Rect(cama.x + 14, cama.y + 50, cama.w - 28, cama.h - 18)
        pygame.draw.rect(tela, cob_esc, cobertor.move(0, 3), border_radius=8)
        pygame.draw.rect(tela, cob, cobertor, border_radius=8)
        pygame.draw.rect(tela, cob_luz, (cobertor.x + 8, cobertor.y + 6, cobertor.w - 16, 9), border_radius=4)
        pygame.draw.line(tela, cob_esc, (cobertor.x + 14, cobertor.y + 31), (cobertor.right - 14, cobertor.y + 31), 2)
        pygame.draw.line(tela, cob_esc, (cobertor.x + 16, cobertor.y + 16), (cobertor.x + 7, cobertor.y + 28), 1)
        pygame.draw.line(tela, cob_esc, (cobertor.right - 16, cobertor.y + 16), (cobertor.right - 7, cobertor.y + 28), 1)

        #  15/MAX: acabamento simples de cama melhorada.
        if nivel_cama >= 15:
            pygame.draw.line(tela, (230, 220, 170), (cama.x + 22, cama.y + 14), (cama.right - 22, cama.y + 14), 2)
            pygame.draw.line(tela, (230, 220, 170), (cama.x + 22, cama.bottom - 16), (cama.right - 22, cama.bottom - 16), 2)

        # Zzz simples. Sem nuvem e só aparece enquanto não há monstro batendo na porta.
        if not alerta_porta:
            t = pygame.time.get_ticks()
            bob = (t // 550) % 3
            cx = cama.centerx + 57
            cy = cama.y + 15 - int(bob)
            zcor = (176, 200, 226)
            z1x, z1y = cx, cy
            pygame.draw.line(tela, zcor, (z1x, z1y), (z1x + 9, z1y), 2)
            pygame.draw.line(tela, zcor, (z1x + 9, z1y), (z1x, z1y + 8), 2)
            pygame.draw.line(tela, zcor, (z1x, z1y + 8), (z1x + 9, z1y + 8), 2)
            z2x, z2y = cx + 13, cy - 10
            pygame.draw.line(tela, zcor, (z2x, z2y), (z2x + 6, z2y), 1)
            pygame.draw.line(tela, zcor, (z2x + 6, z2y), (z2x, z2y + 6), 1)
            pygame.draw.line(tela, zcor, (z2x, z2y + 6), (z2x + 6, z2y + 6), 1)


    def desenhar_cama_hospitalar(self, tela, cama, fonte, nivel_cama=1, alerta_porta=False):
        """Cama hospitalar desenhada direto no Pygame.
        Não usa imagem externa, então evita lag no Android/Pydroid.
        Mantém o mesmo Rect da cama para colisão, upgrades e moedas.
        """
        # Paleta hospitalar simples e barata.
        metal_esc = (26, 31, 36)
        metal = (145, 158, 164)
        metal_luz = (222, 230, 232)
        verde = (42, 128, 91)
        verde_esc = (25, 85, 65)
        verde_luz = (68, 154, 112)
        branco = (232, 236, 238)
        sombra = (8, 12, 18)

        # Sombra da cama.
        pygame.draw.rect(tela, sombra, cama.move(5, 7), border_radius=7)

        # Base metálica externa.
        pygame.draw.rect(tela, metal_esc, cama, border_radius=7)
        pygame.draw.rect(tela, metal, cama.inflate(-10, -10), border_radius=5)
        pygame.draw.rect(tela, metal_luz, (cama.x + 16, cama.y + 8, cama.w - 32, 8), border_radius=3)
        pygame.draw.rect(tela, metal_luz, (cama.x + 16, cama.bottom - 18, cama.w - 32, 7), border_radius=3)

        # Postes laterais altos.
        for px in (cama.x + 2, cama.right - 14):
            pygame.draw.rect(tela, metal_esc, (px, cama.y - 6, 12, cama.h + 12), border_radius=4)
            pygame.draw.rect(tela, metal_luz, (px + 3, cama.y, 6, cama.h - 2), border_radius=3)
            pygame.draw.line(tela, (92, 104, 112), (px + 8, cama.y + 14), (px + 8, cama.bottom - 14), 2)

        # Barras de proteção da cama hospitalar.
        pygame.draw.rect(tela, metal_esc, (cama.x + 16, cama.y + 19, cama.w - 32, 9), border_radius=3)
        pygame.draw.rect(tela, metal_luz, (cama.x + 18, cama.y + 21, cama.w - 36, 4), border_radius=2)
        pygame.draw.rect(tela, metal_esc, (cama.x + 16, cama.bottom - 31, cama.w - 32, 8), border_radius=3)
        pygame.draw.rect(tela, metal_luz, (cama.x + 18, cama.bottom - 29, cama.w - 36, 4), border_radius=2)

        # Colchão branco.
        colchao = pygame.Rect(cama.x + 20, cama.y + 28, cama.w - 40, cama.h - 54)
        pygame.draw.rect(tela, branco, colchao, border_radius=7)
        pygame.draw.rect(tela, (178, 190, 196), colchao, 2, border_radius=7)

        # Travesseiro grande.
        trav = pygame.Rect(cama.centerx - 47, cama.y + 30, 94, 30)
        pygame.draw.rect(tela, (246, 248, 248), trav, border_radius=9)
        pygame.draw.rect(tela, (195, 204, 209), trav, 2, border_radius=9)
        pygame.draw.line(tela, (212, 218, 222), (trav.x + 10, trav.y + 7), (trav.x + 23, trav.y + 20), 2)
        pygame.draw.line(tela, (212, 218, 222), (trav.right - 10, trav.y + 7), (trav.right - 23, trav.y + 20), 2)

        # Cabeça do paciente.
        pele = (235, 160, 108)
        cabelo = (76, 40, 18)
        rosto = pygame.Rect(cama.centerx - 19, cama.y + 41, 38, 28)
        pygame.draw.rect(tela, pele, rosto, border_radius=9)
        pygame.draw.rect(tela, cabelo, (rosto.x - 2, rosto.y - 10, rosto.w + 4, 18), border_radius=8)
        pygame.draw.rect(tela, cabelo, (rosto.x - 3, rosto.y + 1, 8, 14), border_radius=4)
        pygame.draw.rect(tela, cabelo, (rosto.right - 5, rosto.y + 1, 7, 14), border_radius=4)
        olho = (24, 21, 24)
        if alerta_porta:
            pygame.draw.rect(tela, (248, 248, 238), (rosto.x + 8, rosto.y + 14, 8, 6), border_radius=2)
            pygame.draw.rect(tela, (248, 248, 238), (rosto.right - 16, rosto.y + 14, 8, 6), border_radius=2)
            pygame.draw.rect(tela, olho, (rosto.x + 11, rosto.y + 15, 3, 4), border_radius=1)
            pygame.draw.rect(tela, olho, (rosto.right - 13, rosto.y + 15, 3, 4), border_radius=1)
        else:
            pygame.draw.line(tela, olho, (rosto.x + 8, rosto.y + 17), (rosto.x + 16, rosto.y + 17), 2)
            pygame.draw.line(tela, olho, (rosto.right - 16, rosto.y + 17), (rosto.right - 8, rosto.y + 17), 2)

        # Lençol verde até o pescoço.
        lencol = pygame.Rect(cama.x + 18, cama.y + 62, cama.w - 36, cama.h - 49)
        pygame.draw.rect(tela, verde_esc, lencol.move(0, 3), border_radius=8)
        pygame.draw.rect(tela, verde, lencol, border_radius=8)
        pygame.draw.rect(tela, verde_luz, (lencol.x + 9, lencol.y + 6, lencol.w - 18, 9), border_radius=4)
        pygame.draw.line(tela, verde_esc, (lencol.x + 14, lencol.y + 36), (lencol.right - 14, lencol.y + 36), 2)
        pygame.draw.line(tela, verde_esc, (lencol.x + 13, lencol.y + 17), (lencol.x + 4, lencol.y + 32), 1)
        pygame.draw.line(tela, verde_esc, (lencol.right - 13, lencol.y + 17), (lencol.right - 4, lencol.y + 32), 1)

        # Painelzinho/rodinhas na base.
        pygame.draw.rect(tela, (32, 70, 62), (cama.centerx - 22, cama.bottom - 49, 44, 17), border_radius=3)
        pygame.draw.rect(tela, (20, 45, 42), (cama.centerx - 15, cama.bottom - 42, 22, 5), border_radius=2)
        pygame.draw.rect(tela, (198, 55, 45), (cama.centerx + 11, cama.bottom - 44, 7, 7), border_radius=2)
        for px in (cama.x + 17, cama.right - 24):
            pygame.draw.rect(tela, metal_esc, (px, cama.bottom - 4, 14, 8), border_radius=3)
            pygame.draw.circle(tela, (20, 24, 30), (px + 7, cama.bottom + 5), 5)
            pygame.draw.circle(tela, (88, 96, 102), (px + 7, cama.bottom + 5), 3)

        # Zzz do paciente dormindo. Some quando algum monstro está batendo na porta.
        if not alerta_porta:
            t = pygame.time.get_ticks()
            bob = (t // 520) % 3
            zcor = (176, 200, 226)
            cx = cama.centerx + 42
            cy = cama.y + 31 - bob
            # Z maior
            pygame.draw.line(tela, zcor, (cx, cy), (cx + 10, cy), 2)
            pygame.draw.line(tela, zcor, (cx + 10, cy), (cx, cy + 9), 2)
            pygame.draw.line(tela, zcor, (cx, cy + 9), (cx + 10, cy + 9), 2)
            # Z menor acima, para parecer sono sem pesar no jogo.
            z2x, z2y = cx + 14, cy - 10
            pygame.draw.line(tela, zcor, (z2x, z2y), (z2x + 7, z2y), 1)
            pygame.draw.line(tela, zcor, (z2x + 7, z2y), (z2x, z2y + 6), 1)
            pygame.draw.line(tela, zcor, (z2x, z2y + 6), (z2x + 7, z2y + 6), 1)

        # Monitor cardíaco separado ao lado direito da cama.
        mx = min(self.rect.right - 70, cama.right + 24)
        my = cama.y + 5
        tela_clip = tela.get_clip()
        mon = pygame.Rect(mx, my, 58, 37)
        pygame.draw.rect(tela, sombra, mon.move(3, 4), border_radius=5)
        pygame.draw.rect(tela, metal_esc, mon, border_radius=5)
        pygame.draw.rect(tela, metal_luz, mon.inflate(-7, -7), border_radius=4)
        tela_mon = mon.inflate(-15, -15)
        tela_mon.h = 20
        tela_mon.y = mon.y + 9
        pygame.draw.rect(tela, (11, 23, 29), tela_mon, border_radius=2)
        ecg = (67, 220, 125)
        pts = [
            (tela_mon.x + 3, tela_mon.centery), (tela_mon.x + 12, tela_mon.centery),
            (tela_mon.x + 17, tela_mon.y + 5), (tela_mon.x + 23, tela_mon.bottom - 4),
            (tela_mon.x + 30, tela_mon.y + 7), (tela_mon.x + 34, tela_mon.centery),
            (tela_mon.right - 3, tela_mon.centery)
        ]
        pygame.draw.lines(tela, ecg, False, pts, 2)
        pygame.draw.circle(tela, (48, 120, 82), (tela_mon.right - 6, tela_mon.bottom - 5), 2)
        pygame.draw.line(tela, metal_esc, (mon.centerx, mon.bottom), (mon.centerx, mon.bottom + 56), 4)
        pygame.draw.line(tela, metal_luz, (mon.centerx - 2, mon.bottom + 3), (mon.centerx - 2, mon.bottom + 52), 2)
        base = pygame.Rect(mon.centerx - 24, mon.bottom + 54, 48, 12)
        pygame.draw.rect(tela, metal_esc, base, border_radius=3)
        pygame.draw.rect(tela, metal, base.inflate(-6, -4), border_radius=2)
        pygame.draw.circle(tela, (20, 24, 30), (base.x + 8, base.bottom + 3), 4)
        pygame.draw.circle(tela, (20, 24, 30), (base.right - 8, base.bottom + 3), 4)

    def desenhar_base(self, tela):
        tamanho = tela.get_size()
        ambiente_id = getattr(self, "ambiente_id", "quarto_infantil")
        if self._cache_base is None or self._cache_tamanho != tamanho or self._cache_ambiente != ambiente_id:
            self._cache_tamanho = tamanho
            self._cache_ambiente = ambiente_id
            self._cache_base = self._criar_cache_base(tamanho)
        tela.blit(self._cache_base, (0, 0))

    def desenhar(self, tela, fonte, vida_porta, vida_porta_max, torres, pulso_cama=0, tremor_porta=0, nivel_cama=1, nivel_porta=1, alerta_porta=False, flash_reparo=0):
        self.desenhar_base(tela)
        # Sem texto fixo no quarto: menos poluição visual e menos renderização por frame.
        self.desenhar_slots(tela, torres)

        # v1.21.6: ambiente vivo e leve.
        # Cama respira 1px e reage quando a porta fica crítica, sem sprites ou Surface extra.
        vida_ratio = max(0.0, min(1.0, float(vida_porta) / max(1, float(vida_porta_max))))
        ticks = pygame.time.get_ticks()
        respira = int(math.sin(ticks * 0.0032) * 1) if not alerta_porta else 0

        # Cama central. No Hospital, desenha direto em Pygame uma cama hospitalar
        # com paciente e monitor, sem carregar PNG grande nos assets.
        cama = self.cama.move(0, respira)
        ambiente_id = getattr(self, "ambiente_id", "quarto_infantil")

        # Brilho vermelho discreto quando a porta está crítica.
        if vida_ratio <= 0.30:
            pulse = 1 + (ticks // 160) % 2
            pygame.draw.rect(tela, (95, 20, 28), cama.inflate(10 + pulse*2, 8 + pulse*2), 2, border_radius=8)

        if ambiente_id == "hospital_abandonado":
            self.desenhar_cama_hospitalar(tela, cama, fonte, nivel_cama, alerta_porta)
        else:
            madeira_escura = (34, 20, 12)
            madeira = (105, 58, 27)
            madeira_luz = (145, 80, 35)
            if nivel_cama >= 15:
                madeira_escura = (42, 30, 26)
                madeira = (125, 78, 42)
                madeira_luz = (178, 114, 58)
            elif nivel_cama >= 10:
                madeira = (118, 66, 31)
                madeira_luz = (160, 92, 44)

            # Sombra única e leve.
            pygame.draw.rect(tela, (8, 10, 18), cama.move(5, 7), border_radius=6)

            # Estrutura de madeira no formato da cama da referência, mas simples.
            pygame.draw.rect(tela, madeira_escura, cama, border_radius=6)
            pygame.draw.rect(tela, madeira, (cama.x + 8, cama.y + 8, cama.w - 16, cama.h - 16), border_radius=4)
            pygame.draw.rect(tela, madeira_luz, (cama.x + 14, cama.y + 12, cama.w - 28, 8), border_radius=3)
            pygame.draw.rect(tela, madeira_luz, (cama.x + 14, cama.bottom - 19, cama.w - 28, 8), border_radius=3)

            # Postes/cantos de madeira, poucos retângulos para melhor desempenho.
            for px, py in ((cama.x + 2, cama.y + 2), (cama.right - 14, cama.y + 2), (cama.x + 2, cama.bottom - 22), (cama.right - 14, cama.bottom - 22)):
                pygame.draw.rect(tela, madeira_escura, (px, py, 12, 20), border_radius=3)
                pygame.draw.rect(tela, madeira_luz, (px + 3, py + 3, 6, 10), border_radius=2)

            # Área interna do colchão, quase toda coberta pela pessoa/cobertor.
            pygame.draw.rect(tela, (210, 216, 224), (cama.x + 18, cama.y + 22, cama.w - 36, cama.h - 40), border_radius=6)

            # Pessoa + cobertor + Zzz na cama do meio.
            self.desenhar_corpo_cama_meio(tela, cama, fonte, nivel_cama, alerta_porta)

            # Pés escuros discretos.
            pygame.draw.rect(tela, (12, 14, 22), (cama.x + 10, cama.bottom - 3, 20, 7), border_radius=3)
            pygame.draw.rect(tela, (12, 14, 22), (cama.right - 30, cama.bottom - 3, 20, 7), border_radius=3)

        # Porta evolutiva v1.2.1: madeira -> reforçada -> ferro -> blindada.
        dy = int(tremor_porta) if tremor_porta else 0
        porta = self.porta.move(0, dy)
        if nivel_porta >= 10:
            cor_base=(72,78,88); cor_borda=(200,205,214); cor_linha=(38,42,50); cor_detalhe=(245,210,90)
        elif nivel_porta >= 7:
            cor_base=(86,92,104); cor_borda=(170,178,190); cor_linha=(45,48,56); cor_detalhe=(200,200,210)
        elif nivel_porta >= 4:
            cor_base=MARROM; cor_borda=(150,105,55); cor_linha=MARROM_ESCURO; cor_detalhe=AMARELO_ESCURO
        else:
            cor_base=MARROM; cor_borda=MARROM_ESCURO; cor_linha=MARROM_ESCURO; cor_detalhe=AMARELO_ESCURO

        pygame.draw.rect(tela, cor_borda, porta.inflate(10, 10), border_radius=4)
        pygame.draw.rect(tela, cor_base, porta, border_radius=4)
        if flash_reparo > 0:
            pygame.draw.rect(tela, (70, 220, 110), porta.inflate(14, 12), 2, border_radius=7)
            pygame.draw.line(tela, (110, 255, 150), (porta.x + 12, porta.y - 4), (porta.right - 12, porta.y - 4), 2)
        pygame.draw.line(tela, cor_linha, (porta.x + 8, porta.centery), (porta.right - 8, porta.centery), 2)
        if nivel_porta >= 4:
            pygame.draw.rect(tela, cor_borda, (porta.x+12, porta.y+5, porta.w-24, 5), border_radius=2)
            pygame.draw.rect(tela, cor_borda, (porta.x+12, porta.bottom-10, porta.w-24, 5), border_radius=2)
        if nivel_porta >= 7:
            pygame.draw.rect(tela, cor_linha, (porta.x+24, porta.y+3, 8, porta.h-6), border_radius=2)
            pygame.draw.rect(tela, cor_linha, (porta.right-32, porta.y+3, 8, porta.h-6), border_radius=2)
        if nivel_porta >= 10:
            for px in (porta.x+18, porta.centerx, porta.right-18):
                pygame.draw.circle(tela, cor_detalhe, (px, porta.centery), 3)
        pygame.draw.circle(tela, cor_detalhe, (porta.centerx, porta.bottom - 7), 3)

        # Rachaduras por dano: poucas linhas, só visual.
        if vida_ratio <= 0.75:
            pygame.draw.line(tela, (32, 24, 20), (porta.x + 28, porta.y + 8), (porta.x + 38, porta.y + 16), 2)
            pygame.draw.line(tela, (32, 24, 20), (porta.x + 38, porta.y + 16), (porta.x + 32, porta.y + 24), 1)
        if vida_ratio <= 0.50:
            pygame.draw.line(tela, (32, 24, 20), (porta.right - 34, porta.y + 7), (porta.right - 45, porta.y + 17), 2)
            pygame.draw.line(tela, (32, 24, 20), (porta.right - 45, porta.y + 17), (porta.right - 37, porta.y + 27), 1)
        if vida_ratio <= 0.25:
            pygame.draw.line(tela, (32, 24, 20), (porta.centerx, porta.y + 5), (porta.centerx - 7, porta.y + 17), 2)
            pygame.draw.line(tela, (32, 24, 20), (porta.centerx - 7, porta.y + 17), (porta.centerx + 3, porta.y + 29), 1)
            # Alerta simples acima da porta.
            if (ticks // 260) % 2 == 0:
                pygame.draw.polygon(tela, (210, 40, 45), [(porta.right + 12, porta.y - 4), (porta.right + 2, porta.y + 16), (porta.right + 22, porta.y + 16)])
                pygame.draw.line(tela, BRANCO, (porta.right + 12, porta.y + 2), (porta.right + 12, porta.y + 9), 2)
                pygame.draw.circle(tela, BRANCO, (porta.right + 12, porta.y + 13), 1)

        desenhar_barra(tela, porta.centerx - (porta.w + 12)//2, porta.y - 15, porta.w + 12, 10, vida_porta, vida_porta_max, VERDE)
