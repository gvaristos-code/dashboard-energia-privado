import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import tempfile
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Dashboard Energía - Parque Industrial",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 1rem; }
    h1 { color: #1f77b4; font-weight: bold; }
    h2 { color: #2c3e50; font-weight: bold; margin-top: 2rem; }
    h3 { color: #34495e; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def cargar_datos(ruta_archivo):
    df = pd.read_excel(ruta_archivo)
    df['Mes'] = pd.to_datetime(df['Mes'])
    df = df.sort_values('Mes').reset_index(drop=True)
    return df

def obtener_ultimos_6_meses(df, mes_seleccionado):
    meses_sorted = sorted(df['Mes'].unique())
    try:
        idx = list(meses_sorted).index(mes_seleccionado)
        inicio = max(0, idx - 5)
        meses_filtrados = meses_sorted[inicio:idx + 1]
        return df[df['Mes'].isin(meses_filtrados)].copy()
    except:
        return df.tail(6)

def obtener_mes_anterior(df, mes_seleccionado):
    meses_sorted = sorted(df['Mes'].unique())
    try:
        idx = list(meses_sorted).index(mes_seleccionado)
        return meses_sorted[idx - 1] if idx > 0 else None
    except:
        return None

def obtener_ultimos_3_meses(df, mes_seleccionado):
    meses_sorted = sorted(df['Mes'].unique())
    try:
        idx = list(meses_sorted).index(mes_seleccionado)
        inicio = max(0, idx - 2)
        return meses_sorted[inicio:idx + 1]
    except:
        return meses_sorted[-3:] if len(meses_sorted) >= 3 else meses_sorted

def obtener_ultimos_12_meses(df, mes_seleccionado):
    meses_sorted = sorted(df['Mes'].unique())
    try:
        idx = list(meses_sorted).index(mes_seleccionado)
        inicio = max(0, idx - 11)
        meses_filtrados = meses_sorted[inicio:idx + 1]
        return df[df['Mes'].isin(meses_filtrados)].copy()
    except:
        return df.tail(12)

def formatear_moneda(valor):
    return f"${valor:,.2f}"

def verificar_credenciales():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.markdown("""
            <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; color: white;'>
                <h1 style='color: white; margin: 0;'>🔐 DASHBOARD DE ENERGÍA</h1>
                <p style='font-size: 16px; margin: 0.5rem 0;'>Acceso Restringido - Parque Industrial</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.warning("⚠️ Debes iniciar sesión para acceder al dashboard")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔑 Iniciar Sesión")
            
            usuario = st.text_input("👤 Usuario:", placeholder="Ingresa tu usuario")
            contrasena = st.text_input("🔑 Contraseña:", type="password", placeholder="Ingresa tu contraseña")
            
            col_boton1, col_boton2 = st.columns(2)
            
            with col_boton1:
                if st.button("🚀 Ingresar", use_container_width=True):
                    USUARIO_CORRECTO = st.secrets["usuario"]
                    CONTRASENA_CORRECTA = st.secrets["contrasena"]
                    
                    if usuario == USUARIO_CORRECTO and contrasena == CONTRASENA_CORRECTA:
                        st.session_state.autenticado = True
                        st.success("✅ Acceso permitido")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
            
            with col_boton2:
                st.info("📝 Demo: demo / demo")
        
        st.stop()

verificar_credenciales()

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white;'>
        <h1 style='color: white; margin: 0;'>⚡ DASHBOARD DE ENERGÍA</h1>
        <p style='font-size: 18px; margin: 0.5rem 0;'>Parque Industrial - Análisis de Consumo y Facturación</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

RUTA_ARCHIVO_BASE = r"D:\FACT MENSUAL\CONSUMOS.xlsx"

st.sidebar.markdown("## 📂 Gestión de Datos")
st.sidebar.markdown("---")

col_cargar1, col_cargar2 = st.sidebar.columns(2)

with col_cargar1:
    usar_base = st.checkbox("📥 Usar base local", value=True, help="Carga la ruta fija del archivo")

with col_cargar2:
    if st.button("🔄 Limpiar cache", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Cache limpiado")

uploaded_file = None
if not usar_base:
    uploaded_file = st.sidebar.file_uploader("📁 O carga un archivo actualizado", type=['xlsx'])
    st.sidebar.info("📌 Si cargas un archivo aquí, se usará en lugar de la ruta local")

st.sidebar.markdown("---")

try:
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        df = cargar_datos(tmp_path)
        st.sidebar.success("✅ Archivo cargado desde upload")
    else:
        import base64
        import io
        datos_b64 = st.secrets["datos_excel_b64"]
        datos_bytes = base64.b64decode(datos_b64)
        df = pd.read_excel(io.BytesIO(datos_bytes))
        df['Mes'] = pd.to_datetime(df['Mes'])
        df = df.sort_values('Mes').reset_index(drop=True)
        st.sidebar.success("✅ Base cargada desde Secrets")
    
    meses_disponibles = sorted(df['Mes'].unique())
    tipos_cliente = sorted(df['TIPO CLIENTE'].unique())
    
    st.sidebar.markdown("## 🎛️ CONTROLES")
    st.sidebar.markdown("---")
    
    tipo_cliente_seleccionado = st.sidebar.selectbox("Selecciona Tipo de Cliente:", tipos_cliente, index=0)
    st.sidebar.markdown("")
    
    labels_meses = [mes.strftime('%B %Y').upper() for mes in meses_disponibles]
    mes_seleccionado_idx = st.sidebar.selectbox("Selecciona el mes de análisis:", range(len(meses_disponibles)), format_func=lambda x: labels_meses[x], index=len(meses_disponibles) - 1)
    mes_seleccionado = meses_disponibles[mes_seleccionado_idx]
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 📊 Información General")
    df_filtrado = df[df['TIPO CLIENTE'] == tipo_cliente_seleccionado]
    clientes_filtrados = df_filtrado['Cliente'].nunique()
    col_sid1, col_sid2 = st.sidebar.columns(2)
    with col_sid1:
        st.metric("Clientes", clientes_filtrados)
    with col_sid2:
        st.metric("Meses de Datos", len(meses_disponibles))
    
    st.sidebar.markdown("")
    st.sidebar.info(f"📌 Tipo: **{tipo_cliente_seleccionado}**\n📅 Mes: **{mes_seleccionado.strftime('%B %Y')}**")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumen 6M", "👤 Por Cliente", "🏆 Top 10", "⚠️ Desviaciones", "💡 Conclusiones"])
    
    with tab1:
        st.markdown(f"## 📊 Resumen Facturación - Últimos 6 Meses ({tipo_cliente_seleccionado})")
        st.markdown(f"**Período base:** {mes_seleccionado.strftime('%B de %Y')}")
        st.markdown("---")
        
        df_6m = obtener_ultimos_6_meses(df_filtrado, mes_seleccionado)
        resumen_6m = df_6m.groupby('Mes').agg({'Consumo Total': 'sum', '$ Total': 'sum'}).reset_index().sort_values('Mes')
        
        col1, col2, col3, col4 = st.columns(4)
        consumo_total = df_6m['Consumo Total'].sum()
        facturacion_total = df_6m['$ Total'].sum()
        consumo_promedio = df_6m.groupby('Mes')['Consumo Total'].sum().mean()
        facturacion_promedio = df_6m.groupby('Mes')['$ Total'].sum().mean()
        
        with col1:
            st.metric("Consumo Total 6M", f"{consumo_total:,.0f} kWh", f"{consumo_promedio:,.0f} kWh/mes")
        with col2:
            st.metric("Facturación Total 6M", formatear_moneda(facturacion_total), formatear_moneda(facturacion_promedio))
        with col3:
            consumo_mes_actual = df_6m[df_6m['Mes'] == mes_seleccionado]['Consumo Total'].sum()
            st.metric("Consumo Mes Actual", f"{consumo_mes_actual:,.0f} kWh")
        with col4:
            factura_mes_actual = df_6m[df_6m['Mes'] == mes_seleccionado]['$ Total'].sum()
            st.metric("Facturación Mes Actual", formatear_moneda(factura_mes_actual))
        
        st.markdown("")
        col_tabla, col_grafico = st.columns(2)
        
        with col_tabla:
            st.markdown("### 📋 Tabla Resumen")
            resumen_display = resumen_6m.copy()
            resumen_display['Mes'] = resumen_display['Mes'].dt.strftime('%b %Y')
            resumen_display['Consumo Total'] = resumen_display['Consumo Total'].apply(lambda x: f"{x:,.0f} kWh")
            resumen_display['$ Total'] = resumen_display['$ Total'].apply(formatear_moneda)
            st.dataframe(resumen_display, use_container_width=True, hide_index=True)
        
        with col_grafico:
            st.markdown("### 📈 Evolución Mensual")
            df_grafico = df_6m.groupby('Mes').agg({'Consumo Total': 'sum', '$ Total': 'sum'}).reset_index()
            df_grafico['Mes_str'] = df_grafico['Mes'].dt.strftime('%b %y')
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_grafico['Mes_str'], y=df_grafico['Consumo Total'], name='Consumo Total (kWh)', marker=dict(color='#1f77b4'), yaxis='y1'))
            fig.add_trace(go.Scatter(x=df_grafico['Mes_str'], y=df_grafico['$ Total'], name='$ Monto', marker=dict(color='#ff7f0e', size=8), yaxis='y2', mode='lines+markers', line=dict(width=3)))
            fig.update_layout(title="Consumo vs Facturación", xaxis=dict(title="Mes"), yaxis=dict(title="Consumo Total (kWh)", title_font=dict(color='#1f77b4')), yaxis2=dict(title="Facturación ($)", title_font=dict(color='#ff7f0e'), overlaying='y', side='right'), height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown(f"## 👤 Análisis Detallado por Cliente ({tipo_cliente_seleccionado})")
        st.markdown("---")
        
        clientes = sorted(df_filtrado['Cliente'].unique())
        cliente_seleccionado = st.selectbox("Selecciona un cliente:", clientes)
        
        df_cliente_12m = obtener_ultimos_12_meses(df_filtrado, mes_seleccionado)
        df_cliente_12m = df_cliente_12m[df_cliente_12m['Cliente'] == cliente_seleccionado]
        
        if len(df_cliente_12m) == 0:
            st.warning("❌ No hay datos disponibles para este cliente en los últimos 12 meses")
            st.info("ℹ️ Selecciona otro cliente o verifica los datos")
        else:
            st.markdown(f"### Cliente: {cliente_seleccionado}")
            st.markdown(f"**Períodos disponibles:** {len(df_cliente_12m)} meses")
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Consumo Total 12M", f"{df_cliente_12m['Consumo Total'].sum():,.0f} kWh")
            with col2:
                st.metric("Facturación Total 12M", formatear_moneda(df_cliente_12m['$ Total'].sum()))
            with col3:
                consumo_prom = df_cliente_12m['Consumo Total'].mean() if len(df_cliente_12m) > 0 else 0
                st.metric("Consumo Promedio", f"{consumo_prom:,.0f} kWh")
            with col4:
                fact_prom = df_cliente_12m['$ Total'].mean() if len(df_cliente_12m) > 0 else 0
                st.metric("Facturación Promedio", formatear_moneda(fact_prom))
            
            st.markdown("")
            col_tabla, col_grafico = st.columns(2)
            
            with col_tabla:
                st.markdown("### 📋 Histórico del Cliente (12 Meses)")
                df_tabla = df_cliente_12m[['Mes', 'Consumo Total', '$ Total', 'FP', 'Demanda']].copy()
                df_tabla['Mes'] = df_tabla['Mes'].dt.strftime('%b %Y')
                df_tabla['Consumo Total'] = df_tabla['Consumo Total'].apply(lambda x: f"{x:,.0f}")
                df_tabla['$ Total'] = df_tabla['$ Total'].apply(formatear_moneda)
                df_tabla['FP'] = df_tabla['FP'].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "N/A")
                df_tabla['Demanda'] = df_tabla['Demanda'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(df_tabla, use_container_width=True, hide_index=True)
            
            with col_grafico:
                st.markdown("### 📊 Evolución (12 Meses)")
                df_gráfico_cliente = df_cliente_12m.copy()
                df_gráfico_cliente['Mes_str'] = df_gráfico_cliente['Mes'].dt.strftime('%b %y')
                
                fig_cliente = go.Figure()
                fig_cliente.add_trace(go.Bar(x=df_gráfico_cliente['Mes_str'], y=df_gráfico_cliente['Consumo Total'], name='Consumo (kWh)', marker=dict(color='#2ca02c'), yaxis='y1'))
                fig_cliente.add_trace(go.Scatter(x=df_gráfico_cliente['Mes_str'], y=df_gráfico_cliente['$ Total'], name='Facturación ($)', marker=dict(color='#d62728', size=8), yaxis='y2', mode='lines+markers', line=dict(width=3)))
                fig_cliente.update_layout(title=f"Evolución - {cliente_seleccionado}", yaxis=dict(title="Consumo (kWh)"), yaxis2=dict(title="Facturación ($)", overlaying='y', side='right'), height=400, hovermode='x unified')
                st.plotly_chart(fig_cliente, use_container_width=True)
            
            st.markdown("")
            st.markdown("### ⚡ Análisis de Demanda")
            
            col_p, col_v, col_r, col_d = st.columns(4)
            with col_p:
                demanda_max = df_cliente_12m['Demanda'].max() if 'Demanda' in df_cliente_12m.columns and len(df_cliente_12m) > 0 else 0
                st.metric("Demanda Máxima", f"{demanda_max:,.0f} kW")
            with col_v:
                demanda_min = df_cliente_12m['Demanda'].min() if 'Demanda' in df_cliente_12m.columns and len(df_cliente_12m) > 0 else 0
                st.metric("Demanda Mínima", f"{demanda_min:,.0f} kW")
            with col_r:
                demanda_prom = df_cliente_12m['Demanda'].mean() if 'Demanda' in df_cliente_12m.columns and len(df_cliente_12m) > 0 else 0
                st.metric("Demanda Promedio", f"{demanda_prom:,.0f} kW")
            with col_d:
                punta = df_cliente_12m['Consumo Punta'].sum() if 'Consumo Punta' in df_cliente_12m.columns else 0
                st.metric("Consumo Punta", f"{punta:,.0f} kWh")
            
            st.markdown("")
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                st.markdown("#### 📊 Evolución de Demanda (12 Meses)")
                if 'Demanda' in df_cliente_12m.columns and len(df_cliente_12m) > 0:
                    df_demanda = df_cliente_12m[['Mes', 'Demanda']].copy()
                    df_demanda['Mes_str'] = df_demanda['Mes'].dt.strftime('%b %y')
                    
                    fig_demanda = go.Figure()
                    fig_demanda.add_trace(go.Bar(x=df_demanda['Mes_str'], y=df_demanda['Demanda'], name='Demanda (kW)', marker=dict(color='#9467bd'), yaxis='y1'))
                    fig_demanda.add_trace(go.Scatter(x=df_demanda['Mes_str'], y=df_demanda['Demanda'], name='Tendencia', marker=dict(color='#ff7f0e', size=8), yaxis='y1', mode='lines+markers', line=dict(width=3)))
                    fig_demanda.update_layout(title="Demanda Mensual", xaxis=dict(title="Mes"), yaxis=dict(title="Demanda (kW)"), height=350, hovermode='x unified')
                    st.plotly_chart(fig_demanda, use_container_width=True)
                else:
                    st.info("Sin datos de demanda disponibles")
            
            with col_b2:
                st.markdown("#### 📈 Evolución Mensual de Bandas")
                if 'Consumo Punta' in df_cliente_12m.columns:
                    df_bandas = df_cliente_12m[['Mes', 'Consumo Punta', 'Consumo Valle', 'Consumo Resto']].copy()
                    df_bandas['Mes_str'] = df_bandas['Mes'].dt.strftime('%b %y')
                    
                    fig_bandas = go.Figure()
                    fig_bandas.add_trace(go.Bar(x=df_bandas['Mes_str'], y=df_bandas['Consumo Punta'], name='Punta', marker=dict(color='#ff6b6b')))
                    fig_bandas.add_trace(go.Bar(x=df_bandas['Mes_str'], y=df_bandas['Consumo Valle'], name='Valle', marker=dict(color='#4ecdc4')))
                    fig_bandas.add_trace(go.Bar(x=df_bandas['Mes_str'], y=df_bandas['Consumo Resto'], name='Resto', marker=dict(color='#95e1d3')))
                    fig_bandas.update_layout(barmode='stack', title="Consumo por Banda", height=350, hovermode='x unified')
                    st.plotly_chart(fig_bandas, use_container_width=True)
                else:
                    st.info("Sin datos de bandas horarias")
    
    with tab3:
        st.markdown(f"## 🏆 Top 10 Clientes por Facturación ({tipo_cliente_seleccionado})")
        st.markdown(f"**Mes:** {mes_seleccionado.strftime('%B de %Y')}")
        st.markdown("---")
        
        df_mes = df_filtrado[df_filtrado['Mes'] == mes_seleccionado]
        
        if len(df_mes) == 0:
            st.warning("No hay datos disponibles para el mes seleccionado")
        else:
            mes_anterior = obtener_mes_anterior(df_filtrado, mes_seleccionado)
            meses_3m = obtener_ultimos_3_meses(df_filtrado, mes_seleccionado)
            df_3m = df_filtrado[df_filtrado['Mes'].isin(meses_3m)]
            
            top10 = df_mes.nlargest(10, '$ Total').copy()
            comparativas = []
            
            for _, row in top10.iterrows():
                cliente = row['Cliente']
                factura_mes = row['$ Total']
                factura_mes_ant = 0
                if mes_anterior:
                    factura_mes_ant = df_filtrado[(df_filtrado['Mes'] == mes_anterior) & (df_filtrado['Cliente'] == cliente)]['$ Total'].sum()
                factura_3m = df_3m[df_3m['Cliente'] == cliente]['$ Total'].sum() / len(meses_3m) if len(meses_3m) > 0 else 0
                var_mes_ant = ((factura_mes - factura_mes_ant) / factura_mes_ant * 100) if factura_mes_ant > 0 else 0
                var_3m = ((factura_mes - factura_3m) / factura_3m * 100) if factura_3m > 0 else 0
                
                comparativas.append({'Cliente': cliente, 'Factura Mes': factura_mes, 'Mes Anterior': factura_mes_ant, 'Var % (Mes Ant)': var_mes_ant, 'Promedio 3M': factura_3m, 'Var % (3M)': var_3m})
            
            df_comp = pd.DataFrame(comparativas)
            col_tabla, col_grafico = st.columns([1.2, 1])
            
            with col_tabla:
                st.markdown("### 📊 Tabla Comparativa")
                df_disp = df_comp.copy()
                df_disp['Factura Mes'] = df_disp['Factura Mes'].apply(formatear_moneda)
                df_disp['Mes Anterior'] = df_disp['Mes Anterior'].apply(formatear_moneda)
                df_disp['Var % (Mes Ant)'] = df_disp['Var % (Mes Ant)'].apply(lambda x: f"{x:+.1f}%")
                df_disp['Promedio 3M'] = df_disp['Promedio 3M'].apply(formatear_moneda)
                df_disp['Var % (3M)'] = df_disp['Var % (3M)'].apply(lambda x: f"{x:+.1f}%")
                st.dataframe(df_disp, use_container_width=True, hide_index=True)
            
            with col_grafico:
                st.markdown("### 📈 Top 10")
                df_top = df_comp.sort_values('Factura Mes')
                fig_top = go.Figure(data=[go.Bar(y=[f"{x}" for x in df_top['Cliente']], x=df_top['Factura Mes'], orientation='h', marker=dict(color='#1f77b4'), text=[formatear_moneda(x) for x in df_top['Factura Mes']], textposition='outside')])
                fig_top.update_layout(title="Facturación", height=400, xaxis=dict(title="Facturación ($)"), yaxis=dict(title="Cliente"))
                st.plotly_chart(fig_top, use_container_width=True)
            
            st.markdown("")
            col_v1, col_v2 = st.columns(2)
            
            with col_v1:
                st.markdown("### 📊 Variación vs Mes Anterior (%)")
                df_var = df_comp.sort_values('Var % (Mes Ant)')
                colors = ['#d62728' if x < 0 else '#2ca02c' for x in df_var['Var % (Mes Ant)']]
                fig_var = go.Figure(data=[go.Bar(y=[f"{x}" for x in df_var['Cliente']], x=df_var['Var % (Mes Ant)'], orientation='h', marker=dict(color=colors), text=[f"{x:+.1f}%" for x in df_var['Var % (Mes Ant)']], textposition='outside')])
                fig_var.update_layout(height=400, xaxis=dict(title="Variación (%)"), yaxis=dict(title="Cliente"))
                st.plotly_chart(fig_var, use_container_width=True)
            
            with col_v2:
                st.markdown("### 📊 Variación vs Promedio 3M (%)")
                df_var2 = df_comp.sort_values('Var % (3M)')
                colors2 = ['#d62728' if x < 0 else '#2ca02c' for x in df_var2['Var % (3M)']]
                fig_var2 = go.Figure(data=[go.Bar(y=[f"{x}" for x in df_var2['Cliente']], x=df_var2['Var % (3M)'], orientation='h', marker=dict(color=colors2), text=[f"{x:+.1f}%" for x in df_var2['Var % (3M)']], textposition='outside')])
                fig_var2.update_layout(height=400, xaxis=dict(title="Variación (%)"), yaxis=dict(title="Cliente"))
                st.plotly_chart(fig_var2, use_container_width=True)
    
    with tab4:
        st.markdown(f"## ⚠️ Análisis de Desviaciones ({tipo_cliente_seleccionado})")
        st.markdown(f"**Mes:** {mes_seleccionado.strftime('%B de %Y')}")
        st.markdown("---")
        
        df_mes = df_filtrado[df_filtrado['Mes'] == mes_seleccionado]
        
        if len(df_mes) == 0:
            st.warning("No hay datos disponibles para analizar desviaciones")
        else:
            meses_sorted = sorted(df_filtrado['Mes'].unique())
            idx_mes = list(meses_sorted).index(mes_seleccionado)
            inicio = max(0, idx_mes - 11)
            df_historico = df_filtrado[df_filtrado['Mes'].isin(meses_sorted[inicio:idx_mes + 1])]
            
            stats = df_historico.groupby('Cliente').agg({'Consumo Total': ['mean', 'std'], '$ Total': ['mean', 'std'], 'Demanda': ['mean', 'std']}).reset_index()
            stats.columns = ['Cliente', 'Cons_mean', 'Cons_std', 'Fact_mean', 'Fact_std', 'Dem_mean', 'Dem_std']
            stats[['Cons_std', 'Fact_std', 'Dem_std']] = stats[['Cons_std', 'Fact_std', 'Dem_std']].fillna(0)
            
            df_mes_stats = df_mes.merge(stats, on='Cliente', how='left')
            df_mes_stats['Desv_Consumo'] = (df_mes_stats['Consumo Total'] - df_mes_stats['Cons_mean']) / (df_mes_stats['Cons_std'] + 1)
            df_mes_stats['Desv_Factura'] = (df_mes_stats['$ Total'] - df_mes_stats['Fact_mean']) / (df_mes_stats['Fact_std'] + 1)
            df_mes_stats['Desv_Demanda'] = (df_mes_stats['Demanda'] - df_mes_stats['Dem_mean']) / (df_mes_stats['Dem_std'] + 1)
            df_mes_stats['Magnitud_Desv'] = (abs(df_mes_stats['Desv_Consumo']) + abs(df_mes_stats['Desv_Factura']) + abs(df_mes_stats['Desv_Demanda'])) / 3
            
            umbral = 1.5
            df_desv = df_mes_stats[(abs(df_mes_stats['Desv_Consumo']) > umbral) | (abs(df_mes_stats['Desv_Factura']) > umbral) | (abs(df_mes_stats['Desv_Demanda']) > umbral)].sort_values('Magnitud_Desv', ascending=False)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Clientes", len(df_mes))
            with col2:
                st.metric("Con Desviaciones", len(df_desv))
            with col3:
                st.metric("% Desviados", f"{(len(df_desv)/len(df_mes)*100):.1f}%" if len(df_mes) > 0 else "0%")
            with col4:
                st.metric("Umbral", f"{umbral}σ")
            
            st.markdown("")
            
            if len(df_desv) > 0:
                st.markdown("### 📋 Clientes con Mayor Desviación")
                df_tabla_desv = df_desv[['Cliente', 'Consumo Total', 'Cons_mean', 'Desv_Consumo', '$ Total', 'Fact_mean', 'Desv_Factura']].copy()
                df_tabla_desv['Consumo Total'] = df_tabla_desv['Consumo Total'].apply(lambda x: f"{x:,.0f}")
                df_tabla_desv['Cons_mean'] = df_tabla_desv['Cons_mean'].apply(lambda x: f"{x:,.0f}")
                df_tabla_desv['Desv_Consumo'] = df_tabla_desv['Desv_Consumo'].apply(lambda x: f"{x:+.2f}σ")
                df_tabla_desv['$ Total'] = df_tabla_desv['$ Total'].apply(formatear_moneda)
                df_tabla_desv['Fact_mean'] = df_tabla_desv['Fact_mean'].apply(formatear_moneda)
                df_tabla_desv['Desv_Factura'] = df_tabla_desv['Desv_Factura'].apply(lambda x: f"{x:+.2f}σ")
                st.dataframe(df_tabla_desv, use_container_width=True, hide_index=True)
                
                st.markdown("")
                col_d1, col_d2 = st.columns(2)
                
                with col_d1:
                    st.markdown("#### Desviación de Consumo")
                    df_plot = df_desv.nlargest(15, 'Magnitud_Desv').sort_values('Desv_Consumo')
                    colors = ['#d62728' if x < 0 else '#2ca02c' for x in df_plot['Desv_Consumo']]
                    fig = go.Figure(data=[go.Bar(y=[f"{x}" for x in df_plot['Cliente']], x=df_plot['Desv_Consumo'], orientation='h', marker=dict(color=colors), text=[f"{x:+.2f}σ" for x in df_plot['Desv_Consumo']], textposition='outside')])
                    fig.update_layout(title="Desviaciones Consumo", height=400, xaxis=dict(title="Desviación (σ)"), yaxis=dict(title="Cliente"))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_d2:
                    st.markdown("#### Desviación de Facturación")
                    df_plot2 = df_desv.nlargest(15, 'Magnitud_Desv').sort_values('Desv_Factura')
                    colors2 = ['#d62728' if x < 0 else '#2ca02c' for x in df_plot2['Desv_Factura']]
                    fig2 = go.Figure(data=[go.Bar(y=[f"{x}" for x in df_plot2['Cliente']], x=df_plot2['Desv_Factura'], orientation='h', marker=dict(color=colors2), text=[f"{x:+.2f}σ" for x in df_plot2['Desv_Factura']], textposition='outside')])
                    fig2.update_layout(title="Desviaciones Facturación", height=400, xaxis=dict(title="Desviación (σ)"), yaxis=dict(title="Cliente"))
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("✅ No se detectaron desviaciones significativas en este período")
    
    with tab5:
        st.markdown(f"## 💡 Análisis y Conclusiones ({tipo_cliente_seleccionado})")
        st.markdown(f"**Mes Seleccionado:** {mes_seleccionado.strftime('%B de %Y')}")
        st.markdown("---")
        
        df_mes = df_filtrado[df_filtrado['Mes'] == mes_seleccionado]
        df_6m = obtener_ultimos_6_meses(df_filtrado, mes_seleccionado)
        
        if len(df_mes) == 0:
            st.warning("No hay datos disponibles para mostrar conclusiones")
        else:
            factura_mes = df_mes['$ Total'].sum()
            consumo_mes = df_mes['Consumo Total'].sum()
            demanda_mes = df_mes['Demanda'].mean() if 'Demanda' in df_mes.columns else 0
            
            factura_prom = df_6m.groupby('Mes')['$ Total'].sum().mean()
            consumo_prom = df_6m.groupby('Mes')['Consumo Total'].sum().mean()
            
            var_fact = ((factura_mes - factura_prom) / factura_prom * 100) if factura_prom > 0 else 0
            var_cons = ((consumo_mes - consumo_prom) / consumo_prom * 100) if consumo_prom > 0 else 0
            
            st.markdown("### 📌 Resumen Ejecutivo")
            st.markdown(f"**Período:** {mes_seleccionado.strftime('%B de %Y')}")
            st.markdown(f"**Métricas Principales:**")
            st.markdown(f"- 💰 Facturación Total: {formatear_moneda(factura_mes)}")
            st.markdown(f"- ⚡ Consumo Total: {consumo_mes:,.0f} kWh")
            st.markdown(f"- 🔌 Demanda Promedio: {demanda_mes:,.0f} kW")
            st.markdown(f"- 📊 Clientes: {len(df_mes)}")
            
            st.markdown("---")
            st.markdown("### 📈 Análisis Comparativo (vs Promedio 6M anterior)")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if var_fact > 0:
                    st.success(f"**↑ Facturación:** {var_fact:+.1f}% vs promedio 6M")
                else:
                    st.warning(f"**↓ Facturación:** {var_fact:+.1f}% vs promedio 6M")
            with col_a2:
                if var_cons > 0:
                    st.success(f"**↑ Consumo:** {var_cons:+.1f}% vs promedio 6M")
                else:
                    st.warning(f"**↓ Consumo:** {var_cons:+.1f}% vs promedio 6M")
            
            st.markdown("---")
            st.markdown("### 🎯 Recomendaciones Clave")
            
            recomendaciones = []
            top3 = df_mes.nlargest(3, '$ Total')
            pct_top3 = (top3['$ Total'].sum() / factura_mes * 100) if factura_mes > 0 else 0
            recomendaciones.append(f"**1. Monitoreo Top 3:** Los 3 mayores consumidores representan {pct_top3:.1f}% de la facturación")
            
            if var_cons > 10:
                recomendaciones.append(f"**2. Aumento significativo:** Consumo {var_cons:.1f}% arriba del promedio - revisar eficiencia")
            elif var_cons < -10:
                recomendaciones.append(f"**3. Reducción en consumo:** {abs(var_cons):.1f}% por debajo del promedio")
            
            fp_prom = df_mes['FP'].mean() if 'FP' in df_mes.columns else 0
            if fp_prom < 0.9:
                recomendaciones.append(f"**4. Factor de potencia bajo:** {fp_prom:.3f} - implementar correcciones")
            
            for rec in recomendaciones:
                st.markdown(f"- {rec}")
            
            st.markdown("---")
            st.markdown("### 📊 KPIs Principales")
            col_k1, col_k2, col_k3 = st.columns(3)
            with col_k1:
                costo_kwh = factura_mes / consumo_mes if consumo_mes > 0 else 0
                st.metric("Costo promedio/kWh", f"${costo_kwh:.3f}")
            with col_k2:
                st.metric("Factor de Potencia", f"{fp_prom:.3f}", "Ideal: >0.95")
            with col_k3:
                st.metric("Demanda Promedio", f"{demanda_mes:,.0f} kW")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    import traceback

    st.error(traceback.format_exc())


