import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="Calculadora de Capacity", layout="wide")
st.title("📈 Calculadora de Capacity com Análise de Entrantes")

st.markdown("""
Este app permite:
- Upload de duas planilhas: **Entrantes** e **TMA**
- Cálculos de média geral, pico e vale
- Gráficos interativos e exportação para Excel
""")

# Uploads
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

    # Pré-processamento
    df_inicial['Date'] = pd.to_datetime(df_inicial['Date']).dt.date
    df_entrantes = df_inicial.pivot_table(index='Hour', columns='Date', values='Entrantes', aggfunc='sum', fill_value=0)

    stacked = df_entrantes.stack().reset_index(name='Entrantes')
    top5 = stacked.groupby('Hour')['Entrantes'].nlargest(5).groupby('Hour').mean().reset_index(name='Media_pico')
    df_entrantes = df_entrantes.merge(top5, left_index=True, right_on='Hour').set_index('Hour')

    colunas_para_media = [col for col in df_entrantes.columns if col not in ['Media_pico']]
    stacked = df_entrantes[colunas_para_media].stack().reset_index(name='Entrantes')
    media_vale = (stacked.groupby('Hour')['Entrantes']
                  .apply(lambda x: x.sort_values(ascending=False).iloc[5:])
                  .groupby('Hour').mean().reset_index(name='madia_vale'))
    df_entrantes = df_entrantes.merge(media_vale, left_index=True, right_on='Hour').set_index('Hour')

    cols_to_average = [col for col in df_entrantes.columns if col not in ['Media_pico', 'madia_vale']]
    df_entrantes['media_geral'] = df_entrantes[cols_to_average].mean(axis=1).astype(int)

    cols_to_sum = [col for col in df_entrantes.columns if col not in ['Media_pico', 'madia_vale', 'media_geral']]
    coluna_somas = df_entrantes[cols_to_sum].sum()
    top_5_dias = coluna_somas.sort_values(ascending=False).head(5)

    # TMA
    def parse_minutes_seconds(time_str):
        if isinstance(time_str, str):
            try:
                minutes, seconds = map(int, time_str.split(':'))
                return pd.Timedelta(minutes=minutes, seconds=seconds)
            except ValueError:
                return pd.NaT
        return pd.NaT

    df_TMA['Average Talk Time'] = df_TMA['Average Talk Time'].apply(parse_minutes_seconds)
    df_TMA['Average Talk Time (seconds)'] = df_TMA['Average Talk Time'].apply(lambda x: x.total_seconds() if pd.notnull(x) else None)
    df_TMA['Average Talk Time (seconds)'] = df_TMA['Average Talk Time (seconds)'].fillna(0).astype(int)

    # Merge
    df_entrantes = df_entrantes.merge(
        df_TMA[['Hour', 'Average Talk Time (seconds)']],
        left_index=True,
        right_on='Hour'
    ).set_index('Hour')

    # Inputs
    st.header("⚙️ Parâmetros de Cálculo")
    quantidade_slots = st.number_input("Quantidade de Slots", min_value=1, value=10)
    pausa_percent = st.number_input("Tempo de Pausa (%)", min_value=0.0, value=15.0)
    absenteismo_percent = st.number_input("Absenteísmo (%)", min_value=0.0, value=10.0)

    pausa = pausa_percent / 100
    absenteismo = absenteismo_percent / 100
    ajuste = (1 + pausa) * (1 + absenteismo)

    df_entrantes['Qtd_Slots'] = quantidade_slots
    df_entrantes['Capacity_Calculado'] = (df_entrantes['media_geral'] * df_entrantes['Average Talk Time (seconds)'] * ajuste) / 3600 / quantidade_slots
    df_entrantes['Capacity_Calculado_pico'] = np.ceil((df_entrantes['Media_pico'] * df_entrantes['Average Talk Time (seconds)'] * ajuste) / 3600 / quantidade_slots).astype(int)
    df_entrantes['Capacity_Calculado_vale'] = np.ceil((df_entrantes['madia_vale'] * df_entrantes['Average Talk Time (seconds)'] * ajuste) / 3600 / quantidade_slots).astype(int)
    df_entrantes['Capacity_Calculado'] = df_entrantes['Capacity_Calculado'].astype(int)

    # Resultado
    st.header("📊 Resultados e Tabela Final")
    st.dataframe(df
