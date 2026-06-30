import math

# Regras de dosagem de concreto por tipo de elemento estrutural
REGRAS_FCK = {
    "Viga Baldrame": {"fck": 20, "cimento_por_m3": 7.0, "areia_por_m3": 0.66, "brita_por_m3": 0.60, "tipo_brita": "Brita 1"},
    "Laje": {"fck": 25, "cimento_por_m3": 8.0, "areia_por_m3": 0.57, "brita_por_m3": 0.59, "tipo_brita": "Brita 0"},
    "Pilar": {"fck": 25, "cimento_por_m3": 8.5, "areia_por_m3": 0.55, "brita_por_m3": 0.58, "tipo_brita": "Brita 1"},
    "Fundação - Estaca": {"fck": 25, "cimento_por_m3": 8.0, "areia_por_m3": 0.57, "brita_por_m3": 0.59, "tipo_brita": "Brita 1"},
    "Fundação - Radie": {"fck": 30, "cimento_por_m3": 9.0, "areia_por_m3": 0.48, "brita_por_m3": 0.55, "tipo_brita": "Brita 1"},
}

# Regras de recomendação de aço por tipo de elemento
REGRAS_ACO = {
    "Viga Baldrame": {"aco": "CA-50", "bitola_min": "8 mm", "bitola_max": "12.5 mm"},
    "Laje": {"aco": "CA-25", "bitola_min": "6 mm", "bitola_max": "10 mm"},
    "Pilar": {"aco": "CA-50", "bitola_min": "10 mm", "bitola_max": "20 mm"},
    "Fundação - Estaca": {"aco": "CA-50", "bitola_min": "12 mm", "bitola_max": "20 mm"},
    "Fundação - Radie": {"aco": "CA-50", "bitola_min": "12 mm", "bitola_max": "20 mm"},
}

# Regras de consumo para Alvenaria e Fechamento (valores aproximados por m²)
REGRAS_ALVENARIA = {
    "Chapisco": {"cimento_por_m2": 0.5, "areia_por_m2": 0.012},
    "Emboço": {"cimento_por_m2": 1.2, "areia_por_m2": 0.03},
    "Reboco": {"cimento_por_m2": 1.0, "areia_por_m2": 0.025},
    "Tijolo (Bloco)": {"blocos_por_m2": 13, "argamassa_por_m2": 0.02},
}

# ---------------------------
# Funções de cálculo
# ---------------------------

def validar_dimensoes(largura: float, altura: float, comprimento: float) -> None:
    if largura <= 0 or altura <= 0 or comprimento <= 0:
        raise ValueError("Todas as dimensões devem ser maiores que zero.")

def calcular_volume(largura: float, altura: float, comprimento: float) -> float:
    return largura * altura * comprimento

def calcular_volume_estaca(diametro: float, profundidade: float) -> float:
    if diametro <= 0 or profundidade <= 0:
        raise ValueError("Diâmetro e profundidade devem ser maiores que zero.")
    raio = diametro / 2
    volume = math.pi * (raio ** 2) * profundidade
    return round(volume, 3)

def calcular_materiais(tipo: str, volume: float) -> dict:
    config = REGRAS_FCK[tipo]
    volume_total = volume * 1.05
    cimento = math.ceil(volume_total * config["cimento_por_m3"])
    areia = round(volume_total * config["areia_por_m3"], 2)
    brita = round(volume_total * config["brita_por_m3"], 2)
    return {
        "tipo": tipo,
        "fck": config["fck"],
        "volume_total": round(volume_total, 2),
        "cimento": cimento,
        "areia": areia,
        "brita": brita,
        "tipo_brita": config.get("tipo_brita", "Brita 1")
    }

def recomendar_aco(tipo: str, volume: float) -> dict:
    regra = REGRAS_ACO[tipo]
    bitola = regra["bitola_min"] if volume <= 1.0 else regra["bitola_max"]
    return {"aco": regra["aco"], "bitola": bitola}

def calcular_alvenaria(tipo: str, area: float) -> dict:
    config = REGRAS_ALVENARIA[tipo]
    if tipo == "Tijolo (Bloco)":
        blocos = math.ceil(area * config["blocos_por_m2"])
        argamassa = round(area * config["argamassa_por_m2"], 2)
        return {"tipo": tipo, "area": area, "blocos": blocos, "argamassa_m3": argamassa}
    else:
        cimento = round(area * config["cimento_por_m2"], 2)
        areia = round(area * config["areia_por_m2"], 3)
        return {"tipo": tipo, "area": area, "cimento_kg": cimento, "areia_m3": areia}