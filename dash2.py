import streamlit as st
import pandas as pd
import plotly.express as px
import re
import plotly.graph_objects as go
import numpy as np
import os
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Fundos de Investimentos",
    layout="wide"
)

# Função para limpar e padronizar CNPJs
def clean_cnpj(cnpj):
    if pd.isna(cnpj):
        return ""
    # Remove todos os caracteres não numéricos
    cnpj_limpo = re.sub(r'[^0-9]', '', str(cnpj))
    # Garante que tenha 14 dígitos, preenchendo com zeros à esquerda
    return cnpj_limpo.zfill(14)

# Função para limpar e padronizar nomes
def clean_name(name):
    if pd.isna(name):
        return ""
    # Converte para maiúsculas
    name = str(name).upper()
    # Remove caracteres especiais e números, mantendo apenas letras e espaços
    name = re.sub(r'[^A-ZÀ-ÿ\s]', '', name)
    # Remove espaços extras
    name = ' '.join(name.split())
    return name

# Função para formatar valores monetários
def format_currency(value):
    return f"R$ {value:,.2f}"

# Função para formatar grandes valores (milhões, bilhões)
def format_large_value(value):
    if value >= 1_000_000_000:
        return f"R$ {value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"R$ {value/1_000_000:.1f}M"
    else:
        return f"R$ {value:,.0f}"

# Carregar os dados
@st.cache_data
def load_data():
    # Caminho base para os arquivos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    registro_fundo = pd.read_csv(os.path.join(base_dir, "registro_fundo.csv"), 
                                encoding='latin1',
                                sep=';',  
                                on_bad_lines='skip',
                                low_memory=False)
    
    oferta_resolucao_160 = pd.read_csv(os.path.join(base_dir, "oferta_resolucao_160.csv"), 
                                      encoding='latin1',
                                      sep=';',
                                      on_bad_lines='skip',
                                      low_memory=False)
    
    fidc_info = pd.read_csv(os.path.join(base_dir, "inf_mensal_fidc_202502/inf_mensal_fidc_tab_II_202502.csv"),
                           encoding='latin1',
                           sep=';',
                           on_bad_lines='skip',
                           low_memory=False)
    
    fidc_tab_vi = pd.read_csv(os.path.join(base_dir, 'inf_mensal_fidc_202502/inf_mensal_fidc_tab_VI_202502.csv'), 
                              sep=';', 
                              encoding='latin1',
                              on_bad_lines='skip',
                              low_memory=False)
    
    fidc_tab_vii = pd.read_csv(os.path.join(base_dir, 'inf_mensal_fidc_202502/inf_mensal_fidc_tab_VII_202502.csv'), 
                               sep=';', 
                               encoding='latin1',
                               on_bad_lines='skip',
                               low_memory=False) 

    # Padronizar os CNPJs
    registro_fundo["CNPJ_Fundo"] = registro_fundo["CNPJ_Fundo"].astype(str).apply(clean_cnpj)
    oferta_resolucao_160["CNPJ_Emissor"] = oferta_resolucao_160["CNPJ_Emissor"].astype(str).apply(clean_cnpj)
    fidc_info["CNPJ_FUNDO_CLASSE"] = fidc_info["CNPJ_FUNDO_CLASSE"].astype(str).apply(clean_cnpj)
    fidc_tab_vi["CNPJ_FUNDO_CLASSE"] = fidc_tab_vi["CNPJ_FUNDO_CLASSE"].astype(str).apply(clean_cnpj)
    fidc_tab_vii["CNPJ_FUNDO_CLASSE"] = fidc_tab_vii["CNPJ_FUNDO_CLASSE"].astype(str).apply(clean_cnpj)
    
    # Limpar e padronizar nomes
    registro_fundo["Gestor"] = registro_fundo["Gestor"].apply(clean_name)
    registro_fundo["Administrador"] = registro_fundo["Administrador"].apply(clean_name)
    oferta_resolucao_160["Gestor"] = oferta_resolucao_160["Gestor"].apply(clean_name)
    oferta_resolucao_160["Nome_Lider"] = oferta_resolucao_160["Nome_Lider"].apply(clean_name)
    oferta_resolucao_160["Nome_Emissor"] = oferta_resolucao_160["Nome_Emissor"].apply(clean_name)
    
    return registro_fundo, oferta_resolucao_160, fidc_info, fidc_tab_vi, fidc_tab_vii

