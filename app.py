import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import math

st.set_page_config(page_title="Simulasi Piket IT Del", page_icon="🍱", layout="wide")

st.title("🍱 Simulasi Sistem Piket Makan Siang IT Del")

# Sidebar Parameter
st.sidebar.header("Parameter")
total_meja = st.sidebar.number_input("Total Meja", value=60, min_value=1, step=1)
mahasiswa_per_meja = st.sidebar.number_input("Mahasiswa per Meja", value=3, min_value=1, step=1)
total_ompreng = total_meja * mahasiswa_per_meja
st.sidebar.success(f"📦 Total: {total_ompreng}")

tim_size = st.sidebar.number_input("Jumlah Piket", value=7, min_value=1, step=1)
kapasitas_angkut = st.sidebar.slider("Kapasitas Angkut", min_value=1, max_value=tim_size, value=7)

t_lauk = st.sidebar.number_input("Isi Lauk (detik)", min_value=10, max_value=120, value=45)
t_angkat = st.sidebar.number_input("Angkut (detik)", min_value=10, max_value=120, value=40)
t_nasi = st.sidebar.number_input("Isi Nasi (detik)", min_value=10, max_value=120, value=45)

start_time_str = st.sidebar.time_input("Waktu Mulai", value=datetime.strptime("07:00", "%H:%M").time())

st.sidebar.divider()
run_simulation = st.sidebar.button("🚀 Jalankan", type="primary", use_container_width=True)

if run_simulation:
    num_cycles = math.ceil(total_ompreng / kapasitas_angkut)
    time_coordination = 15
    
    data_sim = []
    current_time_offset = 0
    ompreng_processed = 0
    
    for i in range(1, num_cycles + 1):
        start_ompreng = ompreng_processed + 1
        end_ompreng = min((i * kapasitas_angkut), total_ompreng)
        jumlah_ompreng = end_ompreng - start_ompreng + 1
        
        lauk_start = current_time_offset
        lauk_end = lauk_start + t_lauk
        angkat_start = lauk_end
        angkat_end = angkat_start + t_angkat
        nasi_start = angkat_end
        nasi_end = nasi_start + t_nasi
        cycle_end = nasi_end
        
        if i < num_cycles:
            current_time_offset = lauk_end + time_coordination
        else:
            current_time_offset = cycle_end
        
        base_dt = datetime.combine(datetime.today(), start_time_str)
        t_start = base_dt + timedelta(seconds=lauk_start)
        t_end = base_dt + timedelta(seconds=cycle_end)
        
        data_sim.append({
            "Ronde": i,
            "Ompreng Awal": start_ompreng,
            "Ompreng Akhir": end_ompreng,
            "Jumlah Ompreng": jumlah_ompreng,
            "Waktu Mulai": t_start.strftime("%H:%M:%S"),
            "Waktu Selesai": t_end.strftime("%H:%M:%S"),
            "Akumulasi Waktu (menit)": round(cycle_end / 60, 2)
        })
        ompreng_processed = end_ompreng

    df_sim = pd.DataFrame(data_sim)
    total_duration_seconds = float(df_sim['Akumulasi Waktu (menit)'].max() * 60)
    final_finish_time = (datetime.combine(datetime.today(), start_time_str) + timedelta(seconds=total_duration_seconds)).strftime("%H:%M:%S")

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Laporan Ompreng", f"{total_ompreng}/{total_ompreng}")
    with col2:
        st.metric("⏳ Durasi Total", f"{total_duration_seconds/60:.1f} Menit")
    with col3:
        st.metric("🕒 Selesai Pukul", final_finish_time)

    st.divider()

    # Gantt Chart
    st.subheader("📅 Timeline Proses")
    gantt_data = []
    visual_offset = 0
    for _, row in df_sim.iterrows():
        ronde = row['Ronde']
        gantt_data.append({"Ronde": f"Ronde {ronde}", "Stage": "Isi Lauk", "Start": visual_offset, "Duration": t_lauk, "Color": "#2196F3"})
        gantt_data.append({"Ronde": f"Ronde {ronde}", "Stage": "Angkut", "Start": visual_offset + t_lauk, "Duration": t_angkat, "Color": "#FFC107"})
        gantt_data.append({"Ronde": f"Ronde {ronde}", "Stage": "Isi Nasi", "Start": visual_offset + t_lauk + t_angkat, "Duration": t_nasi, "Color": "#4CAF50"})
        if ronde < num_cycles:
            visual_offset = visual_offset + t_lauk + time_coordination
        else:
            visual_offset = visual_offset + t_lauk + t_angkat + t_nasi
    
    df_gantt = pd.DataFrame(gantt_data)
    fig_gantt = go.Figure()
    for color in df_gantt['Color'].unique():
        df_color = df_gantt[df_gantt['Color'] == color]
        fig_gantt.add_trace(go.Bar(
            y=df_color['Ronde'], x=df_color['Duration'], base=df_color['Start'],
            orientation='h', name=df_color['Stage'].iloc[0], marker_color=color, opacity=0.8
        ))
    fig_gantt.update_layout(height=400, xaxis_title="Waktu (Detik)", yaxis_title="Ronde", barmode='overlay', margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_gantt, use_container_width=True)

    # Progress Line
    st.subheader("📈 Progress Waktu")
    fig_line = px.line(df_sim, x="Ronde", y="Akumulasi Waktu (menit)", markers=True)
    fig_line.update_traces(line_color='#FF9800', line_width=3)
    fig_line.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_line, use_container_width=True)

    # Detail Table
    with st.expander("📋 Tabel Detail"):
        st.dataframe(df_sim[['Ronde', 'Ompreng Awal', 'Ompreng Akhir', 'Jumlah Ompreng', 'Waktu Mulai', 'Waktu Selesai']], use_container_width=True, hide_index=True)

else:
    st.info("Atur parameter di sidebar, lalu klik tombol Jalankan.")