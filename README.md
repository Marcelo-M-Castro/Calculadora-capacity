📈 Calculadora de Capacity com Análise de Entrantes
Este é um aplicativo interativo desenvolvido com Streamlit para auxiliar na análise de capacidade operacional com base em dados de entrantes e tempo médio de atendimento (TMA). Ideal para times de atendimento, planejamento ou operações que precisam dimensionar equipes com mais precisão.

🚀 Funcionalidades
Upload de duas planilhas: Entrantes e TMA

Cálculo automático de:

Média geral de entrantes por hora

Médias de pico e vale

Capacidade necessária por hora

Visualizações:

Tabela dinâmica com métricas calculadas

Gráficos de linha, barra e heatmap

Exportação dos resultados para Excel

📂 Formato esperado das planilhas
🟢 Entrantes
Colunas obrigatórias:

Date: data no formato YYYY-MM-DD

Hour: hora do dia (inteiro ou string no formato HH)

Entrantes: quantidade de chamadas/entradas por hora

🔵 TMA
Colunas obrigatórias:

Hour: hora correspondente à média

Average Talk Time: tempo médio de atendimento no formato MM:SS

🧮 Parâmetros ajustáveis
Durante a execução, o usuário pode ajustar:

Quantidade de slots (agentes disponíveis)

Percentual de pausa

Percentual de absenteísmo

Esses parâmetros são usados no cálculo da capacidade necessária por hora.

📊 Visualizações
Tabela final com todos os indicadores

Gráfico de capacidade calculada (geral, pico e vale)

Gráfico de barras com total de entrantes por dia

Heatmap visualizando o volume de entrantes por hora x dia

💾 Exportação
É possível baixar o resultado da análise em um arquivo .xlsx diretamente pelo app.
