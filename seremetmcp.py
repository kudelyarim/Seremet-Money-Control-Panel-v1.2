import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import requests
from datetime import datetime


# =========================================================
# VERİTABANI
# =========================================================

db = sqlite3.connect("seremet.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS islemler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tip TEXT NOT NULL,
    kategori TEXT NOT NULL,
    aciklama TEXT,
    tutar REAL NOT NULL,
    tarih TEXT NOT NULL
)
""")

db.commit()

# Persistent notes storage
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
""")
db.commit()

# Borçlar ve kısmi ödeme geçmişi
cursor.execute("""
CREATE TABLE IF NOT EXISTS borclar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kaynak TEXT NOT NULL,
    baslik TEXT NOT NULL,
    toplam_borc REAL NOT NULL,
    kalan_borc REAL NOT NULL,
    olusturma_tarihi TEXT NOT NULL,
    son_odeme_tarihi TEXT,
    notlar TEXT,
    durum TEXT NOT NULL DEFAULT 'Açık'
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS borc_odemeleri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    borc_id INTEGER NOT NULL,
    tutar REAL NOT NULL,
    tarih TEXT NOT NULL,
    notlar TEXT,
    FOREIGN KEY (borc_id) REFERENCES borclar(id)
)
""")

# Kredi kartları
cursor.execute("""
CREATE TABLE IF NOT EXISTS kredi_kartlari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banka TEXT NOT NULL,
    kart_adi TEXT NOT NULL,
    kart_agi TEXT NOT NULL,
    limit_tutari REAL NOT NULL,
    guncel_borc REAL NOT NULL DEFAULT 0,
    ekstre_kesim_tarihi TEXT,
    son_odeme_tarihi TEXT
)
""")
db.commit()


# =========================================================
# RENKLER
# =========================================================
BG = "#0b1220"
CARD = "#121d2e"
CARD2 = "#1b2a3e"
TEXT = "#edf3fb"
MUTED = "#9aa9bd"
GREEN = "#35d39a"
RED = "#ff6878"
GOLD = "#f2bd55"
SILVER = "#bac7d8"
BLUE = "#65a5ff"
BORDER = "#26364b"
HOVER = "#243852"


# =========================================================
# ANA PENCERE
# =========================================================

app = tk.Tk()

app.title("Seremet Money Control Panel")
app.geometry("1240x800")
app.minsize(1100, 700)
app.configure(bg=BG)

# Modern, consistent table and form styling
style = ttk.Style(app)
try:
    style.theme_use("clam")
except tk.TclError:
    pass
style.configure(
    "Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD,
    rowheight=34, borderwidth=0, font=("Segoe UI", 10)
)
style.configure(
    "Treeview.Heading", background=CARD2, foreground=TEXT,
    relief="flat", borderwidth=0, padding=(10, 10),
    font=("Segoe UI", 10, "bold")
)
style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", "#ffffff")])
style.map("Treeview.Heading", background=[("active", HOVER)])
style.configure("TNotebook", background=BG, borderwidth=0)
style.configure("TNotebook.Tab", background=CARD2, foreground=TEXT, padding=(14, 8), font=("Segoe UI", 10, "bold"))
style.map("TNotebook.Tab", background=[("selected", BLUE)], foreground=[("selected", "#ffffff")])
style.configure("TCombobox", fieldbackground=CARD2, background=CARD2, foreground=TEXT, arrowcolor=TEXT, padding=6)


# =========================================================
# MODERN ANA YERLEŞİM
# =========================================================

shell = tk.Frame(app, bg=BG)
shell.pack(fill="both", expand=True)

sidebar = tk.Frame(shell, bg="#121720", width=205)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

content = tk.Frame(shell, bg=BG)
content.pack(side="left", fill="both", expand=True)

tk.Label(sidebar, text="SM", bg="#121720", fg=BLUE,
         font=("Segoe UI", 27, "bold")).pack(anchor="w", padx=22, pady=(24, 0))
tk.Label(sidebar, text="MONEY CONTROL", bg="#121720", fg=TEXT,
         font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=22, pady=(0, 28))
tk.Label(sidebar, text="WORKSPACE", bg="#121720", fg=MUTED,
         font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=18, pady=(0, 8))

# =========================================================
# BAŞLIK
# =========================================================

header = tk.Frame(
    content,
    bg=BG
)

header.pack(
    fill="x",
    padx=30,
    pady=(22, 8)
)


tk.Label(
    header,
    text='SEREMET MONEY CONTROL PANEL',
    bg=BG,
    fg=TEXT,
    font=("Segoe UI", 23, "bold")
).pack(side="left")


tarih_label = tk.Label(
    header,
    text=datetime.now().strftime("%d.%m.%Y"),
    bg=BG,
    fg=MUTED,
    font=("Segoe UI", 8)
)
version_label = tk.Label(
    header,
    text="v1.2",
    bg=BG,
    fg="#ffffff",
    font=("Segoe UI", 10)
)
version_label.pack(side="right", padx=10, pady=10)
tarih_label.pack(
    side="right",
    pady=10
)
# =========================================================
# SEKME ALANI
# =========================================================

sekme_cubugu = tk.Frame(sidebar, bg="#121720")
sekme_cubugu.pack(fill="x", padx=30, pady=(8, 12))
sekme_cubugu.configure(highlightbackground=BORDER, highlightthickness=1)

ana_sayfa_butonu = tk.Button(
    sekme_cubugu,
    text='Main',
    bg=CARD2,
    fg=TEXT,
    activebackground=HOVER,
    activeforeground=TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    anchor="w",
    padx=16,
    pady=12
)
ana_sayfa_butonu.pack(fill="x", pady=3)

varliklar_butonu = tk.Button(
    sekme_cubugu,
    text='Assets',
    bg=CARD2,
    fg=TEXT,
    activebackground=HOVER,
    activeforeground=TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    anchor="w",
    padx=16,
    pady=12
)
varliklar_butonu.pack(fill="x", pady=3)

notlar_butonu = tk.Button(
    sekme_cubugu,
    text="My Notes",
    bg=CARD2,
    fg=TEXT,
    activebackground=HOVER,
    activeforeground=TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    anchor="w",
    padx=16,
    pady=12
)
notlar_butonu.pack(fill="x", pady=3)

