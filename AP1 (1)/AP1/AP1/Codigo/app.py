import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Shein Insights: Preços & Descontos", page_icon="🛍️")

# CSS customizado para fundo rosa e botões pretos
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

# Limpar coluna preco2 (ex: "R$34,21" -> 34.21 float)
df['preco2'] = df['preco2'].astype(str).str.replace('R\$', '', regex=True).str.replace(',', '.').astype(float)

# Limpar coluna desconto
df['desconto'] = df['desconto'].fillna('0')

def extrair_desconto(x):
    x = str(x).strip()
    if '%' in x:
        return float(x.replace('%', '').replace(',', '.'))
    elif 'R$' in x:
        val = x.replace('R$', '').replace(',', '.')
        try:
            return float(val)
        except:
            return 0
    else:
        try:
            return float(x.replace(',', '.'))
        except:
            return 0

df['desconto_limpo'] = df['desconto'].apply(extrair_desconto)

# Criar coluna desconto_percentual
if df['desconto'].str.contains('%').any():
    # Se tem desconto em %, usa direto
    df['desconto_percentual'] = df['desconto_limpo']
else:
    # Se desconto é em R$, calcula %
    df['desconto_percentual'] = (df['desconto_limpo'] / (df['preco2'] + df['desconto_limpo'])) * 100

# Slider para faixa de preço
preco_min, preco_max = float(df['preco2'].min()), float(df['preco2'].max())
preco_range = st.slider("Filtrar por faixa de preço (R$)", min_value=preco_min, max_value=preco_max, value=(preco_min, preco_max))

df_filtrado = df[(df['preco2'] >= preco_range[0]) & (df['preco2'] <= preco_range[1])]

st.subheader("Resumo estatístico dos dados filtrados:")
st.write(df_filtrado[['preco2', 'desconto_percentual']].describe())

st.subheader("Tabela de Dados Filtrados")
st.dataframe(df_filtrado[['preco2', 'desconto', 'desconto_percentual']])

st.subheader("Gráficos Univariados")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Histograma de Preços**")
    fig1, ax1 = plt.subplots()
    sns.histplot(df_filtrado['preco2'], bins=20, ax=ax1)
    st.pyplot(fig1)

with col2:
    st.markdown("**Boxplot de Preços**")
    fig2, ax2 = plt.subplots()
    sns.boxplot(x=df_filtrado['preco2'], ax=ax2)
    st.pyplot(fig2)

st.subheader("Gráficos Bivariados")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Scatter Plot: Preço vs Desconto (%)**")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=df_filtrado, x='preco2', y='desconto_percentual', ax=ax3)
    st.pyplot(fig3)

with col4:
    st.markdown("**Boxplot: Desconto por Faixa de Preço**")
    df_filtrado['faixa_preco'] = pd.cut(df_filtrado['preco2'], bins=5)
    fig4, ax4 = plt.subplots()
    sns.boxplot(data=df_filtrado, x='faixa_preco', y='desconto_percentual', ax=ax4)
    plt.xticks(rotation=45)
    st.pyplot(fig4)
