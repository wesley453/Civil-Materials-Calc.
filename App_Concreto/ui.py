import streamlit as st
import datetime
import requests
import pandas as pd
import os
from fpdf import FPDF
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

# ---------------------------
# Histórico de cálculos
# ---------------------------
historico_calculos = []

def salvar_historico(tipo: str, resultado: dict):
    registro = {"tipo": tipo, "resultado": resultado}
    historico_calculos.append(registro)

def mostrar_historico():
    if historico_calculos:
        df = pd.DataFrame([
            {"Elemento": r["tipo"], **r["resultado"]}
            for r in historico_calculos
        ])
        st.dataframe(df)

        # Exportar CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar histórico em CSV",
            data=csv,
            file_name="historico_calculos.csv",
            mime="text/csv",
        )

        # Exportar Excel
        if st.button("📊 Exportar para Excel", key="export_excel"):
            excel_file = "relatorio_calculos.xlsx"
            df.to_excel(excel_file, index=False)
            st.success(f"Relatório gerado: {excel_file}")

        # Exportar PDF
        if st.button("📄 Exportar para PDF", key="export_pdf"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, "Relatório de Cálculos", ln=True, align="C")
            for r in historico_calculos:
                pdf.cell(200, 10, f"Elemento: {r['tipo']}", ln=True)
                for k, v in r["resultado"].items():
                    pdf.cell(200, 10, f"{k}: {v}", ln=True)
                pdf.ln(5)
            pdf_file = "relatorio_calculos.pdf"
            pdf.output(pdf_file)
            st.success(f"Relatório gerado: {pdf_file}")
    else:
        st.info("Nenhum cálculo realizado ainda.")

# ---------------------------
# Simulação de custos
# ---------------------------
PRECOS_MATERIAIS = {
    "cimento": 35.0,
    "areia": 120.0,
    "brita": 150.0,
    "aco": 8.0,
    "bloco": 3.5,
    "argamassa": 250.0
}

def calcular_custos(resultado):
    custo_total = 0
    detalhes = {}

    # Cimento em sacos
    if "cimento" in resultado:
        custo = resultado["cimento"] * PRECOS_MATERIAIS["cimento"]
        detalhes["Cimento"] = custo
        custo_total += custo

    # Cimento em kg (para alvenaria)
    if "cimento_kg" in resultado:
        sacos = resultado["cimento_kg"] / 50  # converte kg para sacos
        custo = sacos * PRECOS_MATERIAIS["cimento"]
        detalhes["Cimento"] = custo
        custo_total += custo

    if "areia" in resultado:
        custo = resultado["areia"] * PRECOS_MATERIAIS["areia"]
        detalhes["Areia"] = custo
        custo_total += custo

    if "areia_m3" in resultado:
        custo = resultado["areia_m3"] * PRECOS_MATERIAIS["areia"]
        detalhes["Areia"] = custo
        custo_total += custo

    if "brita" in resultado:
        custo = resultado["brita"] * PRECOS_MATERIAIS["brita"]
        detalhes["Brita"] = custo
        custo_total += custo

    if "blocos" in resultado:
        custo = resultado["blocos"] * PRECOS_MATERIAIS["bloco"]
        detalhes["Blocos"] = custo
        custo_total += custo

    if "argamassa_m3" in resultado:
        custo = resultado["argamassa_m3"] * PRECOS_MATERIAIS["argamassa"]
        detalhes["Argamassa"] = custo
        custo_total += custo

    return {"detalhes": detalhes, "custo_total": round(custo_total, 2)}

