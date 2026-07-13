import pygame
import math
from config import *

TIPOS_TORRE = {
    # v1.11.0: Arsenal Avançado. Cada arma tem uma função e uma prioridade própria.
    # Mantive as armas antigas compatíveis, mas dei identidade maior ao combate.
    "metralhadora": {"nome":"Metralhadora", "icone":"M", "custo":55, "dano":6, "alcance":220, "cooldown":0.16, "cor":AMARELO, "tipo_proj":"normal", "prioridade":"perto_porta"},
    "sniper": {"nome":"Sniper", "icone":"S", "custo":950, "dano":55, "alcance":390, "cooldown":1.75, "cor":(210,235,255), "tipo_proj":"sniper", "prioridade":"maior_vida"},
    "veneno": {"nome":"Veneno", "icone":"V", "custo":145, "dano":10, "alcance":245, "cooldown":0.72, "cor":(80,220,90), "tipo_proj":"veneno", "prioridade":"sem_dot"},
    "canhao": {"nome":"Canhão", "icone":"C", "custo":135, "dano":44, "alcance":250, "cooldown":1.05, "cor":LARANJA, "tipo_proj":"explosivo", "prioridade":"grupo"},
    "gelo": {"nome":"Gelo", "icone":"G", "custo":95, "dano":9, "alcance":252, "cooldown":0.68, "cor":CIANO, "tipo_proj":"gelo", "prioridade":"rapido"},
    "eletrica": {"nome":"Tesla", "icone":"T", "custo":175, "dano":17, "alcance":258, "cooldown":0.78, "cor":(185,120,255), "tipo_proj":"eletrico", "prioridade":"grupo"},
    # v1.23.3: arma lendária desbloqueada na Loja Lendária.
    # v1.24.23: Laser Supremo virou feixe contínuo. Dano base ajustado para DPS lendário sem derreter chefes instantaneamente.
    "laser_supremo": {"nome":"Laser Supremo", "icone":"L", "custo":780, "dano":30, "alcance":380, "cooldown":0.38, "cor":(255,70,70), "tipo_proj":"laser", "prioridade":"maior_vida"},
    # v1.23.4: segunda arma lendária. Cone forte, ótimo para limpar grupos próximos.
    "espingarda_suprema": {"nome":"Espingarda Suprema", "icone":"E", "custo":720, "dano":52, "alcance":285, "cooldown":1.05, "cor":(255,135,55), "tipo_proj":"espingarda", "prioridade":"grupo"},
    "chamas": {"nome":"Lança-chamas", "icone":"F", "custo":195, "dano":8, "alcance":170, "cooldown":0.13, "cor":(255,92,35), "tipo_proj":"fogo", "prioridade":"perto"},
}


def alvo_fantasma_vulneravel(m):
    return getattr(m, "tipo", "") not in ("fantasma", "sombra") or getattr(m, "estado", "andando") == "atacando"

