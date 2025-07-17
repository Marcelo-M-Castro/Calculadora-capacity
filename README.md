# 📈 Calculadora de Capacity com Análise de Entrantes

Este é um aplicativo interativo desenvolvido com **Streamlit** para auxiliar na análise de **capacidade operacional** com base em dados de **entrantes** e **tempo médio de atendimento (TMA)**. Ideal para times de atendimento, planejamento ou operações que precisam dimensionar equipes com mais precisão.

---

## 🚀 Funcionalidades

- Upload de duas planilhas: **Entrantes** e **TMA**
- Cálculo automático de:
  - Média geral de entrantes por hora
  - Médias de pico e vale
  - Capacidade necessária por hora
- Visualizações:
  - Tabela dinâmica com métricas calculadas
  - Gráficos de linha, barra e heatmap
- Exportação dos resultados para Excel

---

## 📂 Formato esperado das planilhas

### 🟢 Entrantes

A planilha de entrantes deve conter as seguintes colunas:

| Coluna   | Descrição                                   |
|----------|---------------------------------------------|
| `Date`   | Data no formato `YYYY-MM-DD`                |
| `Hour`   | Hora do dia (ex: `8`, `15`, `22`)           |
| `Entrantes` | Quantidade de entradas/chamadas por hora |

### 🔵 TMA

A planilha de TMA (Tempo Médio de Atendimento) deve conter:

| Coluna                | Descrição                                       |
|------------------------|-------------------------------------------------|
| `Hour`                | Hora correspondente ao atendimento              |
| `Average Talk Time`   | Tempo médio no formato `MM:SS` (minutos:segundos) |

---

## 🧮 Parâmetros ajustáveis

Durante a execução do app, é possível configurar os seguintes parâmetros:

- **Quantidade de slots**: número de agentes disponíveis
- **Pausa (%)**: percentual de tempo destinado a pausas
- **Absenteísmo (%)**: percentual estimado de ausências

Esses valores são usados no cálculo da **capacidade real ajustada**, considerando indisponibilidades.

---

## 📊 Visualizações

O aplicativo apresenta as seguintes visualizações interativas:

- **📋 Tabela final**: com dados de entrada, TMA e capacidade calculada
- **📈 Gráfico de linha**: capacidade geral, pico e vale por hora
- **📊 Gráfico de barras**: volume total de entrantes por dia
- **🔥 Heatmap (hora x dia)**: intensidade de entrantes ao longo da semana

---

## 💾 Exportação

Após a análise, é possível **baixar os resultados em Excel (`.xlsx`)** com todos os dados processados diretamente pela interface do app.


https://calculadora-capacity.streamlit.app/

