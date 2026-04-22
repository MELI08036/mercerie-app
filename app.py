import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
from datetime import datetime, date
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
#  CONFIG & STYLE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MerceriePro · Gestion Boutique",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Jost:wght@300;400;500;600&display=swap');

:root {
    --creme:    #FAF7F2;
    --or:       #C9A84C;
    --or-light: #E8D5A3;
    --bordeaux: #7D2035;
    --bordeaux-light: #A64455;
    --brun:     #3D2B1F;
    --gris:     #8A8078;
    --blanc:    #FFFFFF;
    --vert:     #2D6A4F;
    --rouge:    #C0392B;
    --bg:       #F5F1EB;
}

html, body, [class*="css"] {
    font-family: 'Jost', sans-serif;
    background-color: var(--bg);
    color: var(--brun);
}
.stApp { background: var(--bg); }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, var(--brun) 0%, #5C3D2E 100%);
    border-right: 3px solid var(--or);
}
[data-testid="stSidebar"] * { color: var(--creme) !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem; letter-spacing: 0.04em; }

h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--brun) !important; }
h1 { font-size: 2.1rem !important; letter-spacing: -0.02em; }
h2 { font-size: 1.5rem !important; border-bottom: 2px solid var(--or); padding-bottom: 6px; }
h3 { font-size: 1.15rem !important; color: var(--bordeaux) !important; }

.kpi-card {
    background: var(--blanc);
    border-radius: 12px;
    padding: 22px 24px;
    border-left: 5px solid var(--or);
    box-shadow: 0 2px 12px rgba(61,43,31,0.10);
    transition: transform 0.2s;
    margin-bottom: 8px;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-title { font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--gris); margin-bottom: 6px; }
.kpi-value { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: var(--brun); }
.kpi-sub   { font-size: 0.82rem; color: var(--gris); margin-top: 2px; }

.alerte-rupture {
    background: #FFF0F0; border-left: 5px solid var(--rouge);
    border-radius: 8px; padding: 12px 16px; margin: 4px 0; font-size: 0.9rem;
}
.alerte-faible {
    background: #FFFBEC; border-left: 5px solid #E8A020;
    border-radius: 8px; padding: 12px 16px; margin: 4px 0; font-size: 0.9rem;
}

.stButton > button {
    background: linear-gradient(135deg, var(--bordeaux), var(--bordeaux-light));
    color: white !important; border: none; border-radius: 8px;
    padding: 10px 28px; font-family: 'Jost', sans-serif; font-weight: 600;
    letter-spacing: 0.05em; font-size: 0.92rem; transition: all 0.25s;
    box-shadow: 0 3px 10px rgba(125,32,53,0.25);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(125,32,53,0.35); }

.stTextInput input, .stNumberInput input {
    border-radius: 8px !important; border: 1.5px solid var(--or-light) !important;
    font-family: 'Jost', sans-serif !important; background: var(--blanc) !important;
}
.stDataFrame { border-radius: 10px; overflow: hidden; }

.or-divider {
    border: none; height: 2px;
    background: linear-gradient(90deg, transparent, var(--or), transparent);
    margin: 20px 0;
}

.recu-box {
    background: var(--blanc); border: 1.5px dashed var(--or);
    border-radius: 10px; padding: 20px 24px;
    font-family: 'Courier New', monospace; font-size: 0.88rem; line-height: 1.8;
}

