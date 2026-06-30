import streamlit as st
import datetime
import requests
from calculos import (
    calcular_volume,
    calcular_materiais,
    recomendar_aco,
    validar_dimensoes,
    calcular_volume_estaca,
    calcular_alvenaria,
    REGRAS_FCK,
    REGRAS_ACO,
    REGRAS_ALVENARIA
)

def main():
    st.title("🏗️ Calculadora para Construção Civil")
    st.caption("Ferramenta prática para estimar materiais e aço")

    aba = st.tabs(["Infraestrutura e Estrutura", "Alvenaria e Fechamento", "Tabela de Referência", "Condições Ambientais"])

    # ---------------------------
    # Aba 1: Infraestrutura e Estrutura
    # ---------------------------
    with aba[0]:
        st.subheader("Selecione o elemento de infraestrutura ou estrutura")
        tipo = st.selectbox("Elemento", ["Estaca", "Radie", "Viga Baldrame", "Pilar", "Laje"])

        if tipo == "Estaca":
            diametro_str = st.text_input("Diâmetro (m)", "0.00")
            profundidade_str = st.text_input("Profundidade (m)", "0.00")
            if st.button("Calcular Estaca"):
                try:
                    diametro = float(diametro_str)
                    profundidade = float(profundidade_str)
                    validar_dimensoes(diametro, profundidade, 1)
                    vol_estaca = calcular_volume_estaca(diametro, profundidade)
                    materiais = calcular_materiais("Fundação - Estaca", vol_estaca)
                    recomendacao = recomendar_aco("Fundação - Estaca", vol_estaca)
                    st.success(
                        f"""
                        📐 Volume total: {materiais['volume_total']} m³  
                        🏗️ Fck: {materiais['fck']} MPa  
                        🧱 Cimento: {materiais['cimento']} sacos  
                        🏖️ Areia: {materiais['areia']} m³  
                        🪨 Brita: {materiais['brita']} m³  
                        🪨 Tipo de Brita: {materiais['tipo_brita']}  
                        🔩 Aço recomendado: {recomendacao['aco']}  
                        📏 Bitola sugerida: {recomendacao['bitola']}
                        """
                    )
                except Exception as ex:
                    st.error(f"Erro: {ex}")
        else:
            largura_str = st.text_input("Largura (m)", "0.00")
            altura_str = st.text_input("Altura (m)", "0.00")
            comprimento_str = st.text_input("Comprimento (m)", "0.00")
            if st.button("Calcular"):
                try:
                    largura = float(largura_str)
                    altura = float(altura_str)
                    comprimento = float(comprimento_str)
                    validar_dimensoes(largura, altura, comprimento)
                    vol = calcular_volume(largura, altura, comprimento)
                    materiais = calcular_materiais(tipo, vol)
                    recomendacao = recomendar_aco(tipo, vol)
                    st.success(
                        f"""
                        📐 Volume total: {materiais['volume_total']} m³  
                        🏗️ Fck: {materiais['fck']} MPa  
                        🧱 Cimento: {materiais['cimento']} sacos  
                        🏖️ Areia: {materiais['areia']} m³  
                        🪨 Brita: {materiais['brita']} m³  
                        🪨 Tipo de Brita: {materiais['tipo_brita']}  
                        🔩 Aço recomendado: {recomendacao['aco']}  
                        📏 Bitola sugerida: {recomendacao['bitola']}
                        """
                    )
                except Exception as ex:
                    st.error(f"Erro: {ex}")

    # ---------------------------
    # Aba 2: Alvenaria e Fechamento
    # ---------------------------
    with aba[1]:
        st.subheader("Selecione o elemento de alvenaria ou fechamento")

        tipo_alv = st.selectbox("Elemento", list(REGRAS_ALVENARIA.keys()))
        area_str = st.text_input("Área (m²)", "0.00")

        if st.button("Calcular Alvenaria"):
            try:
                area = float(area_str)
                if area <= 0:
                    raise ValueError("A área deve ser maior que zero.")
                resultado = calcular_alvenaria(tipo_alv, area)

                if tipo_alv == "Tijolo (Bloco)":
                    st.success(
                        f"""
                        🧱 Tipo: {resultado['tipo']}  
                        📐 Área: {resultado['area']} m²  
                        🔢 Blocos necessários: {resultado['blocos']} unidades  
                        🪣 Argamassa: {resultado['argamassa_m3']} m³
                        """
                    )
                else:
                    st.success(
                        f"""
                        🧱 Tipo: {resultado['tipo']}  
                        📐 Área: {resultado['area']} m²  
                        🏗️ Cimento: {resultado['cimento_kg']} kg  
                        🏖️ Areia: {resultado['areia_m3']} m³
                        """
                    )
            except Exception as ex:
                st.error(f"Erro: {ex}")

    # ---------------------------
    # Aba 3: Tabela de Referência
    # ---------------------------
    with aba[2]:
        st.subheader("📊 Tabela de Referência")

        elementos = []
        fcks = []
        aco_recomendado = []
        bitolas = []

        for elemento in REGRAS_FCK.keys():
            elementos.append(elemento)
            fcks.append(REGRAS_FCK[elemento]["fck"])
            aco_recomendado.append(REGRAS_ACO[elemento]["aco"])
            bitolas.append(f"{REGRAS_ACO[elemento]['bitola_min']} – {REGRAS_ACO[elemento]['bitola_max']}")

        st.table({
            "Elemento": elementos,
            "Fck (MPa)": fcks,
            "Aço recomendado": aco_recomendado,
            "Bitola sugerida": bitolas
        })

    # ---------------------------
    # Aba 4: Condições Ambientais
    # ---------------------------
    with aba[3]:
        st.subheader("🌦️ Condições Ambientais")

        agora = datetime.datetime.now()
        st.write(f"📅 Data: {agora.strftime('%d/%m/%Y')}")
        st.write(f"⏰ Hora: {agora.strftime('%H:%M:%S')}")

        try:
            api_key = "0b016931acd15f3eaf4f497e5a60ae69"
            cidade = "Brasilia,BR"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
            resposta = requests.get(url).json()
            if resposta.get("main"):
                temperatura = resposta["main"]["temp"]
                umidade = resposta["main"]["humidity"]
                st.write(f"🌡️ Temperatura do ar: {temperatura} °C")
                st.write(f"💧 Umidade do ar: {umidade}%")
            else:
                st.warning(f"Não foi possível obter os dados climáticos. Resposta da API: {resposta}")
        except Exception as e:
            st.error(f"Erro ao acessar a API de clima: {e}")