registro_fundo, oferta_resolucao_160, fidc_tab_ii, fidc_tab_vi, fidc_tab_vii = load_data()

# Adicionando o logo e o cabeçalho
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo = Image.open(os.path.join(base_dir, 'logo_bamboo.png'))
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image(logo, width=200)
    with col2:
        st.markdown("<h1 style='text-align: center;'>Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Não foi possível carregar a logo: {e}")
    st.markdown("<h1 style='text-align: center;'>Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)

# Aplicar estilo CSS personalizado
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f0f8f0;
    }
    .css-1d391kg {
        background-color: #1a472a;
        color: white;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
    }
    h1, h2, h3 {
        color: #1a472a;
    }
</style>
""", unsafe_allow_html=True)

# Criar lista única de gestores (assets)
assets_registro = set(registro_fundo["Gestor"].dropna().unique())
assets_oferta = set(oferta_resolucao_160["Gestor"].dropna().unique())

# Unir as duas fontes para ter todas as gestoras possíveis e remover strings vazias
assets_disponiveis = sorted([asset for asset in assets_registro.union(assets_oferta) if asset.strip()])

# Sidebar para selecionar a Asset
st.sidebar.markdown("<h2 style='text-align: center; color: #2ca356;'>Selecionar Gestora</h2>", unsafe_allow_html=True)
selected_asset = st.sidebar.selectbox("Escolha uma Gestora:", assets_disponiveis)

# Filtrar dados da Asset escolhida
fundos_asset = registro_fundo[registro_fundo["Gestor"] == selected_asset]
ofertas_asset = oferta_resolucao_160[oferta_resolucao_160["Gestor"] == selected_asset]

# Criar uma lista de CNPJs dos fundos da gestora selecionada
cnpjs_fundos_gestora = fundos_asset["CNPJ_Fundo"].unique().tolist()

# Filtrar FIDCs pelos CNPJs dos fundos da gestora
fidc_ii_gestora = fidc_tab_ii[fidc_tab_ii["CNPJ_FUNDO_CLASSE"].isin(cnpjs_fundos_gestora)]
fidc_vi_gestora = fidc_tab_vi[fidc_tab_vi["CNPJ_FUNDO_CLASSE"].isin(cnpjs_fundos_gestora)]
fidc_vii_gestora = fidc_tab_vii[fidc_tab_vii["CNPJ_FUNDO_CLASSE"].isin(cnpjs_fundos_gestora)]

# Título personalizado com a gestora selecionada
st.markdown(f"""
<div style='background-color: #1a472a; padding: 10px; border-radius: 5px;'>
    <h1 style='color: white; text-align: center;'>Dashboard - {selected_asset}</h1>