.msg-succes {
    background: linear-gradient(135deg, #E8F5E9, #F1F8F2);
    border-left: 5px solid var(--vert); border-radius: 8px;
    padding: 14px 20px; margin-top: 10px; font-weight: 500;
}

.hero-header {
    background: linear-gradient(135deg, var(--brun) 0%, #5C3D2E 60%, var(--bordeaux) 100%);
    border-radius: 16px; padding: 32px 40px; margin-bottom: 28px;
    display: flex; align-items: center; gap: 20px;
    box-shadow: 0 8px 30px rgba(61,43,31,0.2);
}
.hero-header h1 { color: var(--creme) !important; margin: 0 !important; }
.hero-header p  { color: var(--or-light) !important; margin: 0 !important; font-size: 0.95rem; }

.sidebar-brand {
    text-align: center; padding: 20px 10px 16px;
    border-bottom: 1px solid rgba(201,168,76,0.3); margin-bottom: 20px;
}
.sidebar-brand h2 { font-family: 'Playfair Display', serif; color: var(--or) !important; font-size: 1.5rem !important; border: none !important; }
.sidebar-brand p  { color: var(--or-light) !important; font-size: 0.78rem; letter-spacing: 0.14em; text-transform: uppercase; }

/* ✅ FIX SIDEBAR : on masque uniquement le menu hamburger Streamlit
   et le footer, sans toucher au header ni au bouton collapse/expand */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONNEXION SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    """Retourne le client Supabase. Priorité : variables d'environnement (Render)."""
    from supabase import create_client

    # 1. Variables d'environnement système — Render
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()

    # 2. Si vides, essayer st.secrets — Streamlit Cloud
    if not url or not key:
        try:
            url = str(st.secrets.get("SUPABASE_URL", "")).strip()
            key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
        except Exception:
            pass

    if not url or not key:
        st.error(
            "❌ Variables SUPABASE_URL et SUPABASE_KEY introuvables. "
            "Sur Render → Environment → vérifiez les deux variables → Save Changes."
        )
        st.stop()

    return create_client(url, key)


# ─────────────────────────────────────────────
#  COLONNES
# ─────────────────────────────────────────────
CAT_COLS   = ["id", "nom", "categorie", "prix_unitaire", "stock_initial",
              "stock_actuel", "unite", "photo_base64", "date_ajout"]
VENTE_COLS = ["id", "date", "heure", "article_id", "article_nom",
              "categorie", "quantite", "prix_unitaire", "total", "vendeur"]

CATEGORIES = ["Fils & Laines", "Tissus", "Boutons & Fermetures", "Rubans & Dentelles",
              "Aiguilles & Crochets", "Patrons & Gabarits", "Accessoires Couture", "Mercerie Générale"]
UNITES = ["mètre", "bobine", "pièce", "rouleau", "paquet", "paire", "lot"]


# ─────────────────────────────────────────────
#  FONCTIONS DONNÉES — Supabase
# ─────────────────────────────────────────────
def charger_catalogue():
    sb = get_supabase()
    if sb is None:
        st.error("❌ Connexion Supabase impossible. Vérifiez SUPABASE_URL et SUPABASE_KEY.")
        return pd.DataFrame(columns=CAT_COLS)
    try:
        res = sb.table("catalogue").select("*").execute()
        if not res.data:
            return pd.DataFrame(columns=CAT_COLS)
        df = pd.DataFrame(res.data)
        for col in ["prix_unitaire", "stock_initial", "stock_actuel"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"❌ Erreur lecture catalogue : {e}")
        return pd.DataFrame(columns=CAT_COLS)


def ajouter_article(article: dict):
    sb = get_supabase()
    if sb is None:
        return False
    try:
        sb.table("catalogue").insert(article).execute()
        return True
    except Exception as e:
        st.error(f"❌ Erreur ajout article : {e}")
        return False


def mettre_a_jour_stock(article_id: str, nouveau_stock: int):
    sb = get_supabase()
    if sb is None:
        return False
    try:
        sb.table("catalogue").update({"stock_actuel": nouveau_stock}).eq("id", article_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Erreur mise à jour stock : {e}")
        return False


def charger_ventes():
    sb = get_supabase()
    if sb is None:
        return pd.DataFrame(columns=VENTE_COLS)
    try:
        res = sb.table("ventes").select("*").execute()
        if not res.data:
            return pd.DataFrame(columns=VENTE_COLS)
        df = pd.DataFrame(res.data)
        for col in ["quantite", "prix_unitaire", "total"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"❌ Erreur lecture ventes : {e}")
        return pd.DataFrame(columns=VENTE_COLS)


def enregistrer_vente(vente: dict):
    sb = get_supabase()
    if sb is None:
        return False
    try:
        sb.table("ventes").insert(vente).execute()
        return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement vente : {e}")
        return False


def prochain_id(df, prefix="A"):
    if df.empty:
        return f"{prefix}001"
    nums = []
    for i in df["id"].dropna().tolist():
        try:
            nums.append(int(str(i).replace(prefix, "")))
        except:
            pass
    return f"{prefix}{(max(nums) + 1):03d}" if nums else f"{prefix}001"


def image_to_b64(uploaded_file):
    if uploaded_file is None:
        return ""
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


def afficher_image_b64(b64str, width=80):
    if b64str and len(b64str) > 10:
        try:
            st.image(BytesIO(base64.b64decode(b64str)), width=width)
            return
        except:
            pass
    st.write("📷")


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🧵 MerceriePro</h2>
        <p>Gestion Boutique</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Tableau de Bord", "📦  Catalogue", "🛒  Caisse", "📊  Statistiques"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(201,168,76,0.3);'>", unsafe_allow_html=True)

    cat_df_sb  = charger_catalogue()
    vente_df_sb = charger_ventes()

    nb_articles = len(cat_df_sb)
    nb_ventes   = len(vente_df_sb)
    ca_total    = vente_df_sb["total"].sum() if not vente_df_sb.empty else 0

    st.markdown(f"""
    <div style='padding:10px 4px;font-size:0.82rem;line-height:2'>
        <div>📦 <b>{nb_articles}</b> articles en catalogue</div>
        <div>🛒 <b>{nb_ventes}</b> ventes enregistrées</div>
        <div>💰 <b>{ca_total:,.0f} FCFA</b> de CA total</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(201,168,76,0.3);'>", unsafe_allow_html=True)

    ruptures_sb = cat_df_sb[cat_df_sb["stock_actuel"] <= 0] if not cat_df_sb.empty else pd.DataFrame()
    faibles_sb  = cat_df_sb[(cat_df_sb["stock_actuel"] > 0) & (cat_df_sb["stock_actuel"] <= 5)] if not cat_df_sb.empty else pd.DataFrame()
    if len(ruptures_sb) > 0:
        st.markdown(f"🔴 **{len(ruptures_sb)} rupture(s)** de stock !")
    if len(faibles_sb) > 0:
        st.markdown(f"🟡 **{len(faibles_sb)} article(s)** en stock faible")

    st.markdown(
        f"<div style='font-size:0.72rem;color:rgba(250,247,242,0.45);margin-top:30px;text-align:center'>"
        f"{datetime.now().strftime('%d/%m/%Y · %H:%M')}</div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
#  PAGE 0 · TABLEAU DE BORD
# ─────────────────────────────────────────────
if "🏠" in page:
    st.markdown("""
    <div class="hero-header">
        <div style="font-size:3rem">🏠</div>
        <div>
            <h1>Tableau de Bord</h1>
            <p>Bienvenue dans votre espace de gestion — MerceriePro</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cat_df   = charger_catalogue()
    vente_df = charger_ventes()

    ca_total    = vente_df["total"].sum() if not vente_df.empty else 0
    nb_articles = len(cat_df)
    auj         = date.today().isoformat()
    ca_auj      = 0
    if not vente_df.empty and "date" in vente_df.columns:
        try:
            ca_auj = vente_df[vente_df["date"] == auj]["total"].sum()
        except:
            pass

    ruptures_n = len(cat_df[cat_df["stock_actuel"] <= 0]) if not cat_df.empty else 0
    faibles_n  = len(cat_df[(cat_df["stock_actuel"] > 0) & (cat_df["stock_actuel"] <= 5)]) if not cat_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-title">CA Total</div>
            <div class="kpi-value">{ca_total:,.0f}</div>
            <div class="kpi-sub">FCFA encaissés</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card" style="border-left-color:#7D2035">
            <div class="kpi-title">CA Aujourd'hui</div>
            <div class="kpi-value">{ca_auj:,.0f}</div>
            <div class="kpi-sub">FCFA · {auj}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card" style="border-left-color:#2D6A4F">
            <div class="kpi-title">Articles Catalogue</div>
            <div class="kpi-value">{nb_articles}</div>
            <div class="kpi-sub">références enregistrées</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        couleur = "#C0392B" if ruptures_n > 0 else ("#E8A020" if faibles_n > 0 else "#C9A84C")
        st.markdown(f"""<div class="kpi-card" style="border-left-color:{couleur}">
            <div class="kpi-title">Alertes Stock</div>
            <div class="kpi-value">{ruptures_n + faibles_n}</div>
            <div class="kpi-sub">dont {ruptures_n} rupture(s)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)

    col_g, col_d = st.columns([3, 2])
    with col_g:
        st.markdown("## 📈 Évolution du Chiffre d'Affaires")
        if not vente_df.empty and "date" in vente_df.columns:
            try:
                ca_par_jour = vente_df.groupby("date")["total"].sum().reset_index()
                ca_par_jour.columns = ["Date", "CA (FCFA)"]
                ca_par_jour = ca_par_jour.sort_values("Date")
                ca_par_jour["CA cumulé"] = ca_par_jour["CA (FCFA)"].cumsum()

                fig = go.Figure()
                fig.add_trace(go.Bar(x=ca_par_jour["Date"], y=ca_par_jour["CA (FCFA)"],
                                     name="CA Journalier", marker_color="#C9A84C", opacity=0.75))
                fig.add_trace(go.Scatter(x=ca_par_jour["Date"], y=ca_par_jour["CA cumulé"],
                                         name="CA Cumulé", line=dict(color="#7D2035", width=2.5),
                                         mode="lines+markers", yaxis="y2"))
                fig.update_layout(
                    yaxis2=dict(overlaying="y", side="right", showgrid=False),
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Jost", color="#3D2B1F"),
                    legend=dict(orientation="h", y=1.1),
                    margin=dict(l=10, r=10, t=10, b=10), height=280
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Pas encore assez de données pour le graphique.")
        else:
            st.info("💡 Les graphiques apparaîtront dès vos premières ventes enregistrées.")

    with col_d:
        st.markdown("## 🔔 Alertes Stock")
        if not cat_df.empty:
            ruptures = cat_df[cat_df["stock_actuel"] <= 0]
            faibles  = cat_df[(cat_df["stock_actuel"] > 0) & (cat_df["stock_actuel"] <= 5)]
            if ruptures.empty and faibles.empty:
                st.success("✅ Tous les stocks sont satisfaisants !")
            for _, r in ruptures.iterrows():
                st.markdown(f"""<div class="alerte-rupture">🔴 <b>{r['nom']}</b><br>
                <span style='color:#C0392B'>RUPTURE — Plus aucun article en stock</span></div>""",
                            unsafe_allow_html=True)
            for _, r in faibles.iterrows():
                st.markdown(f"""<div class="alerte-faible">🟡 <b>{r['nom']}</b><br>
                <span style='color:#E8A020'>Stock faible · {int(r['stock_actuel'])} {r.get('unite', '')}</span></div>""",
                            unsafe_allow_html=True)
        else:
            st.info("Ajoutez des articles au catalogue pour voir les alertes.")

    if not vente_df.empty:
        st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)
        st.markdown("## 🕐 Dernières Ventes")
        cols_affich = [c for c in ["date", "heure", "article_nom", "categorie", "quantite", "total", "vendeur"] if c in vente_df.columns]
        dern = vente_df.tail(8).iloc[::-1][cols_affich]
        dern.columns = ["Date", "Heure", "Article", "Catégorie", "Qté", "Total (FCFA)", "Vendeur"][:len(cols_affich)]
        st.dataframe(dern, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
#  PAGE 1 · CATALOGUE
# ─────────────────────────────────────────────
elif "📦" in page:
    st.markdown("""
    <div class="hero-header">
        <div style="font-size:3rem">📦</div>
        <div>
            <h1>Gestion du Catalogue</h1>
            <p>Ajoutez, consultez et gérez tous vos articles</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕  Ajouter un article", "📋  Consulter le catalogue"])

    with tab1:
        st.markdown("### Nouvel article")
        c1, c2 = st.columns(2)
        with c1:
            nom       = st.text_input("Nom de l'article *", placeholder="Ex : Fil à coudre blanc 100m")
            categorie = st.selectbox("Catégorie *", CATEGORIES)
            unite     = st.selectbox("Unité", UNITES)
        with c2:
            prix_raw  = st.text_input("Prix unitaire (FCFA) *", placeholder="Ex : 1500")
            stock_raw = st.text_input("Quantité en stock (arrivage) *", placeholder="Ex : 50")
            photo     = st.file_uploader("Photo du produit (optionnel)", type=["jpg", "jpeg", "png", "webp"])

        st.markdown("")
        if st.button("💾  Enregistrer l'article"):
            erreurs = []
            if not nom.strip():
                erreurs.append("Le nom de l'article est obligatoire.")
            prix = None
            try:
                prix = float(prix_raw.replace(",", ".").strip())
                if prix < 0:
                    raise ValueError()
            except:
                erreurs.append("Le prix unitaire doit être un nombre positif (ex : 1500).")
            stock = None
            try:
                stock = int(stock_raw.strip())
                if stock < 0:
                    raise ValueError()
            except:
                erreurs.append("La quantité doit être un nombre entier positif (ex : 50).")

            if erreurs:
                for e in erreurs:
                    st.error(f"⚠️ {e}")
            else:
                cat_df = charger_catalogue()
                if not cat_df.empty and nom.strip().lower() in cat_df["nom"].str.lower().tolist():
                    st.warning("⚠️ Un article portant ce nom existe déjà dans le catalogue.")
                else:
                    nouvel = {
                        "id":            prochain_id(cat_df, "A"),
                        "nom":           nom.strip(),
                        "categorie":     categorie,
                        "prix_unitaire": prix,
                        "stock_initial": stock,
                        "stock_actuel":  stock,
                        "unite":         unite,
                        "photo_base64":  image_to_b64(photo),
                        "date_ajout":    date.today().isoformat(),
                    }
                    if ajouter_article(nouvel):
                        st.markdown(f"""<div class="msg-succes">
                        ✅ Article <b>{nom.strip()}</b> ajouté avec succès !<br>
                        Référence : <b>{nouvel['id']}</b> · Stock : <b>{stock} {unite}</b> · Prix : <b>{prix:,.0f} FCFA</b>
                        </div>""", unsafe_allow_html=True)
                        st.balloons()
                        st.rerun()

    with tab2:
        cat_df = charger_catalogue()
        if cat_df.empty:
            st.info("📂 Aucun article dans le catalogue. Commencez par en ajouter un !")
        else:
            col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
            with col_f1:
                recherche = st.text_input("🔍 Rechercher un article", placeholder="Nom ou référence...")
            with col_f2:
                filtre_cat = st.selectbox("Filtrer par catégorie", ["Toutes"] + CATEGORIES)
            with col_f3:
                filtre_stock = st.selectbox("Filtre stock", ["Tous", "En stock", "Stock faible (≤5)", "Rupture"])

            df_affich = cat_df.copy()
            if recherche:
                mask = df_affich["nom"].str.contains(recherche, case=False, na=False) | \
                       df_affich["id"].str.contains(recherche, case=False, na=False)
                df_affich = df_affich[mask]
            if filtre_cat != "Toutes":
                df_affich = df_affich[df_affich["categorie"] == filtre_cat]
            if filtre_stock == "En stock":
                df_affich = df_affich[df_affich["stock_actuel"] > 5]
            elif filtre_stock == "Stock faible (≤5)":
                df_affich = df_affich[(df_affich["stock_actuel"] > 0) & (df_affich["stock_actuel"] <= 5)]
            elif filtre_stock == "Rupture":
                df_affich = df_affich[df_affich["stock_actuel"] <= 0]

            st.markdown(f"<p style='color:var(--gris);font-size:0.85rem'>{len(df_affich)} article(s) affiché(s)</p>", unsafe_allow_html=True)

            articles = df_affich.reset_index(drop=True)
            cols_par_ligne = 3
            for i in range(0, len(articles), cols_par_ligne):
                cols = st.columns(cols_par_ligne)
                for j, col in enumerate(cols):
                    if i + j < len(articles):
                        art = articles.iloc[i + j]
                        stock_c = int(art["stock_actuel"])
                        couleur_stock = "#C0392B" if stock_c <= 0 else ("#E8A020" if stock_c <= 5 else "#2D6A4F")
                        label_stock   = "RUPTURE" if stock_c <= 0 else (f"⚠️ {stock_c} {art['unite']}" if stock_c <= 5 else f"{stock_c} {art['unite']}")
                        with col:
                            afficher_image_b64(art["photo_base64"], width=100)
                            st.markdown(f"""
                            <div style='background:white;border-radius:10px;padding:12px 14px;margin-bottom:8px;
                                        box-shadow:0 2px 8px rgba(61,43,31,0.08)'>
                                <div style='font-size:0.7rem;color:var(--gris);letter-spacing:0.1em'>{art['id']} · {art['categorie']}</div>
                                <div style='font-family:"Playfair Display",serif;font-size:1rem;font-weight:600;color:var(--brun);margin:4px 0'>{art['nom']}</div>
                                <div style='font-size:1.1rem;font-weight:700;color:var(--bordeaux)'>{float(art['prix_unitaire']):,.0f} FCFA</div>
                                <div style='margin-top:6px;font-size:0.82rem;color:{couleur_stock};font-weight:600'>📦 {label_stock}</div>
                            </div>""", unsafe_allow_html=True)

            st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)
            st.markdown("### ✏️ Réapprovisionnement")
            col_m1, col_m2, col_m3 = st.columns([3, 2, 1])
            with col_m1:
                art_choisi = st.selectbox("Article à réapprovisionner", cat_df["nom"].tolist(), key="reapro_art")
            with col_m2:
                qte_ajout_raw = st.text_input("Quantité à ajouter", placeholder="Ex : 20", key="reapro_qte")
            with col_m3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ Ajouter"):
                    try:
                        qte_ajout = int(qte_ajout_raw.strip())
                        if qte_ajout <= 0:
                            raise ValueError()
                        art_ligne = cat_df[cat_df["nom"] == art_choisi].iloc[0]
                        nouveau_stock = int(art_ligne["stock_actuel"]) + qte_ajout
                        if mettre_a_jour_stock(art_ligne["id"], nouveau_stock):
                            st.success(f"✅ Stock de **{art_choisi}** → **{nouveau_stock} {art_ligne['unite']}**")
                            st.rerun()
                    except:
                        st.error("⚠️ Entrez un nombre entier positif.")


# ─────────────────────────────────────────────
#  PAGE 2 · CAISSE
# ─────────────────────────────────────────────
elif "🛒" in page:
    st.markdown("""
    <div class="hero-header">
        <div style="font-size:3rem">🛒</div>
        <div>
            <h1>Caisse — Enregistrement des Ventes</h1>
            <p>Saisissez les ventes et générez vos reçus clients</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cat_df   = charger_catalogue()
    vente_df = charger_ventes()

    if cat_df.empty:
        st.warning("⚠️ Le catalogue est vide. Ajoutez d'abord des articles dans **📦 Catalogue**.")
    else:
        articles_dispo = cat_df[cat_df["stock_actuel"] > 0]["nom"].tolist()
        if not articles_dispo:
            st.error("🔴 Tous les articles sont en rupture de stock ! Veuillez réapprovisionner.")
        else:
            col_g, col_d = st.columns([3, 2])

            with col_g:
                st.markdown("### 🧾 Nouvelle Vente")
                vendeur = st.text_input("Vendeur(se) *", placeholder="Votre prénom")
                art_nom = st.selectbox("Article *", articles_dispo)
                art_ligne = cat_df[cat_df["nom"] == art_nom].iloc[0]
                prix_unit = float(art_ligne["prix_unitaire"])
                stock_act = int(art_ligne["stock_actuel"])
                unite_art = art_ligne["unite"]

                st.markdown(f"""
                <div style='background:#FFF8F0;border-left:4px solid var(--or);border-radius:8px;
                            padding:12px 16px;margin:8px 0;font-size:0.88rem'>
                    📌 Prix unitaire : <b>{prix_unit:,.0f} FCFA / {unite_art}</b> &nbsp;|&nbsp;
                    Stock disponible : <b style='color:{"#C0392B" if stock_act<=5 else "#2D6A4F"}'>{stock_act} {unite_art}</b>
                </div>""", unsafe_allow_html=True)

                qte_raw = st.text_input("Quantité vendue *", placeholder=f"Max : {stock_act}")

                qte_ok = False
                total_preview = 0
                try:
                    qte_val = int(qte_raw.strip()) if qte_raw.strip() else 0
                    if qte_val > 0:
                        total_preview = qte_val * prix_unit
                        qte_ok = True
                        st.markdown(f"""
                        <div style='background:linear-gradient(135deg,#FAF7F2,#F0EBE0);
                                    border:2px solid var(--or);border-radius:10px;padding:14px 20px;
                                    text-align:center;margin:10px 0'>
                            <div style='font-size:0.78rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--gris)'>Total à encaisser</div>
                            <div style='font-family:"Playfair Display",serif;font-size:2.2rem;font-weight:700;color:var(--bordeaux)'>{total_preview:,.0f} FCFA</div>
                        </div>""", unsafe_allow_html=True)
                except:
                    if qte_raw.strip():
                        st.error("⚠️ La quantité doit être un nombre entier (ex : 3).")

                st.markdown("")
                if st.button("✅  Valider la vente & Générer le Reçu"):
                    erreurs = []
                    if not vendeur.strip():
                        erreurs.append("Le nom du vendeur est obligatoire.")
                    if not qte_ok:
                        erreurs.append("Entrez une quantité valide supérieure à 0.")
                    else:
                        try:
                            qte_final = int(qte_raw.strip())
                            if qte_final <= 0:
                                erreurs.append("La quantité doit être supérieure à 0.")
                            elif qte_final > stock_act:
                                erreurs.append(f"Stock insuffisant : seulement {stock_act} {unite_art} disponible(s).")
                        except:
                            erreurs.append("Quantité invalide.")

                    if erreurs:
                        for e in erreurs:
                            st.error(f"⚠️ {e}")
                    else:
                        qte_final  = int(qte_raw.strip())
                        total_final = qte_final * prix_unit
                        now = datetime.now()

                        nouvelle_vente = {
                            "id":           prochain_id(vente_df, "V"),
                            "date":         now.date().isoformat(),
                            "heure":        now.strftime("%H:%M:%S"),
                            "article_id":   art_ligne["id"],
                            "article_nom":  art_nom,
                            "categorie":    art_ligne["categorie"],
                            "quantite":     qte_final,
                            "prix_unitaire": prix_unit,
                            "total":        total_final,
                            "vendeur":      vendeur.strip(),
                        }
                        ok_vente = enregistrer_vente(nouvelle_vente)
                        ok_stock = mettre_a_jour_stock(art_ligne["id"], stock_act - qte_final)

                        if ok_vente and ok_stock:
                            st.session_state["last_vente"] = nouvelle_vente
                            st.success(f"✅ Vente enregistrée ! Réf. **{nouvelle_vente['id']}**")
                            st.rerun()

            with col_d:
                st.markdown("### 🧾 Reçu Client")
                if "last_vente" in st.session_state:
                    v = st.session_state["last_vente"]
                    st.markdown(f"""
                    <div class="recu-box">
                        <div style='text-align:center;font-family:"Playfair Display",serif;font-size:1.1rem;margin-bottom:8px'>🧵 MERCERIE PRO</div>
                        <div style='text-align:center;font-size:0.75rem;margin-bottom:12px'>——————————————————</div>
                        Date &nbsp;&nbsp;: {v['date']}<br>
                        Heure &nbsp;: {v['heure']}<br>
                        Réf. &nbsp;&nbsp;: {v['id']}<br>
                        Vendeur : {v['vendeur']}<br>
                        <div style='margin:10px 0'>——————————————————</div>
                        Art. &nbsp;&nbsp;: {v['article_nom']}<br>
                        Qté &nbsp;&nbsp;&nbsp;: {v['quantite']} × {v['prix_unitaire']:,.0f} FCFA<br>
                        <div style='margin:10px 0'>——————————————————</div>
                        <div style='font-size:1.05rem;font-weight:700'>TOTAL &nbsp; : {v['total']:,.0f} FCFA</div>
                        <div style='text-align:center;margin-top:14px;font-size:0.78rem'>Merci de votre visite !<br>À bientôt 🙏</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background:white;border-radius:10px;padding:24px;text-align:center;
                                color:var(--gris);border:2px dashed var(--or-light)'>
                        <div style='font-size:2rem'>🧾</div>
                        <div style='margin-top:8px;font-size:0.9rem'>Le reçu de la dernière vente<br>apparaîtra ici</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)
            st.markdown("### 📋 Historique des ventes d'aujourd'hui")
            vf_fresh = charger_ventes()
            auj = date.today().isoformat()
            if not vf_fresh.empty and "date" in vf_fresh.columns:
                ventes_auj = vf_fresh[vf_fresh["date"] == auj]
                if ventes_auj.empty:
                    st.info("Aucune vente enregistrée aujourd'hui.")
                else:
                    total_auj = ventes_auj["total"].sum()
                    st.markdown(f"**{len(ventes_auj)} vente(s)** ce jour · CA : **{total_auj:,.0f} FCFA**")
                    cols_v = [c for c in ["id", "heure", "article_nom", "quantite", "prix_unitaire", "total", "vendeur"] if c in ventes_auj.columns]
                    affich = ventes_auj[cols_v].copy()
                    affich.columns = ["Réf.", "Heure", "Article", "Qté", "PU (FCFA)", "Total (FCFA)", "Vendeur"][:len(cols_v)]
                    st.dataframe(affich, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune vente aujourd'hui.")


# ─────────────────────────────────────────────
#  PAGE 3 · STATISTIQUES
# ─────────────────────────────────────────────
elif "📊" in page:
    st.markdown("""
    <div class="hero-header">
        <div style="font-size:3rem">📊</div>
        <div>
            <h1>Statistiques & Analyse Descriptive</h1>
            <p>Visualisez la performance de votre boutique</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cat_df   = charger_catalogue()
    vente_df = charger_ventes()

    if vente_df.empty:
        st.info("📊 Les statistiques apparaîtront dès vos premières ventes.")
    else:
        col_p1, col_p2 = st.columns(2)
        dates_dispo = sorted(vente_df["date"].unique().tolist())
        with col_p1:
            date_debut = st.selectbox("Du", dates_dispo, index=0)
        with col_p2:
            date_fin = st.selectbox("Au", dates_dispo, index=len(dates_dispo) - 1)

        vf = vente_df[(vente_df["date"] >= date_debut) & (vente_df["date"] <= date_fin)].copy()

        if vf.empty:
            st.warning("Aucune vente sur cette période.")
        else:
            ca_periode      = vf["total"].sum()
            nb_transactions = len(vf)
            panier_moyen    = ca_periode / nb_transactions
            art_top         = vf.groupby("article_nom")["quantite"].sum().idxmax()

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""<div class="kpi-card"><div class="kpi-title">CA Période</div>
                <div class="kpi-value">{ca_periode:,.0f}</div><div class="kpi-sub">FCFA</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="kpi-card" style='border-left-color:#7D2035'><div class="kpi-title">Transactions</div>
                <div class="kpi-value">{nb_transactions}</div><div class="kpi-sub">ventes enregistrées</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="kpi-card" style='border-left-color:#2D6A4F'><div class="kpi-title">Panier Moyen</div>
                <div class="kpi-value">{panier_moyen:,.0f}</div><div class="kpi-sub">FCFA / vente</div></div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""<div class="kpi-card" style='border-left-color:#5C3D2E'><div class="kpi-title">Top Article</div>
                <div class="kpi-value" style='font-size:1rem;line-height:1.3'>{art_top}</div>
                <div class="kpi-sub">+ vendu en qté</div></div>""", unsafe_allow_html=True)

            st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### 🏆 Articles les Plus Vendus")
                top_art = vf.groupby("article_nom")["quantite"].sum().sort_values(ascending=False).head(10).reset_index()
                top_art.columns = ["Article", "Quantité"]
                fig1 = px.bar(top_art, x="Quantité", y="Article", orientation="h",
                              color="Quantité", color_continuous_scale=["#F5E6C8", "#C9A84C", "#7D2035"],
                              template="simple_white")
                fig1.update_layout(font=dict(family="Jost", color="#3D2B1F"),
                                   margin=dict(l=10, r=10, t=10, b=10), height=320,
                                   coloraxis_showscale=False,
                                   yaxis=dict(categoryorder="total ascending"))
                st.plotly_chart(fig1, use_container_width=True)

            with col_b:
                st.markdown("#### 💰 CA par Catégorie")
                ca_cat = vf.groupby("categorie")["total"].sum().reset_index()
                ca_cat.columns = ["Catégorie", "CA (FCFA)"]
                palette = ["#C9A84C", "#7D2035", "#3D2B1F", "#2D6A4F", "#5C3D2E", "#A64455", "#E8D5A3", "#8A8078"]
                fig2 = px.pie(ca_cat, values="CA (FCFA)", names="Catégorie",
                              color_discrete_sequence=palette, hole=0.45, template="simple_white")
                fig2.update_traces(textposition="inside", textinfo="percent+label")
                fig2.update_layout(font=dict(family="Jost", color="#3D2B1F"),
                                   margin=dict(l=10, r=10, t=10, b=10), height=320, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            col_c, col_d2 = st.columns(2)
            with col_c:
                st.markdown("#### 📅 Évolution journalière du CA")
                ca_jour = vf.groupby("date")["total"].sum().reset_index()
                ca_jour.columns = ["Date", "CA (FCFA)"]
                fig3 = px.area(ca_jour, x="Date", y="CA (FCFA)",
                               color_discrete_sequence=["#C9A84C"], template="simple_white")
                fig3.update_traces(fill="tozeroy", fillcolor="rgba(201,168,76,0.15)", line_width=2.5)
                fig3.update_layout(font=dict(family="Jost", color="#3D2B1F"),
                                   margin=dict(l=10, r=10, t=10, b=10), height=280)
                st.plotly_chart(fig3, use_container_width=True)

            with col_d2:
                st.markdown("#### 👤 Performance par Vendeur")
                ca_vendeur = vf.groupby("vendeur")["total"].sum().sort_values(ascending=False).reset_index()
                ca_vendeur.columns = ["Vendeur", "CA (FCFA)"]
                fig4 = px.bar(ca_vendeur, x="Vendeur", y="CA (FCFA)",
                              color="CA (FCFA)", color_continuous_scale=["#E8D5A3", "#C9A84C", "#7D2035"],
                              template="simple_white")
                fig4.update_layout(font=dict(family="Jost", color="#3D2B1F"),
                                   margin=dict(l=10, r=10, t=10, b=10), height=280,
                                   coloraxis_showscale=False)
                st.plotly_chart(fig4, use_container_width=True)

            if not cat_df.empty:
                st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)
                st.markdown("#### 📦 État des Stocks")

                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    stock_df = cat_df[["nom", "stock_initial", "stock_actuel", "categorie"]].copy()
                    stock_df["vendu"] = (stock_df["stock_initial"] - stock_df["stock_actuel"]).clip(lower=0)
                    stock_top = stock_df.sort_values("vendu", ascending=False).head(10)
                    fig5 = go.Figure()
                    fig5.add_trace(go.Bar(name="Vendu", x=stock_top["nom"], y=stock_top["vendu"], marker_color="#7D2035"))
                    fig5.add_trace(go.Bar(name="Stock restant", x=stock_top["nom"], y=stock_top["stock_actuel"], marker_color="#C9A84C"))
                    fig5.update_layout(barmode="stack", template="simple_white",
                                       font=dict(family="Jost", color="#3D2B1F"),
                                       margin=dict(l=10, r=10, t=10, b=80), height=320,
                                       xaxis_tickangle=-30, legend=dict(orientation="h", y=1.1))
                    st.plotly_chart(fig5, use_container_width=True)

                with col_s2:
                    tbl = cat_df[["nom", "categorie", "stock_actuel", "unite", "prix_unitaire"]].copy()
                    tbl["Valeur (FCFA)"] = tbl["stock_actuel"] * tbl["prix_unitaire"]
                    tbl["Statut"] = tbl["stock_actuel"].apply(
                        lambda x: "🔴 RUPTURE" if x <= 0 else ("🟡 Faible" if x <= 5 else "🟢 OK"))
                    tbl = tbl.rename(columns={"nom": "Article", "categorie": "Catégorie",
                                              "stock_actuel": "Stock", "unite": "Unité"})
                    tbl = tbl[["Article", "Catégorie", "Stock", "Unité", "Valeur (FCFA)", "Statut"]].sort_values("Stock")
                    st.dataframe(tbl, use_container_width=True, hide_index=True, height=300)

                valeur_totale = (cat_df["stock_actuel"] * cat_df["prix_unitaire"]).sum()
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,var(--brun),#5C3D2E);border-radius:12px;
                            padding:18px 24px;margin-top:10px;display:flex;justify-content:space-between;align-items:center'>
                    <div style='color:var(--or-light);font-size:0.85rem;letter-spacing:0.1em'>VALEUR TOTALE DU STOCK</div>
                    <div style='font-family:"Playfair Display",serif;color:var(--or);font-size:2rem;font-weight:700'>{valeur_totale:,.0f} FCFA</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div class='or-divider'></div>", unsafe_allow_html=True)
            with st.expander("📄 Données brutes des ventes"):
                st.dataframe(vf, use_container_width=True, hide_index=True)
                st.download_button("⬇️ Télécharger en CSV",
                                   vf.to_csv(index=False).encode("utf-8"),
                                   "ventes_export.csv", "text/csv")
