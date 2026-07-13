# Gerenciador de áudio do Sono Profundo
# Estrutura organizada para ambiente, zumbis, armas, jogador e interface.
import os
import random
import time
import pygame

class Sons:
    def __init__(self):
        self.ativo = True
        self.base = os.path.join(os.path.dirname(__file__), "assets", "sounds")
        self.ambiente_iniciado = False
        self.flash_relampago = 0.0
        self.ultimo_toque = {}
        self.sons = {}

        self.volume_ambiente = 0.55
        self.volume_zumbi = 0.85
        self.volume_efeitos = 0.75

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            # Mais canais para evitar que armas, ambiente, habilidades e monstros disputem o mesmo espaço.
            pygame.mixer.set_num_channels(56)

            # Canais fixos gerais.
            self.canal_ambiente = pygame.mixer.Channel(0)
            self.canal_musica = pygame.mixer.Channel(1)
            self.canal_mapa = pygame.mixer.Channel(2)
            self.canal_jogador = pygame.mixer.Channel(3)
            self.canal_armas = pygame.mixer.Channel(4)   # compatibilidade
            self.canal_ui = pygame.mixer.Channel(5)
            self.canal_extra = pygame.mixer.Channel(6)

            # Canais separados por tipo de monstro.
            # Assim o som do Corredor não corta o Bruto, o Normal não corta o Explosivo, etc.
            self.canais_monstros = {
                "normal": [pygame.mixer.Channel(i) for i in range(8, 11)],       # 8, 9, 10
                "corredor": [pygame.mixer.Channel(i) for i in range(11, 14)],    # 11, 12, 13
                "explosivo": [pygame.mixer.Channel(i) for i in range(14, 17)],   # 14, 15, 16
                "bruto": [pygame.mixer.Channel(i) for i in range(17, 20)],       # 17, 18, 19
                "fantasma": [pygame.mixer.Channel(i) for i in range(20, 23)],    # 20, 21, 22
                "devorador": [pygame.mixer.Channel(i) for i in range(23, 26)],   # 23, 24, 25
                "chefe_baba": [pygame.mixer.Channel(i) for i in range(26, 28)],
                "chefe_demolidor": [pygame.mixer.Channel(i) for i in range(28, 30)],
                "chefe_diretor": [pygame.mixer.Channel(i) for i in range(30, 32)],
                "chefe_fantasma": [pygame.mixer.Channel(i) for i in range(32, 34)],
                "morte": [pygame.mixer.Channel(i) for i in range(34, 37)],
            }

            # Canais próprios para armas, habilidades e porta.
            # Isso evita metralhadora cortar habilidade, porta ou sons dos monstros.
            self.canais_armas = [pygame.mixer.Channel(i) for i in range(37, 45)]       # 37-44
            self.canais_habilidades = [pygame.mixer.Channel(i) for i in range(45, 49)] # 45-48
            self.canais_porta = [pygame.mixer.Channel(i) for i in range(49, 52)]       # 49-51
            self.canais_interface = [pygame.mixer.Channel(i) for i in range(52, 54)]   # 52-53
            self.canais_mapa = [pygame.mixer.Channel(i) for i in range(54, 56)]        # 54-55

            # Compatibilidade com nomes antigos.
            self.canal_zumbi = self.canais_monstros["normal"][0]
            self.canais_zumbis = sum(self.canais_monstros.values(), [])
            self._carregar_sons()
        except Exception:
            self.ativo = False

    def _existe(self, *partes):
        caminho = os.path.join(self.base, *partes)
        return caminho if os.path.exists(caminho) else None

    def _carregar(self, chave, *partes, volume=1.0):
        caminho = self._existe(*partes)
        if not caminho:
            return None
        try:
            som = pygame.mixer.Sound(caminho)
            som.set_volume(volume)
            self.sons[chave] = som
            return som
        except Exception:
            return None

    def _carregar_pasta(self, chave, *partes, volume=1.0):
        pasta = os.path.join(self.base, *partes)
        lista = []
        if os.path.isdir(pasta):
            for nome in sorted(os.listdir(pasta)):
                if nome.lower().endswith((".wav", ".mp3", ".ogg")):
                    try:
                        som = pygame.mixer.Sound(os.path.join(pasta, nome))
                        som.set_volume(volume)
                        lista.append(som)
                    except Exception:
                        pass
        self.sons[chave] = lista
        return lista

    def _carregar_sons(self):
        # Ambiente principal atual.
        self._carregar("ambiente_hospital", "ambiente", "hospital_ambiente.mp3", volume=self.volume_ambiente)
        self._carregar("ambiente_hospital_wav", "ambiente", "hospital_ambiente.wav", volume=self.volume_ambiente)

        # Zumbis comuns: som curto de surgimento.
        # Ele deve tocar apenas uma vez quando o monstro nasce.
        self._carregar_pasta("zumbi_normal_aparece", "zumbis", "normal", "aparecer", volume=0.72)
        self._carregar_pasta("zumbi_corredor_aparece", "zumbis", "corredor", "aparecer", volume=0.72)
        self._carregar_pasta("zumbi_explosivo_aparece", "zumbis", "explosivo", "aparecer", volume=0.72)

        # Pastas antigas mantidas só por compatibilidade, sem repetir som em update.
        self._carregar_pasta("zumbi_normal_morte", "zumbis", "normal", "morte", volume=self.volume_zumbi)
        self._carregar_pasta("zumbi_normal_ataque", "zumbis", "normal", "ataque", volume=self.volume_zumbi)
        self._carregar_pasta("zumbi_normal_gemidos", "zumbis", "normal", "gemidos", volume=0.55)

        # Fantasma.
        self._carregar_pasta("fantasma_aparece", "zumbis", "fantasma", "aparece", volume=0.80)

        # Bruto.
        self._carregar_pasta("bruto_aparece", "zumbis", "bruto", "aparecer", volume=0.88)

        # Devorador / chefe devorador.
        self._carregar_pasta("devorador_aparece", "zumbis", "devorador", "aparecer", volume=0.90)

        # Chefes com sons próprios de surgimento.
        self._carregar_pasta("chefe_baba_aparece", "zumbis", "chefes", "baba_sombria", "aparecer", volume=0.90)
        self._carregar_pasta("chefe_demolidor_aparece", "zumbis", "chefes", "demolidor", "aparecer", volume=0.92)
        self._carregar_pasta("chefe_diretor_aparece", "zumbis", "chefes", "doutor_infectado", "aparecer", volume=0.92)
        self._carregar_pasta("chefe_fantasma_aparece", "zumbis", "chefes", "rei_fantasma", "aparecer", volume=0.90)

        # Explosivo.
        self._carregar_pasta("explosivo_aparece", "zumbis", "explosivo", "aparecer", volume=0.72)
        self._carregar_pasta("explosivo_morte", "zumbis", "explosivo", "morte", volume=1.0)

        # Espaços prontos para próximos sons.
        self._carregar_pasta("porta", "porta", volume=self.volume_efeitos)
        self._carregar_pasta("porta_madeira", "porta", "madeira", volume=0.82)
        self._carregar_pasta("porta_metal", "porta", "metal", volume=0.82)
        self._carregar_pasta("armas", "armas", volume=self.volume_efeitos)
        self._carregar_pasta("metralhadora_disparo", "armas", "metralhadora", "disparo", volume=0.82)
        self._carregar_pasta("canhao_disparo", "armas", "canhao", "disparo", volume=0.88)
        # Veneno e Gelo usam o mesmo efeito do Canhão porque as três armas disparam bola/projétil pesado.
        self._carregar_pasta("veneno_disparo", "armas", "veneno", "disparo", volume=0.84)
        self._carregar_pasta("gelo_disparo", "armas", "gelo", "disparo", volume=0.84)
        self._carregar_pasta("lanca_chamas_disparo", "armas", "lanca_chamas", "disparo", volume=0.78)
        self._carregar_pasta("sniper_disparo", "armas", "sniper", "disparo", volume=0.68)
        self._carregar_pasta("tesla_disparo", "armas", "tesla", "disparo", volume=0.82)
        self._carregar_pasta("laser_disparo", "armas", "laser", "disparo", volume=0.82)
        self._carregar_pasta("espingarda_disparo", "armas", "espingarda", "disparo", volume=0.88)
        self._carregar_pasta("habilidades", "habilidades", volume=self.volume_efeitos)
        # Habilidades do jogador com sons próprios.
        self._carregar_pasta("habilidade_cura", "habilidades", "cura", volume=0.82)
        self._carregar_pasta("habilidade_ganancia", "habilidades", "ganancia", volume=0.82)
        self._carregar_pasta("habilidade_gelo", "habilidades", "gelo", volume=0.84)
        self._carregar_pasta("habilidade_raio", "habilidades", "raio", volume=0.86)
        self._carregar_pasta("habilidade_meteoro", "habilidades", "meteoro", volume=0.88)
        self._carregar_pasta("habilidade_terremoto", "habilidades", "terremoto", volume=0.90)
        self._carregar_pasta("interface", "interface", volume=0.55)

    def iniciar_ambiente(self):
        if not self.ativo or self.ambiente_iniciado:
            return
        som = self.sons.get("ambiente_hospital") or self.sons.get("ambiente_hospital_wav")
        if som:
            try:
                self.canal_ambiente.play(som, loops=-1)
                self.ambiente_iniciado = True
            except Exception:
                pass

    def iniciar_musica_suspense(self):
        # Compatibilidade com versões anteriores: o ambiente atual é o áudio principal.
        self.iniciar_ambiente()

    def _pode_tocar(self, nome, intervalo):
        agora = time.time()
        if intervalo and agora - self.ultimo_toque.get(nome, 0) < intervalo:
            return False
        self.ultimo_toque[nome] = agora
        return True


    def _canal_monstro_livre(self, tipo="normal"):
        """Retorna um canal livre do tipo de monstro, sem cortar sons já tocando."""
        grupos = getattr(self, "canais_monstros", {}) or {}
        canais = grupos.get(tipo) or grupos.get("normal") or [getattr(self, "canal_zumbi", None)]
        canais = [c for c in canais if c is not None]
        for canal in canais:
            try:
                if not canal.get_busy():
                    return canal
            except Exception:
                pass
        # Se todos os canais desse tipo estiverem ocupados, não corta nenhum som.
        # É melhor perder um gemido de spawn do que interromper outro monstro no meio.
        return None

    def _canal_zumbi_livre(self):
        # Compatibilidade com chamadas antigas.
        return self._canal_monstro_livre("normal")

    def _canal_livre(self, canais, fallback=None, cortar=False):
        """Retorna um canal livre de uma lista.
        Por padrão não corta som em andamento; para armas, permite reaproveitar o primeiro
        canal apenas quando todos estiverem ocupados, evitando silêncio em rajadas.
        """
        canais = [c for c in (canais or []) if c is not None]
        for canal in canais:
            try:
                if not canal.get_busy():
                    return canal
            except Exception:
                pass
        if cortar and canais:
            return canais[0]
        return fallback

    def _canal_arma_livre(self):
        return self._canal_livre(getattr(self, "canais_armas", []), fallback=getattr(self, "canal_armas", None), cortar=True)

    def _canal_habilidade_livre(self):
        return self._canal_livre(getattr(self, "canais_habilidades", []), fallback=getattr(self, "canal_jogador", None), cortar=False)

    def _canal_porta_livre(self):
        return self._canal_livre(getattr(self, "canais_porta", []), fallback=getattr(self, "canal_mapa", None), cortar=False)

    def _canal_interface_livre(self):
        return self._canal_livre(getattr(self, "canais_interface", []), fallback=getattr(self, "canal_ui", None), cortar=False)

    def _canal_mapa_livre(self):
        return self._canal_livre(getattr(self, "canais_mapa", []), fallback=getattr(self, "canal_mapa", None), cortar=False)

    def _tocar_sound(self, canal, som, volume=None):
        if not self.ativo or not som or canal is None:
            return None
        try:
            if volume is not None:
                som.set_volume(volume)
            canal.play(som)
            self.ultimo_canal_tocado = canal
            return canal
        except Exception:
            return None

    def tocar(self, nome, volume=None, intervalo=0.0):
        self.ultimo_canal_tocado = None
        if not self.ativo or not self._pode_tocar(nome, intervalo):
            return None

        # Mapeamento dos nomes antigos do jogo para a estrutura nova.
        if nome in ("zumbi_aparece", "zumbi_normal_aparece", "zumbi_normal_andando", "zumbi_gemido"):
            lista = self.sons.get("zumbi_normal_aparece") or self.sons.get("zumbi_normal_gemidos") or []
            if lista:
                # Som curto do zumbi normal quando nasce. Não fica em loop.
                return self._tocar_sound(self._canal_monstro_livre("normal"), random.choice(lista), volume if volume is not None else 0.72)
            return None

        if nome in ("corredor_aparece", "corredor_spawn", "corredor_surge"):
            lista = self.sons.get("zumbi_corredor_aparece") or []
            if lista:
                # Som próprio do Corredor, sem herdar o som do zumbi normal.
                return self._tocar_sound(self._canal_monstro_livre("corredor"), random.choice(lista), volume if volume is not None else 0.72)
            return None

        if nome in ("fantasma_aparece", "fantasma_spawn", "fantasma_surge"):
            lista = self.sons.get("fantasma_aparece") or []
            if lista:
                # Som do Fantasma quando ele aparece.
                return self._tocar_sound(self._canal_monstro_livre("fantasma"), random.choice(lista), volume if volume is not None else 0.80)
            return None

        if nome in ("bruto_aparece", "bruto_spawn", "bruto_surge"):
            lista = self.sons.get("bruto_aparece") or []
            if lista:
                # Som do Bruto quando ele aparece.
                return self._tocar_sound(self._canal_monstro_livre("bruto"), random.choice(lista), volume if volume is not None else 0.88)
            return None

        if nome in ("devorador_aparece", "devorador_spawn", "devorador_surge", "chefe_devorador_aparece"):
            lista = self.sons.get("devorador_aparece") or self.sons.get("bruto_aparece") or []
            if lista:
                # Som do Devorador quando ele aparece.
                return self._tocar_sound(self._canal_monstro_livre("devorador"), random.choice(lista), volume if volume is not None else 0.90)
            return None


        if nome in ("chefe_baba_aparece", "chefe_baba_spawn", "baba_sombria_aparece"):
            lista = self.sons.get("chefe_baba_aparece") or []
            if lista:
                return self._tocar_sound(self._canal_monstro_livre("chefe_baba"), random.choice(lista), volume if volume is not None else 0.90)
            return None

        if nome in ("chefe_demolidor_aparece", "chefe_demolidor_spawn", "demolidor_aparece"):
            lista = self.sons.get("chefe_demolidor_aparece") or []
            if lista:
                return self._tocar_sound(self._canal_monstro_livre("chefe_demolidor"), random.choice(lista), volume if volume is not None else 0.92)
            return None

        if nome in ("chefe_diretor_aparece", "chefe_diretor_spawn", "doutor_infectado_aparece"):
            lista = self.sons.get("chefe_diretor_aparece") or []
            if lista:
                return self._tocar_sound(self._canal_monstro_livre("chefe_diretor"), random.choice(lista), volume if volume is not None else 0.92)
            return None

        if nome in ("chefe_fantasma_aparece", "chefe_fantasma_spawn", "rei_fantasma_aparece"):
            lista = self.sons.get("chefe_fantasma_aparece") or []
            if lista:
                self._tocar_sound(self._canal_monstro_livre("chefe_fantasma"), random.choice(lista), volume if volume is not None else 0.90)
            return

        if nome in ("explosivo_aparece", "explosivo_spawn", "explosivo_surge"):
            # Explosivo tem som próprio. Não cai mais para o som do zumbi normal.
            lista = self.sons.get("explosivo_aparece") or self.sons.get("zumbi_explosivo_aparece") or []
            if lista:
                self._tocar_sound(self._canal_monstro_livre("explosivo"), random.choice(lista), volume if volume is not None else 0.82)
            return

        if nome in ("explosivo_morte", "explosivo_explode", "explosao"):
            lista = self.sons.get("explosivo_morte") or []
            if lista:
                # Explosão do Zumbi Explosivo quando morre.
                self._tocar_sound(self._canal_monstro_livre("morte") or self.canal_mapa, random.choice(lista), volume if volume is not None else 1.0)
            return

        if nome in ("zumbi_morte", "zumbi_normal_morte"):
            # Correção: som de morte do zumbi normal desativado.
            # Isso evita o gemido tocar ao vencer a noite ou quando o último zumbi some.
            return


        if nome in ("metralhadora_disparo", "metralhadora_tiro", "tiro_metralhadora"):
            lista = self.sons.get("metralhadora_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.82)
            return

        if nome in ("canhao_disparo", "canhao_tiro", "tiro_canhao"):
            lista = self.sons.get("canhao_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.88)
            return

        if nome in ("veneno_disparo", "veneno_tiro", "tiro_veneno"):
            lista = self.sons.get("veneno_disparo") or self.sons.get("canhao_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.84)
            return

        if nome in ("gelo_disparo", "gelo_tiro", "tiro_gelo"):
            lista = self.sons.get("gelo_disparo") or self.sons.get("canhao_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.84)
            return

        if nome in ("lanca_chamas_disparo", "lanca_chamas_tiro", "lanca_chama_disparo", "chamas_disparo"):
            lista = self.sons.get("lanca_chamas_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.78)
            return

        if nome in ("sniper_disparo", "sniper_tiro", "tiro_sniper"):
            lista = self.sons.get("sniper_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 1.0)
            return

        if nome in ("tesla_disparo", "tesla_tiro", "eletrica_disparo", "choque_disparo"):
            lista = self.sons.get("tesla_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.82)
            return

        if nome in ("laser_disparo", "laser_tiro", "tiro_laser"):
            lista = self.sons.get("laser_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.82)
            return

        if nome in ("espingarda_disparo", "espingarda_tiro", "tiro_espingarda"):
            lista = self.sons.get("espingarda_disparo") or []
            if lista:
                self._tocar_sound(self._canal_arma_livre(), random.choice(lista), volume if volume is not None else 0.88)
            return

        if nome in ("porta_madeira_hit", "porta_madeira"):
            lista = self.sons.get("porta_madeira") or self.sons.get("porta") or []
            if lista:
                return self._tocar_sound(self._canal_porta_livre(), random.choice(lista), volume if volume is not None else 0.82)
            return None

        if nome in ("porta_metal_hit", "porta_metal"):
            lista = self.sons.get("porta_metal") or self.sons.get("porta") or []
            if lista:
                return self._tocar_sound(self._canal_porta_livre(), random.choice(lista), volume if volume is not None else 0.82)
            return None

        if nome in ("porta_hit", "porta"):
            lista = self.sons.get("porta") or []
            if lista:
                return self._tocar_sound(self._canal_porta_livre(), random.choice(lista), volume)
            return None

        # Sons próprios das habilidades do jogador.
        habilidades_map = {
            "congelar": ("habilidade_gelo", 0.84),
            "habilidade_gelo": ("habilidade_gelo", 0.84),
            "gelo_habilidade": ("habilidade_gelo", 0.84),
            "meteoro": ("habilidade_meteoro", 0.88),
            "habilidade_meteoro": ("habilidade_meteoro", 0.88),
            "reparar": ("habilidade_cura", 0.82),
            "cura": ("habilidade_cura", 0.82),
            "curar": ("habilidade_cura", 0.82),
            "raio": ("habilidade_raio", 0.86),
            "choque_habilidade": ("habilidade_raio", 0.86),
            "habilidade_raio": ("habilidade_raio", 0.86),
            "terremoto": ("habilidade_terremoto", 0.90),
            "habilidade_terremoto": ("habilidade_terremoto", 0.90),
            "ganancia": ("habilidade_ganancia", 0.82),
            "ganância": ("habilidade_ganancia", 0.82),
            "habilidade_ganancia": ("habilidade_ganancia", 0.82),
        }
        if nome in habilidades_map:
            chave, volume_padrao = habilidades_map[nome]
            lista = self.sons.get(chave) or self.sons.get("habilidades") or []
            if lista:
                self._tocar_sound(self._canal_habilidade_livre(), random.choice(lista), volume if volume is not None else volume_padrao)
            return

        if nome in ("habilidade",):
            lista = self.sons.get("habilidades") or []
            if lista:
                self._tocar_sound(self._canal_habilidade_livre(), random.choice(lista), volume)
            return

        if nome in ("moeda", "upgrade", "vitoria", "game_over", "noite"):
            lista = self.sons.get("interface") or []
            if lista:
                self._tocar_sound(self._canal_interface_livre(), random.choice(lista), volume)
            return

    def tocar_variacao(self, nomes, volume=None, intervalo=0.0):
        if nomes:
            self.tocar(random.choice(list(nomes)), volume=volume, intervalo=intervalo)

    def atualizar_ambiente(self, dt):
        self.flash_relampago = 0.0
        if self.ativo and not self.ambiente_iniciado:
            self.iniciar_ambiente()

    def obter_flash_relampago(self):
        return 0.0

    def parar_tudo(self):
        if not self.ativo:
            return
        try:
            pygame.mixer.stop()
            self.ambiente_iniciado = False
        except Exception:
            pass
