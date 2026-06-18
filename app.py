import streamlit as st
import pandas as pd

# Fungsi untuk merapikan format Rupiah
def format_rupiah(angka):
    return f"Rp {int(angka):,}".replace(",", ".")

# Pengaturan halaman
st.set_page_config(page_title="Kalkulator Closing", page_icon="☕")
st.title("☕ Kalkulator Closing Otomatis")
st.write("Upload laporan kasir hari ini, dan sistem akan menghitung pembagian amplop secara otomatis.")

# Input Uang Fisik (Agar langsung tahu setoran owner)
total_kas = st.number_input("💵 Total Uang Fisik di Kasir (setelah dikurangi kembalian):", min_value=0, step=1000)

# Tempat Upload File POS Kasir
pos_file = st.file_uploader("📂 Upload Rekap Penjualan Hari Ini (.xlsx)", type=['xlsx'])

if pos_file is not None and total_kas > 0:
    try:
        # 1. Baca Master Menu yang sudah kamu simpan di GitHub
        df_master = pd.read_excel("master_menu.xlsx")
        
        # 2. Baca file dari HP Kasir
        df_pos = pd.read_excel(pos_file)
        
        # 3. Samakan huruf menjadi huruf kecil agar pencocokan akurat
        df_master['Produk'] = df_master['Produk'].astype(str).str.lower().str.strip()
        df_pos['Produk'] = df_pos['Produk'].astype(str).str.lower().str.strip()
        
        # 4. Gabungkan Data (Pencocokan Otomatis)
        df_gabung = pd.merge(df_pos, df_master, on='Produk', how='left')
        
        df_gabung['Kategori Bahan Utama'] = df_gabung['Kategori Bahan Utama'].astype(str).str.lower().str.strip()
        df_gabung['Menggunakan Cup?'] = df_gabung['Menggunakan Cup?'].astype(str).str.upper().str.strip()
        
        # 5. Hitung Total Cup
        qty_bubuk = df_gabung[df_gabung['Kategori Bahan Utama'] == 'bubuk']['Item'].sum()
        qty_sirup = df_gabung[df_gabung['Kategori Bahan Utama'] == 'sirup']['Item'].sum()
        qty_cup = df_gabung[df_gabung['Menggunakan Cup?'] == 'YA']['Item'].sum()
        
        qty_bubuk = 0 if pd.isna(qty_bubuk) else int(qty_bubuk)
        qty_sirup = 0 if pd.isna(qty_sirup) else int(qty_sirup)
        qty_cup = 0 if pd.isna(qty_cup) else int(qty_cup)
        
        # 6. Hitung Nominal Uang Amplop
        uang_bubuk = qty_bubuk * 2500
        uang_sirup = qty_sirup * 2600
        uang_cup = qty_cup * 600
        
        listrik = 20000
        wifi = 20000
        cicilan = 100000
        
        total_amplop = uang_bubuk + uang_sirup + uang_cup + listrik + wifi + cicilan
        uang_owner = total_kas - total_amplop
        
        st.success("✅ Perhitungan Selesai!")
        
        # Peringatan jika ada menu baru yang belum dimasukkan ke Master Menu
        produk_tidak_dikenal = df_gabung[df_gabung['Kategori Bahan Utama'] == 'nan']['Produk'].tolist()
        if produk_tidak_dikenal:
            st.warning(f"⚠️ Ada produk terjual tapi tidak ada di master menu: {', '.join(produk_tidak_dikenal)}")
            
        st.subheader("✉️ Rincian Pembagian Amplop:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Bubuk:** {format_rupiah(uang_bubuk)}\n\n*({qty_bubuk} cup)*")
            st.info(f"**Sirup:** {format_rupiah(uang_sirup)}\n\n*({qty_sirup} cup)*")
            st.info(f"**Cup Plastik:** {format_rupiah(uang_cup)}\n\n*({qty_cup} cup)*")
            
        with col2:
            st.info(f"**Listrik:** {format_rupiah(listrik)}")
            st.info(f"**Wifi:** {format_rupiah(wifi)}")
            st.info(f"**Cicilan:** {format_rupiah(cicilan)}")
            
        st.markdown("---")
        st.header(f"💰 Sisa Uang Owner: {format_rupiah(uang_owner)}")
        
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {e}")
elif pos_file is not None and total_kas == 0:
    st.warning("⚠️ Masukkan total uang fisik di kasir terlebih dahulu untuk memunculkan hasil.")
