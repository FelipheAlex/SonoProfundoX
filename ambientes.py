# Sono Profundo v1.11.1
# Base segura dos Ambientes dos Pesadelos.
#
# IMPORTANTE:
# Este arquivo ainda NÃO é importado pelo jogo.
# Ele foi criado separado para preparar os mapas sem mexer na base estável v1.11.0.
# Assim o jogo deve abrir exatamente como antes.

AMBIENTE_PADRAO = "hospital_abandonado"

AMBIENTES = {
    "quarto_infantil": {
        "id": "quarto_infantil",
        "nome": "Ala Infantil",
        "icone": "🧸",
        "descricao": "2º andar. Brinquedos, berços e um silêncio estranho.",
        "desbloqueado": False,
        "bonus_moedas": 1.00,
        "evento_favorito": "normal",
        "inimigos_favorecidos": [],
        "cor_fundo": (22, 22, 32),
        "cor_chao": (70, 45, 34),
    },
    "hospital_abandonado": {
        "id": "hospital_abandonado",
        "nome": "Hospital",
        "icone": "🏥",
        "descricao": "1º andar. Sobreviva até a Noite 20 e enfrente o Diretor.",
        "desbloqueado": True,
        "bonus_moedas": 1.15,
        "evento_favorito": "nevoa",
        "inimigos_favorecidos": ["fantasma"],
        "cor_fundo": (18, 34, 32),
        "cor_chao": (238, 242, 238),
    },
}


def obter_ambiente(ambiente_id=None):
    """Retorna os dados de um ambiente sem alterar o jogo principal."""
    if not ambiente_id:
        ambiente_id = AMBIENTE_PADRAO
    return AMBIENTES.get(ambiente_id, AMBIENTES[AMBIENTE_PADRAO])


def listar_ambientes():
    """Retorna uma lista com todos os ambientes cadastrados."""
    return list(AMBIENTES.values())


# v1.14.0: campanha leve por andares.
# Só dados simples: sem imagens, sem cutscenes pesadas.
ANDARES_CAMPANHA = [
    {"andar": 1, "nome": "Hospital", "ambiente": "hospital_abandonado", "inicio": 1, "fim": 20, "chefe": "Diretor do Hospital"},
    {"andar": 2, "nome": "Ala Infantil", "ambiente": "quarto_infantil", "inicio": 21, "fim": 40, "chefe": "Babá Amaldiçoada"},
    {"andar": 3, "nome": "Laboratório", "ambiente": "laboratorio", "inicio": 41, "fim": 60, "chefe": "Cientista Mutante"},
    {"andar": 4, "nome": "Necrotério", "ambiente": "necrotorio", "inicio": 61, "fim": 80, "chefe": "O Legista"},
    {"andar": 5, "nome": "Subsolo", "ambiente": "subsolo", "inicio": 81, "fim": 100, "chefe": "Origem do Pesadelo"},
]

def obter_andar_por_noite(noite):
    try:
        noite = int(noite)
    except Exception:
        noite = 1
    for andar in ANDARES_CAMPANHA:
        if andar["inicio"] <= noite <= andar["fim"]:
            return andar
    return ANDARES_CAMPANHA[-1]

def obter_andar(numero):
    for andar in ANDARES_CAMPANHA:
        if int(andar["andar"]) == int(numero):
            return andar
    return ANDARES_CAMPANHA[0]
