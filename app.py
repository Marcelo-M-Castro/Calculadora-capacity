# app.py
import os
import io
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import google.generativeai as genai

# ==============================
# Configurações iniciais
# ==============================
st.set_page_config(page_title="Calculadora de Capacity", layout="wide")
st.title("📈 Calculadora de Capacity com Análise de Entrantes + Q&A")

st.markdown("""
Este app permite:
- Upload de duas planilhas: **Entrantes** e **TMA**
- Cálculos de média geral, pico e vale
- Gráficos interativos e exportação para Excel
- Perguntas e respostas em linguagem natural usando Gemini API
""")

# Configuração da API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ==============================
# Uploads
# ==============================
st.header("📁 Upload de Planilhas")

col1, col2 = st.columns(2)
with col1:
    file_entrantes = st.file_uploader("Envie a planilha de Entrantes", type="xlsx")
with col2:
    file_tma = st.file_uploader("Envie a planilha de TMA", type="xlsx")

if file_entrantes and file_tma:
    df_inicial = pd.read_excel(file_entrantes)
    df_TMA = pd.read_excel(file_tma)

    st.success("Arquivos carregados com sucesso!")

    # ==============================
    # Pré-processamento Entrantes
    # ==============================
    df_inicial['Date'] = pd.to_datetime(df_inicial['Date']).dt.date
    df_entrantes = df_inicial.pivot_table(
        index='Hour',
        columns='Date',
        values='Entrantes',
        aggfunc='sum',
        fill_value=0
    )

    stacked = df_entrantes.stack().reset_index(name='Entrantes')
    top5 = stacked.groupby('Hour')['Entrantes'].nlargest(5).groupby('Hour').mean().reset_index(name='Media_pico')
    df_entrantes = df_entrantes.merge(top5, left_index=True, right_on='Hour').set_index('Hour')

    colunas_para_media = [col for col in df_entrantes.columns if col not in ['Media_pico']]
    stacked = df_entrantes[colunas_para_media].stack().reset_index(name='Entrantes')
    media_vale = (
        stacked.groupby('Hour')['Entrantes']
        .apply(lambda x: x.sort_values(ascending=False).iloc[5:])
        .groupby('Hour').mean().reset_index(name='madia_vale')
    )
    df_entrantes = df_entrantes.merge(media_vale, left_index=True, right_on='Hour').set_index('Hour')

    cols_to_average = [col for col in df_entrantes.columns if col not in ['Media_pico', 'madia_vale']]
    df_entrantes['media_geral'] = df_entrantes[cols_to_average].mean(axis=1).astype(int)

    cols_to_sum = [col for col in df_entrantes.columns if col not in ['Media_pico', 'madia_vale', 'media_geral']]
    coluna_somas = df_entrantes[cols_to_sum].sum()
    top_5_dias = coluna_somas.sort_values(ascending=False).head(5)

    # ==============================
    # Pré-processamento TMA
    # ==============================
    def parse_minutes_seconds(time_str):
        if isinstance(time_str, str):
            try:
                minutes, seconds = map(int, time_str.split(':'))
                return pd.Timedelta(minutes=minutes, seconds=seconds)
            except ValueError:
                return pd.NaT
        return pd.NaT

    df_TMA['Average Talk Time'] = df_TMA['Average Talk Time'].apply(parse_minutes_seconds)
    df_TMA['Average Talk Time (seconds)'] = df_TMA['Average Talk Time'].apply(
        lambda x: x.total_seconds() if pd.notnull(x) else None
    )
    df_TMA['Average Talk Time (seconds)'] = df_TMA['Average Talk Time (seconds)'].fillna(0).astype(int)

    # Merge
    df_entrantes = df_entrantes.merge(
        df_TMA[['Hour', 'Average Talk Time (seconds)']],
        left_index=True,
        right_on='Hour'
    ).set_index('Hour')

    # ==============================
    # Parâmetros de cálculo
    # ==============================
    st.header("⚙️ Parâmetros de Cálculo")
    quantidade_slots = st.number_input("Quantidade de Slots", min_value=1, value=10)
    pausa_percent = st.number_input("Tempo de Pausa (%)", min_value=0.0, value=15.0)
    absenteismo_percent = st.number_input("Absenteísmo (%)", min_value=0.0, value=10.0)

    pausa = pausa_percent / 100
    absenteismo = absenteismo_percent / 100
    ajuste = (1 + pausa) * (1 + absenteismo)

    df_entrantes['Qtd_Slots'] = quantidade_slots
    df_entrantes['Capacity_Calculado'] = (
        df_entrantes['media_geral'] * df_entrantes['Average Talk Time (seconds)'] * ajuste
    ) / 3600 / quantidade_slots
    df_entrantes['Capacity_Calculado_pico'] = np.ceil(
        (df_entrantes['Media_pico'] * df_entrantes['Average Talk Time (seconds)'] * ajuste) / 3600 / quantidade_slots
    ).astype(int)
    df_entrantes['Capacity_Calculado_vale'] = np.ceil(
        (df_entrantes['madia_vale'] * df_entrantes['Average Talk Time (seconds)'] * ajuste) / 3600 / quantidade_slots
    ).astype(int)
    df_entrantes['Capacity_Calculado'] = df_entrantes['Capacity_Calculado'].astype(int)

    # ==============================
    # Resultados
    # ==============================
    st.header("📊 Resultados e Tabela Final")
    st.dataframe(df_entrantes)

    # Exportação
    to_excel = io.BytesIO()
    df_entrantes.to_excel(to_excel, index=True)
    st.download_button("📥 Baixar resultado em Excel", data=to_excel.getvalue(), file_name="df_entrantes.xlsx")

    # 📈 Linha de capacidade
    st.subheader("📈 Capacity calculado por hora")
    fig_cap, ax = plt.subplots()
    df_entrantes[['Capacity_Calculado', 'Capacity_Calculado_pico', 'Capacity_Calculado_vale']].plot(ax=ax)
    ax.set_title("Capacidade calculada por hora")
    ax.set_ylabel("Nº de Agentes")
    ax.set_xlabel("Hora")
    st.pyplot(fig_cap)

    # 📊 Entrantes por dia (barras)
    st.subheader("📊 Volume total de entrantes por dia")
    entrantes_por_dia = df_entrantes[cols_to_sum].sum().sort_index()
    fig_dia, ax = plt.subplots(figsize=(10, 4))
    entrantes_por_dia.plot(kind='bar', ax=ax)
    ax.set_title("Total de entrantes por dia")
    ax.set_ylabel("Quantidade")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig_dia)

    # 🔥 Heatmap hora x dia
    st.subheader("🔥 Heatmap de Entrantes (Hora x Dia)")
    heat_data = df_entrantes[cols_to_sum]
    fig_heat, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(heat_data, cmap="Blues", annot=False, ax=ax)
    ax.set_title("Entrantes por Hora x Dia")
    st.pyplot(fig_heat)

