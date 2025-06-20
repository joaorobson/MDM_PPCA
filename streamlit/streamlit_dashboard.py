#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt

#######################
# Page configuration
st.set_page_config(
    page_title="Dashboard de Projetos de Lei - Congresso Nacional",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -5rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
    margin-bottom: 1rem;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 700;
}

[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df = pd.read_json('pls_full_2_norm.json')
df["ano"] = pd.to_datetime(df["data_apresentacao"]).dt.year

#######################
# Sidebar
with st.sidebar:
    st.title('📜 Filtros de Projetos de Lei')
    
    ano_min, ano_max = int(df["ano"].min()), int(df["ano"].max())
    selected_ano_range = st.slider(
        "Selecione o intervalo de anos",
        min_value=ano_min,
        max_value=ano_max,
        value=(ano_min, ano_max)
    )
    
    # Filtra o dataframe
    df_filtrado = df[(df["ano"] >= selected_ano_range[0]) & (df["ano"] <= selected_ano_range[1])]
    
#######################
# Helper function: Pie chart for proportion
def make_pie_chart(df_pie, label_col, value_col, title):
    chart = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field=value_col, type="quantitative"),
        color=alt.Color(field=label_col, type="nominal", legend=alt.Legend(title=title)),
        tooltip=[label_col, value_col]
    ).properties(width=400, height=400)
    return chart

#######################
# Main layout with columns
col1, col2, col3 = st.columns((3, 4, 3), gap="large")

with col1:
    st.header("Distribuição de Projetos por Casa Legislativa")
    dist_casa = df_filtrado["casa_origem"].value_counts().reset_index()
    dist_casa.columns = ["Casa", "Quantidade"]

    bar_casa = alt.Chart(dist_casa).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X('Casa:N', sort='-y', title='Casa Legislativa'),
        y=alt.Y('Quantidade:Q', title='Quantidade de Projetos'),
        color=alt.Color('Casa:N',
                        scale=alt.Scale(
                            domain=['Câmara dos Deputados', 'Senado Federal'],
                            range=['#2F7958', '#005B9E']
                        ),
                        legend=None)
    ).properties(width=300, height=300)

   
    st.altair_chart(bar_casa, use_container_width=True)
    
    st.header("Proporção de Projetos Transformados em Lei")
    prop_viraram_lei = df_filtrado["transformado_em_norma"].value_counts(normalize=True).reset_index()
    prop_viraram_lei.columns = ["Transformado em Lei", "Proporção"]
    prop_viraram_lei["Transformado em Lei"] = prop_viraram_lei["Transformado em Lei"].map({True: "Sim", False: "Não"})
    
    st.altair_chart(make_pie_chart(prop_viraram_lei, "Transformado em Lei", "Proporção", "Transformado em Lei"), use_container_width=True)

with col2:
    st.header("Número de Projetos Propostos por Ano por Casa Legislativa")
    
    # Agrupa por ano e casa_origem
    projetos_ano_casa = df_filtrado.groupby(["ano", "casa_origem"]).size().reset_index(name="Quantidade")
    
    # Gráfico de barras agrupadas
    bar = alt.Chart(projetos_ano_casa).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('ano:O', title='Ano'),
        y=alt.Y('Quantidade:Q', title='Quantidade de Projetos'),
        color=alt.Color('casa_origem:N', title='Casa Legislativa', scale=alt.Scale(domain=['Câmara dos Deputados', 'Senado Federal'],
                    range=['#2F7958', '#005B9E'])),
        tooltip=[alt.Tooltip('ano:O', title='Ano'),
                 alt.Tooltip('casa_origem:N', title='Casa'),
                 alt.Tooltip('Quantidade:Q', title='Quantidade')]
    ).properties(width=600, height=350).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    
    st.altair_chart(bar, use_container_width=True)

with col3:
    st.header("Temas Predominantes entre Projetos que Viraram Lei")

    # Filtra só projetos que viraram norma
    senado_df = df_filtrado[df_filtrado["casa_origem"] == "Senado Federal"]

    df_lei = senado_df[senado_df["transformado_em_norma"] == True]
    df_nao_lei = senado_df[senado_df["transformado_em_norma"] == False]

    # Função para extrair todas as descrições de classificações numa lista plana
    def extrair_classificacoes(df):
        all_classificacoes = []
        for classificacoes_lista in df["classificacoes"].dropna():
            for classificacao in classificacoes_lista:
                descricao = classificacao.get("descricao") if isinstance(classificacao, dict) else None
                if descricao:
                    all_classificacoes.append(descricao)
        return all_classificacoes

    # Extrai as classificações
    temas_leis= extrair_classificacoes(df_lei)
    temas_nao_leis = extrair_classificacoes(df_nao_lei)
    # Conta a frequência das classificações
    temas_count = pd.Series(temas_leis).value_counts().reset_index()
    temas_count.columns = ["Tema", "Quantidade"]

    temas_count_2 = pd.Series(temas_nao_leis).value_counts().reset_index()
    temas_count_2.columns = ["Tema", "Quantidade"]

    # Gráfico de barras com Altair
    bar_temas = alt.Chart(temas_count.head(10)).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Quantidade:Q", title="Quantidade"),
        y=alt.Y("Tema:N", sort='-x', title="Tema"),
        tooltip=[alt.Tooltip("Tema:N"), alt.Tooltip("Quantidade:Q")]
    ).properties(width=300, height=350)

    st.altair_chart(bar_temas, use_container_width=True)

    st.header("Temas Predominantes entre Projetos que não Viraram Lei") 
    bar_temas = alt.Chart(temas_count_2.head(10)).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Quantidade:Q", title="Quantidade"),
        y=alt.Y("Tema:N", sort='-x', title="Tema"),
        tooltip=[alt.Tooltip("Tema:N"), alt.Tooltip("Quantidade:Q")]
    ).properties(width=300, height=350)

    st.altair_chart(bar_temas, use_container_width=True)



#######################
# Footer / About
st.markdown("---")
st.markdown("""
#### Sobre este dashboard

- Dados extraídos do Congresso Nacional Brasileiro (2000–2024).
- Visualização dinâmica baseada em filtros.
- Ferramenta para análise da produção legislativa e seus temas predominantes.
""")
