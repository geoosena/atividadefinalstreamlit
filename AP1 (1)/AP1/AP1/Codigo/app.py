import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(layout="wide", page_title="Shein Insights: Preços & Descontos", page_icon="🛍️")

# Estilo customizado: fundo rosa claro, texto preto, botões preto com rosa
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFC0CB;  /* rosa claro */
        color: black;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: black;
    }

    .stButton > button {
        background-color: black;
        color: #FFC0CB;
        border: none;
    }
    .stButton > button:hover {
        background-color: #333333;
        color: #ff99bb;
    }

    .stTextInput>div>input, .stSlider>div>input {
        border: 1px solid black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Shein Insights: Preços & Descontos")
st.markdown("Aplicação interativa para explorar preços e descontos de produtos da Shein.")

# Carregar dados
caminho_dados = 'AP1 (1)/AP1/AP1/Codigo/dados_shein.csv'
try:
    df = pd.read_csv(caminho_dados, sep=';')
    st.success("Dados carregados com sucesso")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Padronizar nomes das colunas
df.columns = df.columns.str.lower().str.strip()

# Verificar coluna de desconto correta
if 'desconto' in df.columns:
    col_desconto = 'desconto'
elif 'descontos' in df.columns:
    col_desconto = 'descontos'
else:
    st.error("Coluna de desconto não encontrada no arquivo CSV.")
    st.stop()

# Limpar e converter preço
df['preco2'] = df['preco2'].astype(str).str.replace('R\$', '', regex=True).str.replace(',', '.').astype(float)

# Limpar e converter desconto
df[col_desconto] = df[col_desconto].fillna('0').astype(str)
df[col_desconto] = df[col_desconto].str.replace('R\$', '', regex=True)
df[col_desconto] = df[col_desconto].str.replace('%', '', regex=True)
df[col_desconto] = df[col_desconto].str.replace('-', '0')
df[col_desconto] = df[col_desconto].str.replace(',', '.')
df[col_desconto] = pd.to_numeric(df[col_desconto], errors='coerce').fillna(0)

# Calcular desconto percentual (se desconto for em valor monetário)
df['desconto_percentual'] = (df[col_desconto] / (df['preco2'] + df[col_desconto])) * 100

# Slider de faixa de preço
preco_min, preco_max = float(df['preco2'].min()), float(df['preco2'].max())
preco_range = st.slider("Filtrar por faixa de preço (R$)", min_value=preco_min, max_value=preco_max, value=(preco_min, preco_max))

# Filtrar dados conforme faixa de preço selecionada
df_filtrado = df[(df['preco2'] >= preco_range[0]) & (df['preco2'] <= preco_range[1])]

# Criar faixa de preço categórica para boxplot
labels = [f"{round(interval.left,2)} - {round(interval.right,2)}" for interval in pd.cut(df_filtrado['preco2'], bins=5).cat.categories]
df_filtrado['faixa_preco'] = pd.cut(df_filtrado['preco2'], bins=5, labels=labels)

# Mostrar resumo estatístico
st.subheader("Resumo Estatístico dos Dados Filtrados")
st.write(df_filtrado[['preco2', col_desconto, 'desconto_percentual']].describe().round(2))

# Gráficos univariados
st.subheader("Gráficos Univariados")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Histograma de Preços**")
    fig1, ax1 = plt.subplots()
    sns.histplot(df_filtrado['preco2'], bins=20, ax=ax1, color='black')
    st.pyplot(fig1)

with col2:
    st.markdown("**Boxplot de Preços**")
    fig2, ax2 = plt.subplots()
    sns.boxplot(x=df_filtrado['preco2'], ax=ax2, color='pink')
    st.pyplot(fig2)

# Gráficos bivariados
st.subheader("Gráficos Bivariados")
col3, col4 = st.columns(2)

with col3:
    st.markdown("**Scatter Plot: Preço vs Desconto (%)**")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=df_filtrado, x='preco2', y='desconto_percentual', ax=ax3, color='black')
    ax3.set_ylabel("Desconto (%)")
    st.pyplot(fig3)

with col4:
    st.markdown("**Boxplot: Desconto por Faixa de Preço**")
    fig4, ax4 = plt.subplots(figsize=(8,5))
    sns.boxplot(data=df_filtrado, x='faixa_preco', y='desconto_percentual', ax=ax4, palette="pink")
    plt.xticks(rotation=45)
    ax4.set_xlabel("Faixa de Preço (R$)")
    ax4.set_ylabel("Desconto (%)")
    st.pyplot(fig4)