# ==============================
# Perguntas e Respostas (Gemini) baseado em resumo da Tabela Final
# ==============================
st.header("💬 Pergunte sobre os dados (Resumo Estatístico da Tabela Final)")

user_question = st.text_area("Digite sua pergunta:", placeholder="Ex: Qual foi a hora com maior capacity calculado?")

if st.button("Responder"):
    if user_question.strip():
        # Criar resumo da Tabela Final
        df_resumo = pd.DataFrame({
            "media_geral": [df_entrantes['media_geral'].mean()],
            "media_pico": [df_entrantes['Media_pico'].max()],
            "media_vale": [df_entrantes['madia_vale'].min()],
            "top_5_capacity_pico": [df_entrantes['Capacity_Calculado_pico'].nlargest(5).tolist()],
            "top_5_capacity_vale": [df_entrantes['Capacity_Calculado_vale'].nlargest(5).tolist()],
            "top_5_horas_capacity": [df_entrantes['Capacity_Calculado'].nlargest(5).index.tolist()]
        })

        data_sample = df_resumo.to_dict(orient="records")

        prompt = f"""
        Você é um analista de dados de contact center.
        Use os dados do resumo estatístico abaixo para responder à pergunta do usuário de forma clara, objetiva e em português.

        Resumo Estatístico (JSON): {json.dumps(data_sample, default=str)}
        Pergunta: {user_question}
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            st.success(response.text)
        except Exception as e:
            st.error(f"Erro ao chamar a API Gemini: {e}")
