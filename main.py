import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import altair as alt
import plotly.express as px
import numpy as np

#Leer archivo csv
def cargar_archivo():
    data = pd.read_csv('Meta_FNCER__Incorporar_en_la_matriz_energ_tica_nueva_capacidad_instalada_a_partir_de_Fuentes_No_Convencionales_de_Energ_a_Renovable_-_FNCER_20241003.csv')
    return data


df_energias_renovables = cargar_archivo()

st.title('Energía Renovable Sostenible y Eficiente')

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Datos", "Proyectos Por Departamento", "Tipo de energia", "Mapa", "Circular", "Histograma"])

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
    
    department_energy = df_energias_renovables.groupby(['Departamento']).Energia.sum().reset_index()

    # Show results
    st.write("Total Energy by Department:")
    st.write(department_energy)

    # Optionally, show a bar chart
    st.bar_chart(department_energy.set_index('Departamento'))
    
with tab5:
    chart_data = pd.DataFrame(
        {
            "col1": list(range(20)) * 3,
            "col2": np.random.randn(60),
            "col3": ["A"] * 20 + ["B"] * 20 + ["C"] * 20,
        }
    )

    st.bar_chart(chart_data, x="col1", y="col2", color="col3")
