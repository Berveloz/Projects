import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
        page_title="Dashboard de Vazão Hidrologicos",
        page_icon="🌊",
        layout="wide",
        initial_sidebar_state="expanded"
)

# ==========================================
# CSS PERSONALIZADO
# ==========================================
st.markdown("""
<style>

.main {
        background: linear-gradient(
                135deg,
                #f5f7fa 0%,
                #e4ecfb 100%
        );
}

h1 {
        color: #0f4c81;
        text-align: center;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0f4c81,
        #1b6ca8
    );
}

[data-testid="stSidebar"] * {
    color: white;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: center;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #1b6ca8;
}

.metric-title {
    font-size: 14px;
    color: gray;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CABEÇALHO
# ==========================================
st.title("🌊 Dashboard de Monitoramento de Vazão Hidrologicos")

st.markdown(
    """
    Sistema para análise de vazão afluente,
    geração de gráficos e monitoramento operacional.
    """
)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/728/728093.png",
    width=100
)

st.sidebar.write('''
                Feito por:  
                Bernardo Torquato   
                Nicolas Prado   
                Gustavo Henrik  
                Guilherme Gamon 
                Rafael Moreira
''')
# ==========================================
# MÉTRICAS EM CARDS
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-title">
                Vazão Média
            </div>
            <div class="metric-value">
                285 m³/s
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-title">
                Vazão Máxima
            </div>
            <div class="metric-value">
                412 m³/s
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-title">
                Vazão Mínima
            </div>
            <div class="metric-value">
                198 m³/s
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# ÁREA DOS GRÁFICOS
# ==========================================

st.title("📊 Gráficos")
arquivo = st.file_uploader( type=["csv"])

if arquivo is not None:
    df = pd.read_csv(
            arquivo, 
            sep=";", 
            encoding="latin1")
else:
    df = pd.read_csv(
            "DADOS_HIDROLOGICOS_HO_2019_01.csv", 
            sep=";", 
            encoding="latin1")    

    # =============================
    # Gráfico 1
    # =============================

    if (
        "nom_reservatorio" in df.columns and
        "val_volumeutil" in df.columns
    ):

        volume_medio = (
            df.groupby(
                "nom_reservatorio",
                as_index=False
            )["val_volumeutil"]
            .mean()
            .sort_values(
                "val_volumeutil",
                ascending=False
            )
        )

        fig = px.bar(
            volume_medio.head(10),
            x="val_volumeutil",
            y="nom_reservatorio",
            orientation="h",
            title="Top 10 Reservatórios por Volume Útil Médio",
            labels={
                "val_volumeutil": "Volume Útil Médio",
                "nom_reservatorio": "Reservatório"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("""
        O gráfico compara o volume útil médio dos dez reservatórios analisados.
        Entre eles, SALTO PILAO apresenta o maior valor, ficando acima dos demais.
        """)
        
    # =============================
    # Gráfico 2
    # =============================

    if (
        "din_instante" in df.columns and
        "val_vazaoafluente" in df.columns
    ):

        df["hora"] = pd.to_datetime(
            df["din_instante"],
            errors="coerce"
        ).dt.hour

        vazao_hora = (
            df.groupby(
                "hora",
                as_index=False
            )["val_vazaoafluente"]
            .mean()
        )

        fig = px.line(
            vazao_hora,
            x="hora",
            y="val_vazaoafluente",
            markers=True,
            title="Vazão Afluente Média por Hora do Dia",
            labels={
                "hora": "Hora do Dia",
                "val_vazaoafluente": "Vazão Afluente Média"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("""
        O gráfico apresenta a vazão afluente média ao longo das horas do dia,
        evidenciando variações ao longo do período analisado.
        """)

    # =============================
    # Dados
    # =============================

    with st.expander("🧹 Limpeza de Dados"):

        # Converter data
        if "din_instante" in df.columns:
                df["din_instante"] = pd.to_datetime(
                        df["din_instante"],
                        errors="coerce"
                )

        # Colunas numéricas
        colunas_numericas = [
                "val_nivelmontante",
                "val_niveljusante",
                "val_volumeutil",
                "val_vazaoafluente",
                "val_vazaodefluente",
                "val_vazaoturbinada",
                "val_vazaovertida"
        ]

        for coluna in colunas_numericas:
                if coluna in df.columns:
                        df[coluna] = pd.to_numeric(
                                df[coluna],
                                errors="coerce"
                        )

        # Valores ausentes
        valores_ausentes = df.isnull().sum()

        # Duplicados
        duplicados = df.duplicated().sum()

        # Valores negativos
        negativos = {}

        for coluna in colunas_numericas:
                if coluna in df.columns:
                        negativos[coluna] = (df[coluna] < 0).sum()

        # Resumo estatístico
        resumo_numerico = df.describe()

        # Métricas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
                st.metric(
                        "Quantidade de registros",
                        f"{df.shape[0]:,}"
                )

        with col2:
                st.metric(
                        "Quantidade de colunas",
                        df.shape[1]
                )

        with col3:
                if "nom_reservatorio" in df.columns:
                        st.metric(
                                "Reservatórios únicos",
                                df["nom_reservatorio"].nunique()
                        )

        with col4:
                if "val_vazaoafluente" in df.columns:
                        st.metric(
                                "Vazão Média",
                                round(
                                        df["val_vazaoafluente"].mean(),
                                        2
                                )
                        )

        st.subheader("Visualização dos Dados")
        st.dataframe(df.head())

        st.subheader("Valores Ausentes")
        st.dataframe(
                valores_ausentes.reset_index().rename(
                        columns={
                                "index": "Coluna",
                                0: "Quantidade de Ausentes"
                        }
                )
        )

        st.subheader("Registros Duplicados")
        st.write(f"Quantidade de registros duplicados: {duplicados}")

        st.subheader("Valores Negativos Encontrados")
        st.dataframe(
                pd.DataFrame(
                        negativos.items(),
                        columns=["Coluna", "Quantidade"]
                )
        )

        st.subheader("Resumo Estatístico")
        st.dataframe(resumo_numerico)
