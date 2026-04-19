import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import date

from crud import (
    get_all_vetements, get_all_tenues, get_vetements_from_tenue,
    add_vetement, delete_vetement, update_proprete_vetement,
    create_tenue, delete_tenue, add_vetement_to_tenue,
)
from meteo import get_previsions, geocoder_ville
from moteur_decisionel import recommander_tenues, get_stats_port


st.set_page_config(
    page_title="MonPetitDressing",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=Playfair+Display:wght@700&display=swap');

:root {
    --b50 : #e1eefe;
    --b100: #c3ddfd;
    --b200: #93c5fd;
    --b400: #60a5fa;
    --b600: #3779e3;
    --b800: #1e40af;
    --b950: #0d1f4c;
}

html, body, [class*="css"]        { font-family: 'Sora', sans-serif; }
h1, h2, h3                        { font-family: 'Playfair Display', serif; color: var(--b950); }
.stApp                            { background: linear-gradient(155deg,#f5f9ff 0%,#e8f2ff 100%); }

/* ─── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(185deg, var(--b950) 0%, #1a3a7a 62%, var(--b600) 100%) !important;
}
[data-testid="stSidebar"] *                    { color: var(--b50) !important; }
[data-testid="stSidebar"] label                { color: var(--b100) !important; font-size:.72em !important; letter-spacing:.08em !important; text-transform:uppercase !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background:rgba(255,255,255,.09) !important; border:1px solid rgba(225,238,254,.20) !important; border-radius:10px !important; }
[data-testid="stSidebar"] input                { background:rgba(255,255,255,.09) !important; border:1px solid rgba(225,238,254,.20) !important; border-radius:10px !important; color:var(--b600) !important; }
[data-testid="stSidebar"] .stButton > button   { background:rgba(255,255,255,.12) !important; border:1px solid rgba(225,238,254,.25) !important; color:var(--b50) !important; border-radius:10px !important; width:100% !important; font-size:.85em !important; }
[data-testid="stSidebar"] .stButton > button:hover { background:rgba(255,255,255,.22) !important; }

/* ─── Metric cards ────────────────────────────────── */
[data-testid="metric-container"]  { background:white; border:1.5px solid var(--b100); border-top:4px solid var(--b600); border-radius:14px; padding:18px 20px; box-shadow:0 4px 20px rgba(55,121,227,.09); }
[data-testid="stMetricValue"]     { color:var(--b800) !important; font-weight:600; }

/* ─── Cards ───────────────────────────────────────── */
.card          { background:white; border-radius:16px; padding:22px; box-shadow:0 2px 16px rgba(55,121,227,.07); border:1px solid var(--b100); margin-bottom:14px; }
.card-accent   { border-left:4px solid var(--b600); }
.card-success  { border-left:4px solid #10b981; }
.card-warning  { border-left:4px solid #f59e0b; }
.card-danger   { border-left:4px solid #ef4444; }

/* ─── Hero banner ─────────────────────────────────── */
.hero-banner {
    background: linear-gradient(118deg, var(--b600) 0%, var(--b800) 100%);
    border-radius:22px; padding:30px 36px; color:white;
    margin-bottom:24px; position:relative; overflow:hidden;
    box-shadow:0 8px 32px rgba(55,121,227,.25);
}
.hero-banner::after {  position:absolute; right:32px; top:50%; transform:translateY(-50%); font-size:6em; opacity:.12; pointer-events:none; }
.hero-banner h1     { color:white !important; font-size:1.85em; margin:0 0 5px 0; }
.hero-sub           { color:rgba(255,255,255,.72); font-size:.9em; }

/* ─── Chip ────────────────────────────────────────── */
.chip { display:inline-flex; align-items:center; gap:6px; background:var(--b50); border:1px solid var(--b100); color:var(--b800); border-radius:20px; padding:4px 14px; font-size:.78em; font-weight:600; letter-spacing:.05em; text-transform:uppercase; margin-bottom:10px; }

/* ─── Météo day cards ────────────────────────────── */
.mday      { background:white; border-radius:14px; padding:14px 6px; text-align:center; box-shadow:0 2px 10px rgba(55,121,227,.07); border:1.5px solid var(--b100); transition:all .2s; }
.mday:hover{ transform:translateY(-4px); box-shadow:0 10px 28px rgba(55,121,227,.18); border-color:var(--b600); }
.mday-now  { background:linear-gradient(155deg,var(--b600) 0%,var(--b800) 100%); border-color:transparent; box-shadow:0 6px 20px rgba(55,121,227,.30); }

/* ─── Tenue card ──────────────────────────────────── */
.tenue-card { background:linear-gradient(135deg,var(--b50) 0%,#f0f7ff 100%); border-radius:20px; padding:24px; border:1.5px solid var(--b100); margin-bottom:20px; }

/* ─── Bouton primary ──────────────────────────────── */
.stButton > button[kind="primary"] { background:linear-gradient(135deg,var(--b600) 0%,var(--b800) 100%) !important; border:none !important; border-radius:10px !important; color:white !important; font-weight:500 !important; box-shadow:0 4px 14px rgba(55,121,227,.30) !important; transition:all .2s !important; }
.stButton > button[kind="primary"]:hover { transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(55,121,227,.42) !important; }

/* ─── Scrollbar ──────────────────────────────────── */
::-webkit-scrollbar       { width:5px; }
::-webkit-scrollbar-track { background:var(--b50); }
::-webkit-scrollbar-thumb { background:var(--b400); border-radius:4px; }

/* ─── Divers ──────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; border:1px solid var(--b100) !important; }
hr { border-color:var(--b100) !important; }
</style>
""", unsafe_allow_html=True)


if "ville_nom"   not in st.session_state: st.session_state.ville_nom   = "Toulouse"
if "ville_lat"   not in st.session_state: st.session_state.ville_lat   = 43.6047
if "ville_lon"   not in st.session_state: st.session_state.ville_lon   = 1.4442
if "ville_label" not in st.session_state: st.session_state.ville_label = "Toulouse, France"


with st.sidebar:

    st.markdown("""
    <div style="padding:10px 0 6px 0">
      <div style="font-family:'Playfair Display',serif;font-size:1.5em;font-weight:700;
                  color:#e1eefe;line-height:1.2">MonPetitDressing</div>
 
    </div>
    <hr style="border-color:rgba(225,238,254,.13);margin:12px 0">
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:.68em;color:rgba(225,238,254,.42);letter-spacing:.10em;"
                "text-transform:uppercase;margin-bottom:5px'>Menu</p>",
                unsafe_allow_html=True)
    menu = st.selectbox("nav",
        ["Accueil","Gestion Dressing","Assistant Tenues","Dressing Virtuel","Historique des Tenues"],
        label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(225,238,254,.13);margin:16px 0'>",
                unsafe_allow_html=True)

    st.markdown("<p style='font-size:.68em;color:rgba(225,238,254,.42);letter-spacing:.10em;"
                "text-transform:uppercase;margin-bottom:5px'>📍 Ville météo</p>",
                unsafe_allow_html=True)
    ville_input = st.text_input("ville", value=st.session_state.ville_nom,
                                placeholder="Ex : Lyon, Bordeaux…",
                                label_visibility="collapsed")
    if st.button("Valider la ville", key="btn_ville"):
        with st.spinner("Recherche…"):
            res = geocoder_ville(ville_input)
        if res:
            st.session_state.ville_nom   = res["nom"]
            st.session_state.ville_lat   = res["latitude"]
            st.session_state.ville_lon   = res["longitude"]
            reg = f", {res['region']}" if res["region"] else ""
            st.session_state.ville_label = f"{res['nom']}{reg}, {res['pays']}"
            st.rerun()
        else:
            st.error("Ville introuvable.")

    st.markdown("<hr style='border-color:rgba(225,238,254,.13);margin:14px 0'>",
                unsafe_allow_html=True)
    _prev1 = get_previsions(latitude=st.session_state.ville_lat,
                             longitude=st.session_state.ville_lon, jours=1)
    if _prev1:
        p = _prev1[0]
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.09);border-radius:14px;
                    padding:16px;border:1px solid rgba(225,238,254,.15)">
          <div style="font-size:.66em;color:rgba(225,238,254,.42);text-transform:uppercase;
                      letter-spacing:.09em;margin-bottom:4px">Aujourd'hui</div>
          <div style="font-size:.8em;color:#c3ddfd;font-weight:500;margin-bottom:10px">
            📍 {st.session_state.ville_label}</div>
          <div style="display:flex;align-items:center;gap:12px">
            <span style="font-size:2.4em">{p['emoji']}</span>
            <div>
              <div style="font-size:2em;font-weight:700;color:#e1eefe;line-height:1">
                {p['temp_moyenne']:.0f}°C</div>
              <div style="font-size:.72em;color:rgba(225,238,254,.55)">{p['description']}</div>
              <div style="font-size:.68em;color:rgba(225,238,254,.38);margin-top:2px">
                {p['temp_min']:.0f}° – {p['temp_max']:.0f}°C &nbsp;·&nbsp; 💧 {p['precipitation']:.0f} mm
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(225,238,254,.13);margin:14px 0'>",
                unsafe_allow_html=True)


_lat   = st.session_state.ville_lat
_lon   = st.session_state.ville_lon
_label = st.session_state.ville_label

BLUES  = ["#3779e3","#1e40af","#60a5fa","#93c5fd","#c3ddfd","#e1eefe"]
ICONS  = {"Haut simple":"👕","Haut chaud":"🧥","Bas court":"🩳",
          "Bas long":"👖","Ensemble":"🤵","Accessoire":"👒"}



if menu == "Accueil":

    st.markdown(f"""
    <div class="hero-banner">
      <h1>Dashbaord Dressing</h1>
      <div class="hero-sub">Pour éviter la surconsommation textile pensez à revendre vos vêtements inutilisés et ne pas acheter des vêtements que vous avez déjà !<br>
        <span style="font-size:.85em;opacity:.65">📍 {_label}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    vetements = get_all_vetements()
    tenues    = get_all_tenues()
    stats     = get_stats_port()
    nb_sales  = sum(1 for v in vetements if not v[5])
    nb_jamais = len(stats["jamais_portes"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vêtements",          len(vetements))
    c2.metric("Tenues enregitrées",             len(tenues))
    c3.metric("À laver",            nb_sales,
              delta="Tout propre !" if nb_sales == 0 else f" ",
              delta_color="normal" if nb_sales == 0 else "inverse")
    c4.metric("Jamais portés",      nb_jamais,
              delta="À valoriser !" if nb_jamais > 0 else "Excellent !",
              delta_color="inverse" if nb_jamais > 0 else "normal")

    st.markdown("<br>", unsafe_allow_html=True)


    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        if vetements:
            st.markdown(
                '<div class="chip">Répartition des vêtements</div>',
                unsafe_allow_html=True
            )

            tc = pd.Series([v[2] for v in vetements]).value_counts().reset_index()
            tc.columns = ["Type", "Nombre"]

            fig = px.bar(
                tc,
                x="Type",
                y="Nombre",
                color="Type",
                text="Nombre",
                color_discrete_sequence=BLUES
            )

            fig.update_layout(
                margin=dict(t=10, b=10, l=0, r=0),
                height=290,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="",
                yaxis_title="",
            )

            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
            )

            st.plotly_chart(fig, width='stretch')

    with col_r:
        if vetements:
            st.markdown('<div class="chip">Nombre de vêtements par couleur</div>',
                        unsafe_allow_html=True)
            cc = (pd.Series([v[3].lower() for v in vetements])
                  .value_counts().head(8).reset_index())
            cc.columns = ["Couleur", "Nombre"]
            fig2 = px.bar(cc, x="Nombre", y="Couleur", orientation="h",
                          color="Nombre",
                          color_continuous_scale=[[0,"#c3ddfd"],[.5,"#3779e3"],[1,"#0d1f4c"]])
            fig2.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=290,
                coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(autorange="reversed"))
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, width='stretch')

    st.markdown("---")

    st.markdown('<div class="chip">Consommation responsable</div>',
                unsafe_allow_html=True)
    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("**Vêtements jamais portés**")
        if stats["jamais_portes"]:
            df_j = pd.DataFrame(stats["jamais_portes"],
                columns=["ID","Nom","Type","Couleur principale","Couleur secondaire","Propre"]
            )[["Nom","Type","Couleur principale"]]
            st.dataframe(df_j, width='stretch', hide_index=True)
            st.markdown(
                f'<div class="card card-warning" style="padding:12px;margin-top:4px">'
                f'💡 <b>{len(stats["jamais_portes"])}</b> vêtement(s) à redécouvrir !</div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="card card-success" style="padding:12px">'
                        'Tous tes vêtements ont été portés récemment !</div>',
                        unsafe_allow_html=True)

    with col_e2:
        st.markdown("**Top 8 des vêtements les plus portés**")
        if stats["frequence_par_vet"]:
            freq = stats["frequence_par_vet"]
            noms = stats["noms_par_id"]
            df_f = pd.DataFrame([
                {"Vêtement": noms.get(k, f"ID {k}"), "Fois porté": v}
                for k, v in sorted(freq.items(), key=lambda x: -x[1])
            ])
            fig3 = px.bar(df_f, x="Fois porté", y="Vêtement", orientation="h",
                          color="Fois porté",
                          color_continuous_scale=[[0,"#e1eefe"],[.5,"#3779e3"],[1,"#0d1f4c"]])
            fig3.update_layout(margin=dict(t=5,b=5,l=0,r=0), height=268,
                coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig3, width='stretch')
        else:
            st.info("Pas encore assez d'historique de tenues.")



    st.markdown("---")
    st.markdown(f'<div class="chip">Prévisions — {_label} (7 jours)</div>',
                unsafe_allow_html=True)
    previsions = get_previsions(latitude=_lat, longitude=_lon, jours=7)
    if previsions:
        cols_m = st.columns(len(previsions))
        for i, (col_m, prev) in enumerate(zip(cols_m, previsions)):
            label = "Auj." if i == 0 else prev["date"].strftime("%a %d")
            if i == 0:
                html = (
                    f'<div class="mday mday-now">'
                    f'<div style="font-size:.72em;font-weight:600;color:rgba(255,255,255,.75)">{label}</div>'
                    f'<div style="font-size:1.9em;margin:5px 0">{prev["emoji"]}</div>'
                    f'<div style="font-size:1.15em;font-weight:700;color:white">{prev["temp_moyenne"]:.0f}°C</div>'
                    f'<div style="font-size:.68em;color:rgba(255,255,255,.60)">{prev["temp_min"]:.0f}–{prev["temp_max"]:.0f}°C</div>'
                    f'<div style="font-size:.68em;color:rgba(255,255,255,.55);margin-top:2px">💧{prev["precipitation"]:.0f}mm</div>'
                    f'</div>'
                )
            else:
                html = (
                    f'<div class="mday">'
                    f'<div style="font-size:.72em;color:#888;font-weight:500">{label}</div>'
                    f'<div style="font-size:1.7em;margin:4px 0">{prev["emoji"]}</div>'
                    f'<div style="font-size:1.05em;font-weight:600;color:#0d1f4c">{prev["temp_moyenne"]:.0f}°C</div>'
                    f'<div style="font-size:.68em;color:#aaa">{prev["temp_min"]:.0f}–{prev["temp_max"]:.0f}°C</div>'
                    f'<div style="font-size:.68em;color:#3779e3;margin-top:2px">💧{prev["precipitation"]:.0f}mm</div>'
                    f'</div>'
                )
            with col_m:
                st.markdown(html, unsafe_allow_html=True)
    else:
        st.warning("Impossible de récupérer la météo. Vérifiez votre connexion.")



elif menu == "Gestion Dressing":
    st.title("Gestion des Vêtements et Tenues")
    action = st.radio("Section", ["Vêtements", "Tenues"], horizontal=True)

    if action == "Vêtements":
        with st.expander("➕ Ajouter un vêtement", expanded=True):
            nom  = st.text_input("Nom")
            typ  = st.selectbox("Type", ["Haut simple","Haut chaud","Bas court",
                                         "Bas long","Ensemble","Accessoire"])
            cp   = st.text_input("Couleur principale")
            cs   = st.text_input("Couleur secondaire (optionnel)")
            prop = st.checkbox("Propre", value=True)
            if st.button("Ajouter vêtement", type="primary"):
                if not nom or not cp:
                    st.error("Remplissez les champs obligatoires.")
                else:
                    add_vetement(nom, typ, cp, cs if cs else cp, prop)
                    msg = st.success("✅ Vêtement ajouté !")
                    time.sleep(2); msg.empty(); st.rerun()

        with st.expander("Supprimer un vêtement"):
            vets = get_all_vetements()
            if vets:
                vd = {f"{v[1]} ({v[2]}, {v[3]})": v[0] for v in vets}
                vs = st.selectbox("Sélectionner", list(vd.keys()))
                if st.button("Supprimer", type="secondary"):
                    delete_vetement(vd[vs]); st.success("Supprimé !"); st.rerun()

        with st.expander("Propreté"):
            vets = get_all_vetements()
            if vets:
                df_p = pd.DataFrame(vets, columns=["ID","Nom","Type","Couleur principale","Couleur secondaire","Propre"])
                for _, row in df_p.iterrows():
                    a, b = st.columns([3, 1])
                    a.write(f"**{row['Nom']}** — {row['Type']}")
                    nouveau = b.checkbox("Propre", value=bool(row["Propre"]),
                                         key=f"pr_{row['ID']}")
                    if nouveau != bool(row["Propre"]):
                        update_proprete_vetement(row["ID"], nouveau); st.rerun()

    elif action == "Tenues":
        with st.expander("➕ Créer une tenue", expanded=True):
            c1, c2, c3 = st.columns(3)
            jour  = c1.date_input("Jour", value=date.today())
            temp  = c2.number_input("Température (°C)", -20, 50, 15, 1)
            note  = c3.number_input("Note /10", 0, 10, value=None, step=1)
            if st.button("Créer la tenue", type="primary"):
                id_t = create_tenue(jour, temp, note)
                st.success(f"✅ Tenue créée (ID {id_t})"); st.rerun()

        with st.expander("Associer un vêtement à une tenue"):
            tns = get_all_tenues(); vets = get_all_vetements()
            if tns and vets:
                td = {f"Tenue {t[0]} — {t[1]}": t[0] for t in tns}
                vd = {f"{v[1]} ({v[2]}, {v[3]})": v[0] for v in vets}
                ts = st.selectbox("Tenue", list(td.keys()))
                vs = st.selectbox("Vêtement", list(vd.keys()))
                if st.button("Associer", type="primary"):
                    add_vetement_to_tenue(td[ts], vd[vs])
                    st.success("Vêtement ajouté à la tenue !")

        with st.expander("Supprimer une tenue"):
            tns = get_all_tenues()
            if tns:
                td = {f"Tenue {t[0]} — {t[1]}": t[0] for t in tns}
                ts = st.selectbox("Sélectionner", list(td.keys()))
                if st.button("Supprimer la tenue", type="secondary"):
                    delete_tenue(td[ts]); st.success("Supprimée !"); st.rerun()


elif menu == "Assistant Tenues":
    st.title("Assistant personnel pour la recommandation de tenues")
    st.markdown("")

    previsions = get_previsions(latitude=_lat, longitude=_lon, jours=7)
    col_m, col_p = st.columns([2, 1])

    with col_p:
        st.markdown("#### Paramètres")
        if previsions:
            dates_dispo = {
                prev["date"].strftime("%A %d %b") + f" — {prev['emoji']} {prev['temp_moyenne']:.0f}°C": prev
                for prev in previsions
            }
            choix = st.selectbox("Choisir un jour", list(dates_dispo.keys()))
            pc = dates_dispo[choix]
            t_reco = pc["temp_moyenne"]
            st.markdown(
                f'<div class="card card-accent" style="padding:14px">'
                f'{pc["emoji"]} <b>{pc["description"]}</b><br>'
                f'<span style="font-size:.85em;color:#555">{pc["temp_min"]:.0f}°C → {pc["temp_max"]:.0f}°C'
                f' · 💧 {pc["precipitation"]:.0f} mm</span></div>',
                unsafe_allow_html=True)
        else:
            t_reco = st.slider("Température (°C)", -10, 40, 18)
        nb_prop = st.slider("Nombre de propositions", 1, 5, 3)
        lancer  = st.button("Générer des recommandations", type="primary",
                            width='stretch')



    if lancer:
        st.markdown("---")
        st.markdown(f"### Propositions pour {t_reco:.0f}°C")
        with st.spinner("Analyse du dressing…"):
            propositions = recommander_tenues(t_reco, nb_prop)

        if not propositions:
            st.warning("Pas assez de vêtements pour générer une tenue complète.")
        else:
            for i, prop in enumerate(propositions):
                st.markdown(
                    f'<div class="tenue-card">'
                    f'<div style="font-size:1.1em;font-weight:600;color:#0d1f4c">'
                    f' Proposition {i+1}'
                    f'<span style="float:right;font-size:.85em;color:#3779e3">'
                    f'Score : {prop["score_total"]:.1f}</span></div></div>',
                    unsafe_allow_html=True)

                cv = st.columns(max(1, len(prop["vetements"])))
                for col_v, vet in zip(cv, prop["vetements"]):
                    prp = "Propre" if vet[5] else "À laver"
                    with col_v:
                        st.markdown(
                            f'<div class="card" style="text-align:center">'
                            f'<div style="font-weight:600;margin:8px 0;color:#0d1f4c">{vet[1]}</div>'
                            f'<div style="font-size:.82em;color:#3779e3">{vet[2]}</div>'
                            f'<div style="font-size:.78em;color:#888;margin:4px 0">{vet[3]}'
                            f'{"  /  " + vet[4] if vet[4] != vet[3] else ""}</div>'
                            f'<div style="font-size:.78em">{prp}</div></div>',
                            unsafe_allow_html=True)

                s1, s2, s3 = st.columns(3)
                s1.metric("Score météo",      f"{prop['score_scoring']:.1f}")
                s2.metric("Historique",  f"{prop['score_knn']:.1f}/10")
                s3.metric("Harmonie couleurs", f"{prop['score_couleurs']:+.1f}")

                st.markdown(
                    f'<div class="card card-accent" style="padding:14px;margin-top:6px">'
                    f'<small style="color:#444">{prop["explication"]}</small></div>',
                    unsafe_allow_html=True)


                st.markdown("")



elif menu == "Dressing Virtuel":
    st.title("Mon Dressing Virtuel")
    vets = get_all_vetements()
    if vets:
        df = pd.DataFrame(vets,
             columns=["ID","Nom","Type","Couleur principale","Couleur secondaire","Propre"])
        f1, f2, f3 = st.columns(3)
        types_u = ["Tous"] + sorted(df["Type"].unique().tolist())
        ft  = f1.selectbox("Type", types_u)
        fp  = f2.selectbox("Propreté", ["Tous","Propre","À laver"])
        fc  = f3.text_input("Couleur (recherche)")
        dff = df.copy()
        if ft != "Tous": dff = dff[dff["Type"] == ft]
        if fp == "Propre":   dff = dff[dff["Propre"] == True]
        elif fp == "À laver": dff = dff[dff["Propre"] == False]
        if fc: dff = dff[dff["Couleur principale"].str.lower().str.contains(fc.lower())]
        st.markdown(f"**{len(dff)} vêtement(s) affichés**")
        st.dataframe(dff.style.applymap(
            lambda v: "background-color:#fef9c3" if v is False else "", subset=["Propre"]),
            width='stretch', hide_index=True)
    else:
        st.info("Aucun vêtement dans ton dressing pour l'instant.")



elif menu == "Historique des Tenues":
    st.title("Historique des tenues")
    tns = get_all_tenues()
    if tns:
        df = pd.DataFrame(tns, columns=["ID","Jour","Température","Note"])
        df["Jour"] = pd.to_datetime(df["Jour"])
        notees = df.dropna(subset=["Note"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Tenues totales", len(df))
        c2.metric("Note moyenne", f"{notees['Note'].mean():.1f}/10" if len(notees) > 0 else "—")
        c3.metric("Temp. moyenne portée", f"{df['Température'].mean():.1f}°C")
        st.dataframe(df.sort_values("Jour", ascending=False),
                     width='stretch', hide_index=True)

        st.markdown("---")
        st.subheader("Détails d'une tenue")
        td = {f"Tenue {t[0]} — {t[1]}": t[0] for t in tns}
        ts = st.selectbox("Sélectionner", list(td.keys()))
        vts = get_vetements_from_tenue(td[ts])
        if vts:
            cols = st.columns(len(vts))
            for col, v in zip(cols, vts):
                with col:
                    st.markdown(
                        f'<div class="card" style="text-align:center">'
                        f'<div style="font-weight:600;color:#0d1f4c">{v[1]}</div>'
                        f'<div style="font-size:.82em;color:#3779e3">{v[2]}</div>'
                        f'<div style="font-size:.78em;color:#888">{v[3]}</div></div>',
                        unsafe_allow_html=True)

        t_data = next((t for t in tns if t[0] == td[ts]), None)
        if t_data:
            st.markdown("**Modifier la note**")
            nv = st.number_input("Note /10", 0, 10,
                                  value=int(t_data[3]) if t_data[3] is not None else 5,
                                  key="note_edit")
            if st.button("Enregistrer la note", type="primary"):
                from database import connexion_database
                bdd = connexion_database()
                cur = bdd.cursor()
                cur.execute("UPDATE tenue SET note = %s WHERE id_tenue = %s",
                            (nv, t_data[0]))
                bdd.commit(); cur.close(); bdd.close()
                st.success("Note mise à jour !"); st.rerun()
    else:
        st.info("Aucune tenue enregistrée.")