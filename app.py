import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import json
import time

st.set_page_config(
    page_title="AI Laporan Keuangan UMKM",
    page_icon="💰",
    layout="wide"
)

# ===== SIDEBAR — API KEY & MENU =====
with st.sidebar:
    st.title("⚙️ Pengaturan")
    api_key = st.text_input("🔑 Gemini API Key", type="password", 
                             placeholder="AIza...")
    st.markdown("---")
    menu = st.radio("📌 Menu", [
        "📊 Dashboard",
        "➕ Input Transaksi (AI)",
        "🤖 Tanya AI",
        "⚠️ Deteksi Anomali"
    ])
    st.markdown("---")
    st.caption("AI Laporan Keuangan UMKM v2.0")

# ===== SETUP GEMINI =====
def setup_gemini(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

# ===== FUNGSI AI KATEGORISASI =====
def kategorisasi_ai(model, keterangan, nominal):
    prompt = f"""
    Kamu adalah asisten akuntansi UMKM Indonesia.
    
    Kategorikan transaksi berikut:
    Keterangan : "{keterangan}"
    Nominal    : Rp {nominal:,}
    
    Pilih jenis: Pemasukan atau Pengeluaran
    
    Pilih salah satu kategori:
    - Bahan Baku, Bahan Pembantu, Beban Gaji
    - Beban Sewa, Beban Utilitas, Beban Listrik
    - Beban Pemasaran, Beban Transportasi
    - Beban Keuangan, Beban Perawatan, Beban Pajak
    - Beban Perlengkapan, Pendapatan Penjualan, Modal Pemilik
    
    Jawab HANYA format JSON:
    {{"jenis": "...", "kategori": "...", "alasan": "..."}}
    """
    response = model.generate_content(prompt)
    hasil = response.text.strip()
    hasil = hasil.replace('```json','').replace('```','').strip()
    return json.loads(hasil)

# ===== FUNGSI AI INSIGHT =====
def generate_insight(model, df, tahun):
    df_t = df[df['tahun'] == tahun]
    pemasukan   = df_t[df_t.jenis=='Pemasukan']['nominal'].sum()
    pengeluaran = df_t[df_t.jenis=='Pengeluaran']['nominal'].sum()
    laba        = pemasukan - pengeluaran
    
    per_kat = df_t[df_t.jenis=='Pengeluaran'].groupby('kategori_akun')['nominal'].sum().to_dict()
    per_bulan = df_t.groupby('nama_bulan')['nominal_bersih'].sum().to_dict()
    
    prompt = f"""
    Kamu adalah konsultan keuangan UMKM Indonesia yang berpengalaman.
    
    Analisis data keuangan berikut untuk tahun {tahun}:
    - Total Pemasukan  : Rp {pemasukan:,}
    - Total Pengeluaran: Rp {pengeluaran:,}
    - Laba/Rugi        : Rp {laba:,}
    - Pengeluaran per kategori: {per_kat}
    - Laba/Rugi per bulan: {per_bulan}
    
    Berikan analisis dalam Bahasa Indonesia yang mudah dipahami pemilik UMKM:
    1. Kondisi keuangan secara keseluruhan
    2. 3 masalah utama yang perlu diperhatikan
    3. 3 rekomendasi konkret untuk meningkatkan profitabilitas
    
    Gunakan format yang rapi dengan emoji.
    """
    response = model.generate_content(prompt)
    return response.text

# ===== FUNGSI AI CHAT =====
def tanya_ai(model, pertanyaan, df):
    ringkasan = {
        'total_pemasukan': int(df[df.jenis=='Pemasukan']['nominal'].sum()),
        'total_pengeluaran': int(df[df.jenis=='Pengeluaran']['nominal'].sum()),
        'laba_rugi': int(df['nominal_bersih'].sum()),
        'total_transaksi': len(df),
        'kategori_pengeluaran': df[df.jenis=='Pengeluaran'].groupby('kategori_akun')['nominal'].sum().to_dict(),
        'periode': f"{df['tanggal'].min().strftime('%d/%m/%Y')} - {df['tanggal'].max().strftime('%d/%m/%Y')}"
    }
    
    prompt = f"""
    Kamu adalah asisten keuangan UMKM Indonesia.
    
    Data keuangan yang tersedia:
    {json.dumps(ringkasan, indent=2)}
    
    Pertanyaan dari pemilik usaha:
    "{pertanyaan}"
    
    Jawab dengan bahasa yang mudah dipahami, 
    gunakan angka Rupiah yang jelas, dan berikan 
    saran praktis jika relevan.
    """
    response = model.generate_content(prompt)
    return response.text

# ===== FUNGSI DETEKSI ANOMALI =====
def deteksi_anomali(model, df):
    stats = {
        'rata_nominal': float(df['nominal'].mean()),
        'std_nominal': float(df['nominal'].std()),
        'max_nominal': float(df['nominal'].max()),
        'transaksi_besar': df.nlargest(5,'nominal')[['tanggal','keterangan','jenis','nominal']].to_dict('records')
    }
    
    # Deteksi statistik: transaksi > mean + 2*std
    threshold = stats['rata_nominal'] + 2 * stats['std_nominal']
    anomali = df[df['nominal'] > threshold][['tanggal','keterangan','jenis','nominal','kategori_akun']]
    
    prompt = f"""
    Analisis transaksi keuangan UMKM berikut dan deteksi anomali:
    
    Statistik: {stats}
    Transaksi yang mencurigakan (di atas threshold): 
    {anomali.head(10).to_dict('records')}
    
    Berikan:
    1. Daftar transaksi yang perlu diperiksa
    2. Alasan kenapa mencurigakan
    3. Saran tindak lanjut
    
    Jawab dalam Bahasa Indonesia.
    """
    response = model.generate_content(prompt)
    return response.text, anomali

# ===== LOAD DATA =====
if 'df' not in st.session_state:
    st.session_state.df = None

# Upload file di semua halaman
file = st.file_uploader("📂 Upload CSV Transaksi", type=['csv'])
if file:
    df = pd.read_csv(file)
    if 'keterangan_tambahan' in df.columns:
        df = df.drop(columns=['keterangan_tambahan'])
    df['tanggal'] = pd.to_datetime(df['tanggal'], format='%d/%m/%Y')
    df['bulan'] = df['tanggal'].dt.to_period('M')
    df['tahun'] = df['tanggal'].dt.year
    df['nama_bulan'] = df['tanggal'].dt.strftime('%B %Y')
    df['nominal_bersih'] = df.apply(
        lambda x: x['nominal'] if x['jenis']=='Pemasukan' else -x['nominal'], axis=1
    )
    st.session_state.df = df
    st.success(f"✅ Data berhasil dimuat — {len(df):,} transaksi")

df = st.session_state.df

# ==========================================
# MENU 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Keuangan UMKM")
    
    if df is not None:
        tahun_list = sorted(df['tahun'].unique(), reverse=True)
        tahun_pilih = st.selectbox("📅 Pilih Tahun", tahun_list)
        df_t = df[df['tahun'] == tahun_pilih]

        pemasukan   = df_t[df_t.jenis=='Pemasukan']['nominal'].sum()
        pengeluaran = df_t[df_t.jenis=='Pengeluaran']['nominal'].sum()
        laba        = pemasukan - pengeluaran

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💵 Pemasukan",   f"Rp {pemasukan:,.0f}")
        col2.metric("💸 Pengeluaran", f"Rp {pengeluaran:,.0f}")
        col3.metric("📊 Laba/Rugi",   f"Rp {laba:,.0f}",
                    delta="Untung ✅" if laba >= 0 else "Rugi ❌")
        col4.metric("🧾 Transaksi",   f"{len(df_t):,}")

        st.markdown("---")

        # Chart pemasukan vs pengeluaran
        per_bulan = df_t.groupby(['nama_bulan','jenis'])['nominal'].sum().reset_index()
        per_bulan['sort'] = pd.to_datetime(per_bulan['nama_bulan'], format='%B %Y')
        per_bulan = per_bulan.sort_values('sort')
        fig1 = px.bar(per_bulan, x='nama_bulan', y='nominal', color='jenis',
                      barmode='group',
                      title=f'📈 Pemasukan vs Pengeluaran {tahun_pilih}',
                      color_discrete_map={'Pemasukan':'#2ecc71','Pengeluaran':'#e74c3c'})
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

        # Chart laba rugi
        laba_bulan = df_t.groupby('nama_bulan')['nominal_bersih'].sum().reset_index()
        laba_bulan['sort'] = pd.to_datetime(laba_bulan['nama_bulan'], format='%B %Y')
        laba_bulan = laba_bulan.sort_values('sort')
        laba_bulan['warna'] = laba_bulan['nominal_bersih'].apply(
            lambda x: '#2ecc71' if x >= 0 else '#e74c3c')
        fig2 = go.Figure(go.Bar(
            x=laba_bulan['nama_bulan'], y=laba_bulan['nominal_bersih'],
            marker_color=laba_bulan['warna'],
            text=[f"Rp {v:,.0f}" for v in laba_bulan['nominal_bersih']],
            textposition='outside'
        ))
        fig2.update_layout(title=f'📊 Laba/Rugi per Bulan {tahun_pilih}',
                           xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            per_kat = df_t[df_t.jenis=='Pengeluaran'].groupby('kategori_akun')['nominal'].sum().reset_index()
            fig3 = px.pie(per_kat, values='nominal', names='kategori_akun',
                          title='🔴 Komposisi Pengeluaran')
            st.plotly_chart(fig3, use_container_width=True)
        with col_b:
            per_masuk = df_t[df_t.jenis=='Pemasukan'].groupby('kategori_akun')['nominal'].sum().reset_index()
            fig4 = px.pie(per_masuk, values='nominal', names='kategori_akun',
                          title='🟢 Komposisi Pemasukan',
                          color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig4, use_container_width=True)

        # AI Insight
        st.markdown("---")
        st.subheader("🤖 AI Insight Keuangan")
        if api_key:
            if st.button("✨ Generate Analisis AI"):
                with st.spinner("AI sedang menganalisis data keuangan kamu..."):
                    model = setup_gemini(api_key)
                    insight = generate_insight(model, df, tahun_pilih)
                    st.markdown(insight)
        else:
            st.warning("⚠️ Masukkan Gemini API Key di sidebar untuk fitur AI")

    else:
        st.info("👆 Upload file CSV terlebih dahulu")

# ==========================================
# MENU 2: INPUT TRANSAKSI AI
# ==========================================
elif menu == "➕ Input Transaksi (AI)":
    st.title("➕ Input Transaksi dengan AI")
    st.markdown("Ketik transaksi dengan bahasa bebas — AI akan kategorikan otomatis!")

    if not api_key:
        st.warning("⚠️ Masukkan Gemini API Key di sidebar")
    else:
        col1, col2 = st.columns([2,1])
        with col1:
            keterangan = st.text_input("📝 Keterangan Transaksi",
                placeholder="contoh: bayar listrik kantor 500rb")
        with col2:
            nominal = st.number_input("💰 Nominal (Rp)", 
                min_value=0, step=1000, value=0)

        if st.button("🤖 Kategorikan dengan AI", type="primary"):
            if keterangan and nominal > 0:
                with st.spinner("AI sedang menganalisis..."):
                    model = setup_gemini(api_key)
                    hasil = kategorisasi_ai(model, keterangan, nominal)

                st.success("✅ Berhasil dikategorikan!")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Jenis", hasil['jenis'])
                col_b.metric("Kategori", hasil['kategori'])
                col_c.metric("Nominal", f"Rp {nominal:,}")

                st.info(f"💡 Alasan AI: {hasil.get('alasan','')}")

                # Simpan ke session state
                if 'transaksi_baru' not in st.session_state:
                    st.session_state.transaksi_baru = []
                
                st.session_state.transaksi_baru.append({
                    'keterangan': keterangan,
                    'nominal': nominal,
                    'jenis': hasil['jenis'],
                    'kategori_akun': hasil['kategori'],
                    'tanggal': pd.Timestamp.now().strftime('%d/%m/%Y')
                })
                st.success("✅ Transaksi disimpan ke daftar!")
            else:
                st.error("Isi keterangan dan nominal terlebih dahulu")

        # Tampilkan transaksi yang sudah diinput
        if 'transaksi_baru' in st.session_state and st.session_state.transaksi_baru:
            st.markdown("---")
            st.subheader("📋 Transaksi yang Sudah Diinput")
            df_baru = pd.DataFrame(st.session_state.transaksi_baru)
            st.dataframe(df_baru, use_container_width=True)

            csv = df_baru.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Transaksi Baru (CSV)",
                data=csv, file_name="transaksi_baru.csv", mime='text/csv')

            if st.button("🗑️ Reset Daftar"):
                st.session_state.transaksi_baru = []
                st.rerun()

# ==========================================
# MENU 3: TANYA AI
# ==========================================
elif menu == "🤖 Tanya AI":
    st.title("🤖 Tanya AI tentang Keuangan Kamu")

    if not api_key:
        st.warning("⚠️ Masukkan Gemini API Key di sidebar")
    elif df is None:
        st.info("👆 Upload file CSV terlebih dahulu")
    else:
        st.markdown("Tanyakan apapun tentang data keuangan kamu!")

        # Contoh pertanyaan
        st.markdown("**💡 Contoh pertanyaan:**")
        contoh = [
            "Bulan mana yang paling banyak untung?",
            "Kenapa bulan Januari selalu rugi?",
            "Pengeluaran terbesar saya apa?",
            "Bagaimana cara kurangi pengeluaran bahan baku?",
            "Apakah bisnis saya sehat secara keuangan?"
        ]
        for c in contoh:
            if st.button(f"💬 {c}"):
                st.session_state.pertanyaan = c

        pertanyaan = st.text_input("❓ Pertanyaan kamu:",
            value=st.session_state.get('pertanyaan',''),
            placeholder="Ketik pertanyaan tentang keuangan bisnis kamu...")

        if st.button("🚀 Tanya AI", type="primary"):
            if pertanyaan:
                with st.spinner("AI sedang menjawab..."):
                    model = setup_gemini(api_key)
                    jawaban = tanya_ai(model, pertanyaan, df)
                st.markdown("### 🤖 Jawaban AI:")
                st.markdown(jawaban)
            else:
                st.error("Tulis pertanyaan dulu!")

# ==========================================
# MENU 4: DETEKSI ANOMALI
# ==========================================
elif menu == "⚠️ Deteksi Anomali":
    st.title("⚠️ Deteksi Transaksi Anomali")

    if not api_key:
        st.warning("⚠️ Masukkan Gemini API Key di sidebar")
    elif df is None:
        st.info("👆 Upload file CSV terlebih dahulu")
    else:
        st.markdown("AI akan mendeteksi transaksi yang tidak wajar atau mencurigakan.")

        rata = df['nominal'].mean()
        std  = df['nominal'].std()
        threshold = rata + 2 * std

        st.info(f"📊 Rata-rata transaksi: Rp {rata:,.0f} | Threshold anomali: Rp {threshold:,.0f}")

        anomali = df[df['nominal'] > threshold]
        st.metric("🚨 Transaksi Anomali Ditemukan", f"{len(anomali)} transaksi")

        # Tampilkan tabel anomali
        st.subheader("📋 Daftar Transaksi Anomali")
        st.dataframe(
            anomali[['tanggal','keterangan','jenis','nominal','kategori_akun']]
            .sort_values('nominal', ascending=False)
            .reset_index(drop=True),
            use_container_width=True
        )

        if st.button("🤖 Analisis Anomali dengan AI", type="primary"):
            with st.spinner("AI sedang menganalisis transaksi anomali..."):
                model = setup_gemini(api_key)
                analisis, _ = deteksi_anomali(model, df)
            st.markdown("### 🤖 Analisis AI:")
            st.markdown(analisis)
