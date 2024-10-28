import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import pydeck

st.set_page_config(layout="wide")

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1679580447808-b5b6911aacea");
             background-size: cover;
             background-position: center;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Call the function to add the background
add_bg_from_url()

#Leer archivo csv
def cargar_archivo():
    data = pd.read_csv('data/Meta_FNCER__Incorporar_en_la_matriz_energ_tica_nueva_capacidad_instalada_a_partir_de_Fuentes_No_Convencionales_de_Energ_a_Renovable_-_FNCER_20241003.csv')
    return data

def cargar_posicion():
    data = pd.read_excel('data/departamentos.xlsx', sheet_name='Departamentos')
    return data

df_posicion = cargar_posicion()
df_energias_renovables = cargar_archivo()

##Limpieza de datos
df_energias_renovables = df_energias_renovables.drop_duplicates()
df_energias_renovables['Fecha estimada FPO'] = df_energias_renovables['Fecha estimada FPO'].str[:10]
df_energias_renovables.loc[df_energias_renovables['Proyecto'] == 'PUERTA DE ORO Fase 1', 'Fecha estimada FPO'] = '2023-01-18'
df_energias_renovables.loc[df_energias_renovables['Proyecto'] == 'PUERTA DE ORO Fase 2', 'Fecha estimada FPO'] = '2025-12-31'
df_energias_renovables.loc[df_energias_renovables['Proyecto'] == 'OCELOTE', 'Fecha estimada FPO'] = '2021-01-21'

df_energias_renovables.columns = df_energias_renovables.columns.str.replace(' ', '_')
df_energias_renovables = pd.merge(df_energias_renovables, df_posicion[['Código_Departamento', 'LATITUD', 'LONGITUD']], on='Código_Departamento', how='left')
df_energias_renovables = df_energias_renovables.rename(columns={'Energía_[kWh/día]': 'Energía_kWh_día'})
df_energias_renovables = df_energias_renovables.rename(columns={'Emisiones_CO2_[Ton/año]': 'Emisiones_CO2_Ton_año'})
df_energias_renovables = df_energias_renovables.rename(columns={'Inversión_estimada_[COP]': 'Inversión_estimada_COP'})

# Realizar la operación y guardar el resultado en una nueva columna
Dias_año=365
Kg_Ton=1000
Horas_dia=24
kWh_MWh=1000
df_energias_renovables['Eficiencia_CO2'] = (df_energias_renovables['Emisiones_CO2_Ton_año'] / Dias_año*Kg_Ton) / df_energias_renovables['Energía_kWh_día']
df_energias_renovables['%Utilizacion'] = (df_energias_renovables['Energía_kWh_día']/(df_energias_renovables['Capacidad'] *Horas_dia*kWh_MWh))*100
df_energias_renovables['Valor_capacidad'] = df_energias_renovables['Inversión_estimada_COP']/df_energias_renovables['Capacidad']

st.title('Energía Renovable Sostenible y Eficiente')

tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs(["Datos", "Proyectos Por Departamento", "Tipo de energia", "Mapa", "Energia VS CO2", "Comparativa x departamentos","Comparativa x tipos de energia"])

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
        lista_departamento,
        key='selectbox_departamento'
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

    resultado = df_energias_renovables.groupby('Departamento')[['Energía_kWh_día', 'Emisiones_CO2_Ton_año']].sum().reset_index()

    # Gráfico de barras
    fig = px.bar(resultado, x='Departamento', y=['Energía_kWh_día', 'Emisiones_CO2_Ton_año'],
                title='Generacion de energia vs co2', barmode='group')

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)
with tab6:

    tipos_energia = df_energias_renovables['Tipo'].unique().tolist()
    seleccionados_tipos = st.multiselect('Seleccione los tipos de energía:', tipos_energia)

    # Filtrar el DataFrame según los tipos de energía seleccionados
    if seleccionados_tipos:
        df_filtrado = df_energias_renovables[df_energias_renovables['Tipo'].isin(seleccionados_tipos)]
    else:
        df_filtrado = df_energias_renovables

    # Calcular el promedio de Eficiencia_CO2 por departamento
    promedios_departamento = df_filtrado.groupby('Departamento')['Eficiencia_CO2'].mean().reset_index()

    # Crear gráfico de línea con Plotly
    fig = px.line(promedios_departamento, x='Departamento', y='Eficiencia_CO2', 
                  title='Promedio de Eficiencia_CO2 por Departamento',
                  labels={'Eficiencia_CO2': 'Eficiencia_CO2', 'Departamento': 'Departamento'},
                  markers=True)
        # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    promedios_departamento = df_filtrado.groupby('Departamento')['%Utilizacion'].mean().reset_index()

    # Crear gráfico de línea con Plotly
    fig = px.line(promedios_departamento, x='Departamento', y='%Utilizacion', 
                  title='Promedio de %Utilizacion por Departamento',
                  labels={'%Utilizacion': '% Utilizacion', 'Departamento': 'Departamento'},
                  markers=True)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    if seleccionados_tipos:
        df_filtrado = df_energias_renovables[df_energias_renovables['Tipo'].isin(seleccionados_tipos)]
    else:
        df_filtrado = df_energias_renovables

    # Calcular el promedio de Valor_capacidad por departamento
    promedios_departamento = df_filtrado.groupby('Departamento')['Valor_capacidad'].mean().reset_index()

    # Crear gráfico de línea con Plotly
    fig = px.line(promedios_departamento, x='Departamento', y='Valor_capacidad', 
                  title='Promedio de Valor_capacidad por Departamento',
                  labels={'Valor_capacidad': 'Valor de Capacidad (COP)', 'Departamento': 'Departamento'},
                  markers=True)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

with tab7:
   
    # Calcular promedios por tipo de energía
    promedios_tipo = df_filtrado.groupby('Tipo').agg({
        'Eficiencia_CO2': 'mean',
        '%Utilizacion': 'mean',
        'Valor_capacidad': 'mean'
    }).reset_index()

    # Gráfico 1: Promedio de Eficiencia_CO2 por Tipo de Energía
    fig1 = px.bar(promedios_tipo, x='Tipo', y='Eficiencia_CO2',
                  title='Promedio de Eficiencia_CO2 por Tipo de Energía',
                  labels={'Eficiencia_CO2': 'Eficiencia CO2'})
    st.plotly_chart(fig1)

    # Gráfico 2: Promedio de %Utilizacion por Tipo de Energía
    fig2 = px.bar(promedios_tipo, x='Tipo', y='%Utilizacion',
                  title='Promedio de %Utilizacion por Tipo de Energía',
                  labels={'%Utilizacion': '% Utilizacion'})
    st.plotly_chart(fig2)

    # Gráfico 3: Promedio de Valor_capacidad por Tipo de Energía
    fig3 = px.bar(promedios_tipo, x='Tipo', y='Valor_capacidad',
                  title='Promedio de Valor_capacidad por Tipo de Energía',
                  labels={'Valor_capacidad': 'Valor de Capacidad (COP)'})
    st.plotly_chart(fig3)