borclar_butonu = tk.Button(
    sekme_cubugu, text="Debts", bg=CARD2, fg=TEXT, activebackground=HOVER, activeforeground=TEXT,
    font=("Segoe UI", 10, "bold"), relief="flat", bd=0, anchor="w", padx=16, pady=12
)
borclar_butonu.pack(fill="x", pady=3)

kredi_kartlari_butonu = tk.Button(
    sekme_cubugu, text="Credit Cards", bg=CARD2, fg=TEXT, activebackground=HOVER, activeforeground=TEXT,
    font=("Segoe UI", 10, "bold"), relief="flat", bd=0, anchor="w", padx=16, pady=12
)
kredi_kartlari_butonu.pack(fill="x", pady=3)


# =========================================================
# ÖZET KARTLARI
# =========================================================

summary = tk.Frame(
    content,
    bg=BG
)

summary.pack(
    fill="x",
    padx=30,
    pady=12
)


def kart(parent, baslik, deger, renk):

    frame = tk.Frame(
        parent,
        bg=CARD,
        width=240,
        height=122,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=baslik,
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=18,
        pady=(17, 2)
    )

    label = tk.Label(
        frame,
        text=deger,
        bg=CARD,
        fg=renk,
        font=("Segoe UI", 19, "bold")
    )

    label.pack(
        anchor="w",
        padx=18
    )

    return label


gelir_label = kart(
    summary,
    "TOTAL REVENUE",
    "0.00 TRY",
    GREEN
)

gider_label = kart(
    summary,
    "TOTAL EXPENSES",
    "0.00 TRY",
    RED
)

net_label = kart(
    summary,
    "NET BALANCE",
    "0.00 TRY",
    BLUE
)


# =========================================================
# PİYASA KARTLARI
# =========================================================

market_title = tk.Label(
    content,
    text='MARKET PRICES',
    bg=BG,
    fg=TEXT,
    font=("Segoe UI", 16, "bold")
)

market_title.pack(
    anchor="w",
    padx=36,
    pady=(8, 7)
)


market = tk.Frame(
    content,
    bg=BG
)

market.pack(
    fill="x",
    padx=30
)


def piyasa_karti(parent, baslik, renk):

    frame = tk.Frame(
        parent,
        bg=CARD,
        height=105,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=baslik,
        bg=CARD,
        fg=renk,
        font=("Segoe UI", 12, "bold")
    ).pack(
        anchor="w",
        padx=18,
        pady=(15, 2)
    )

    fiyat = tk.Label(
        frame,
        text='Loading...',
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 18, "bold")
    )

    fiyat.pack(
        anchor="w",
        padx=18
    )

    return fiyat


altin_label = piyasa_karti(
    market,
    "🥇  GOLD",
    GOLD
)

gumus_label = piyasa_karti(
    market,
    "🥈  SILVER",
    SILVER
)

usd_label = piyasa_karti(
    market,
    "💵  USD / TRY",
    GREEN
)


# =========================================================
# FİYATLARI ÇEK
# =========================================================


def fiyatlari_getir():
    try:
        gold_url = (
            "https://api.goldprice.dev/v1/prices"
            "?symbol=XAU-USD-SPOT"
        )

        silver_url = (
            "https://api.goldprice.dev/v1/prices"
            "?symbol=XAG-USD-SPOT"
        )

        gold_response = requests.get(gold_url, timeout=10)
        silver_response = requests.get(silver_url, timeout=10)

        # HTTP hatası varsa yakala
        gold_response.raise_for_status()
        silver_response.raise_for_status()

        gold_data = gold_response.json()
        silver_data = silver_response.json()

        gold_usd = float(gold_data["symbols"][0]["price"])
        silver_usd = float(silver_data["symbols"][0]["price"])

        fx_response = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=TRY",
            timeout=10
        )
        fx_response.raise_for_status()

        fx_data = fx_response.json()
        usd_try = float(fx_data["rates"]["TRY"])

        # Ons fiyatını gram fiyatına çevir
        ons_gram = 31.1034768

        gold_gram = gold_usd * usd_try / ons_gram
        silver_gram = silver_usd * usd_try / ons_gram

        altin_label.config(
            text=f"{gold_gram:,.2f} TRY / gram"
        )

        gumus_label.config(
            text=f"{silver_gram:,.2f} TRY / gram"
        )

        usd_label.config(
            text=f"{usd_try:,.2f} TRY"
        )

        from datetime import datetime
        saat = datetime.now().strftime("%H:%M:%S")

        market_status.config(
            text=f"● Last update: {saat}",
            fg=GREEN
        )

    except Exception as hata:
        market_status.config(
            text='● Price data unavailable',
            fg=RED
        )

        print("Fiyat güncelleme hatası:", hata)

    app.after(660000, fiyatlari_getir)

# =========================================================
# ALT BÖLÜM
# =========================================================

alt = tk.Frame(
    content,
    bg=BG
)

alt.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=12
)


# =========================================================
# İŞLEMLER
# =========================================================

sol = tk.Frame(
    alt,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)

sol.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 7)
)


tk.Label(
    sol,
    text='Recent Transactions',
    bg=CARD,
    fg=TEXT,
    font=("Segoe UI", 15, "bold")
).pack(
    anchor="w",
    padx=18,
    pady=15
)


liste = ttk.Treeview(
    sol,
    columns=(
        "tip",
        "kategori",
        "aciklama",
        "tutar",
        "tarih"
    ),
    show="headings"
)

liste.heading("tip", text='Type')
liste.heading("kategori", text='Category')
liste.heading("aciklama", text='Description')
liste.heading("tutar", text='Amount')
liste.heading("tarih", text='Date')

liste.column("tip", width=75)
liste.column("kategori", width=100)
liste.column("aciklama", width=190)
liste.column("tutar", width=110)
liste.column("tarih", width=90)

liste.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0, 15)
)


# =========================================================
# SAĞ PANEL
# =========================================================

sag = tk.Frame(
    alt,
    bg=CARD,
    width=260
)

sag.pack(
    side="right",
    fill="y",
    padx=(7, 0)
)

sag.pack_propagate(False)


