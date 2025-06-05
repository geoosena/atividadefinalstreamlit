import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 🎨 Configuração da página
st.set_page_config(
    layout="wide", 
    page_title="Shein Insights: Preços & Descontos", 
    page_icon="🛍️"
)

# 🎨 Estilo CSS personalizado
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffc0cb;
        color: black;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton > button {
        background-color: black;
        color: #ffc0cb;
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

# 🚩 Título e descrição
st.title("Shein Insights: Preços & Descontos")
st.markdown("Aplicação interativa para explorar **preços, descontos e padrões** dos produtos da Shein.")

# 📥 Carregamento dos dados
caminho_dados = 'AP1 (1)/AP1/AP1/Codigo/dados_shein.csv'

try:
    df = pd.read_csv(caminho_dados, sep=';')
    st.success("Dados carregados com sucesso!")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# 🧹 Tratamento dos dados
df['preco2'] = df['preco2'].astype(str).str.replace('R\$', '', regex=True).str.replace(',', '.').astype(float)

df['desconto'] = df['desconto'].fillna('0').astype(str)
df['desconto'] = df['desconto'].str.replace('%', '', regex=True).str.replace('-', '0').str.strip()
df['desconto'] = pd.to_numeric(df['desconto'], errors='coerce').fillna(0)

# 🧠 Cálculo do percentual de desconto
df['desconto_percentual'] = (df['desconto'] / (df['preco2'] + df['desconto'])) * 100

# 🎯 Filtro de preço
preco_min, preco_max = float(df['preco2'].min()), float(df['preco2'].max())

preco_range = st.slider(
    "🔎 Filtrar por faixa de preço (R$):", 
    min_value=preco_min, 
    max_value=preco_max, 
    value=(preco_min, preco_max)
)

# 🔍 Aplicando filtro
df_filtrado = df[(df['preco2'] >= preco_range[0]) & (df['preco2'] <= preco_range[1])]

# 📊 Criando faixas de preço
bins = pd.cut(df_filtrado['preco2'], bins=5)
labels = [f"De R${round(i.left, 2)} até R${round(i.right, 2)}" for i in bins.categories]
df_filtrado['faixa_preco'] = pd.cut(df_filtrado['preco2'], bins=5, labels=labels)

# 🧾 Resumo estatístico
st.subheader("📄 Resumo Estatístico dos Dados Filtrados")
st.write(df_filtrado[['preco2', 'desconto', 'desconto_percentual']].describe())

# 🎨 Gráficos Univariados
st.subheader("📊 Gráficos Univariados")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Histograma de Preços**")
    fig1, ax1 = plt.subplots()
    sns.histplot(df_filtrado['preco2'], bins=20, ax=ax1, color='black')
    ax1.set_xlabel('Preço (R$)')
    st.pyplot(fig1)

with col2:
    st.markdown("**Boxplot de Preços**")
    fig2, ax2 = plt.subplots()
    sns.boxplot(x=df_filtrado['preco2'], ax=ax2, color='pink')
    ax2.set_xlabel('Preço (R$)')
    st.pyplot(fig2)

# 🎯 Gráficos Bivariados
st.subheader("📈 Gráficos Bivariados")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Scatter Plot: Preço vs Desconto (%)**")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=df_filtrado, x='preco2', y='desconto_percentual', ax=ax3, color='black')
    ax3.set_xlabel('Preço (R$)')
    ax3.set_ylabel('Desconto (%)')
    st.pyplot(fig3)

with col4:
    st.markdown("**Boxplot: Desconto por Faixa de Preço**")
    fig4, ax4 = plt.subplots()
    sns.boxplot(data=df_filtrado, x='faixa_preco', y='desconto_percentual', ax=ax4, palette='pink')
    ax4.set_xlabel('Faixa de Preço')
    ax4.set_ylabel('Desconto (%)')
    plt.xticks(rotation=45)
    st.pyplot(fig4)

# 📜 Tabela de Dados
st.subheader("🗂️ Tabela de Dados Filtrados")
st.dataframe(df_filtrado)
