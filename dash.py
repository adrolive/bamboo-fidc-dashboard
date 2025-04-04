import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar os dados
@st.cache_data
def load_data():
    registro_fundo = pd.read_csv("registro_fundo.csv", 
                                encoding='latin1',
                                sep=';',  # usando ponto e vírgula como separador
                                on_bad_lines='skip',  # pular linhas problemáticas
                                low_memory=False)  # evitar warnings de tipos mistos
    oferta_resolucao_160 = pd.read_csv("oferta_resolucao_160.csv", 
                                      encoding='latin1',
                                      sep=';',
                                      on_bad_lines='skip',
                                      low_memory=False)
    return registro_fundo, oferta_resolucao_160

registro_fundo, oferta_resolucao_160 = load_data()

# Sidebar para selecionar a Asset
st.sidebar.title("Selecionar Asset")
assets_disponiveis = registro_fundo["Administrador"].unique()
selected_asset = st.sidebar.selectbox("Escolha uma Asset:", assets_disponiveis)

# Filtrar fundos da Asset
fundos_asset = registro_fundo[registro_fundo["Administrador"] == selected_asset]

st.title(f"Dashboard - Fundos da {selected_asset}")

# Exibir informações dos fundos
for _, fundo in fundos_asset.iterrows():
    st.subheader(f"Fundo: {fundo['Denominacao_Social']}")
    st.write(f"**No que investe:** {fundo['Tipo_Fundo']}")
    st.write(f"**Caixa disponível:** R$ {fundo['Patrimonio_Liquido']:,}")
    
    # Comparação com mercado
    tipo_fundo = fundo['Tipo_Fundo']
    media_mercado = registro_fundo[registro_fundo['Tipo_Fundo'] == tipo_fundo]['Patrimonio_Liquido'].mean()
    
    st.write(f"**Média do mercado para {tipo_fundo}:** R$ {media_mercado:,.2f}")
    
    # Gráfico de comparação
    comparacao_df = pd.DataFrame({
        "Categoria": ["Este Fundo", "Média do Mercado"],
        "Patrimônio Líquido": [fundo['Patrimonio_Liquido'], media_mercado]
    })
    fig = px.bar(comparacao_df, x="Categoria", y="Patrimônio Líquido", title="Comparação com o Mercado")
    st.plotly_chart(fig)

st.sidebar.info("Este é um dashboard interativo para análise de fundos.")