</div>
""", unsafe_allow_html=True)

# Criar abas para Fundos, Ofertas e FIDCs
tab1, tab2, tab3 = st.tabs(["Fundos", "Ofertas", "FIDCs"])

# Aba de Fundos
with tab1:
    if not fundos_asset.empty:
        # Adicionar contador para gerar chaves únicas
        for idx, (_, fundo) in enumerate(fundos_asset.iterrows()):
            st.markdown(f"### Fundo: {fundo['Denominacao_Social']}")
            st.write(f"**No que investe:** {fundo['Tipo_Fundo']}")
            st.write(f"**Caixa disponível:** {format_large_value(fundo['Patrimonio_Liquido'])}")
            st.write(f"**Administrador:** {fundo['Administrador']}")

            # Comparação com o mercado
            tipo_fundo = fundo['Tipo_Fundo']
            media_mercado = registro_fundo[registro_fundo['Tipo_Fundo'] == tipo_fundo]['Patrimonio_Liquido'].mean()
            st.write(f"**Média do mercado ({tipo_fundo}):** {format_large_value(media_mercado)}")

            # Gráfico de comparação
            comparacao_df = pd.DataFrame({
                "Categoria": ["Este Fundo", "Média do Mercado"],
                "Patrimônio Líquido": [fundo['Patrimonio_Liquido'], media_mercado]
            })
            fig = px.bar(comparacao_df, x="Categoria", y="Patrimônio Líquido", 
                        title=f"Comparação com o Mercado - {fundo['Denominacao_Social']}")
            fig.update_layout(
                yaxis_title="Patrimônio Líquido",
                yaxis_tickformat=",~s",
                yaxis_tickprefix="R$ "
            )
            # Usar o índice junto com o CNPJ para garantir chave única
            st.plotly_chart(fig, key=f"chart_{idx}_{fundo['CNPJ_Fundo']}")
            st.write("---")  # Linha divisória entre fundos
    else:
        st.write("Nenhum fundo encontrado para esta gestora.")

# Aba de Ofertas
with tab2:
    if not ofertas_asset.empty:
        for _, oferta in ofertas_asset.iterrows():
            st.markdown(f"### Oferta: {oferta['Numero_Requerimento']}")
            st.write(f"**Emissor:** {oferta['Nome_Emissor']}")
            st.write(f"**CNPJ do Emissor:** {oferta['CNPJ_Emissor']}")
            st.write(f"**Tipo de Oferta:** {oferta['Tipo_Oferta']}")
            st.write(f"**Valor Total Registrado:** {format_large_value(oferta['Valor_Total_Registrado'])}")
            st.write(f"**Status:** {oferta['Status_Requerimento']}")
            st.write("---")  # Adiciona uma linha divisória entre as ofertas
    else:
        st.write("Nenhuma oferta encontrada para esta gestora.")

# Aba de FIDCs
with tab3:
    st.header("Análise de FIDCs")
    
    # Verificar se existem FIDCs para esta gestora
    if fidc_ii_gestora.empty and fidc_vi_gestora.empty and fidc_vii_gestora.empty:
        st.warning(f"Não foram encontrados FIDCs específicos para a gestora {selected_asset}. Mostrando dados gerais.")
        # Usar os dados gerais
        fidc_ii_para_analise = fidc_tab_ii
        fidc_vi_para_analise = fidc_tab_vi
        fidc_vii_para_analise = fidc_tab_vii
        
        titulo_graficos = f"Geral (Todos os FIDCs)"
    else:
        # Usar os dados específicos da gestora
        fidc_ii_para_analise = fidc_ii_gestora
        fidc_vi_para_analise = fidc_vi_gestora
        fidc_vii_para_analise = fidc_vii_gestora
        
        st.success(f"Mostrando {len(fidc_ii_para_analise)} FIDCs geridos por {selected_asset}")
        titulo_graficos = selected_asset
    
    # Métricas gerais
    col1, col2, col3 = st.columns(3)
        
    with col1:
        total_com_risco = fidc_vii_para_analise['TAB_VII_A1_2_VL_DIRCRED_RISCO'].sum()
        st.metric("Dir. Creditórios com Risco", format_large_value(total_com_risco))
            
    with col2:
        total_sem_risco = fidc_vii_para_analise['TAB_VII_A2_2_VL_DIRCRED_SEM_RISCO'].sum()
        st.metric("Dir. Creditórios sem Risco", format_large_value(total_sem_risco))
            
    with col3:
        total_inadimplente = fidc_vii_para_analise['TAB_VII_A5_2_VL_DIRCRED_INAD'].sum()
        st.metric("Valor Inadimplente", format_large_value(total_inadimplente))
    
    # Análise Setorial (Tabela II)
    st.subheader("Análise Setorial")
    
    # Calcular totais por setor
    setores = {
        'Industrial': fidc_ii_para_analise['TAB_II_A_VL_INDUST'].sum(),
        'Imobiliário': fidc_ii_para_analise['TAB_II_B_VL_IMOBIL'].sum(),
        'Comercial': fidc_ii_para_analise['TAB_II_C_VL_COMERC'].sum(),
        'Serviços': fidc_ii_para_analise['TAB_II_D_VL_SERV'].sum(),
        'Agronegócio': fidc_ii_para_analise['TAB_II_E_VL_AGRONEG'].sum(),
        'Financeiro': fidc_ii_para_analise['TAB_II_F_VL_FINANC'].sum(),
        'Crédito': fidc_ii_para_analise['TAB_II_G_VL_CREDITO'].sum(),
        'Factoring': fidc_ii_para_analise['TAB_II_H_VL_FACTOR'].sum(),
        'Setor Público': fidc_ii_para_analise['TAB_II_I_VL_SETOR_PUBLICO'].sum(),
        'Judicial': fidc_ii_para_analise['TAB_II_J_VL_JUDICIAL'].sum(),
        'Marca': fidc_ii_para_analise['TAB_II_K_VL_MARCA'].sum()
    }
    
    # Remover setores com valor zero
    setores = {k: v for k, v in setores.items() if v > 0}
    
    if setores:
        # Criar DataFrame para o gráfico de pizza setorial
        setores_df = pd.DataFrame({
            'Setor': list(setores.keys()),
            'Valor': list(setores.values())
        })
        
        # Gráfico de pizza da distribuição setorial
        fig_setores = px.pie(
            setores_df,
            values='Valor',
            names='Setor',
            title=f'Distribuição da Carteira por Setor - {titulo_graficos}',
            hole=0.3
        )
        st.plotly_chart(fig_setores)
    else:
        st.info("Não há dados setoriais disponíveis para esta gestora.")
    
    # Top FIDCs por valor total da carteira
    if not fidc_ii_para_analise.empty:
        st.subheader("FIDCs por Valor Total da Carteira")
        fidc_ii_para_analise['Valor_Total_Carteira'] = fidc_ii_para_analise['TAB_II_VL_CARTEIRA']
        fidc_ii_para_analise['Valor_Formatado'] = fidc_ii_para_analise['Valor_Total_Carteira'].apply(format_large_value)
        carteira_df = fidc_ii_para_analise[['DENOM_SOCIAL', 'Valor_Total_Carteira']].sort_values('Valor_Total_Carteira', ascending=False)
        
        fig_carteira = px.bar(
            carteira_df,
            x='DENOM_SOCIAL',
            y='Valor_Total_Carteira',
            title=f'FIDCs por Valor Total da Carteira - {titulo_graficos}'
        )
        fig_carteira.update_layout(
            xaxis_tickangle=-45,
            yaxis_title="Valor Total",
            yaxis_tickformat=",~s",
            yaxis_tickprefix="R$ "
        )
        st.plotly_chart(fig_carteira)
    
    # Análise do Setor Financeiro
    if not fidc_ii_para_analise.empty:
        st.subheader("Detalhamento do Setor Financeiro")
        
        financeiro = {
            'Crédito Pessoal': fidc_ii_para_analise['TAB_II_F1_VL_CRED_PESSOA'].sum(),
            'Crédito Consignado': fidc_ii_para_analise['TAB_II_F2_VL_CRED_PESSOA_CONSIG'].sum(),
            'Crédito Corporativo': fidc_ii_para_analise['TAB_II_F3_VL_CRED_CORP'].sum(),
            'Middle Market': fidc_ii_para_analise['TAB_II_F4_VL_MIDMARKET'].sum(),
            'Financ. Veículos': fidc_ii_para_analise['TAB_II_F5_VL_VEICULO'].sum(),
            'Financ. Imob. Empresarial': fidc_ii_para_analise['TAB_II_F6_VL_IMOBIL_EMPRESA'].sum(),
            'Financ. Imob. Residencial': fidc_ii_para_analise['TAB_II_F7_VL_IMOBIL_RESID'].sum(),
            'Outros': fidc_ii_para_analise['TAB_II_F8_VL_OUTRO'].sum()
        }
        
        # Remover categorias com valor zero
        financeiro = {k: v for k, v in financeiro.items() if v > 0}
        
        if financeiro:
            financeiro_df = pd.DataFrame({
                'Tipo': list(financeiro.keys()),
                'Valor': list(financeiro.values())
            })
            
            fig_financeiro = px.bar(
                financeiro_df,
                x='Tipo',
                y='Valor',
                title=f'Composição do Setor Financeiro - {titulo_graficos}'
            )
            fig_financeiro.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Valor Total",
                yaxis_tickformat=",~s",
                yaxis_tickprefix="R$ "
            )
            st.plotly_chart(fig_financeiro)
        else:
            st.info("Não há dados do setor financeiro disponíveis para esta gestora.")
    
    # Análise de Prazos e Vencimentos
    if not fidc_vi_para_analise.empty:
        st.subheader("Análise de Prazos e Vencimentos")
        
        prazos = {
            '30 dias': fidc_vi_para_analise['TAB_VI_A1_VL_PRAZO_VENC_30'].sum(),
            '60 dias': fidc_vi_para_analise['TAB_VI_A2_VL_PRAZO_VENC_60'].sum(),
            '90 dias': fidc_vi_para_analise['TAB_VI_A3_VL_PRAZO_VENC_90'].sum(),
            '180 dias': fidc_vi_para_analise['TAB_VI_A6_VL_PRAZO_VENC_180'].sum(),
            '360 dias': fidc_vi_para_analise['TAB_VI_A7_VL_PRAZO_VENC_360'].sum(),
            'Acima de 360 dias': fidc_vi_para_analise['TAB_VI_A8_VL_PRAZO_VENC_720'].sum() + 
                                fidc_vi_para_analise['TAB_VI_A9_VL_PRAZO_VENC_1080'].sum() + 
                                fidc_vi_para_analise['TAB_VI_A10_VL_PRAZO_VENC_MAIOR_1080'].sum()
        }
        
        # Remover prazos com valor zero
        prazos = {k: v for k, v in prazos.items() if v > 0}
        
        if prazos:
            prazos_df = pd.DataFrame({
                'Prazo': list(prazos.keys()),
                'Valor': list(prazos.values())
            })
            
            fig_prazos = px.bar(
                prazos_df,
                x='Prazo',
                y='Valor',
                title=f'Distribuição dos Direitos Creditórios por Prazo de Vencimento - {titulo_graficos}',
                labels={'Valor': 'Valor Total', 'Prazo': 'Prazo até o Vencimento'}
            )
            fig_prazos.update_layout(
                yaxis_tickformat=",~s",
                yaxis_tickprefix="R$ "
            )
            st.plotly_chart(fig_prazos)
        else:
            st.info("Não há dados de prazos disponíveis para esta gestora.")
    
    # Análise de inadimplência
    if not fidc_vii_para_analise.empty:
        st.subheader("Análise de Inadimplência")
        
        fidc_vii_para_analise['Valor_Total'] = fidc_vii_para_analise['TAB_VII_A1_2_VL_DIRCRED_RISCO'] + fidc_vii_para_analise['TAB_VII_A2_2_VL_DIRCRED_SEM_RISCO']
        fidc_vii_para_analise['Taxa_Inadimplencia'] = (fidc_vii_para_analise['TAB_VII_A5_2_VL_DIRCRED_INAD'] / fidc_vii_para_analise['Valor_Total'] * 100).fillna(0)
        inadimplencia_df = fidc_vii_para_analise[['DENOM_SOCIAL', 'Taxa_Inadimplencia']].sort_values('Taxa_Inadimplencia', ascending=False)
        
        if not inadimplencia_df.empty:
            fig_inadimplencia = px.bar(
                inadimplencia_df,
                x='DENOM_SOCIAL',
                y='Taxa_Inadimplencia',
                title=f'Taxa de Inadimplência (%) por FIDC - {titulo_graficos}'
            )
            fig_inadimplencia.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Taxa de Inadimplência (%)"
            )
            st.plotly_chart(fig_inadimplencia)
        else:
            st.info("Não há dados de inadimplência disponíveis para esta gestora.")

st.sidebar.info("Este é um dashboard interativo para análise de fundos, ofertas e FIDCs por gestora.")

# Adicionar rodapé
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col1:
    st.write("")
with footer_col2:
    st.markdown("<p style='text-align: center; color: gray;'>© 2025 BambooDCM <br>Desenvolvido por Bamboo Tech</p>", unsafe_allow_html=True)
with footer_col3:
    from datetime import datetime
    st.markdown(f"<p style='text-align: right; color: gray;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
