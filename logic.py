import pandas as pd

# Datos cargados desde el código proporcionado
ranking_dict = {
    "ATL": {"offense_rank": 5, "defense_rank": 18},
    "ORL": {"offense_rank": 22, "defense_rank": 4}
}

stats_dict = {
    "ATL": {"ppg": 113.5, "oppg": 117.2, "efg": 0.52},
    "ORL": {"ppg": 107.9, "oppg": 104.3, "efg": 0.50}
}

pace_dict = {
    "ATL": 101.8,
    "ORL": 98.4
}

tendencias_dict = {
    "ATL": ['O','U','O','O','P'],
    "ORL": ['U','U','U','P','O']
}

equipos_forma = {
    "ATL": {"dif_5": 2.1, "dif_10": 1.5, "dif_15": 1.0, "dif_20": 0.3, "dif_25": -0.2, "dif_30": -1.0,
            "racha_su": 3, "h2h_diff": 2.0, "prom_of": 111.2, "prom_def": 108.3, "ranking_pos": 8},
    "ORL": {"dif_5": -1.2, "dif_10": 0.0, "dif_15": 0.5, "dif_20": 1.2, "dif_25": 1.8, "dif_30": 2.1,
            "racha_su": 4, "h2h_diff": -1.5, "prom_of": 106.1, "prom_def": 102.7, "ranking_pos": 12}
}

momio_decimal = {
    "ATL": 1.72,
    "ORL": 2.27
}

prob_apertura = {
    "ATL": 0.55,
    "ORL": 0.48
}

tickets_dinero = {
    "ATL": {"tickets": 76, "dinero": 61},
    "ORL": {"tickets": 24, "dinero": 39}
}

contexto_externo = {
    "ATL": {"es_local": 1, "fatiga": 0, "lesiones_clave": 0, "motivacion": 1},
    "ORL": {"es_local": 0, "fatiga": 1, "lesiones_clave": 1, "motivacion": 0}
}

movimientos = {
    "ATL": {"ml_apertura": 1.65, "ml_actual": 1.52, "spread_apertura": -4.5, "spread_actual": -4.5,
            "tickets_ml": 76, "dinero_ml": 61, "tickets_ha": 88, "dinero_ha": 73,
            "forma_negativa": True, "ha_momio": -155},
    "ORL": {"ml_apertura": 2.45, "ml_actual": 2.27, "spread_apertura": 4.5, "spread_actual": 4.5,
            "tickets_ml": 24, "dinero_ml": 39, "tickets_ha": 12, "dinero_ha": 27,
            "forma_negativa": False, "ha_momio": 130}
}

# Funciones del modelo
def normalizar_rankings_equipos(d):
    df = pd.DataFrame(d).T
    return df.apply(lambda x: (x.max() - x) / (x.max() - x.min()), axis=0).mean(axis=1).round(3).to_dict()

def calcular_puntaje_produccion_eficiencia(d):
    df = pd.DataFrame(d).T
    return df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=0).mean(axis=1).round(3).to_dict()

def calcular_puntaje_pace(d):
    s = pd.Series(d)
    return ((s - s.min()) / (s.max() - s.min())).round(3).to_dict()

def puntaje_tendencia_ou(d):
    return {k: round((sum([1 if x == 'O' else -1 if x == 'U' else 0 for x in v]) / len(v) + 1) / 2, 3)
            for k, v in d.items()}

def calcular_ritmo_estilo(ranking, stats, pace, tendencia):
    r1 = normalizar_rankings_equipos(ranking)
    r2 = calcular_puntaje_produccion_eficiencia(stats)
    r3 = calcular_puntaje_pace(pace)
    r4 = puntaje_tendencia_ou(tendencia)
    return {team: round(0.4*r1[team] + 0.3*r2[team] + 0.2*r3[team] + 0.1*r4[team], 3) for team in r1}

def calcular_forma_score(equipos):
    data = {}
    for team, val in equipos.items():
        dif = (val["dif_5"]*0.25 + val["dif_10"]*0.2 + val["dif_15"]*0.15 +
               val["dif_20"]*0.15 + val["dif_25"]*0.15 + val["dif_30"]*0.1)
        su = val["racha_su"] / 5
        h2h = (val["h2h_diff"] + 20) / 40
        net = (val["prom_of"] - val["prom_def"] + 30) / 60
        pos = (30 - val["ranking_pos"]) / 30
        data[team] = round(0.35*dif + 0.15*su + 0.2*h2h + 0.2*net + 0.1*pos, 3)
    return data

def calcular_probabilidad_implicita(momios):
    return {team: round(1 / m, 4) for team, m in momios.items()}

def calcular_valor_esperado(prob_modelo, prob_implicita):
    return {team: round(prob_modelo[team] - prob_implicita[team], 4) for team in prob_modelo}