tk.Label(
    sag,
    text='Quick Actions',
    bg=CARD,
    fg=TEXT,
    font=("Segoe UI", 15, "bold")
).pack(
    anchor="w",
    padx=20,
    pady=20
)


def buton(parent, text, command, renk):

    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=renk,
        fg="white",
        activebackground=renk,
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        height=2,
        padx=12,
        pady=3,
        cursor="hand2"
    )


# =========================================================
# VERİLERİ GÜNCELLE
# =========================================================

def verileri_guncelle():

    for item in liste.get_children():
        liste.delete(item)

    cursor.execute("""
        SELECT tip, kategori, aciklama, tutar, tarih
        FROM islemler
        ORDER BY id DESC
    """)

    islemler = cursor.fetchall()

    gelir = 0
    gider = 0

    for islem in islemler:

        tip = {"Gelir": "Income", "Gider": "Expense"}.get(islem[0], islem[0])
        kategori = islem[1]
        aciklama = islem[2]
        tutar = islem[3]
        tarih = islem[4]

        if islem[0] == "Gelir":
            gelir += tutar
        else:
            gider += tutar

        liste.insert(
            "",
            "end",
            values=(
                tip,
                kategori,
                aciklama,
                f"{tutar:,.2f} TRY",
                tarih
            )
        )

    net = gelir - gider

    gelir_label.config(
        text=f"{gelir:,.2f} TRY"
    )

    gider_label.config(
        text=f"{gider:,.2f} TRY"
    )

    net_label.config(
        text=f"{net:,.2f} TRY"
    )


# =========================================================
# İŞLEM EKLE
# =========================================================

def islem_ekle():

    pencere = tk.Toplevel(app)

    pencere.title('New Transaction')
    pencere.geometry("420x470")
    pencere.configure(bg=BG)

    tk.Label(
        pencere,
        text='New Transaction',
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 21, "bold")
    ).pack(pady=25)


    tk.Label(
        pencere,
        text='Transaction Type',
        bg=BG,
        fg=MUTED
    ).pack()

    tip = ttk.Combobox(
        pencere,
        values=['Income', 'Expense'],
        state="readonly",
        width=30
    )

    tip.current(0)

    tip.pack(pady=8)


    tk.Label(
        pencere,
        text='Category',
        bg=BG,
        fg=MUTED
    ).pack()

    kategori = tk.Entry(
        pencere,
        width=32
    )

    kategori.pack(pady=8)


    tk.Label(
        pencere,
        text='Description',
        bg=BG,
        fg=MUTED
    ).pack()

    aciklama = tk.Entry(
        pencere,
        width=32
    )

    aciklama.pack(pady=8)


    tk.Label(
        pencere,
        text='Amount',
        bg=BG,
        fg=MUTED
    ).pack()

    tutar = tk.Entry(
        pencere,
        width=32
    )

    tutar.pack(pady=8)


    def kaydet():

        try:

            miktar = float(
                tutar.get().replace(",", ".")
            )

            if miktar <= 0:
                raise ValueError

            cursor.execute("""
                INSERT INTO islemler
                (tip, kategori, aciklama, tutar, tarih)
                VALUES (?, ?, ?, ?, ?)
            """, (
                {"Income": "Gelir", "Expense": "Gider"}.get(tip.get(), tip.get()),
                kategori.get(),
                aciklama.get(),
                miktar,
                datetime.now().strftime("%d.%m.%Y")
            ))

            db.commit()

            pencere.destroy()

            verileri_guncelle()

        except ValueError:

            messagebox.showerror(
                "Error",
                "Enter a valid amount."
            )


    buton(
        pencere,
        "Save Transaction",
        kaydet,
        BLUE
    ).pack(
        fill="x",
        padx=50,
        pady=25
    )


# =========================================================
# SİL
# =========================================================

def islem_sil():

    secilen = liste.selection()

    if not secilen:

        messagebox.showwarning(
            "Warning",
            "Select a transaction to delete."
        )

        return

    index = liste.index(
        secilen[0]
    )

    cursor.execute("""
        SELECT id
        FROM islemler
        ORDER BY id DESC
    """)

    ids = cursor.fetchall()

    if index >= len(ids):
        return

    id_no = ids[index][0]

    onay = messagebox.askyesno(
        "Delete Transaction",
        "Are you sure you want to delete this transaction?"
    )

    if not onay:
        return

    cursor.execute(
        "DELETE FROM islemler WHERE id = ?",
        (id_no,)
    )

    db.commit()

    verileri_guncelle()


# =========================================================
# BUTONLAR
# =========================================================

buton(
    sag,
    "＋Add Income / Expense",
    islem_ekle,
    BLUE
).pack(
    fill="x",
    padx=20,
    pady=7
)


buton(
    sag,
    "🗑 Delete Selected Transaction",
    islem_sil,
    RED
).pack(
    fill="x",
    padx=20,
    pady=7
)


buton(
    sag,
    "↻ Refresh Market Prices",
    fiyatlari_getir,
    CARD2
).pack(
    fill="x",
    padx=20,
    pady=7
)


market_status = tk.Label(
    sag,
    text='● Waiting for data...',
    bg=CARD,
    fg=MUTED,
    font=("Segoe UI", 9)
)

market_status.pack(
    pady=20
)


# =========================================================
# TREEVIEW TASARIMI
# =========================================================

style = ttk.Style()

style.theme_use("clam")

style.configure(
    "Treeview",
    background=CARD,
    foreground=TEXT,
    fieldbackground=CARD,
    rowheight=34,
    borderwidth=0,
    font=("Segoe UI", 9)
)

style.configure(
    "Treeview.Heading",
    background=CARD2,
    foreground=MUTED,
    relief="flat",
    font=("Segoe UI", 9, "bold")
)

style.map(
    "Treeview",
    background=[("selected", BLUE)],
    foreground=[("selected", "white")]
)

style.map(
    "Treeview.Heading", background=[("active", BLUE)]
)

style.map(
    "Treeview",
    background=[
        ("selected", "#303846")
    ]
)


# =========================================================
# BAŞLAT
# =========================================================

verileri_guncelle()

app.after(
    500,
    fiyatlari_getir
)


# =========================================================
# VARLIKLARIM PENCERESİ
# =========================================================


