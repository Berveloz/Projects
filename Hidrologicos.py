import streamlit as st
import pandas as pd
import plotly.express as px
 
st.set_page_config(
    page_title="Dados de ",
    layout="wide"
)
 
st.title("Dashboard de Dados")
 
st.write("""
Este dashboard apresenta uma análise exploratória de dados hidrológicos e operacionais associados a reservatórios utilizados na geração de energia hidrelétrica.
 
O objetivo é avaliar o comportamento das variáveis de armazenamento e vazão, identificando padrões temporais, diferenças entre bacias hidrográficas e características operacionais dos reservatórios. A análise busca fornecer insights sobre a disponibilidade hídrica e sua relação com a geração de energia, contribuindo para a compreensão da dinâmica do sistema elétrico brasileiro.
""")
 
st.write("""
Foi utilizado o conjunto de dados "DADOS_HIDROLOGICOS_HO_2019_01.csv" para realizar a análise exploratória. O arquivo contém informações detalhadas sobre os reservatórios, incluindo níveis de água, volumes úteis, vazões afluentes e defluentes, entre outros parâmetros relevantes para a gestão hídrica e geração de energia hidrelétrica.
    """)
 
arquivo = st.file_uploader(
    "Envie um arquivo CSV",
    type=["csv"]
)
 
if arquivo is not None:
 
    # Leitura do arquivo
    df = pd.read_csv(
        arquivo,
        sep=';',
        encoding='latin1'
    )
 
    # Converter data
    if 'din_instante' in df.columns:
        df['din_instante'] = pd.to_datetime(
            df['din_instante'],
            errors='coerce'
        )
 
    # Converter colunas numéricas
    colunas_numericas = [
        'val_nivelmontante',
        'val_niveljusante',
        'val_volumeutil',
        'val_vazaoafluente',
        'val_vazaodefluente',
        'val_vazaoturbinada',
        'val_vazaovertida'
    ]
 
    for coluna in colunas_numericas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(
                df[coluna],
                errors='coerce'
            )
 
    # Verificar valores ausentes
    valores_ausentes = df.isnull().sum()
 
    # Verificar duplicados
    duplicados = df.duplicated().sum()
 
    # Verificar valores negativos
    negativos = {}
 
    for coluna in colunas_numericas:
        if coluna in df.columns:
            negativos[coluna] = (df[coluna] < 0).sum()
 
    resumo_numerico = df.describe()
 
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
 
    col1.metric(
        "Quantidade de registros",
        f"{df.shape[0]:,}"
    )
 
    col2.metric(
        "Quantidade de colunas",
        df.shape[1]
    )
 
    col3.metric(
        "Reservatórios únicos",
        df["nom_reservatorio"].nunique()
    )
 
    col4.metric(
        "Vazão Média",
        round(df["val_vazaoafluente"].mean(), 2)
    )
 
    # Visualização dos dados
    st.subheader("Visualização dos dados")
    st.dataframe(df.head())
 
    # Valores ausentes
    st.subheader("Valores ausentes")
 
    st.dataframe(
        valores_ausentes.reset_index().rename(
            columns={
                'index': 'Coluna',
                0: 'Quantidade de ausentes'
            }
        )
    )
 
    # Duplicados
    st.subheader("Registros duplicados")
    st.write(duplicados)
 
    # Negativos
    st.subheader("Valores negativos encontrados")
 
    st.dataframe(
        pd.DataFrame(
            negativos.items(),
            columns=['Coluna', 'Quantidade']
        )
    )
 
    # Estatísticas
    st.subheader("Resumo estatístico")
    st.dataframe(resumo_numerico)
 
    # =============================
    # Gráfico 1
    # =============================
 
    if (
        'nom_reservatorio' in df.columns and
        'val_volumeutil' in df.columns
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
 
    st.markdown(
        """O gráfico compara o volume útil médio dos dez reservatórios analisados. Entre eles, SALTO PILAO apresenta o maior valor, ficando bem acima dos demais reservatórios. SAO MANOEL e ERNESTINA também registram volumes úteis médios mais elevados, mas ainda inferiores ao de SALTO PILAO. Os dados mostram que a maior parte dos reservatórios possui volumes úteis médios próximos entre si, concentrados em torno de 100 unidades. Já SALTO PILAO se destaca de forma expressiva no conjunto analisado, indicando uma distribuição desigual dos volumes úteis médios entre os reservatórios avaliados.
        """)
 
    # =============================
    # Gráfico de Vazão por Hora
    # =============================
    if "din_instante" in df.columns and "val_vazaoafluente" in df.columns:
 
        df["hora"] = pd.to_datetime(
            df["din_instante"],
            errors="coerce"
        ).dt.hour
 
        vazao_hora = (
            df.groupby("hora", as_index=False)["val_vazaoafluente"]
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
 
        st.markdown(
            """O gráfico apresenta a vazão afluente média ao longo das horas do dia. Observa-se que a vazão tende a ser mais baixa durante as primeiras horas da manhã, aumentando gradualmente até atingir um pico por volta do meio-dia. Após esse ponto, há uma diminuição na vazão durante a tarde e início da noite, com uma leve recuperação nas últimas horas do dia. Esse padrão sugere que fatores como o ciclo diário de consumo de água ou variações climáticas podem influenciar significativamente a vazão afluente ao longo do dia.
            """
        )
 
    st.write("Foi utilizado a IA para corrigir, analizar e interpretar os dados e a análise.")
    st.write("Trabalho realizados por: Nicolas Prado")
 
 