# ---------------------------
# Interface principal
# ---------------------------
def main():
    st.title("🏗️ Calculadora para Construção Civil")
    st.caption("Ferramenta prática para estimar materiais, aço e custos")

    aba = st.tabs([
        "Infraestrutura e Estrutura",
        "Alvenaria e Fechamento",
        "Tabela de Referência",
        "Condições Ambientais",
        "Histórico"
    ])

    # Aba 1: Infraestrutura e Estrutura
    with aba[0]:
        st.subheader("Selecione o elemento de infraestrutura ou estrutura")
        tipo = st.selectbox("Elemento", ["Estaca", "Radie", "Viga Baldrame", "Pilar", "Laje"])

        if tipo == "Estaca":
            diametro_str = st.text_input("Diâmetro (m)", "0.00")
            profundidade_str = st.text_input("Profundidade (m)", "0.00")
            if st.button("Calcular Estaca", key="calcular_estaca"):
                try:
                    diametro = float(diametro_str)
                    profundidade = float(profundidade_str)
                    validar_dimensoes(diametro, profundidade, 1)
                    vol_estaca = calcular_volume_estaca(diametro, profundidade)
                    materiais = calcular_materiais("Fundação - Estaca", vol_estaca)
                    recomendacao = recomendar_aco("Fundação - Estaca", vol_estaca)
                    salvar_historico("Fundação - Estaca", materiais)

                    st.success(f"""
                        📐 Volume total: {materiais['volume_total']} m³  
                        🏗️ Fck: {materiais['fck']} MPa  
                        🧱 Cimento: {materiais['cimento']} sacos  
                        🏖️ Areia: {materiais['areia']} m³  
                        🪨 Brita: {materiais['brita']} m³  
                        🪨 Tipo de Brita: {materiais['tipo_brita']}  
                        🔩 Aço recomendado: {recomendacao['aco']}  
                        📏 Bitola sugerida: {recomendacao['bitola']}
                    """)

                    custos = calcular_custos(materiais)
                    st.write("💰 Custos estimados:")
                    for material, valor in custos["detalhes"].items():
                        st.write(f"- {material}: R$ {valor:.2f}")
                    st.success(f"💵 Custo total estimado: R$ {custos['custo_total']:.2f}")
                except Exception as ex:
                    st.error(f"Erro: {ex}")
        else:
            largura_str = st.text_input("Largura (m)", "0.00")
            altura_str = st.text_input("Altura (m)", "0.00")
            comprimento_str = st.text_input("Comprimento (m)", "0.00")
            if st.button("Calcular", key="calcular_estrutura"):
                try:
                    largura = float(largura_str)
                    altura = float(altura_str)
                    comprimento = float(comprimento_str)
                    validar_dimensoes(largura, altura, comprimento)
                    vol = calcular_volume(largura, altura, comprimento)
                    materiais = calcular_materiais(tipo, vol)
                    recomendacao = recomendar_aco(tipo, vol)
                    salvar_historico(tipo, materiais)

                    st.success(f"""
                        📐 Volume total: {materiais['volume_total']} m³  
                        🏗️ Fck: {materiais['fck']} MPa  
                        🧱 Cimento: {materiais['cimento']} sacos  
                        🏖️ Areia: {materiais['areia']} m³  
                        🪨 Brita: {materiais['brita']} m³  
                        🪨 Tipo de Brita: {materiais['tipo_brita']}  
                        🔩 Aço recomendado: {recomendacao['aco']}  
                        📏 Bitola sugerida: {recomendacao['bitola']}
                    """)

                    custos = calcular_custos(materiais)
                    st.write("💰 Custos estimados:")
                    for material, valor in custos["detalhes"].items():
                        st.write(f"- {material}: R$ {valor:.2f}")
                    st.success(f"💵 Custo total estimado: R$ {custos['custo_total']:.2f}")
                except Exception as ex:
                    st.error(f"Erro: {ex}")
                    
                        # Aba 2: Alvenaria e Fechamento
    with aba[1]:
        st.subheader("Selecione o elemento de alvenaria ou fechamento")
        tipo_alv = st.selectbox("Elemento", list(REGRAS_ALVENARIA.keys()))
        area_str = st.text_input("Área (m²)", "0.00")

        if tipo_alv == "Chapisco":
            botao = st.button("Calcular", key="calcular_chapisco")
        else:
            botao = st.button("Calcular Alvenaria", key="calcular_alvenaria")

        if botao:
            try:
                area = float(area_str)
                if area <= 0:
                    raise ValueError("A área deve ser maior que zero.")
                resultado = calcular_alvenaria(tipo_alv, area)
                salvar_historico(tipo_alv, resultado)

                if tipo_alv == "Tijolo (Bloco)":
                    st.success(f"""
                        🧱 Tipo: {resultado['tipo']}  
                        📐 Área: {resultado['area']} m²  
                        🔢 Blocos necessários: {resultado['blocos']} unidades  
                        🪣 Argamassa: {resultado['argamassa_m3']} m³
                    """)
                else:
                    st.success(f"""
                        🧱 Tipo: {resultado['tipo']}  
                        📐 Área: {resultado['area']} m²  
                        🏗️ Cimento: {resultado['cimento_kg']} kg  
                        🏖️ Areia: {resultado['areia_m3']} m³
                    """)

                # Sempre exibir custos
                custos = calcular_custos(resultado)
                st.write("💰 Custos estimados:")
                for material, valor in custos["detalhes"].items():
                    st.write(f"- {material}: R$ {valor:.2f}")
                st.success(f"💵 Custo total estimado: R$ {custos['custo_total']:.2f}")
            except Exception as ex:
                st.error(f"Erro: {ex}")

    # Aba 3: Tabela de Referência
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

    # Aba 4: Condições Ambientais
    with aba[3]:
        st.subheader("🌦️ Condições Ambientais")
        agora = datetime.datetime.now()
        st.write(f"📅 Data: {agora.strftime('%d/%m/%Y')}")
        st.write(f"⏰ Hora: {agora.strftime('%H:%M:%S')}")

        try:
            api_key = os.getenv("OPENWEATHER_KEY")
            cidade = "Brasilia,BR"
            if api_key:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
                resposta = requests.get(url).json()
                if resposta.get("main"):
                    temperatura = resposta["main"]["temp"]
                    umidade = resposta["main"]["humidity"]
                    st.write(f"🌡️ Temperatura do ar: {temperatura} °C")
                    st.write(f"💧 Umidade do ar: {umidade}%")
                else:
                    st.warning("Não foi possível obter os dados climáticos.")
            else:
                st.error("Chave da API não configurada. Defina OPENWEATHER_KEY nas variáveis de ambiente.")
        except Exception as e:
            st.error(f"Erro ao acessar a API de clima: {e}")

    # Aba 5: Histórico
    with aba[4]:
        st.subheader("📜 Histórico de cálculos")
        mostrar_historico()

# Executa a aplicação
if __name__ == "__main__":
    main()