def varliklar_penceresi():
    pencere = tk.Toplevel(app)
    pencere.title('My Assets')
    pencere.geometry("850x620")
    pencere.configure(bg=BG)

    with sqlite3.connect("seremet.db") as veritabani:
        veritabani.execute("""
            CREATE TABLE IF NOT EXISTS varliklar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tur TEXT NOT NULL,
                miktar REAL NOT NULL,
                aciklama TEXT
            )
        """)

    tk.Label(
        pencere,
        text='MY ASSETS',
        bg=BG, fg=TEXT,
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=25, pady=(20, 5))

    tk.Label(
        pencere,
        text='Add assets, increase or decrease your holdings.',
        bg=BG, fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", padx=25)

    # Giriş formu
    form = tk.Frame(pencere, bg=BG)
    form.pack(fill="x", padx=25, pady=15)

    tk.Label(
        form, text='Asset Type',
        bg=BG, fg=TEXT
    ).grid(row=0, column=0, sticky="w")

    tur_secimi = ttk.Combobox(
        form,
        values=['Gold', 'Silver', 'Cash'],
        state="readonly",
        width=15
    )
    tur_secimi.set("Gold")
    tur_secimi.grid(row=1, column=0, padx=(0, 10), pady=5)

    tk.Label(
        form, text='Amount (grams or TRY)',
        bg=BG, fg=TEXT
    ).grid(row=0, column=1, sticky="w")

    miktar_girdisi = tk.Entry(
        form, bg=CARD, fg=TEXT,
        insertbackground=TEXT, width=20
    )
    miktar_girdisi.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(
        form, text='Description',
        bg=BG, fg=TEXT
    ).grid(row=0, column=2, sticky="w")

    aciklama_girdisi = tk.Entry(
        form, bg=CARD, fg=TEXT,
        insertbackground=TEXT, width=22
    )
    aciklama_girdisi.grid(row=1, column=2, padx=10, pady=5)

    # Varlık tablosu
    tablo = ttk.Treeview(
        pencere,
        columns=("id", "tur", "miktar", "aciklama", "deger"),
        show="headings"
    )

    tablo.heading("id", text='No')
    tablo.heading("tur", text='Asset')
    tablo.heading("miktar", text='Amount')
    tablo.heading("aciklama", text='Description')
    tablo.heading("deger", text='Current Value')

    tablo.column("id", width=45)
    tablo.column("tur", width=110)
    tablo.column("miktar", width=130)
    tablo.column("aciklama", width=200)
    tablo.column("deger", width=160)

    tablo.pack(fill="both", expand=True, padx=25, pady=10)

    toplam_label = tk.Label(
        pencere,
        text='Total assets: 0.00 TRY',
        bg=BG, fg=GREEN,
        font=("Segoe UI", 14, "bold")
    )
    toplam_label.pack(anchor="w", padx=25, pady=10)

    # Canlı gram fiyatını etiketten oku
    def fiyat_oku(label):
        metin = label.cget("text").split()[0]
        return float(metin.replace(",", ""))

    # Varlıkları listele ve toplamı hesapla
    def listele():
        for satir in tablo.get_children():
            tablo.delete(satir)

        toplam = 0

        with sqlite3.connect("seremet.db") as veritabani:
            satirlar = veritabani.execute("""
                SELECT id, tur, miktar, aciklama
                FROM varliklar
                ORDER BY id DESC
            """).fetchall()

        simgeler = {
            "Altın": "🥇 Gold",
            "Gümüş": "🥈 Silver",
            "Nakit": "💵 Cash"
        }

        for kimlik, tur, miktar, aciklama in satirlar:
            try:
                if tur == "Altın":
                    deger = miktar * fiyat_oku(altin_label)
                elif tur == "Gümüş":
                    deger = miktar * fiyat_oku(gumus_label)
                else:
                    deger = miktar

                toplam += deger
                deger_yazi = f"{deger:,.2f} TRY"

            except (ValueError, IndexError):
                deger_yazi = "Price unavailable"

            birim = "grams" if tur in ("Altın", "Gümüş") else "TRY"

            tablo.insert(
                "", "end",
                values=(
                    kimlik,
                    simgeler.get(tur, tur),
                    f"{miktar:,.3f} {birim}",
                    aciklama or "-",
                    deger_yazi
                )
            )

        toplam_label.config(
            text=f"Total assets: {toplam:,.2f} TRY"
        )

    # Yeni varlık kaydet
    def varlik_ekle():
        tur = {"Gold": "Altın", "Silver": "Gümüş", "Cash": "Nakit"}.get(tur_secimi.get(), tur_secimi.get())

        try:
            miktar = float(
                miktar_girdisi.get().strip().replace(",", ".")
            )
            if miktar <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid amount",
                "Enter a positive amount. Example: 12.5",
                parent=pencere
            )
            return

        with sqlite3.connect("seremet.db") as veritabani:
            veritabani.execute("""
                INSERT INTO varliklar (tur, miktar, aciklama)
                VALUES (?, ?, ?)
            """, (
                tur,
                miktar,
                aciklama_girdisi.get().strip()
            ))

        miktar_girdisi.delete(0, tk.END)
        aciklama_girdisi.delete(0, tk.END)
        listele()

    # Seçili varlığın miktarını artır veya azalt
    def varlik_miktar_degistir(islem):
        secim = tablo.selection()

        if not secim:
            messagebox.showwarning(
                "Select an asset",
                "Select an asset from the table first.",
                parent=pencere
            )
            return

        try:
            miktar = float(
                miktar_girdisi.get().strip().replace(",", ".")
            )
            if miktar <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid amount",
                "Enter the amount to add or subtract.",
                parent=pencere
            )
            return

        kimlik = tablo.item(secim[0], "values")[0]

        with sqlite3.connect("seremet.db") as veritabani:
            sonuc = veritabani.execute(
                "SELECT miktar FROM varliklar WHERE id = ?",
                (kimlik,)
            ).fetchone()

            if sonuc is None:
                return

            yeni_miktar = sonuc[0] + miktar * islem

            if yeni_miktar < 0:
                messagebox.showwarning(
                    "Insufficient assets",
                    "You cannot subtract more than you own.",
                    parent=pencere
                )
                return

            veritabani.execute(
                "UPDATE varliklar SET miktar = ? WHERE id = ?",
                (yeni_miktar, kimlik)
            )

        miktar_girdisi.delete(0, tk.END)
        listele()

    def varlik_arttir():
        varlik_miktar_degistir(1)

    def varlik_azalt():
        varlik_miktar_degistir(-1)

    # Seçili varlığı tamamen sil
    def varlik_sil():
        secim = tablo.selection()

        if not secim:
            messagebox.showwarning(
                "Selection required",
                "Select the asset you want to delete first.",
                parent=pencere
            )
            return

        kimlik = tablo.item(secim[0], "values")[0]

        with sqlite3.connect("seremet.db") as veritabani:
            veritabani.execute(
                "DELETE FROM varliklar WHERE id = ?",
                (kimlik,)
            )

        listele()

    # Düğmeler
    buton(
        pencere, "＋ Add New Asset",
        varlik_ekle, BLUE
    ).pack(fill="x", padx=25, pady=4)

    buton(
        pencere, "＋ Add to Selected Asset",
        varlik_arttir, GREEN
    ).pack(fill="x", padx=25, pady=4)

    buton(
        pencere, "− Subtract from Selected Asset",
        varlik_azalt, RED
    ).pack(fill="x", padx=25, pady=4)

    buton(
        pencere, "🗑 Delete Selected Asset",
        varlik_sil, CARD2
    ).pack(fill="x", padx=25, pady=4)

    listele()


