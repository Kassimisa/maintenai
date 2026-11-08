"""Démo MaintenAI : surveillance d'une pompe + assistant IA.

Lancement :
    streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import streamlit as st

from maintenai.anomaly.data import list_experiments, load_file
from maintenai.anomaly.model import AnomalyDetector
from maintenai.config import SENSOR_LABELS

st.set_page_config(page_title="MaintenAI", page_icon="🔧", layout="wide")
st.title("🔧 MaintenAI")
st.caption("Copilote IA pour les techniciens de maintenance · démo sur le jeu de données SKAB")

tab_monitor, tab_assistant = st.tabs(["📈 Surveillance machine", "💬 Assistant IA"])


@st.cache_data
def run_detection(path: str, train_rows: int, window: int, quantile: float):
    df = load_file(Path(path))
    model = AnomalyDetector(window=window, threshold_quantile=quantile).fit(df.iloc[:train_rows])
    df = df.assign(score=model.score(df), alert=model.predict(df))
    df.loc[df.index[:train_rows], "alert"] = 0  # période d'apprentissage : pas d'alerte
    return df, model.threshold


with tab_monitor:
    try:
        experiments = list_experiments()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    col1, col2, col3 = st.columns(3)
    group = col1.selectbox("Groupe d'expériences", list(experiments))
    path = col2.selectbox("Expérience", experiments[group], format_func=lambda p: p.name)
    window = col3.slider("Fenêtre glissante (s)", 1, 60, 10)
    train_rows, quantile = 400, 0.99

    df, threshold = run_detection(str(path), train_rows, window, quantile)
    test = df.iloc[train_rows:]
    n_alerts = int(test["alert"].sum())

    m1, m2, m3 = st.columns(3)
    m1.metric("Points surveillés", len(test))
    m2.metric("Alertes levées", n_alerts)
    m3.metric("Anomalies réelles (étiquettes)", int(test["anomaly"].sum()))

    if n_alerts:
        first = test.index[test["alert"] == 1][0]
        st.error(f"⚠️ Anomalie détectée à partir de {first:%H:%M:%S} sur la pompe du banc SKAB")
    else:
        st.success("✅ Aucun comportement anormal détecté")

    sensors = st.multiselect(
        "Capteurs affichés", list(SENSOR_LABELS),
        default=["Accelerometer1RMS", "Pressure", "Current", "Volume Flow RateRMS"],
        format_func=SENSOR_LABELS.get,
    )
    fig, axes = plt.subplots(len(sensors) + 1, 1, figsize=(12, 2 * (len(sensors) + 1)), sharex=True)
    axes = list(axes) if len(sensors) else [axes]
    for ax, col in zip(axes, sensors):
        ax.plot(df.index, df[col], lw=0.8, color="#1f4e78")
        ax.fill_between(df.index, df[col].min(), df[col].max(), where=df["anomaly"] == 1,
                        color="#e07a2e", alpha=0.25, label="anomalie réelle")
        ax.set_ylabel(SENSOR_LABELS[col], fontsize=8)
    ax = axes[-1]
    ax.plot(df.index, df["score"], lw=0.8, color="#333333", label="score d'anomalie")
    ax.axhline(threshold, color="#c0392b", ls="--", lw=1, label="seuil d'alerte")
    ax.axvline(df.index[train_rows], color="grey", ls=":", lw=1, label="fin de l'apprentissage")
    ax.legend(loc="upper left", fontsize=7)
    ax.set_ylabel("Score", fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    st.caption("Zones orange : anomalies réelles étiquetées. Le modèle apprend sur les 400 "
               "premières secondes (fonctionnement normal) puis surveille la suite.")

    if n_alerts:
        st.session_state["alert_context"] = (
            f"Anomalie détectée sur une pompe à eau (expérience {group}/{path.name}) : "
            "comportement anormal des capteurs de vibration, pression, courant et débit."
        )

with tab_assistant:
    st.write("Posez une question : l'assistant répond à partir des manuels indexés et cite ses sources.")
    try:
        from maintenai.assistant.ollama_client import OllamaError
        from maintenai.assistant.rag import Index, answer
        index = Index.load()
    except FileNotFoundError as exc:
        st.info(f"{exc}\n\nAjoutez des PDF dans `data/manuals/` puis lancez l'indexation.")
        st.stop()

    context = st.session_state.get("alert_context")
    use_alert = bool(context) and st.checkbox("Inclure la dernière alerte machine", value=True)
    if "history" not in st.session_state:
        st.session_state.history = []
    for role, text in st.session_state.history:
        st.chat_message(role).write(text)

    if question := st.chat_input("Ex. : La pompe vibre anormalement, que dois-je vérifier ?"):
        st.chat_message("user").write(question)
        try:
            with st.spinner("Recherche dans les manuels…"):
                reply, hits = answer(question, index, context if use_alert else None)
            sources = ", ".join(f"{h['source']} p.{h['page']}" for h in hits)
            reply = f"{reply}\n\n*Sources : {sources}*"
        except OllamaError as exc:
            reply = f"❌ {exc}"
        st.chat_message("assistant").write(reply)
        st.session_state.history += [("user", question), ("assistant", reply)]