class Impacto:
    def __init__(self, x, y, cor=AMARELO, raio=18):
        self.x=x; self.y=y; self.t=0.24; self.cor=cor; self.raio=raio
        # v1.17.0: faíscas/fragmentos leves no ponto de impacto.
        self.particulas=[]
        for i in range(5):
            ang = (i * 1.256) + 0.35
            vel = 34 + i * 8
            self.particulas.append([float(x), float(y), math.cos(ang)*vel, math.sin(ang)*vel, 0.18 + i*0.012])
    def atualizar(self, dt):
        self.t-=dt
        for p in self.particulas:
            p[0]+=p[2]*dt; p[1]+=p[3]*dt; p[4]-=dt
        self.particulas=[p for p in self.particulas if p[4]>0]
    def desenhar(self, tela):
        r=int(self.raio*max(0,self.t/0.24))
        if r>1:
            pygame.draw.circle(tela,self.cor,(int(self.x),int(self.y)),r,2)
            pygame.draw.circle(tela,BRANCO,(int(self.x),int(self.y)),max(2,r//3),1)
        for px,py,_,_,vida in self.particulas:
            tam = 2 if vida > 0.08 else 1
            pygame.draw.rect(tela,self.cor,(int(px),int(py),tam,tam))


class LaserFeixe:
    """Feixe visual curto do Laser Supremo contínuo.
    A torre recria este rastro várias vezes por segundo enquanto estiver derretendo o alvo.
    """
    def __init__(self, x1, y1, x2, y2, forte=False):
        self.x1=float(x1); self.y1=float(y1); self.x2=float(x2); self.y2=float(y2)
        self.t=0.095 if not forte else 0.13; self.vivo=True; self.impactou=None; self.forte=forte
    def atualizar(self, dt, monstros=None):
        self.t -= dt
        if self.t <= 0:
            self.vivo=False
    def desenhar(self, tela):
        if self.t <= 0: return
        # Núcleo branco + borda vermelha. Sem alpha/surface para manter leve no Android.
        p1=(int(self.x1), int(self.y1)); p2=(int(self.x2), int(self.y2))
        largura = (7 if self.forte else 5) if self.t > 0.05 else 3
        pygame.draw.line(tela, (85,8,18), p1, p2, largura+4)
        pygame.draw.line(tela, (190,25,35), p1, p2, largura+2)
        pygame.draw.line(tela, (255,55,65), p1, p2, largura)
        pygame.draw.line(tela, (255,245,245), p1, p2, 2)
        pygame.draw.circle(tela, (255,245,245), p1, 4)
        pygame.draw.circle(tela, (255,80,80), p2, 7 if self.forte else 5, 1)



class EspingardaRajada:
    """Rajada visual curta da Espingarda Suprema.
    O dano em cone é aplicado pela Torre; esta classe só desenha os estilhaços.
    """
    def __init__(self, x, y, angulo, alcance):
        self.x=float(x); self.y=float(y); self.angulo=float(angulo); self.alcance=float(alcance)
        self.t=0.11; self.vivo=True; self.impactou=None
    def atualizar(self, dt, monstros=None):
        self.t -= dt
        if self.t <= 0:
            self.vivo=False
    def desenhar(self, tela):
        if self.t <= 0:
            return
        brilho = 1.0 if self.t > 0.055 else 0.55
        base_len = min(152, self.alcance * 0.62)
        # 7 linhas leves em leque. Sem partículas extras para manter FPS no Android.
        for i, off in enumerate((-0.42, -0.30, -0.18, -0.07, 0.0, 0.07, 0.18, 0.30, 0.42)):
            a = self.angulo + off
            ax, ay = math.cos(a), math.sin(a)
            dist = base_len + (i % 3) * 10
            p1 = (int(self.x + ax * 4), int(self.y + ay * 4))
            p2 = (int(self.x + ax * dist), int(self.y + ay * dist))
            pygame.draw.line(tela, (90, 48, 25), p1, p2, 4)
            pygame.draw.line(tela, (255, 170, 70), p1, p2, 2)
            if brilho > 0.8:
                pygame.draw.circle(tela, (255, 235, 165), p2, 2)

class Projetil:
    def __init__(self,x,y,alvo,dano,tipo="normal",alcance_area=0):
        self.x=float(x); self.y=float(y); self.alvo=alvo; self.dano=dano; self.tipo=tipo
        self.origem_x=float(x); self.origem_y=float(y); self.distancia_percorrida=0.0
        self.vel=620 if tipo=="sniper" else (500 if tipo=="normal" else (300 if tipo=="fogo" else (360 if tipo=="veneno" else 390)))
        self.vivo=True; self.raio=3 if tipo=="sniper" else (4 if tipo=="normal" else 6); self.impactou=None; self.alcance_area=alcance_area
        # Correção: quando outra arma mata o alvo antes, o projétil não some no meio do mapa.
        # Ele guarda o último destino/direção e decide o comportamento por tipo.
        if alvo:
            self.destino_x=float(alvo.rect.centerx); self.destino_y=float(alvo.rect.centery)
        else:
            self.destino_x=float(x); self.destino_y=float(y)
        dx=self.destino_x-self.x; dy=self.destino_y-self.y; dist=math.hypot(dx,dy) or 1
        self.dir_x=dx/dist; self.dir_y=dy/dist
        self.distancia_max=max(900.0, dist + 360.0)

    def _cor(self):
        return CIANO if self.tipo=="gelo" else ((185,120,255) if self.tipo=="eletrico" else ((80,220,90) if self.tipo=="veneno" else ((210,235,255) if self.tipo=="sniper" else ((255,92,35) if self.tipo=="fogo" else (LARANJA if self.tipo=="explosivo" else AMARELO)))))

    def _monstro_colidido(self, monstros, ignorar=None):
        if not monstros:
            return None
        raio = 16 if self.tipo in ("normal", "sniper", "eletrico", "fogo") else 18
        for m in monstros:
            if m is ignorar or m.vida <= 0:
                continue
            if getattr(m, "invisivel_tempo", 0) > 0 or not alvo_fantasma_vulneravel(m):
                continue
            if math.hypot(m.rect.centerx-self.x, m.rect.centery-self.y) <= raio:
                return m
        return None

    def _aplicar_impacto(self, alvo, ax, ay, monstros=None):
        cor=self._cor()
        if self.tipo=="explosivo":
            if monstros:
                for m in monstros:
                    if m.vida>0 and alvo_fantasma_vulneravel(m) and math.hypot(m.rect.centerx-ax,m.rect.centery-ay)<=62:
                        dano_area = int(self.dano*0.75)
                        if getattr(m, "tipo", "") in ("fantasma", "sombra"):
                            dano_area = max(1, int(dano_area * 0.55))
                        m.sofrer_dano(dano_area, origem="arma")
            self.impactou=Impacto(ax,ay,cor,34)
        elif self.tipo=="gelo":
            if alvo and alvo.vida>0:
                alvo.sofrer_dano(self.dano, origem="arma")
                alvo.aplicar_lentidao(0.45,1.7)
            self.impactou=Impacto(ax,ay,cor,22)
        elif self.tipo=="eletrico" and monstros:
            if alvo and alvo.vida>0:
                alvo.sofrer_dano(self.dano, origem="arma")
            pulos=0
            for m in monstros:
                if m is not alvo and m.vida>0 and alvo_fantasma_vulneravel(m) and pulos<2 and math.hypot(m.rect.centerx-ax,m.rect.centery-ay)<=95:
                    m.sofrer_dano(int(self.dano*0.55), origem="arma"); pulos+=1
            self.impactou=Impacto(ax,ay,cor,24)
        elif self.tipo=="veneno":
            if alvo and alvo.vida>0:
                alvo.sofrer_dano(max(1, int(self.dano*0.55)), origem="arma")
                if hasattr(alvo, "aplicar_queimadura"):
                    alvo.aplicar_queimadura(max(1, self.dano), 3.0)
            self.impactou=Impacto(ax,ay,cor,18)
        elif self.tipo=="sniper":
            if alvo and alvo.vida>0:
                alvo.sofrer_dano(int(self.dano*1.35), origem="arma")
            self.impactou=Impacto(ax,ay,cor,20)
        elif self.tipo=="fogo":
            dano = self.dano
            if alvo and alvo.vida>0:
                alvo.sofrer_dano(dano, origem="arma")
                if hasattr(alvo, "aplicar_queimadura"):
                    alvo.aplicar_queimadura(max(1, dano//2), 2.2)
            if monstros:
                for m in monstros:
                    if m is not alvo and m.vida>0 and alvo_fantasma_vulneravel(m) and abs(m.rect.centery-ay)<42 and math.hypot(m.rect.centerx-ax,m.rect.centery-ay)<=74:
                        m.sofrer_dano(max(1, int(dano*0.45)), origem="arma")
                        if hasattr(m, "aplicar_queimadura"):
                            m.aplicar_queimadura(max(1, dano//3), 1.5)
            self.impactou=Impacto(ax,ay,cor,16)
        else:
            if alvo and alvo.vida>0:
                dano = self.dano
                if getattr(alvo, "tipo", "") in ("fantasma", "sombra") and self.tipo in ("normal", "explosivo"):
                    dano = max(1, int(dano * 0.55))
                alvo.sofrer_dano(dano, origem="arma")
            self.impactou=Impacto(ax,ay,cor,18)
        self.vivo=False

    def atualizar(self,dt,monstros=None):
        alvo_vivo = self.alvo and self.alvo.vida > 0

        # Canhão/Gelo/Veneno: se o alvo morreu antes, seguem até o último ponto de destino
        # e fazem o impacto lá, em vez de sumirem no meio do mapa.
        if not alvo_vivo and self.tipo in ("explosivo", "gelo", "veneno"):
            ax, ay = self.destino_x, self.destino_y
            dx,dy=ax-self.x,ay-self.y; dist=math.hypot(dx,dy) or 1
            if dist < 15:
                self._aplicar_impacto(None, ax, ay, monstros)
                return
            passo = self.vel * dt
            self.x += (dx/dist)*passo; self.y += (dy/dist)*passo
            self.distancia_percorrida += passo
            if self.distancia_percorrida > self.distancia_max:
                self._aplicar_impacto(None, self.x, self.y, monstros)
            return

        # Projéteis comuns: se o alvo morreu, continuam na direção que já estavam seguindo
        # até sair do mapa/alcance ou acertar outro monstro.
        if not alvo_vivo:
            novo_alvo = self._monstro_colidido(monstros)
            if novo_alvo:
                self._aplicar_impacto(novo_alvo, novo_alvo.rect.centerx, novo_alvo.rect.centery, monstros)
                return
            passo = self.vel * dt
            self.x += self.dir_x * passo; self.y += self.dir_y * passo
            self.distancia_percorrida += passo
            if self.distancia_percorrida > self.distancia_max:
                self.vivo=False
            return

        ax,ay=self.alvo.rect.center
        self.destino_x=float(ax); self.destino_y=float(ay)
        dx,dy=ax-self.x,ay-self.y; dist=math.hypot(dx,dy) or 1
        self.dir_x=dx/dist; self.dir_y=dy/dist
        if dist<15:
            self._aplicar_impacto(self.alvo, ax, ay, monstros)
            return
        passo = self.vel*dt
        self.x+=self.dir_x*passo; self.y+=self.dir_y*passo
        self.distancia_percorrida += passo
    def desenhar(self,tela):
        # v1.19.2: cada arma ganhou um projétil com leitura própria.
        # Metralhadora = bala fina, canhão = bola preta, Tesla = pequeno zip-raio.
        cor=CIANO if self.tipo=="gelo" else ((185,120,255) if self.tipo=="eletrico" else ((80,220,90) if self.tipo=="veneno" else ((210,235,255) if self.tipo=="sniper" else ((255,92,35) if self.tipo=="fogo" else (LARANJA if self.tipo=="explosivo" else (215,205,150))))))
        x, y = int(self.x), int(self.y)

        if self.tipo == "normal":
            # Bala fina, estilo metralhadora: curta, rápida e sem bolinha grande.
            ang = math.atan2(self.dir_y, self.dir_x)
            if self.alvo and self.alvo.vida > 0:
                dx = self.alvo.rect.centerx - self.x
                dy = self.alvo.rect.centery - self.y
                ang = math.atan2(dy, dx)
            ax, ay = math.cos(ang), math.sin(ang)
            p1 = (int(self.x - ax * 4), int(self.y - ay * 4))
            p2 = (int(self.x + ax * 8), int(self.y + ay * 8))
            pygame.draw.line(tela, (70, 68, 62), p1, p2, 3)
            pygame.draw.line(tela, (235, 225, 160), p1, p2, 1)
            return

        if self.tipo == "explosivo":
            # Canhão: bola preta pesada, com contorno cinza leve.
            pygame.draw.circle(tela, (8, 8, 10), (x, y), 6)
            pygame.draw.circle(tela, (70, 70, 78), (x, y), 6, 1)
            pygame.draw.circle(tela, (150, 145, 130), (x-2, y-2), 1)
            return

        if self.tipo == "eletrico":
            # Tesla: pequeno zip-raio em vez de bala redonda.
            ang = math.atan2(self.dir_y, self.dir_x)
            if self.alvo and self.alvo.vida > 0:
                dx = self.alvo.rect.centerx - self.x
                dy = self.alvo.rect.centery - self.y
                ang = math.atan2(dy, dx)
            ax, ay = math.cos(ang), math.sin(ang)
            px, py = -ay, ax
            pts = []
            for i, off in enumerate((0, 5, 10, 15)):
                z = -2 if i % 2 == 0 else 2
                pts.append((int(self.x + ax*off + px*z), int(self.y + ay*off + py*z)))
            pygame.draw.lines(tela, (210, 250, 255), False, pts, 2)
            pygame.draw.lines(tela, (165, 105, 255), False, pts, 1)
            return

        if self.tipo == "sniper":
            # v1.19.4: projétil da sniper mais longo e mais grosso que a metralhadora,
            # mas ainda fino. Dá leitura de tiro pesado sem virar bola.
            ang = math.atan2(self.dir_y, self.dir_x)
            if self.alvo and self.alvo.vida > 0:
                dx = self.alvo.rect.centerx - self.x
                dy = self.alvo.rect.centery - self.y
                ang = math.atan2(dy, dx)
            ax, ay = math.cos(ang), math.sin(ang)
            p1 = (int(self.x - ax * 8), int(self.y - ay * 8))
            p2 = (int(self.x + ax * 14), int(self.y + ay * 14))
            r1 = (int(self.x - ax * 14), int(self.y - ay * 14))
            r2 = (int(self.x - ax * 4), int(self.y - ay * 4))
            pygame.draw.line(tela, (32, 36, 44), p1, p2, 4)
            pygame.draw.line(tela, (210, 235, 255), p1, p2, 2)
            pygame.draw.line(tela, (125, 165, 205), r1, r2, 1)
            return

        if self.tipo == "fogo":
            # v1.19.4: chama em cone leve: começa fina e abre um pouco.
            ang = math.atan2(self.dir_y, self.dir_x)
            if self.alvo and self.alvo.vida > 0:
                dx = self.alvo.rect.centerx - self.x
                dy = self.alvo.rect.centery - self.y
                ang = math.atan2(dy, dx)
            ax, ay = math.cos(ang), math.sin(ang)
            px, py = -ay, ax
            base = (int(self.x - ax * 3), int(self.y - ay * 3))
            meio = (int(self.x + ax * 8), int(self.y + ay * 8))
            ponta = (int(self.x + ax * 16), int(self.y + ay * 16))
            abertura = 5
            p_a = (int(meio[0] + px * abertura), int(meio[1] + py * abertura))
            p_b = (int(meio[0] - px * abertura), int(meio[1] - py * abertura))
            pygame.draw.polygon(tela, (190, 42, 28), [base, p_a, ponta, p_b])
            abertura2 = 3
            p_c = (int(meio[0] + px * abertura2), int(meio[1] + py * abertura2))
            p_d = (int(meio[0] - px * abertura2), int(meio[1] - py * abertura2))
            pygame.draw.polygon(tela, (255, 112, 35), [base, p_c, ponta, p_d])
            pygame.draw.line(tela, (255, 230, 90), base, (int(self.x + ax * 10), int(self.y + ay * 10)), 2)
            # faísca simples alternando pela posição, sem random para não pesar.
            if (int(self.x + self.y) // 7) % 2 == 0:
                pygame.draw.rect(tela, (255, 210, 85), (int(ponta[0]-1), int(ponta[1]-1), 2, 2))
            return

        # Gelo e veneno continuam com o comportamento visual anterior.
        pygame.draw.circle(tela,cor,(x,y),self.raio)
        pygame.draw.circle(tela,BRANCO,(x,y),self.raio,1)

class Torre:
    def __init__(self,x,y,tipo="metralhadora"):
        cfg=TIPOS_TORRE.get(tipo,TIPOS_TORRE["metralhadora"])
        self.rect=pygame.Rect(x,y,42,42); self.tipo=tipo; self.nome=cfg["nome"]; self.icone=cfg["icone"]
        self.nivel=1; self.dano=cfg["dano"]; self.alcance=cfg["alcance"]; self.cooldown=cfg["cooldown"]; self.cor=cfg["cor"]; self.tipo_proj=cfg["tipo_proj"]
        self.tempo_tiro=0; self.pulso=0
        # v1.21.3: base de polimento das torres.
        # Feedback visual leve: brilho quando pronta, recuo e flash já existentes.
        self.pronto_pulso = 0.0
        self.angulo = 0.0  # v1.16.7: direção visual da arma, em radianos
        # v1.17.0: polimento visual do disparo sem imagens externas.
        self.recuo = 0.0
        self.flash_tempo = 0.0
        self.capsulas = []
        # v1.19.6: metralhadora usa 1 cano até o penúltimo nível.
        # No nível MAX, libera 2 canos e alterna a origem do disparo.
        self._metralhadora_cano_lado = -1
        self._metralhadora_offset_disparo = 0.0
        # v1.7.4: torres não precisam procurar alvo em todo frame.
        # 8 a 10 buscas por segundo mantêm a sensação de resposta e reduzem muito o custo no Android.
        self._alvo_cache = None
        self._busca_alvo_tick = 0
        # v1.24.23: estado do Laser Supremo contínuo.
        self.laser_dano_tick = 0.0
        self.laser_visual_tick = 0.0
        # Audio: o jogo.py lê esta flag depois do update para tocar o som da arma.
        self.som_disparo_pendente = None
    def custo_upgrade(self):
        # v1.4.1: cada defesa tem sua própria curva de upgrade.
        # No nível máximo, as armas passam de 30K até perto de 100K.
        if self.nivel >= 15:
            return 999999
        curvas = {
            "metralhadora": 1.634,  # último upgrade ~32K
            "gelo": 1.584,          # último upgrade ~48K
            "veneno": 1.586,        # último upgrade ~58K
            "canhao": 1.586,        # último upgrade ~65K
            "eletrica": 1.587,      # último upgrade ~82K
            "sniper": 1.575,        # último upgrade ~90K
            "chamas": 1.589,        # último upgrade ~100K
            "laser_supremo": 1.56,   # lendária: upgrades caros, mas controlados
            "espingarda_suprema": 1.565,
        }
        base = TIPOS_TORRE[self.tipo]["custo"] * (0.62 if self.tipo == "sniper" else 1.35)
        mult = curvas.get(self.tipo, 1.78)
        return int(base * (mult ** (self.nivel - 1)))
    def melhorar(self):
        if self.nivel >= 15:
            return
        self.nivel+=1
        # Upgrade mais previsível: bastante dano, pouco alcance e cadência controlada.
        self.dano=int(self.dano*1.26)+3
        self.alcance+=6
        self.cooldown=max(0.10,self.cooldown*0.945)
    def _pontuar_alvo(self, m, sx, sy):
        dx=m.rect.centerx-sx; dy=m.rect.centery-sy
        dist2=dx*dx+dy*dy
        prioridade = TIPOS_TORRE.get(self.tipo, {}).get("prioridade", "perto")
        if prioridade == "maior_vida":
            return -m.vida
        if prioridade == "perto_porta":
            return -m.rect.y
        if prioridade == "rapido":
            return -getattr(m, "velocidade", 0)
        if prioridade == "sem_dot" and getattr(m, "queimadura_tempo", 0) <= 0:
            return -1000000 + dist2
        if prioridade == "grupo":
            grupo = 0
            for o in getattr(m, "_lista_ref", []):
                if o is not m and o.vida>0:
                    ox=o.rect.centerx-m.rect.centerx; oy=o.rect.centery-m.rect.centery
                    if ox*ox+oy*oy <= 95*95:
                        grupo += 1
            return -grupo*100000 + dist2
        return dist2

    def atualizar(self,dt,monstros,projeteis,bonus_dano=1.0):
        self.som_disparo_pendente = None
        self.tempo_tiro+=dt; self.pulso=max(0,self.pulso-dt)
        self.pronto_pulso = (self.pronto_pulso + dt * 3.0) % 6.283
        self.recuo = max(0.0, self.recuo - dt * 42)
        self.flash_tempo = max(0.0, self.flash_tempo - dt)
        for c in self.capsulas:
            c[0]+=c[2]*dt; c[1]+=c[3]*dt; c[3]+=95*dt; c[4]-=dt
        self.capsulas=[c for c in self.capsulas if c[4] > 0]
        self._busca_alvo_tick -= dt
        alvo = self._alvo_cache

        # Mantém o alvo atual se ele ainda serve. Usa distância ao quadrado para evitar sqrt.
        alcance2 = self.alcance * self.alcance
        if alvo is not None:
            if alvo.vida <= 0 or getattr(alvo, "invisivel_tempo", 0) > 0 or not alvo_fantasma_vulneravel(alvo):
                alvo = None
            else:
                dx = alvo.rect.centerx - self.rect.centerx
                dy = alvo.rect.centery - self.rect.centery
                if dx*dx + dy*dy > alcance2:
                    alvo = None

        # Busca alvo poucas vezes por segundo, não em todo frame.
        if alvo is None or self._busca_alvo_tick <= 0:
            self._busca_alvo_tick = 0.12
            alvo=None; melhor=999999999
            sx, sy = self.rect.centerx, self.rect.centery
            # Referência temporária só para a prioridade de grupo, sem criar listas extras por torre.
            for mm in monstros:
                mm._lista_ref = monstros
            for m in monstros:
                if m.vida<=0: continue
                if getattr(m, "invisivel_tempo", 0) > 0 or not alvo_fantasma_vulneravel(m):
                    continue
                dx=m.rect.centerx-sx; dy=m.rect.centery-sy
                dist2=dx*dx+dy*dy
                if dist2<=alcance2:
                    score = self._pontuar_alvo(m, sx, sy)
                    if score<melhor:
                        melhor=score; alvo=m
            self._alvo_cache = alvo

        if alvo:
            dx = alvo.rect.centerx - self.rect.centerx
            dy = alvo.rect.centery - self.rect.centery
            if dx or dy:
                self.angulo = math.atan2(dy, dx)

        # v1.24.23: Laser Supremo contínuo.
        # Ele trava no alvo, causa dano várias vezes por segundo e troca automaticamente quando o alvo cai.
        if self.tipo == "laser_supremo":
            self.laser_dano_tick = max(0.0, getattr(self, "laser_dano_tick", 0.0) - dt)
            self.laser_visual_tick = max(0.0, getattr(self, "laser_visual_tick", 0.0) - dt)
            if not alvo:
                self.flash_tempo = 0.0
                return

            # Pequeno aquecimento inicial para não ligar no mesmo frame em que a torre é construída.
            if self.tempo_tiro < self.cooldown:
                return

            ponta_x, ponta_y = self.ponta_cano()
            forte = getattr(alvo, "tipo", "") in ("bruto", "chefe", "chefe_devorador", "chefe_fantasma", "chefe_demolidor", "chefe_caos", "chefe_diretor", "chefe_baba")

            # Visual contínuo perfurante: o feixe atravessa o alvo e vai até o fim do alcance.
            ax, ay = math.cos(self.angulo), math.sin(self.angulo)
            fim_x = ponta_x + ax * self.alcance
            fim_y = ponta_y + ay * self.alcance
            raio_linha = 18

            if self.laser_visual_tick <= 0:
                self.laser_visual_tick = 0.045
                projeteis.append(LaserFeixe(ponta_x, ponta_y, fim_x, fim_y, forte=forte))

            # Dano contínuo: 10 pulsos por segundo, com buff de aproximadamente 30% no dano total.
            # O alvo principal recebe 100%. Inimigos atrás/alinhados recebem dano reduzido.
            if self.laser_dano_tick <= 0:
                self.laser_dano_tick = 0.10
                dano_tick = max(2, int(self.dano * 0.22 * bonus_dano * 1.30))
                if forte:
                    dano_tick = max(2, int(dano_tick * 0.88))  # chefes/brutos resistem um pouco mais

                # Audio: laser contínuo toca em pulsos controlados quando realmente causa dano.
                self.som_disparo_pendente = "laser_disparo"
                alvo.sofrer_dano(dano_tick, origem="arma")

                for m in monstros:
                    if m is alvo or m.vida <= 0:
                        continue
                    if getattr(m, "invisivel_tempo", 0) > 0 or not alvo_fantasma_vulneravel(m):
                        continue
                    vx = m.rect.centerx - ponta_x
                    vy = m.rect.centery - ponta_y
                    proj_linha = vx * ax + vy * ay
                    if proj_linha < 0 or proj_linha > self.alcance:
                        continue
                    px_l = ponta_x + ax * proj_linha
                    py_l = ponta_y + ay * proj_linha
                    dist_linha = math.hypot(m.rect.centerx - px_l, m.rect.centery - py_l)
                    if dist_linha <= raio_linha:
                        dano_secundario = max(1, int(dano_tick * 0.70))
                        if getattr(m, "tipo", "") in ("fantasma", "sombra"):
                            dano_secundario = max(1, int(dano_secundario * 0.70))
                        m.sofrer_dano(dano_secundario, origem="arma")

                self.pulso = 0.10
                self.recuo = 2.2
                self.flash_tempo = 0.08
            return

        if alvo and self.tempo_tiro>=self.cooldown:
            self.tempo_tiro=0; self.pulso=0.12
            sons_por_arma = {
                "metralhadora": "metralhadora_disparo",
                "canhao": "canhao_disparo",
                "veneno": "veneno_disparo",
                "gelo": "gelo_disparo",
                "chamas": "lanca_chamas_disparo",
                "sniper": "sniper_disparo",
                "eletrica": "tesla_disparo",
                "laser_supremo": "laser_disparo",
                "espingarda_suprema": "espingarda_disparo",
            }
            self.som_disparo_pendente = sons_por_arma.get(self.tipo)
            self.recuo = 8.5 if self.tipo == "espingarda_suprema" else (6.0 if self.tipo in ("sniper", "canhao") else (4.0 if self.tipo != "chamas" else 2.5))
            self.flash_tempo = 0.105 if self.tipo == "espingarda_suprema" else (0.055 if self.tipo != "chamas" else 0.085)
            # Cápsula ejetada para o lado oposto ao cano. Limite baixo para manter FPS.
            if len(self.capsulas) < 8 and self.tipo not in ("gelo", "eletrica"):
                lado = self.angulo - math.pi/2
                cx = self.rect.centerx - math.cos(self.angulo) * 3
                cy = self.rect.centery - math.sin(self.angulo) * 3
                self.capsulas.append([cx, cy, math.cos(lado)*55, math.sin(lado)*55-20, 0.38])
            # v1.16.7/v1.19.6: projétil sai da ponta do cano ativo.
            # Metralhadora MAX alterna esquerda/direita; antes do MAX fica em um cano central.
            if self.tipo == "metralhadora" and self.nivel >= 15:
                self._metralhadora_offset_disparo = 3.2 * self._metralhadora_cano_lado
                self._metralhadora_cano_lado *= -1
            else:
                self._metralhadora_offset_disparo = 0.0
            ponta_x, ponta_y = self.ponta_cano()
            dano_final = max(1, int(self.dano * bonus_dano))
            if self.tipo == "laser_supremo":
                # Feixe instantâneo: atravessa os pesadelos em linha reta.
                ax, ay = math.cos(self.angulo), math.sin(self.angulo)
                fim_x = ponta_x + ax * self.alcance
                fim_y = ponta_y + ay * self.alcance
                raio_linha = 18
                acertou = False
                for m in monstros:
                    if m.vida <= 0 or getattr(m, "invisivel_tempo", 0) > 0 or not alvo_fantasma_vulneravel(m):
                        continue
                    vx = m.rect.centerx - ponta_x
                    vy = m.rect.centery - ponta_y
                    proj = vx * ax + vy * ay
                    if proj < 0 or proj > self.alcance:
                        continue
                    px_l = ponta_x + ax * proj
                    py_l = ponta_y + ay * proj
                    dist = math.hypot(m.rect.centerx - px_l, m.rect.centery - py_l)
                    if dist <= raio_linha:
                        m.sofrer_dano(dano_final, origem="arma")
                        acertou = True
                if acertou:
                    projeteis.append(LaserFeixe(ponta_x, ponta_y, fim_x, fim_y))
            elif self.tipo == "espingarda_suprema":
                # Cone instantâneo: espalha estilhaços e pune grupos próximos.
                ax, ay = math.cos(self.angulo), math.sin(self.angulo)
                cos_abertura = math.cos(0.48)
                acertou = False
                for m in monstros:
                    if m.vida <= 0 or getattr(m, "invisivel_tempo", 0) > 0 or not alvo_fantasma_vulneravel(m):
                        continue
                    vx = m.rect.centerx - ponta_x
                    vy = m.rect.centery - ponta_y
                    dist = math.hypot(vx, vy) or 1
                    if dist > self.alcance:
                        continue
                    alinhamento = (vx / dist) * ax + (vy / dist) * ay
                    if alinhamento < cos_abertura:
                        continue
                    fator_dist = 1.0 - min(0.45, dist / max(1, self.alcance) * 0.45)
                    fator_centro = 0.78 + max(0.0, alinhamento - cos_abertura) * 0.85
                    dano = max(1, int(dano_final * fator_dist * fator_centro))
                    if getattr(m, "tipo", "") in ("fantasma", "sombra"):
                        dano = max(1, int(dano * 0.70))
                    m.sofrer_dano(dano, origem="arma")
                    acertou = True
                if acertou:
                    projeteis.append(EspingardaRajada(ponta_x, ponta_y, self.angulo, self.alcance))
            else:
                projeteis.append(Projetil(ponta_x,ponta_y,alvo,dano_final,self.tipo_proj))
    def comprimento_cano(self):
        # Distância do centro da torre até a ponta visual de cada arma.
        # Valores pequenos para manter o projétil dentro da escala do sprite.
        return {
            "metralhadora": 22,
            "sniper": 29,
            "canhao": 23,
            "veneno": 23,
            "eletrica": 25,
            "chamas": 29,
            "gelo": 22,
            "laser_supremo": 31,
            "espingarda_suprema": 24,
        }.get(self.tipo, 21)

    def ponta_cano(self):
        # v1.19.3: o tiro nasce no mesmo pivô da cabeça/cano giratório.
        # v1.19.6: no MAX da metralhadora, usa o cano esquerdo/direito alternado.
        dist = self.comprimento_cano() - self.recuo
        piv_x = self.rect.centerx
        piv_y = self.rect.centery - 4
        ax, ay = math.cos(self.angulo), math.sin(self.angulo)
        px, py = -ay, ax
        off = self._offset_cano_metralhadora()
        return (
            piv_x + px * off + ax * dist,
            piv_y + py * off + ay * dist,
        )

    def _offset_cano_metralhadora(self):
        if self.tipo == "metralhadora" and self.nivel >= 15:
            return float(getattr(self, "_metralhadora_offset_disparo", 0.0))
        return 0.0


    def _nivel_visual_info(self):
        """v1.18.0: evolução visual universal das armas, 1 a 15.
        Mantém o sprite pequeno e só acrescenta pixels/detalhes leves.
        """
        nv = max(1, min(15, int(getattr(self, "nivel", 1))))
        tier = (nv - 1) // 3  # 0..4
        passo = (nv - 1) % 3  # 0..2
        return nv, tier, passo

    def _cor_evolucao(self):
        nv, tier, passo = self._nivel_visual_info()
        # v1.18.1: cores por fase, com variação por arma para nenhuma evolução parecer copiada.
        paletas = {
            "metralhadora": [(185,190,198),(195,170,95),(110,190,115),(105,190,235),(255,205,75)],
            "sniper":       [(190,198,205),(150,112,70),(105,175,115),(125,185,240),(255,220,95)],
            "canhao":       [(175,170,165),(205,145,80),(210,120,70),(225,178,85),(255,205,70)],
            "veneno":       [(160,205,165),(80,220,95),(120,240,130),(185,120,255),(230,255,125)],
            "eletrica":     [(170,180,210),(125,190,255),(175,125,255),(110,230,255),(245,235,120)],
            "chamas":       [(190,175,160),(225,105,55),(255,150,45),(230,190,75),(255,225,90)],
            "gelo":         [(175,215,230),(130,225,255),(105,190,255),(180,145,255),(235,255,255)],
            "laser_supremo": [(255,90,90),(255,120,95),(255,70,130),(255,160,90),(255,230,170)],
            "espingarda_suprema": [(255,135,55),(255,165,70),(255,110,45),(255,190,90),(255,225,145)],
        }
        return paletas.get(self.tipo, paletas["metralhadora"])[max(0,min(4,tier))]

    def _detalhe_pixel(self, tela_draw, cor, x, y, w=2, h=2):
        pygame.draw.rect(tela_draw, cor, (int(x), int(y), int(w), int(h)))

    def _aplicar_evolucao_visual(self, tela_draw, cx, cy):
        """v1.18.1: evolução visual refinada e consistente para todas as armas.
        Cada tipo recebe detalhes próprios, mas segue a mesma escala 1-15:
        1-3 básico, 4-6 aprimorado, 7-9 avançado, 10-12 elite, 13-15 lendário.
        Não muda colisão, tamanho da torre, rotação nem ponta do cano.
        """
        nv, tier, passo = self._nivel_visual_info()
        if nv <= 1:
            return

        cor = self._cor_evolucao()
        brilho = (255, 250, 205) if tier >= 4 else (230, 238, 245)
        sombra = (32, 34, 42)
        escuro = (20, 22, 28)

        # Base universal: trilhos, reforços e brilho leve. Todas as armas recebem isso.
        if nv >= 2:
            self._detalhe_pixel(tela_draw, cor, cx-8, cy-8, 4 + passo*2, 1)
        if nv >= 3:
            self._detalhe_pixel(tela_draw, brilho, cx+2, cy-6, 2, 1)
        if nv >= 4:
            self._detalhe_pixel(tela_draw, sombra, cx-5, cy+6, 8 + passo*2, 2)
        if nv >= 7:
            self._detalhe_pixel(tela_draw, sombra, cx-6, cy-12, 10 + passo*2, 2)
        if nv >= 10:
            self._detalhe_pixel(tela_draw, cor, cx-16, cy-6, 3, 3)
            self._detalhe_pixel(tela_draw, cor, cx+15, cy-7, 3, 3)
        if nv >= 13:
            self._detalhe_pixel(tela_draw, cor, cx-19, cy-1, 2, 2)
            self._detalhe_pixel(tela_draw, cor, cx+19, cy-1, 2, 2)

        # Detalhes exclusivos por categoria, para evitar que todas pareçam a mesma arma.
        if self.tipo == "metralhadora":
            if nv >= 5: self._detalhe_pixel(tela_draw, cor, cx-3, cy+6, 4, 7)      # carregador melhor
            if nv >= 8: self._detalhe_pixel(tela_draw, brilho, cx+8, cy-5, 5, 1)   # cano polido
            if nv >= 11: pygame.draw.line(tela_draw, cor, (cx-14,cy+5), (cx-19,cy+9), 1)
            if nv >= 14: self._detalhe_pixel(tela_draw, brilho, cx+19, cy-3, 2, 5)

        elif self.tipo == "sniper":
            if nv >= 5: self._detalhe_pixel(tela_draw, cor, cx-7, cy-12, 15, 2)    # luneta maior
            if nv >= 8: self._detalhe_pixel(tela_draw, brilho, cx+18, cy-3, 6, 1)  # cano longo refinado
            if nv >= 11: self._detalhe_pixel(tela_draw, cor, cx-21, cy+3, 8, 2)    # coronha reforçada
            if nv >= 14: self._detalhe_pixel(tela_draw, brilho, cx+25, cy-2, 2, 4)

        elif self.tipo == "canhao":
            if nv >= 5: pygame.draw.circle(tela_draw, cor, (cx+16, cy), 6, 1)      # boca reforçada
            if nv >= 8: self._detalhe_pixel(tela_draw, brilho, cx-11, cy-9, 11, 2)
            if nv >= 11: self._detalhe_pixel(tela_draw, cor, cx-15, cy+10, 28, 2)  # base pesada
            if nv >= 14: pygame.draw.circle(tela_draw, brilho, (cx+16, cy), 3, 1)

        elif self.tipo == "veneno":
            if nv >= 5: self._detalhe_pixel(tela_draw, cor, cx-12, cy-15, 16, 2)   # tanque químico maior
            if nv >= 8: pygame.draw.circle(tela_draw, brilho, (cx+21, cy), 3, 1)
            if nv >= 11: pygame.draw.line(tela_draw, cor, (cx-12,cy-5), (cx+13,cy+6), 1)
            if nv >= 14: self._detalhe_pixel(tela_draw, brilho, cx+16, cy-4, 2, 8)

        elif self.tipo == "eletrica":
            if nv >= 5: pygame.draw.line(tela_draw, cor, (cx-9,cy-14), (cx+7,cy-6), 2)
            if nv >= 8: pygame.draw.line(tela_draw, brilho, (cx+7,cy+3), (cx+22,cy-3), 1)
            if nv >= 11: self._detalhe_pixel(tela_draw, cor, cx-13, cy-7, 4, 14)   # bateria lateral
            if nv >= 14: pygame.draw.circle(tela_draw, brilho, (cx+22, cy), 4, 1)

        elif self.tipo == "chamas":
            if nv >= 5: self._detalhe_pixel(tela_draw, cor, cx-17, cy-14, 11, 3)   # tanque reforçado
            if nv >= 8: self._detalhe_pixel(tela_draw, brilho, cx+14, cy-11, 9, 2) # bico melhor
            if nv >= 11: pygame.draw.line(tela_draw, cor, (cx-6,cy+2), (cx+16,cy-9), 2)
            if nv >= 14: self._detalhe_pixel(tela_draw, brilho, cx+24, cy-10, 3, 4)

        elif self.tipo == "gelo":
            if nv >= 5: pygame.draw.polygon(tela_draw, cor, [(cx+8,cy-1),(cx+19,cy-10),(cx+19,cy+8)])
            if nv >= 8: pygame.draw.line(tela_draw, brilho, (cx+7,cy-5), (cx+16,cy+4), 1)
            if nv >= 11: self._detalhe_pixel(tela_draw, cor, cx-14, cy-8, 4, 16)
            if nv >= 14: pygame.draw.circle(tela_draw, brilho, (cx+18, cy), 4, 1)

        # Final lendário universal: moldura pequena e brilho na ponta, sem exagero.
        if nv >= 15:
            pygame.draw.line(tela_draw, cor, (cx-18, cy-10), (cx-12, cy-12), 1)
            pygame.draw.line(tela_draw, cor, (cx+12, cy-12), (cx+20, cy-9), 1)
            self._detalhe_pixel(tela_draw, brilho, cx+22, cy-2, 2, 4)
            self._detalhe_pixel(tela_draw, escuro, cx-2, cy-1, 4, 1)


    def _cor_raridade_visual(self):
        """v1.18.2: borda discreta por raridade da arma, baseada no nível atual."""
        nv = max(1, min(15, int(getattr(self, "nivel", 1))))
        if nv >= 13:
            return (245, 205, 70)     # lendária
        if nv >= 10:
            return (175, 105, 245)    # épica
        if nv >= 7:
            return (85, 165, 245)     # rara
        if nv >= 4:
            return (100, 215, 120)    # incomum
        return (150, 155, 165)        # comum

    def _desenhar_fundo_arma_discreto(self, tela):
        """v1.18.3: fundo continua discreto, mas sem apagar as cores da arma.
        Alpha menor, cantos arredondados e borda fina por raridade.
        """
        w, h = 46, 38
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        rect = surf.get_rect()
        # Preto um pouco mais transparente que a v1.18.2. Mantém leitura no piso claro
        # sem roubar saturação do sprite da arma.
        pygame.draw.rect(surf, (0, 0, 0, 68), rect, border_radius=11)
        pygame.draw.rect(surf, (*self._cor_raridade_visual(), 210), rect.inflate(-1, -1), 1, border_radius=10)
        # Brilho interno quase imperceptível para integrar com a UI.
        pygame.draw.line(surf, (255, 255, 255, 32), (8, 5), (w - 8, 5), 1)
        tela.blit(surf, surf.get_rect(center=self.rect.center))

    def _desenhar_arma_pixel(self, tela):
        """v1.19.3: corpo em pé sem cano fixo.
        A base/corpo fica parada; todo cano visível é desenhado somente em
        _desenhar_cabeca_rotativa(). Isso remove o efeito de "dois canos":
        um parado e outro girando.
        """
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        cx, cy = 30, 30
        tela_draw = surf

        nv, tier, passo = self._nivel_visual_info()
        pesadelo = (145, 82, 220)
        pesadelo_claro = (215, 175, 255)
        metal = (142, 151, 164)
        metal_claro = (212, 220, 230)
        metal_escuro = (43, 48, 58)
        sombra = (12, 13, 18)
        base_escura = (25, 26, 34)
        madeira = (96, 58, 35)
        brilho_arma = self._cor_evolucao()

        def px(cor, x, y, w=2, h=2):
            pygame.draw.rect(tela_draw, cor, (int(x), int(y), int(w), int(h)))

        # Sombra e base fixa: silhueta de torreta em pé.
        pygame.draw.ellipse(tela_draw, (0, 0, 0, 85), (cx-18, cy+15, 36, 9))
        pygame.draw.rect(tela_draw, sombra, (cx-18, cy+9, 36, 11), border_radius=4)
        pygame.draw.rect(tela_draw, base_escura, (cx-16, cy+7, 32, 10), border_radius=4)
        pygame.draw.rect(tela_draw, madeira, (cx-19, cy+17, 38, 4), border_radius=2)
        pygame.draw.line(tela_draw, metal, (cx-12, cy+11), (cx+12, cy+11), 1)

        # Coluna central sem cano. Ela serve só como suporte do pivô giratório.
        pygame.draw.rect(tela_draw, metal_escuro, (cx-8, cy-2, 16, 12), border_radius=3)
        pygame.draw.rect(tela_draw, (62, 66, 78), (cx-6, cy-8, 12, 10), border_radius=3)

        # Núcleo de pesadelo discreto.
        core = 3 + min(2, tier)
        pygame.draw.circle(tela_draw, pesadelo, (cx, cy+5), core)
        pygame.draw.circle(tela_draw, pesadelo_claro, (cx-1, cy+4), max(1, core-2))
        if tier >= 2:
            pygame.draw.circle(tela_draw, (92, 45, 150), (cx, cy+5), core+3, 1)

        # Corpo por tipo: apenas base/miolo. Nada aqui deve parecer cano fixo.
        if self.tipo == "metralhadora":
            pygame.draw.rect(tela_draw, metal_escuro, (cx-12, cy-11, 24, 18), border_radius=5)
            pygame.draw.rect(tela_draw, metal, (cx-9, cy-14, 18, 8), border_radius=3)
            px(brilho_arma, cx-9, cy-12, 4, 3)
            if nv >= 7:
                px(metal_claro, cx-12, cy-7, 4, 5)
                px(metal_claro, cx+8, cy-7, 4, 5)

        elif self.tipo == "sniper":
            pygame.draw.rect(tela_draw, (45, 53, 67), (cx-11, cy-10, 22, 17), border_radius=5)
            pygame.draw.rect(tela_draw, (28, 31, 42), (cx-10, cy-16, 20, 5), border_radius=2)
            pygame.draw.rect(tela_draw, (140, 205, 255), (cx-3, cy-15, 6, 2))
            px(brilho_arma, cx-13, cy-3, 5, 6)

        elif self.tipo == "canhao":
            pygame.draw.rect(tela_draw, (67, 66, 74), (cx-14, cy-10, 28, 19), border_radius=6)
            pygame.draw.rect(tela_draw, (94, 90, 96), (cx-9, cy-16, 18, 12), border_radius=5)
            px(brilho_arma, cx-8, cy-13, 16, 2)
            pygame.draw.circle(tela_draw, metal_escuro, (cx-10, cy+16), 4)
            pygame.draw.circle(tela_draw, metal_escuro, (cx+10, cy+16), 4)

        elif self.tipo == "veneno":
            pygame.draw.rect(tela_draw, metal_escuro, (cx-12, cy-9, 24, 17), border_radius=5)
            pygame.draw.rect(tela_draw, (48, 145, 68), (cx-10, cy-18, 20, 10), border_radius=5)
            pygame.draw.rect(tela_draw, (116, 245, 135), (cx-4, cy-16, 8, 5), border_radius=2)
            pygame.draw.circle(tela_draw, (160, 255, 170), (cx, cy-19), 2)

        elif self.tipo == "eletrica":
            pygame.draw.rect(tela_draw, (52, 46, 77), (cx-13, cy-9, 26, 18), border_radius=5)
            pygame.draw.rect(tela_draw, metal, (cx-10, cy-18, 6, 11), border_radius=2)
            pygame.draw.rect(tela_draw, metal, (cx+4, cy-18, 6, 11), border_radius=2)
            pygame.draw.line(tela_draw, pesadelo_claro, (cx-6, cy-17), (cx+5, cy-9), 2)
            px(brilho_arma, cx-3, cy-15, 6, 3)

        elif self.tipo == "chamas":
            pygame.draw.rect(tela_draw, (67, 61, 62), (cx-12, cy-9, 24, 17), border_radius=5)
            pygame.draw.rect(tela_draw, (188, 56, 42), (cx-17, cy-18, 10, 18), border_radius=4)
            pygame.draw.rect(tela_draw, (255, 148, 54), (cx-15, cy-15, 3, 9), border_radius=1)
            pygame.draw.polygon(tela_draw, (255, 116, 35), [(cx+4,cy-17),(cx+1,cy-12),(cx+7,cy-12)])
            pygame.draw.polygon(tela_draw, (255, 230, 92), [(cx+4,cy-15),(cx+2,cy-12),(cx+6,cy-12)])

        elif self.tipo == "gelo":
            pygame.draw.rect(tela_draw, (56, 84, 108), (cx-12, cy-9, 24, 17), border_radius=5)
            pygame.draw.polygon(tela_draw, (150, 232, 255), [(cx,cy-20),(cx-9,cy-9),(cx+9,cy-9)])
            pygame.draw.polygon(tela_draw, (220, 252, 255), [(cx,cy-17),(cx-4,cy-11),(cx+4,cy-11)])
            pygame.draw.line(tela_draw, BRANCO, (cx,cy-18), (cx,cy-11), 1)

        elif self.tipo == "laser_supremo":
            pygame.draw.rect(tela_draw, (60, 18, 24), (cx-13, cy-10, 26, 18), border_radius=5)
            pygame.draw.rect(tela_draw, (120, 28, 35), (cx-9, cy-17, 18, 9), border_radius=3)
            pygame.draw.rect(tela_draw, (255, 90, 90), (cx-4, cy-15, 8, 4), border_radius=2)
            pygame.draw.circle(tela_draw, (255, 235, 235), (cx, cy-16), 2)
            pygame.draw.line(tela_draw, (255, 80, 80), (cx-14, cy+7), (cx+14, cy+7), 2)

        elif self.tipo == "espingarda_suprema":
            pygame.draw.rect(tela_draw, (72, 42, 28), (cx-14, cy-10, 28, 18), border_radius=5)
            pygame.draw.rect(tela_draw, (118, 74, 42), (cx-12, cy-15, 24, 8), border_radius=3)
            pygame.draw.rect(tela_draw, (225, 142, 62), (cx-8, cy-17, 16, 5), border_radius=2)
            pygame.draw.line(tela_draw, (255, 210, 120), (cx-12, cy+7), (cx+12, cy+7), 2)
            pygame.draw.circle(tela_draw, (255, 230, 165), (cx, cy-15), 2)

        else:
            pygame.draw.rect(tela_draw, metal_escuro, (cx-12, cy-9, 24, 17), border_radius=5)
            pygame.draw.rect(tela_draw, self.cor, (cx-5, cy-17, 10, 8), border_radius=2)

        # Evolução visual leve: detalhes laterais, nunca canos fixos.
        if nv >= 4:
            px(brilho_arma, cx-15, cy+5, 5 + passo*2, 3)
            px(brilho_arma, cx+9, cy+5, 5 + passo*2, 3)
        if nv >= 7:
            px(pesadelo, cx-18, cy-4, 3, 3)
            px(pesadelo, cx+15, cy-4, 3, 3)
        if nv >= 10:
            pygame.draw.rect(tela_draw, (24, 22, 31), (cx-20, cy-2, 5, 9), border_radius=2)
            pygame.draw.rect(tela_draw, (24, 22, 31), (cx+15, cy-2, 5, 9), border_radius=2)
            px(pesadelo_claro, cx-18, cy, 2, 2)
            px(pesadelo_claro, cx+16, cy, 2, 2)
        if nv >= 13:
            pygame.draw.line(tela_draw, brilho_arma, (cx-15, cy-13), (cx-8, cy-17), 1)
            pygame.draw.line(tela_draw, brilho_arma, (cx+8, cy-17), (cx+15, cy-13), 1)

        tela.blit(surf, surf.get_rect(center=self.rect.center))

        # Único cano visível: a cabeça rotativa.
        self._desenhar_cabeca_rotativa(tela)

        # Flash alinhado com a ponta do cano giratório.
        if self.flash_tempo > 0:
            fx, fy = self.ponta_cano()
            ax, ay = math.cos(self.angulo), math.sin(self.angulo)
            px1 = (int(fx), int(fy))
            px2 = (int(fx + ax * 11), int(fy + ay * 11))
            if self.tipo == "chamas":
                pygame.draw.line(tela, (255, 110, 35), px1, px2, 5)
                pygame.draw.line(tela, (255, 230, 90), px1, (int(fx + ax * 7), int(fy + ay * 7)), 2)
            elif self.tipo == "eletrica":
                pygame.draw.line(tela, (185, 245, 255), px1, px2, 2)
                pygame.draw.line(tela, pesadelo_claro, (int(fx-2), int(fy)), (int(fx + ax * 9), int(fy + ay * 9 + 3)), 2)
            elif self.tipo == "gelo":
                pygame.draw.circle(tela, (210, 250, 255), px1, 4, 1)
            elif self.tipo == "laser_supremo":
                pygame.draw.line(tela, (255, 50, 50), px1, px2, 5)
                pygame.draw.line(tela, (255, 245, 245), px1, px2, 2)
            elif self.tipo == "espingarda_suprema":
                pygame.draw.line(tela, (255, 135, 55), px1, px2, 6)
                pygame.draw.line(tela, (255, 235, 165), px1, px2, 2)
            else:
                pygame.draw.line(tela, (255, 216, 70), px1, px2, 3)
                pygame.draw.circle(tela, BRANCO, px1, 2)

        # Cápsulas pequenas no mundo, no estilo arcade/pixel leve.
        for cx2, cy2, _, _, vida in self.capsulas:
            tam = 3 if vida > 0.18 else 2
            pygame.draw.rect(tela, (214, 164, 72), (int(cx2), int(cy2), tam, max(1, tam-1)))

    def _desenhar_cabeca_rotativa(self, tela):
        """v1.19.2: base fica em pé/fixa e só a cabeça/cano acompanha o alvo.
        Evita o visual de arma deitada, mas mantém a mira clara e o tiro saindo da ponta.
        """
        px = self.rect.centerx
        py = self.rect.centery - 4
        ax, ay = math.cos(self.angulo), math.sin(self.angulo)
        perp_x, perp_y = -ay, ax
        rec = min(5.0, self.recuo)
        comp = self.comprimento_cano() - rec
        ponta = (int(px + ax * comp), int(py + ay * comp))
        base = (int(px), int(py))

        metal = (58, 62, 72)
        metal_claro = (166, 174, 185)
        escuro = (14, 15, 20)
        roxo = (160, 95, 240)

        # miolo giratório pequeno
        pygame.draw.circle(tela, escuro, base, 7)
        pygame.draw.circle(tela, metal, base, 6)
        pygame.draw.circle(tela, roxo, base, 3)

        if self.tipo == "canhao":
            # cano grosso, mas curto
            pygame.draw.line(tela, escuro, base, ponta, 9)
            pygame.draw.line(tela, (98, 96, 104), base, ponta, 6)
            pygame.draw.circle(tela, escuro, ponta, 5)
        elif self.tipo == "metralhadora":
            # v1.19.6: 1 cano até o penúltimo nível; 2 canos apenas no MAX.
            if self.nivel >= 15:
                p1 = (int(px + perp_x*3), int(py + perp_y*3))
                p2 = (int(px - perp_x*3), int(py - perp_y*3))
                q1 = (int(p1[0] + ax*comp), int(p1[1] + ay*comp))
                q2 = (int(p2[0] + ax*comp), int(p2[1] + ay*comp))
                pygame.draw.line(tela, escuro, p1, q1, 4)
                pygame.draw.line(tela, escuro, p2, q2, 4)
                pygame.draw.line(tela, metal_claro, p1, q1, 2)
                pygame.draw.line(tela, metal_claro, p2, q2, 2)
            else:
                pygame.draw.line(tela, escuro, base, ponta, 4)
                pygame.draw.line(tela, metal_claro, base, ponta, 2)
        elif self.tipo == "eletrica":
            pygame.draw.line(tela, (80, 65, 115), base, ponta, 5)
            pygame.draw.line(tela, (190, 240, 255), base, ponta, 2)
            pygame.draw.circle(tela, (205, 250, 255), ponta, 4, 1)
        elif self.tipo == "chamas":
            pygame.draw.line(tela, escuro, base, ponta, 7)
            pygame.draw.line(tela, (190, 72, 45), base, ponta, 4)
            pygame.draw.circle(tela, (255, 145, 45), ponta, 3)
        elif self.tipo == "gelo":
            pygame.draw.line(tela, (40, 78, 102), base, ponta, 6)
            pygame.draw.line(tela, (190, 245, 255), base, ponta, 3)
        elif self.tipo == "veneno":
            pygame.draw.line(tela, (35, 80, 45), base, ponta, 6)
            pygame.draw.line(tela, (115, 240, 125), base, ponta, 3)
        elif self.tipo == "laser_supremo":
            pygame.draw.line(tela, (60, 12, 18), base, ponta, 7)
            pygame.draw.line(tela, (255, 70, 70), base, ponta, 4)
            pygame.draw.line(tela, (255, 235, 235), base, ponta, 2)
            pygame.draw.circle(tela, (255, 245, 245), ponta, 4)
        elif self.tipo == "espingarda_suprema":
            boca1 = (int(ponta[0] + perp_x*4), int(ponta[1] + perp_y*4))
            boca2 = (int(ponta[0] - perp_x*4), int(ponta[1] - perp_y*4))
            pygame.draw.line(tela, (42, 24, 16), base, ponta, 8)
            pygame.draw.line(tela, (135, 78, 38), base, ponta, 5)
            pygame.draw.line(tela, (235, 150, 70), base, ponta, 2)
            pygame.draw.circle(tela, (45, 31, 24), boca1, 3)
            pygame.draw.circle(tela, (45, 31, 24), boca2, 3)
            pygame.draw.line(tela, (255, 210, 120), boca1, boca2, 1)
        else:
            pygame.draw.line(tela, escuro, base, ponta, 5)
            pygame.draw.line(tela, metal_claro, base, ponta, 2)


    def _desenhar_brilho_pronta(self, tela):
        """v1.21.3: brilho mínimo para mostrar que a torre está pronta.
        Não cria partículas nem superfícies grandes: só um círculo fino e discreto.
        """
        if self.cooldown <= 0:
            return
        progresso = min(1.0, self.tempo_tiro / self.cooldown)
        if progresso < 0.98:
            return
        # Pulso bem discreto. Não usa alpha para evitar custo extra no Android.
        raio = 24 + int((math.sin(self.pronto_pulso) + 1) * 1.5)
        cor = self._cor_evolucao()
        pygame.draw.circle(tela, cor, self.rect.center, raio, 1)
        if self.nivel >= 10:
            pygame.draw.circle(tela, (230, 238, 245), self.rect.center, max(12, raio-10), 1)

    def _desenhar_mira_alvo(self, tela):
        """v1.21.3: pequena mira na direção do alvo/cano.
        Ajuda a leitura de que o cano está apontando, sem poluir a tela.
        """
        if self.pulso <= 0:
            return
        fx, fy = self.ponta_cano()
        ax, ay = math.cos(self.angulo), math.sin(self.angulo)
        p1 = (int(fx + ax * 5), int(fy + ay * 5))
        p2 = (int(fx + ax * 13), int(fy + ay * 13))
        pygame.draw.line(tela, self._cor_evolucao(), p1, p2, 1)

    def desenhar(self,tela,fonte,selecionada=False):
        if selecionada:
            pygame.draw.circle(tela,(65,65,75),self.rect.center,self.alcance,1)
            pygame.draw.rect(tela,self._cor_raridade_visual(),self.rect.inflate(10,10),2,border_radius=10)

        # v1.21.3: brilho pronto antes do fundo, para ficar atrás da arma.
        self._desenhar_brilho_pronta(tela)

        # v1.18.2: o fundo preto pesado virou uma base discreta.
        # O pulso continua, mas bem mais suave e atrás do painel.
        if self.pulso > 0:
            raio = 20 + int(self.pulso * 22)
            pygame.draw.circle(tela, self.cor, self.rect.center, raio, 1)
        self._desenhar_fundo_arma_discreto(tela)
        self._desenhar_arma_pixel(tela)
        self._desenhar_mira_alvo(tela)

        # v1.18.5: números de nível removidos de baixo das armas/suportes.
        # A evolução agora é comunicada pelo sprite e pela borda de raridade.
