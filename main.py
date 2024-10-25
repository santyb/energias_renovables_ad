import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import altair as alt
import plotly.express as px
import numpy as np
import pydeck

#Leer archivo csv
def cargar_archivo():
    data = pd.read_csv('data/Meta_FNCER__Incorporar_en_la_matriz_energ_tica_nueva_capacidad_instalada_a_partir_de_Fuentes_No_Convencionales_de_Energ_a_Renovable_-_FNCER_20241003.csv')
    return data

def cargar_posicion():
    data = pd.read_excel('data/departamentos.xlsx', sheet_name='Departamentos')
    return data

df_posicion = cargar_posicion()
df_energias_renovables = cargar_archivo()
df_energias_renovables['Fecha estimada FPO'] = df_energias_renovables['Fecha estimada FPO'].str[:10]
df_energias_renovables.columns = df_energias_renovables.columns.str.replace(' ', '_')
df_energias_renovables = pd.merge(df_energias_renovables, df_posicion[['Código_Departamento', 'LATITUD', 'LONGITUD']], on='Código_Departamento', how='left')
df_energias_renovables = df_energias_renovables.rename(columns={'Energía_[kWh/día]': 'Energía_kWh_día'})
df_energias_renovables = df_energias_renovables.rename(columns={'Emisiones_CO2_[Ton/año]': 'Emisiones_CO2_Ton_año'})
st.title('Energía Renovable Sostenible y Eficiente')

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Datos", "Proyectos Por Departamento", "Tipo de energia", "Mapa", "Energia Vs CO2"])

with tab1:
    ver_df = st.toggle('Ver DataFrame', value=True)
    if ver_df:
        st.write(df_energias_renovables)
with tab2:
    
    departamentos = df_energias_renovables['Departamento'].value_counts()
    with st.container(border=True):
        st.header('Proyectos por Departamento')
        st.bar_chart(departamentos)
    
        
with tab3:
    # Grafico de contagios por sexo
    
    lista_departamento=df_energias_renovables['Departamento'].sort_values().unique().tolist()
    lista_departamento.insert(0, 'Todos')
    option=st.selectbox(
        'Seleccione el departamento',
        lista_departamento
    )
    if option == 'Todos':
        df_tipo_energia=df_energias_renovables.groupby(['Tipo']).Proyecto.count()
    else:
        df_tipo_energia=df_energias_renovables[df_energias_renovables['Departamento']==option].groupby(['Tipo']).Proyecto.count()

    fig, ax = plt.subplots()
    ax.pie(df_tipo_energia, labels=df_tipo_energia.index, autopct='%1.1f%%')
    with st.container(border=True):
        st.header('Tipo de energia por departamento')
        st.pyplot(fig)
        
with tab4:

 # Mapa  1

    df_energia_departamento_mapa = df_energias_renovables.groupby(by=['Departamento', 'LATITUD','LONGITUD'], as_index=False).Energía_kWh_día.sum()
    df_energia_departamento_mapa['size'] = df_energia_departamento_mapa['Energía_kWh_día'] * 0.008
    with st.container(border=True):
        st.header('Mapa de energia generada')
        st.map(df_energia_departamento_mapa, latitude='LATITUD', longitude='LONGITUD', size='size')

    capas=pydeck.Layer(
        "ScatterplotLayer",
        data=df_energia_departamento_mapa,
        get_position=["LONGITUD", "LATITUD"],
        get_color="[255, 75, 75]",
        pickable=True,
        auto_highlight=True,
        get_radius="size"
    )

    vista_inicial=pydeck.ViewState(
        latitude=4,
        longitude=-74,
        zoom=4.5,
    )

    with st.container(border=True):
        st.header('Mapa de energia generada')
        st.pydeck_chart(
            pydeck.Deck(
                layers=capas,
                map_style=None,
                initial_view_state=vista_inicial,
                tooltip={"text": "{Departamento}\nEnergia_generada: {Energía_kWh_día}"}
            )
        )

with tab5:
    energia_generada = df_energias_renovables.groupby('Departamento').agg({'Energía_kWh_día': 'sum'})
    co2_generad0 = df_energias_renovables.groupby('Departamento').agg({'Emisiones_CO2_Ton_año': 'sum'})
    print('esta es la energia generada', energia_generada)

    resultado = df_energias_renovables.groupby('Departamento')[['Energía_kWh_día', 'Emisiones_CO2_Ton_año']].sum().reset_index()
    print('esta es el df', resultado)

    # Gráfico de barras
    fig = px.bar(resultado, x='Departamento', y=['Energía_kWh_día', 'Emisiones_CO2_Ton_año'],
                title='Generacion de energia vs co2', barmode='group')

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)