# Varlıklarım düğmesini pencereye bağla
varliklar_butonu.config(
    command=varliklar_penceresi
)


# =========================================================
# NOTES
# =========================================================
def notes_window():
    window = tk.Toplevel(app)
    window.title("My Notes")
    window.geometry("900x600")
    window.configure(bg=BG)

    tk.Label(
        window, text="My Notes", bg=BG, fg=TEXT,
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=25, pady=(20, 10))

    body = tk.Frame(window, bg=BG)
    body.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    sidebar = tk.Frame(body, bg=CARD, width=270)
    sidebar.pack(side="left", fill="y", padx=(0, 12))
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="Saved notes", bg=CARD, fg=TEXT,
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(12, 6))
    notes_list = tk.Listbox(
        sidebar, bg=CARD2, fg=TEXT, selectbackground=BLUE,
        selectforeground="white", relief="flat",
        font=("Segoe UI", 10), activestyle="none"
    )
    notes_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    editor = tk.Frame(body, bg=BG)
    editor.pack(side="left", fill="both", expand=True)

    tk.Label(editor, text="Title", bg=BG, fg=TEXT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    title_entry = tk.Entry(editor, bg=CARD, fg=TEXT, insertbackground=TEXT,
                           relief="flat", font=("Segoe UI", 12))
    title_entry.pack(fill="x", pady=(5, 12), ipady=7)

    tk.Label(editor, text="Note", bg=BG, fg=TEXT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    content_text = tk.Text(editor, bg=CARD, fg=TEXT, insertbackground=TEXT,
                           relief="flat", font=("Segoe UI", 11), wrap="word")
    content_text.pack(fill="both", expand=True, pady=(5, 12))

    selected_note_id = {"id": None}
    note_rows = []

    def refresh_notes(select_id=None):
        nonlocal note_rows
        note_rows = cursor.execute(
            "SELECT id, title, content, updated_at FROM notes ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        notes_list.delete(0, tk.END)
        for row in note_rows:
            notes_list.insert(tk.END, row[1] or "Untitled note")
        if select_id is not None:
            for index, row in enumerate(note_rows):
                if row[0] == select_id:
                    notes_list.selection_clear(0, tk.END)
                    notes_list.selection_set(index)
                    notes_list.activate(index)
                    load_selected_note()
                    break

    def load_selected_note(_event=None):
        selection = notes_list.curselection()
        if not selection:
            return
        row = note_rows[selection[0]]
        selected_note_id["id"] = row[0]
        title_entry.delete(0, tk.END)
        title_entry.insert(0, row[1])
        content_text.delete("1.0", tk.END)
        content_text.insert("1.0", row[2])

    def new_note():
        selected_note_id["id"] = None
        notes_list.selection_clear(0, tk.END)
        title_entry.delete(0, tk.END)
        content_text.delete("1.0", tk.END)
        title_entry.focus_set()

    def save_note():
        title = title_entry.get().strip() or "Untitled note"
        content = content_text.get("1.0", "end-1c").strip()
        if not content and title == "Untitled note":
            messagebox.showwarning("Empty note", "Enter a title or some note text.", parent=window)
            return
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if selected_note_id["id"] is None:
            cursor.execute(
                "INSERT INTO notes (title, content, updated_at) VALUES (?, ?, ?)",
                (title, content, updated_at)
            )
            db.commit()
            selected_note_id["id"] = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
                (title, content, updated_at, selected_note_id["id"])
            )
            db.commit()
        refresh_notes(selected_note_id["id"])
        messagebox.showinfo("Saved", "Your note has been saved.", parent=window)

    def delete_note():
        note_id = selected_note_id["id"]
        if note_id is None:
            messagebox.showwarning("No note selected", "Select a saved note to delete.", parent=window)
            return
        if not messagebox.askyesno("Delete note", "Delete this note permanently?", parent=window):
            return
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        db.commit()
        new_note()
        refresh_notes()

    notes_list.bind("<<ListboxSelect>>", load_selected_note)
    buttons = tk.Frame(editor, bg=BG)
    buttons.pack(fill="x")
    tk.Button(buttons, text="New note", command=new_note, bg=CARD2, fg=TEXT,
              relief="flat", padx=15, pady=8).pack(side="left", padx=(0, 8))
    tk.Button(buttons, text="Save note", command=save_note, bg=BLUE, fg="white",
              relief="flat", padx=15, pady=8).pack(side="left", padx=(0, 8))
    tk.Button(buttons, text="Delete note", command=delete_note, bg=RED, fg="white",
              relief="flat", padx=15, pady=8).pack(side="left")

    refresh_notes()

notlar_butonu.config(command=notes_window)



# =========================================================
# BORÇLAR
# =========================================================
def borclar_penceresi():
    pencere = tk.Toplevel(app)
    pencere.title("Debts")
    pencere.geometry("1080x700")
    pencere.configure(bg=BG)

    tk.Label(pencere, text="DEBT CONTROL", bg=BG, fg=TEXT,
             font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=22, pady=(18, 4))
    tk.Label(pencere, text="Track debts, record partial payments, and keep paid debts in history.",
             bg=BG, fg=MUTED).pack(anchor="w", padx=22)

    form = tk.Frame(pencere, bg=CARD)
    form.pack(fill="x", padx=22, pady=14)

    tk.Label(form, text="Source", bg=CARD, fg=TEXT).grid(row=0, column=0, sticky="w", padx=8, pady=(10, 2))
    kaynak = ttk.Combobox(form, values=["Bank", "Credit Card", "Personal", "Family", "Shopping", "Other"], width=17)
    kaynak.set("Bank")
    kaynak.grid(row=1, column=0, padx=8, pady=(0, 10))

    tk.Label(form, text="Debt name / person", bg=CARD, fg=TEXT).grid(row=0, column=1, sticky="w", padx=8, pady=(10, 2))
    baslik = tk.Entry(form, width=22, bg=CARD2, fg=TEXT, insertbackground=TEXT)
    baslik.grid(row=1, column=1, padx=8, pady=(0, 10))

    tk.Label(form, text="Amount (TRY)", bg=CARD, fg=TEXT).grid(row=0, column=2, sticky="w", padx=8, pady=(10, 2))
    tutar = tk.Entry(form, width=15, bg=CARD2, fg=TEXT, insertbackground=TEXT)
    tutar.grid(row=1, column=2, padx=8, pady=(0, 10))

    tk.Label(form, text="Due date (DD.MM.YYYY)", bg=CARD, fg=TEXT).grid(row=0, column=3, sticky="w", padx=8, pady=(10, 2))
    vade = tk.Entry(form, width=18, bg=CARD2, fg=TEXT, insertbackground=TEXT)
    vade.grid(row=1, column=3, padx=8, pady=(0, 10))

    tk.Label(form, text="Note", bg=CARD, fg=TEXT).grid(row=0, column=4, sticky="w", padx=8, pady=(10, 2))
    not_girdisi = tk.Entry(form, width=18, bg=CARD2, fg=TEXT, insertbackground=TEXT)
    not_girdisi.grid(row=1, column=4, padx=8, pady=(0, 10))

    tabs = ttk.Notebook(pencere)
    tabs.pack(fill="both", expand=True, padx=22, pady=(0, 10))
    acik_frame = tk.Frame(tabs, bg=BG)
    gecmis_frame = tk.Frame(tabs, bg=BG)
    tabs.add(acik_frame, text="Open debts")
    tabs.add(gecmis_frame, text="Paid history")

    columns = ("id", "kaynak", "baslik", "toplam", "kalan", "olusturma", "vade", "notlar")
    headers = {"id":"No", "kaynak":"Source", "baslik":"Debt", "toplam":"Original (TRY)",
               "kalan":"Remaining (TRY)", "olusturma":"Created", "vade":"Due date", "notlar":"Note"}
    acik_tablo = ttk.Treeview(acik_frame, columns=columns, show="headings")
    gecmis_tablo = ttk.Treeview(gecmis_frame, columns=columns, show="headings")
    for tablo in (acik_tablo, gecmis_tablo):
        for col in columns:
            tablo.heading(col, text=headers[col])
            tablo.column(col, width=100 if col not in ("baslik", "notlar") else 150, anchor="w")
        tablo.column("id", width=45)
        tablo.pack(fill="both", expand=True, padx=5, pady=5)

    toplam_label = tk.Label(pencere, text="Open debt total: 0.00 TRY", bg=BG, fg=GOLD,
                            font=("Segoe UI", 13, "bold"))
    toplam_label.pack(anchor="w", padx=25, pady=5)

    def listele():
        for tablo in (acik_tablo, gecmis_tablo):
            for item in tablo.get_children():
                tablo.delete(item)
        with sqlite3.connect("seremet.db") as conn:
            rows = conn.execute("""
                SELECT id, kaynak, baslik, toplam_borc, kalan_borc, olusturma_tarihi,
                       COALESCE(son_odeme_tarihi, ''), COALESCE(notlar, ''), durum
                FROM borclar ORDER BY id DESC
            """).fetchall()
        toplam = 0
        for row in rows:
            values = (row[0], row[1], row[2], f"{row[3]:,.2f}", f"{row[4]:,.2f}",
                      row[5], row[6] or "-", row[7] or "-")
            if row[8] == "Ödendi" or row[4] <= 0:
                gecmis_tablo.insert("", "end", values=values)
            else:
                acik_tablo.insert("", "end", values=values)
                toplam += row[4]
        toplam_label.config(text=f"Open debt total: {toplam:,.2f} TRY")

    def borc_ekle():
        kaynak_degeri = kaynak.get().strip()
        baslik_degeri = baslik.get().strip()
        try:
            miktar = float(tutar.get().strip().replace(" ", "").replace(",", "."))
            if miktar <= 0 or not kaynak_degeri or not baslik_degeri:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid information", "Enter a source, debt name, and a positive amount.", parent=pencere)
            return
        vade_degeri = vade.get().strip()
        if vade_degeri:
            try:
                datetime.strptime(vade_degeri, "%d.%m.%Y")
            except ValueError:
                messagebox.showwarning("Invalid date", "Due date must be DD.MM.YYYY.", parent=pencere)
                return
        with sqlite3.connect("seremet.db") as conn:
            conn.execute("""INSERT INTO borclar
                (kaynak, baslik, toplam_borc, kalan_borc, olusturma_tarihi, son_odeme_tarihi, notlar, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Açık')""",
                (kaynak_degeri, baslik_degeri, miktar, miktar,
                 datetime.now().strftime("%d.%m.%Y"), vade_degeri, not_girdisi.get().strip()))
        baslik.delete(0, tk.END); tutar.delete(0, tk.END)
        vade.delete(0, tk.END); not_girdisi.delete(0, tk.END)
        listele()

    def odeme_al():
        secim = acik_tablo.selection()
        if not secim:
            messagebox.showwarning("Select a debt", "Select an open debt first.", parent=pencere)
            return
        debt_id = acik_tablo.item(secim[0], "values")[0]
        with sqlite3.connect("seremet.db") as conn:
            row = conn.execute("SELECT kalan_borc FROM borclar WHERE id=?", (debt_id,)).fetchone()
        if not row:
            listele(); return
        kalan = float(row[0])
        odeme_penceresi = tk.Toplevel(pencere)
        odeme_penceresi.title("Record payment")
        odeme_penceresi.geometry("360x240")
        odeme_penceresi.configure(bg=BG)
        tk.Label(odeme_penceresi, text=f"Remaining: {kalan:,.2f} TRY", bg=BG, fg=GOLD,
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 8))
        tk.Label(odeme_penceresi, text="Payment amount (TRY)", bg=BG, fg=TEXT).pack()
        odeme_tutar = tk.Entry(odeme_penceresi, bg=CARD, fg=TEXT, insertbackground=TEXT)
        odeme_tutar.pack(pady=8)
        tk.Label(odeme_penceresi, text="Payment note (optional)", bg=BG, fg=TEXT).pack()
        odeme_notu = tk.Entry(odeme_penceresi, bg=CARD, fg=TEXT, insertbackground=TEXT)
        odeme_notu.pack(pady=5)

        def kaydet_odeme():
            try:
                miktar = float(odeme_tutar.get().strip().replace(" ", "").replace(",", "."))
                if miktar <= 0 or miktar > kalan:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid payment", f"Payment must be greater than zero and no more than {kalan:,.2f} TRY.", parent=odeme_penceresi)
                return
            yeni_kalan = round(kalan - miktar, 2)
            with sqlite3.connect("seremet.db") as conn:
                conn.execute("INSERT INTO borc_odemeleri (borc_id, tutar, tarih, notlar) VALUES (?, ?, ?, ?)",
                             (debt_id, miktar, datetime.now().strftime("%d.%m.%Y %H:%M"), odeme_notu.get().strip()))
                conn.execute("UPDATE borclar SET kalan_borc=?, durum=? WHERE id=?",
                             (yeni_kalan, "Ödendi" if yeni_kalan <= 0.005 else "Açık", debt_id))
            odeme_penceresi.destroy()
            listele()
            messagebox.showinfo("Payment saved", f"Payment recorded. Remaining debt: {max(0, yeni_kalan):,.2f} TRY.", parent=pencere)

        buton(odeme_penceresi, "Save payment", kaydet_odeme, GREEN).pack(fill="x", padx=35, pady=10)

    def odeme_gecmisi():
        secim = acik_tablo.selection() or gecmis_tablo.selection()
        if not secim:
            messagebox.showwarning("Select a debt", "Select a debt to see its payment history.", parent=pencere)
            return
        tablo_secili = acik_tablo if acik_tablo.selection() else gecmis_tablo
        debt_id = tablo_secili.item(secim[0], "values")[0]
        gecmis = tk.Toplevel(pencere)
        gecmis.title("Payment history")
        gecmis.geometry("600x360")
        gecmis.configure(bg=BG)
        tk.Label(gecmis, text="PAYMENT HISTORY", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=12)
        odeme_tablo = ttk.Treeview(gecmis, columns=("tutar", "tarih", "not"), show="headings")
        for col, label in (("tutar", "Amount (TRY)"), ("tarih", "Date"), ("not", "Note")):
            odeme_tablo.heading(col, text=label)
            odeme_tablo.column(col, width=170)
        odeme_tablo.pack(fill="both", expand=True, padx=15, pady=10)
        with sqlite3.connect("seremet.db") as conn:
            payments = conn.execute("SELECT tutar, tarih, COALESCE(notlar, '') FROM borc_odemeleri WHERE borc_id=? ORDER BY id DESC",
                                    (debt_id,)).fetchall()
        for payment in payments:
            odeme_tablo.insert("", "end", values=(f"{payment[0]:,.2f}", payment[1], payment[2] or "-"))
        if not payments:
            tk.Label(gecmis, text="No payments recorded yet.", bg=BG, fg=MUTED).pack(pady=5)

    buttons = tk.Frame(pencere, bg=BG)
    buttons.pack(fill="x", padx=22, pady=(0, 16))
    buton(buttons, "＋ Add debt", borc_ekle, BLUE).pack(side="left", padx=(0, 8))
    buton(buttons, "Record partial payment", odeme_al, GREEN).pack(side="left", padx=8)
    buton(buttons, "Payment history", odeme_gecmisi, CARD2).pack(side="left", padx=8)
    listele()


# =========================================================
# KREDİ KARTLARI
# =========================================================
def kredi_kartlari_penceresi():
    pencere = tk.Toplevel(app)
    pencere.title("Credit Cards")
    pencere.geometry("1120x650")
    pencere.configure(bg=BG)

    tk.Label(pencere, text="CREDIT CARD CONTROL", bg=BG, fg=TEXT,
             font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=22, pady=(18, 4))
    tk.Label(pencere, text="Track bank, card network, limit, current debt, statement date, and payment due date.",
             bg=BG, fg=MUTED).pack(anchor="w", padx=22)

    form = tk.Frame(pencere, bg=CARD)
    form.pack(fill="x", padx=22, pady=14)

    def alan(label, row, col, width=17):
        tk.Label(form, text=label, bg=CARD, fg=TEXT).grid(row=row*2, column=col, sticky="w", padx=7, pady=(8, 1))
        entry = tk.Entry(form, width=width, bg=CARD2, fg=TEXT, insertbackground=TEXT)
        entry.grid(row=row*2+1, column=col, padx=7, pady=(0, 8))
        return entry

    banka = alan("Bank", 0, 0)
    kart_adi = alan("Card name", 0, 1)
    limit_girdi = alan("Card limit (TRY)", 0, 2)
    borc_girdi = alan("Current debt (TRY)", 0, 3)
    ekstre_girdi = alan("Statement date (DD.MM.YYYY)", 1, 0, 21)
    vade_girdi = alan("Payment due date (DD.MM.YYYY)", 1, 1, 21)
    tk.Label(form, text="Card network", bg=CARD, fg=TEXT).grid(row=2, column=2, sticky="w", padx=7, pady=(8, 1))
    ag = ttk.Combobox(form, values=["Visa", "Mastercard", "Troy", "LOADİNG", "Other"], state="normal", width=15)
    ag.set("Visa")
    ag.grid(row=3, column=2, padx=7, pady=(0, 8))

    columns = ("id", "banka", "kart", "ag", "limit", "kullanilabilir", "borc", "ekstre", "vade")
    tablo = ttk.Treeview(pencere, columns=columns, show="headings")
    headers = {"id":"No", "banka":"Bank", "kart":"Card", "ag":"Network", "limit":"Limit (TRY)",
               "kullanilabilir":"Available (TRY)", "borc":"Current debt (TRY)", "ekstre":"Statement date", "vade":"Due date"}
    for col in columns:
        tablo.heading(col, text=headers[col])
        tablo.column(col, width=105, anchor="w")
    tablo.column("id", width=40)
    tablo.column("banka", width=120)
    tablo.column("kart", width=120)
    tablo.column("kullanilabilir", width=140)
    tablo.pack(fill="both", expand=True, padx=22, pady=(0, 10))

    toplam_label = tk.Label(pencere, text="Total card debt: 0.00 TRY", bg=BG, fg=GOLD,
                            font=("Segoe UI", 13, "bold"))
    toplam_label.pack(anchor="w", padx=25, pady=5)

    def listele():
        for item in tablo.get_children():
            tablo.delete(item)
        with sqlite3.connect("seremet.db") as conn:
            rows = conn.execute("""SELECT id, banka, kart_adi, kart_agi, limit_tutari, guncel_borc,
                                  ekstre_kesim_tarihi, son_odeme_tarihi FROM kredi_kartlari ORDER BY id DESC""").fetchall()
        toplam_borc = 0
        for row in rows:
            kullanilabilir = row[4] - row[5]
            toplam_borc += row[5]
            tablo.insert("", "end", values=(row[0], row[1], row[2], row[3], f"{row[4]:,.2f}",
                           f"{kullanilabilir:,.2f}", f"{row[5]:,.2f}", row[6] or "-", row[7] or "-"))
        toplam_label.config(text=f"Total card debt: {toplam_borc:,.2f} TRY")

    def tarih_kontrol(deger):
        if not deger.strip():
            return True
        try:
            datetime.strptime(deger.strip(), "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def kart_ekle():
        banka_degeri = banka.get().strip()
        kart_degeri = kart_adi.get().strip()
        ag_degeri = ag.get().strip()
        try:
            limit = float(limit_girdi.get().strip().replace(" ", "").replace(",", "."))
            borc = float(borc_girdi.get().strip().replace(" ", "").replace(",", ".") or "0")
            if not banka_degeri or not kart_degeri or not ag_degeri or limit <= 0 or borc < 0 or borc > limit:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid information", "Enter bank, card name, network, a positive limit, and a debt between 0 and the limit.", parent=pencere)
            return
        ekstre = ekstre_girdi.get().strip()
        vade = vade_girdi.get().strip()
        if not tarih_kontrol(ekstre) or not tarih_kontrol(vade):
            messagebox.showwarning("Invalid date", "Dates must be DD.MM.YYYY (or left blank).", parent=pencere)
            return
        with sqlite3.connect("seremet.db") as conn:
            conn.execute("""INSERT INTO kredi_kartlari
                (banka, kart_adi, kart_agi, limit_tutari, guncel_borc, ekstre_kesim_tarihi, son_odeme_tarihi)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (banka_degeri, kart_degeri, ag_degeri, limit, borc, ekstre, vade))
        for entry in (banka, kart_adi, limit_girdi, borc_girdi, ekstre_girdi, vade_girdi):
            entry.delete(0, tk.END)
        ag.set("Visa")
        listele()

    def borc_guncelle():
        secim = tablo.selection()
        if not secim:
            messagebox.showwarning("Select a card", "Select a card first.", parent=pencere)
            return
        row = tablo.item(secim[0], "values")
        card_id = row[0]
        current = float(str(row[6]).replace(",", ""))
        dialog = tk.Toplevel(pencere)
        dialog.title("Update current debt")
        dialog.geometry("360x190")
        dialog.configure(bg=BG)
        tk.Label(dialog, text=f"{row[2]} — current debt", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(pady=(20, 8))
        entry = tk.Entry(dialog, bg=CARD, fg=TEXT, insertbackground=TEXT)
        entry.insert(0, str(current))
        entry.pack(pady=8)

        def save():
            try:
                value = float(entry.get().strip().replace(" ", "").replace(",", "."))
                limit_value = float(str(row[4]).replace(",", ""))
                if value < 0 or value > limit_value:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid amount", "Debt must be between zero and the card limit.", parent=dialog)
                return
            with sqlite3.connect("seremet.db") as conn:
                conn.execute("UPDATE kredi_kartlari SET guncel_borc=? WHERE id=?", (value, card_id))
            dialog.destroy()
            listele()

        buton(dialog, "Save current debt", save, GREEN).pack(fill="x", padx=35, pady=12)

    def kart_sil():
        secim = tablo.selection()
        if not secim:
            messagebox.showwarning("Select a card", "Select a card to delete.", parent=pencere)
            return
        row = tablo.item(secim[0], "values")
        if messagebox.askyesno("Delete card", f"Delete {row[2]} from {row[1]}?", parent=pencere):
            with sqlite3.connect("seremet.db") as conn:
                conn.execute("DELETE FROM kredi_kartlari WHERE id=?", (row[0],))
            listele()

    buttons = tk.Frame(pencere, bg=BG)
    buttons.pack(fill="x", padx=22, pady=(0, 16))
    buton(buttons, "＋ Add card", kart_ekle, BLUE).pack(side="left", padx=(0, 8))
    buton(buttons, "Update selected card debt", borc_guncelle, GREEN).pack(side="left", padx=8)
    buton(buttons, "Delete selected card", kart_sil, RED).pack(side="left", padx=8)
    listele()


borclar_butonu.config(command=borclar_penceresi)
kredi_kartlari_butonu.config(command=kredi_kartlari_penceresi)


app.mainloop()
db.close()
