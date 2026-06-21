"""Regenera apenas os dois event studies com fontes maiores, para legibilidade
no relatório final (exibidos a meia largura, lado a lado). Não altera números:
mesma especificação DR + covariáveis de diagnostico_callaway_santanna.py.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from diff_diff import CallawaySantAnna, plot_event_study

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# Fontes ampliadas: ao reduzir para 0.49\textwidth no LaTeX, o texto continua legível.
plt.rcParams.update({
    "figure.dpi": 120,
    "font.size": 16,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
})

ROOT = Path(__file__).resolve().parents[2]
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"
FIG_DIR = ROOT / "relatorios/figuras_causal"
ASSETS = ROOT / "codes/streamlit/assets"

OUTCOMES = {
    "taxa_notificacoes": {"label": "Notificações /100k (Acesso)", "cor": "#008080"},
    "taxa_feminicidios": {"label": "Feminicídios /100k (Letalidade)", "cor": "#C0392B"},
}
N_BOOTSTRAP = 999
SEED = 42
TREAT_KW = dict(unit="id_municipio", time="ano", first_treat="first_treat")
COVARIATES = ["taxa_homicidios_masc", "log_populacao",
              "log_pib_per_capita", "delta_homicidios_masc"]
EST_METHOD = "dr"

df = pd.read_csv(PATH_PAINEL).rename(columns={"coorte": "first_treat"})

for col, meta in OUTCOMES.items():
    tag = col.replace("taxa_", "")
    cs = CallawaySantAnna(control_group="never_treated", estimation_method=EST_METHOD,
                          n_bootstrap=N_BOOTSTRAP, cluster="id_municipio", seed=SEED)
    res = cs.fit(df, outcome=col, aggregate="event_study",
                 covariates=COVARIATES, **TREAT_KW)

    fig, ax = plt.subplots(figsize=(9, 6))
    plot_event_study(res, ax=ax, show=False, title=f"Event Study — {meta['label']}",
                     xlabel="Anos relativos à adoção do 24h",
                     ylabel="ATT (taxa /100k)", color=meta["cor"])
    plt.tight_layout()
    out = FIG_DIR / f"{tag}_02_event_study.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"regenerado: {out.relative_to(ROOT)}")

    import shutil
    shutil.copy(out, ASSETS / f"event_study_{tag}.png")
