import streamlit as st
import pandas as pd
import datetime
import requests

# Fungsi untuk merapikan format Rupiah
def format_rupiah(angka):
    return f"Rp {int(angka):,}".replace(",", ".")

# --- MASUKKAN URL WEBHOOK MAKE.COM DI BAWAH INI ---
# Contoh: WEBHOOK_URL = "https://hook.us1.make.com/abcde12345..."
WEBHOOK_URL = "https://hook.us2.make.com/ghy4puzerxjxdevebxfrgh15zwq5et76"
# --------------------------------------------------

# Pengaturan halaman
st.set_page_config(page_title="Kalkulator Closing", page_icon="☕", layout="wide")
st.title("☕ Kalkulator Closing Otomatis")
st.write("Masukkan pengeluaran harian dan upload laporan kasir hari ini. Sistem akan menghitung rincian omset dan sisa bersih untuk owner.")

st.markdown("### 📝 Input Pengeluaran Harian")
col_input1, col_input2 = st.columns(2)
with col_input1:
    uang_kasir = st.number_input("💵 Uang Kasir (Rp)", min_value=0, step=1000)
    uang_makan = st.number_input("🍱 Uang Makan (Rp)", min_value=0, step=1000)
    
with col_input2:
    gaji_1 = st.number_input("🧑‍🍳 Gaji Karyawan 1 (Rp)", min_value=0, step=1000)
    gaji_2 = st.number_input("🧑‍🍳 Gaji Karyawan 2 (Rp)", min_value=0, step=1000)
    gaji_3 = st.number_input("🧑‍🍳 Gaji Karyawan 3 (Rp)", min_value=0, step=1000)

st.markdown("### 📂 Upload Data Kasir")
pos_file = st.file_uploader("Upload Rekap Penjualan Hari Ini (.xlsx)", type=['xlsx'])

if pos_file is not None:
    try:
        df_master = pd.read_excel("master_menu.xlsx")
        df_pos = pd.read_excel(pos_file)
        
        df_pos = df_pos.dropna(subset=['Produk'])
        df_pos = df_pos[df_pos['Produk'].astype(str).str.lower().str.strip() != 'total']

        if 'Penjualan' in df_pos.columns:
            omset = df_pos['Penjualan'].sum()
            omset = 0 if pd.isna(omset) else int(omset)
        else:
            omset = 0
            st.warning("⚠️ Kolom 'Penjualan' tidak ditemukan di file Excel.")

        df_master['Produk'] = df_master['Produk'].astype(str).str.lower().str.strip()
        df_pos['Produk'] = df_pos['Produk'].astype(str).str.lower().str.strip()
        
        df_gabung = pd.merge(df_pos, df_master, on='Produk', how='left')
        df_gabung['Kategori Bahan Utama'] = df_gabung['Kategori Bahan Utama'].astype(str).str.lower().str.strip()
        df_gabung['Menggunakan Cup?'] = df_gabung['Menggunakan Cup?'].astype(str).str.upper().str.strip()
        
        qty_bubuk = df_gabung[df_gabung['Kategori Bahan Utama'] == 'bubuk']['Item'].sum()
        qty_sirup = df_gabung[df_gabung['Kategori Bahan Utama'] == 'sirup']['Item'].sum()
        qty_cup = df_gabung[df_gabung['Menggunakan Cup?'] == 'YA']['Item'].sum()
        
        qty_bubuk = 0 if pd.isna(qty_bubuk) else int(qty_bubuk)
        qty_sirup = 0 if pd.isna(qty_sirup) else int(qty_sirup)
        qty_cup = 0 if pd.isna(qty_cup) else int(qty_cup)
        
        uang_bubuk = qty_bubuk * 2500
        uang_sirup = qty_sirup * 2600
        uang_cup = qty_cup * 600
        
        listrik = 20000
        wifi = 20000
        cicilan = 100000
        
        total_potongan = (uang_bubuk + uang_sirup + uang_cup + 
                          listrik + wifi + cicilan + 
                          uang_kasir + uang_makan + 
                          gaji_1 + gaji_2 + gaji_3)
                          
        uang_owner = omset - total_potongan
        
        st.success("✅ Perhitungan Selesai!")
        
        produk_tidak_dikenal = df_gabung[df_gabung['Kategori Bahan Utama'] == 'nan']['Produk'].tolist()
        if produk_tidak_dikenal:
            st.warning(f"⚠️ Ada produk terjual tapi tidak ada di master menu: {', '.join(produk_tidak_dikenal)}")
            
        st.markdown("---")
        st.header(f"📊 Total Omset Hari Ini: {format_rupiah(omset)}")
        st.markdown("---")
        
        st.subheader("✉️ Rincian Alokasi Omset:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**📦 Modal Bahan Baku**")
            st.info(f"**Bubuk:** {format_rupiah(uang_bubuk)}")
            st.info(f"**Sirup:** {format_rupiah(uang_sirup)}")
            st.info(f"**Cup:** {format_rupiah(uang_cup)}")
        with col2:
            st.markdown("**🏢 Operasional Harian**")
            st.info(f"**Listrik:** {format_rupiah(listrik)}")
            st.info(f"**Wifi:** {format_rupiah(wifi)}")
            st.info(f"**Cicilan:** {format_rupiah(cicilan)}")
            st.info(f"**Uang Kasir:** {format_rupiah(uang_kasir)}")
            st.info(f"**Uang Makan:** {format_rupiah(uang_makan)}")
        with col3:
            st.markdown("**🧑‍🍳 Gaji Tim**")
            st.info(f"**Karyawan 1:** {format_rupiah(gaji_1)}")
            st.info(f"**Karyawan 2:** {format_rupiah(gaji_2)}")
            st.info(f"**Karyawan 3:** {format_rupiah(gaji_3)}")
            
        st.markdown("---")
        if uang_owner >= 0:
            st.success(f"### 💰 Sisa Uang Owner (Profit & Restock): {format_rupiah(uang_owner)}")
        else:
            st.error(f"### ⚠️ Sisa Uang Owner Minus: {format_rupiah(uang_owner)}")
            
        # --- TOMBOL SIMPAN KE DATABASE ---
        st.markdown("---")
        st.subheader("💾 Simpan ke Database Laporan Bulanan")
        if st.button("Simpan Laporan Hari Ini"):
            waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            payload = {
                "tanggal": waktu_sekarang,
                "omset": omset,
                "bubuk": uang_bubuk,
                "sirup": uang_sirup,
                "cup": uang_cup,
                "listrik": listrik,
                "wifi": wifi,
                "cicilan": cicilan,
                "kasir": uang_kasir,
                "makan": uang_makan,
                "gaji1": gaji_1,
                "gaji2": gaji_2,
                "gaji3": gaji_3,
                "profit": uang_owner
            }
            
            if WEBHOOK_URL == "URL_MAKE_COM_KAMU_DISINI":
                st.warning("⚠️ URL Webhook belum dimasukkan di dalam kode app.py!")
            else:
                try:
                    response = requests.post(WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        st.success("✅ Laporan berhasil dikirim ke Buku Kas Owner!")
                    else:
                        st.error("❌ Gagal menyimpan data. Cek kembali Make.com.")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan pengiriman data: {e}")
                    
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {e}")