def etiquetar_valor(ve):
    if ve > 0.05:
        return "ALTO"
    elif ve > 0.02:
        return "MODERADO"
    elif ve > -0.01:
        return "JUSTO"
    return "DESCARTAR"

def calcular_sensibilidad(prob_apertura, prob_actual):
    resultado = {}
    for team in prob_apertura:
        variacion = abs(prob_actual[team] - prob_apertura[team])
        score = 0.8 * 0.15 if variacion >= 0.75 else (variacion / 0.75) * 0.15
        resultado[team] = round(score, 4)
    return resultado

def evaluar_tendencia_publica(picks):
    señales = {}
    for equipo, val in picks.items():
        t, d = val["tickets"], val["dinero"]
        if t >= 70 and d <= 50:
            señales[equipo] = 0.15
        elif d >= 70 and t <= 50:
            señales[equipo] = 0.15
        elif t >= 65 and d >= 65:
            señales[equipo] = 0.10
        elif abs(t - d) <= 5:
            señales[equipo] = 0.05
        else:
            señales[equipo] = 0.07
    return señales

def evaluar_variables_externas(contexto):
    resultado = {}
    for equipo, val in contexto.items():
        local = 0.04 if val["es_local"] else 0.00
        fatiga = -0.03 if val["fatiga"] else 0.00
        lesiones = -0.02 if val["lesiones_clave"] else 0.00
        motivacion = 0.03 if val["motivacion"] else 0.00
        resultado[equipo] = round(0.05 + local + fatiga + lesiones + motivacion, 3)
    return resultado

def detectar_ilusiones_mercado(mov):
    ilusiones = {}
    for team, d in mov.items():
        etiquetas = []
        if d['ha_momio'] <= -150 and d['forma_negativa'] and d['ml_actual'] < d['ml_apertura']:
            etiquetas.append("ILUSIÓN DE PROTECCIÓN")
        if d['tickets_ml'] > 70 and d['dinero_ml'] < d['tickets_ml'] and not d['forma_negativa']:
            etiquetas.append("FALSA ILUSIÓN – FAVORITO CUMPLE")
        if d['ml_apertura'] - d['ml_actual'] > 0.10 and d['spread_apertura'] == d['spread_actual']:
            etiquetas.append("DESFASE ML vs SPREAD")
        if 1.01 <= d['ml_actual'] <= 1.49:
            etiquetas.append("SOBREAJUSTADO – DESCARTADO")
        ilusiones[team] = etiquetas
    return ilusiones

def ensamblar_modelo_completo(inputs):
    output = {}
    for team in inputs['prob_modelo']:
        ve = round(inputs['prob_modelo'][team] - inputs['prob_implicita'][team], 4)
        etiqueta = etiquetar_valor(ve)
        total = round(
            0.20 * inputs['ritmo_estilo'][team] +
            0.20 * inputs['forma'][team] +
            0.20 * inputs['prob_modelo'][team] +
            inputs['sensibilidad'][team] +
            inputs['publico'][team] +
            inputs['externas'][team], 3)
        output[team] = {
            "Puntaje total": total,
            "Probabilidad modelo": inputs['prob_modelo'][team],
            "Probabilidad implícita": inputs['prob_implicita'][team],
            "Valor esperado": ve,
            "Etiqueta valor": etiqueta,
            "Ilusiones detectadas": inputs['ilusiones'].get(team, [])
        }
    return output

# Ejecutar modelo con datos cargados
ritmo_estilo = calcular_ritmo_estilo(ranking_dict, stats_dict, pace_dict, tendencias_dict)
forma = calcular_forma_score(equipos_forma)
prob_implicita = calcular_probabilidad_implicita(momio_decimal)
prob_modelo = {team: round(0.5 + 0.25*(forma[team] - 0.5), 4) for team in forma}  # proxy simplificado
valor_esperado = calcular_valor_esperado(prob_modelo, prob_implicita)
sensibilidad = calcular_sensibilidad(prob_apertura, prob_modelo)
publico = evaluar_tendencia_publica(tickets_dinero)
externas = evaluar_variables_externas(contexto_externo)
ilusiones = detectar_ilusiones_mercado(movimientos)

# Ensamblar
resultados = ensamblar_modelo_completo({
    'ritmo_estilo': ritmo_estilo,
    'forma': forma,
    'prob_modelo': prob_modelo,
    'prob_implicita': prob_implicita,
    'sensibilidad': sensibilidad,
    'publico': publico,
    'externas': externas,
    'ilusiones': ilusiones
})

import ace_tools as tools; tools.display_dataframe_to_user(name="Resultados ATL vs ORL", dataframe=pd.DataFrame(resultados).T)
