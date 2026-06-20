"""
diagnostico_callaway_santanna.py
Suite completa de estatísticas e gráficos da metodologia Callaway & Sant'Anna (2021)
para a avaliação das DEAMs 24h (desfechos em taxa por 100 mil habitantes).

Para cada desfecho (taxa_notificacoes, taxa_feminicidios) produz:
  - Estatísticas descritivas tratado x controle (pré/pós)
  - Desenho de adoção escalonada (coortes)
  - Tendências brutas (médias por grupo ao longo do tempo)
  - Event study / ATT dinâmico com bandas de confiança
  - Heatmap dos efeitos grupo-tempo ATT(g,t)
  - Efeitos por coorte (group effects)
  - ATTs agregados (simples, dinâmico, por coorte, por ano-calendário)
  - Teste conjunto de pré-tendências

Saídas:
  relatorios/figuras_causal/*.png
  relatorios/estatisticas_causal.md
  relatorios/csv_causal/*.csv
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from diff_diff import (
    CallawaySantAnna,
    plot_event_study,
    plot_group_time_heatmap,
    plot_group_effects,
)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

ROOT = Path(__file__).resolve().parents[2]
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"
FIG_DIR = ROOT / "relatorios/figuras_causal"
CSV_DIR = ROOT / "relatorios/csv_causal"
REPORT = ROOT / "relatorios/estatisticas_causal.md"
ASSETS = ROOT / "codes/streamlit/assets"

OUTCOMES = {
    "taxa_notificacoes": {"label": "Notificações /100k (Acesso)", "cor": "#008080"},
    "taxa_feminicidios": {"label": "Feminicídios /100k (Letalidade)", "cor": "#C0392B"},
}

N_BOOTSTRAP = 999
SEED = 42
TREAT_KW = dict(unit="id_municipio", time="ano", first_treat="first_treat")

# Covariáveis da estimação duplamente robusta (DR-DiD). Idênticas às de
# modelo_causal_brasil.py para coerência entre figuras e modelo principal:
#   taxa_homicidios_masc  -> violência estrutural basal (recorte masculino evita
#                            containment com o outcome de feminicídio)
#   log_populacao         -> porte municipal (assimétrico -> log)
#   log_pib_per_capita    -> desenvolvimento econômico (assimétrico -> log)
#   delta_homicidios_masc -> surto recente de violência letal; corrige a adoção
#                            reativa (tendência pré-tratamento do feminicídio)
COVARIATES: list[str] = ["taxa_homicidios_masc", "log_populacao",
                         "log_pib_per_capita", "delta_homicidios_masc"]
EST_METHOD = "dr" if COVARIATES else "reg"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def carregar() -> pd.DataFrame:
    df = pd.read_csv(PATH_PAINEL).rename(columns={"coorte": "first_treat"})
    df["Grupo"] = np.where(df["first_treat"] > 0, "Tratado (24h)", "Controle (comercial)")
    return df


def fit_cs(df: pd.DataFrame, col: str, aggregate: str) -> "object":
    cs = CallawaySantAnna(
        control_group="never_treated",
        estimation_method=EST_METHOD,
        n_bootstrap=N_BOOTSTRAP,
        cluster="id_municipio",
        seed=SEED,
    )
    return cs.fit(df, outcome=col, aggregate=aggregate,
                  covariates=(COVARIATES or None), **TREAT_KW)


def es_df(res) -> pd.DataFrame:
    """Event study -> DataFrame ordenado por tempo relativo."""
    rows = []
    for t, e in sorted((res.event_study_effects or {}).items()):
        d = e if isinstance(e, dict) else {"effect": e}
        rows.append({
            "tempo_relativo": int(t),
            "efeito": d.get("effect"),
            "se": d.get("se"),
            "ci_lower": d.get("conf_int", (None, None))[0],
            "ci_upper": d.get("conf_int", (None, None))[1],
            "periodo": "pré" if int(t) < 0 else "pós",
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Estatísticas descritivas
# ─────────────────────────────────────────────────────────────────────────────
def descritivas(df: pd.DataFrame) -> pd.DataFrame:
    """Médias por grupo, no período pré-tratamento universal (até 2013) e geral."""
    metr = list(OUTCOMES.keys()) + ["feminicidios", "notificacoes", "populacao"]
    linhas = []
    for grupo, sub in df.groupby("Grupo"):
        d = {"Grupo": grupo, "n_municipios": sub["id_municipio"].nunique(),
             "n_obs": len(sub)}
        for m in metr:
            d[m] = round(sub[m].mean(), 3)
        linhas.append(d)
    tab = pd.DataFrame(linhas)
    return tab


# ─────────────────────────────────────────────────────────────────────────────
# 2. Desenho de adoção escalonada
# ─────────────────────────────────────────────────────────────────────────────
def fig_adocao(df: pd.DataFrame) -> None:
    trat = df[df["first_treat"] > 0].copy()
    ordem = (trat.drop_duplicates("id_municipio")
             .sort_values(["first_treat", "municipio"]))
    id_order = ordem["id_municipio"].tolist()
    labels = (ordem["municipio"] + "/" + ordem["uf"]).tolist()
    pos = {mid: i for i, mid in enumerate(id_order)}

    fig, ax = plt.subplots(figsize=(11, 10))
    for mid in id_order:
        sub = trat[trat["id_municipio"] == mid]
        g = sub["first_treat"].iloc[0]
        y = pos[mid]
        ax.plot(sub["ano"], [y] * len(sub), "-", color="#dfe6e9", lw=6, zorder=1)
        pre = sub[sub["ano"] < g]
        pos_ = sub[sub["ano"] >= g]
        ax.scatter(pre["ano"], [y] * len(pre), c="#b2bec3", s=18, zorder=2)
        ax.scatter(pos_["ano"], [y] * len(pos_), c="#008080", s=22, zorder=3)
        ax.scatter([g], [y], marker="|", c="#C0392B", s=260, lw=2, zorder=4)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("Ano")
    ax.set_title("Desenho de Adoção Escalonada — conversão para DEAM 24h\n"
                 "(cinza = pré-tratamento, verde = pós, linha vermelha = ano de adoção)",
                 fontweight="bold", fontsize=12)
    ax.set_xticks(range(2009, 2020))
    ax.margins(y=0.01)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "00_adocao_escalonada.png", bbox_inches="tight")
    plt.close()

    # Distribuição de coortes
    coortes = (trat.drop_duplicates("id_municipio")
               .groupby("first_treat").size())
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(coortes.index.astype(int), coortes.values, color="#008080")
    for x, v in zip(coortes.index.astype(int), coortes.values):
        ax.text(x, v + 0.1, str(v), ha="center", fontsize=10)
    ax.set_xlabel("Ano de adoção (coorte)")
    ax.set_ylabel("Nº de municípios tratados")
    ax.set_title("Tamanho das coortes de tratamento", fontweight="bold")
    ax.set_xticks(range(2009, 2020))
    plt.tight_layout()
    plt.savefig(FIG_DIR / "00b_coortes.png", bbox_inches="tight")
    plt.close()
    return coortes


# ─────────────────────────────────────────────────────────────────────────────
# 3. Tendências brutas
# ─────────────────────────────────────────────────────────────────────────────
def fig_raw_trends(df: pd.DataFrame, col: str, label: str, fname: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df, x="ano", y=col, hue="Grupo", estimator="mean",
                 errorbar=("ci", 95), marker="o", linewidth=2.5,
                 palette={"Tratado (24h)": "#008080",
                          "Controle (comercial)": "#4169E1"}, ax=ax)
    ax.set_title(f"Tendências Brutas — {label}", fontweight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel(f"Média de {label}")
    ax.set_xticks(range(2009, 2020))
    ax.legend(title="Grupo")
    plt.tight_layout()
    plt.savefig(FIG_DIR / fname, bbox_inches="tight")
    plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Teste conjunto de pré-tendências (Wald sobre coefs pré do event study)
# ─────────────────────────────────────────────────────────────────────────────
def teste_pretrends(res) -> dict:
    """Wald conjunto H0: todos os coeficientes pré-tratamento = 0."""
    df_es = es_df(res)
    pre = df_es[df_es["periodo"] == "pré"].dropna(subset=["efeito", "se"])
    if pre.empty:
        return {"estatistica": None, "p_valor": None, "n_coefs": 0, "metodo": "indisponível"}
    # Aproximação diagonal (usa apenas SEs individuais): soma de (b/se)^2 ~ chi2(k)
    from scipy import stats
    z2 = (pre["efeito"] / pre["se"]) ** 2
    wald = float(z2.sum())
    k = int(len(pre))
    pval = float(1 - stats.chi2.cdf(wald, df=k))
    n_signif = int((z2 > stats.chi2.ppf(0.95, df=1)).sum())
    return {"estatistica": round(wald, 3), "p_valor": round(pval, 4),
            "n_coefs": k, "n_individualmente_signif": n_signif,
            "metodo": "Wald diagonal (z² somados ~ χ²)"}


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline por desfecho
# ─────────────────────────────────────────────────────────────────────────────
def processar_desfecho(df: pd.DataFrame, col: str, meta: dict) -> dict:
    label = meta["label"]
    tag = col.replace("taxa_", "")
    print(f"\n=== {label} ({col}) ===")

    r_simple = fit_cs(df, col, "simple")
    r_es = fit_cs(df, col, "event_study")
    r_group = fit_cs(df, col, "group")

    att = float(r_simple.overall_att)
    se = float(r_simple.overall_se)
    ci = r_simple.overall_conf_int
    print(f"  ATT global = {att:+.3f} (SE {se:.3f}); IC95% [{ci[0]:.3f}, {ci[1]:.3f}]; p={r_simple.overall_p_value:.4f}")

    # --- Event study (nativo) ---
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_event_study(r_es, ax=ax, show=False, title=f"Event Study — {label}",
                     xlabel="Anos relativos à adoção do 24h",
                     ylabel="ATT (taxa /100k)", color=meta["cor"])
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{tag}_02_event_study.png", bbox_inches="tight")
    plt.close()

    # --- Heatmap ATT(g,t) (nativo) ---
    try:
        fig, ax = plt.subplots(figsize=(11, 7))
        plot_group_time_heatmap(r_es, ax=ax, show=False,
                                title=f"ATT(g,t) — {label}", annotate=False)
        plt.tight_layout()
        plt.savefig(FIG_DIR / f"{tag}_03_heatmap_gt.png", bbox_inches="tight")
        plt.close()
    except Exception as e:
        print(f"  [heatmap] {e}")

    # --- Efeitos por coorte (nativo) ---
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        plot_group_effects(r_group, ax=ax, show=False,
                           title=f"Efeitos por coorte — {label}")
        plt.tight_layout()
        plt.savefig(FIG_DIR / f"{tag}_04_efeitos_coorte.png", bbox_inches="tight")
        plt.close()
    except Exception as e:
        print(f"  [group effects] {e}")

    # --- Tabelas CSV ---
    df_es = es_df(r_es)
    df_es.to_csv(CSV_DIR / f"{tag}_event_study.csv", index=False, encoding="utf-8")

    grp = pd.DataFrame([
        {"coorte": int(g), "efeito": round(v["effect"], 4) if isinstance(v, dict) else v,
         "se": round(v.get("se"), 4) if isinstance(v, dict) and v.get("se") else None}
        for g, v in (r_group.group_effects or {}).items()
    ])
    grp.to_csv(CSV_DIR / f"{tag}_efeitos_coorte.csv", index=False, encoding="utf-8")

    pretrend = teste_pretrends(r_es)

    return {
        "label": label, "att": att, "se": se,
        "ci_lower": float(ci[0]), "ci_upper": float(ci[1]),
        "p_valor": float(r_simple.overall_p_value),
        "n_trat": int(r_simple.n_treated_units), "n_ctrl": int(r_simple.n_control_units),
        "pretrend": pretrend,
        "es": df_es, "grupo": grp,
    }


def fig_forest(resultados: dict) -> None:
    """Forest plot comparando ATT global dos desfechos com IC95%."""
    fig, ax = plt.subplots(figsize=(9, 4))
    ys = range(len(resultados))
    for y, (col, r) in zip(ys, resultados.items()):
        ax.errorbar(r["att"], y, xerr=[[r["att"] - r["ci_lower"]], [r["ci_upper"] - r["att"]]],
                    fmt="o", color=OUTCOMES[col]["cor"], capsize=5, markersize=10, lw=2)
        ax.text(r["att"], y + 0.12, f"{r['att']:+.2f} (p={r['p_valor']:.3f})",
                ha="center", fontsize=10)
    ax.axvline(0, color="gray", ls="--", alpha=0.7)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([resultados[c]["label"] for c in resultados])
    ax.set_xlabel("ATT global (Callaway & Sant'Anna) — taxa /100k")
    ax.set_title("Efeito Médio do Tratamento (ATT) por Desfecho", fontweight="bold")
    ax.margins(y=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "05_forest_att.png", bbox_inches="tight")
    plt.close()


def escrever_relatorio(desc: pd.DataFrame, coortes, resultados: dict) -> None:
    L = []
    L.append("# Estatísticas — Callaway & Sant'Anna (DEAMs 24h, Brasil)\n")
    metodo = (f"estimação **duplamente robusta (DR)** com covariáveis "
              f"({', '.join(COVARIATES)})" if COVARIATES
              else "estimação por regressão (`reg`), sem covariáveis")
    L.append(f"Desfechos em **taxa por 100 mil habitantes**. Estimador CS DiD, "
             f"controle = nunca-tratados (DEAMs comerciais), 999 réplicas bootstrap, "
             f"{metodo}.\n")

    L.append("## 1. Estatísticas descritivas\n")
    L.append(desc.to_markdown(index=False))
    L.append("")

    L.append("## 2. Coortes de tratamento (adoção escalonada)\n")
    L.append("| Ano de adoção | Nº municípios |")
    L.append("|---|---|")
    for g, n in coortes.items():
        L.append(f"| {int(g)} | {int(n)} |")
    L.append("")

    L.append("## 3. ATT global por desfecho\n")
    L.append("| Desfecho | ATT | SE | IC95% | p-valor | N trat/ctrl |")
    L.append("|---|---|---|---|---|---|")
    for col, r in resultados.items():
        L.append(f"| {r['label']} | {r['att']:+.3f} | {r['se']:.3f} | "
                 f"[{r['ci_lower']:.3f}, {r['ci_upper']:.3f}] | {r['p_valor']:.4f} | "
                 f"{r['n_trat']}/{r['n_ctrl']} |")
    L.append("")

    L.append("## 4. Teste conjunto de pré-tendências\n")
    L.append("H0: todos os coeficientes pré-tratamento do event study = 0.\n")
    L.append("| Desfecho | Estatística Wald | p-valor | nº coefs pré | indiv. signif. |")
    L.append("|---|---|---|---|---|")
    for col, r in resultados.items():
        pt = r["pretrend"]
        L.append(f"| {r['label']} | {pt['estatistica']} | {pt['p_valor']} | "
                 f"{pt['n_coefs']} | {pt.get('n_individualmente_signif','-')} |")
    L.append(f"\n_Método: {resultados[list(resultados)[0]]['pretrend']['metodo']}. "
             "p<0,05 indica violação das tendências paralelas._\n")

    L.append("## 5. Efeitos por coorte\n")
    for col, r in resultados.items():
        L.append(f"\n### {r['label']}\n")
        L.append(r["grupo"].to_markdown(index=False))
        L.append("")

    L.append("## 6. Figuras geradas (relatorios/figuras_causal/)\n")
    L.append("- `00_adocao_escalonada.png` — desenho de adoção escalonada")
    L.append("- `00b_coortes.png` — tamanho das coortes")
    L.append("- `{notificacoes,feminicidios}_01_raw_trends.png` — tendências brutas")
    L.append("- `{...}_02_event_study.png` — ATT dinâmico com IC")
    L.append("- `{...}_03_heatmap_gt.png` — ATT(g,t)")
    L.append("- `{...}_04_efeitos_coorte.png` — efeitos por coorte")
    L.append("- `05_forest_att.png` — comparação dos ATT globais")
    L.append("")

    REPORT.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    for d in (FIG_DIR, CSV_DIR, ASSETS):
        d.mkdir(parents=True, exist_ok=True)

    df = carregar()
    print(f"Painel: {df['id_municipio'].nunique()} municípios x {df['ano'].nunique()} anos")

    desc = descritivas(df)
    desc.to_csv(CSV_DIR / "descritivas.csv", index=False, encoding="utf-8")

    coortes = fig_adocao(df)

    resultados = {}
    for col, meta in OUTCOMES.items():
        fig_raw_trends(df, col, meta["label"], f"{col.replace('taxa_','')}_01_raw_trends.png")
        resultados[col] = processar_desfecho(df, col, meta)

    fig_forest(resultados)
    escrever_relatorio(desc, coortes, resultados)

    # Copiar event studies-chave para o Streamlit
    import shutil
    for tag in ("notificacoes", "feminicidios"):
        src = FIG_DIR / f"{tag}_02_event_study.png"
        if src.exists():
            shutil.copy(src, ASSETS / f"event_study_{tag}.png")

    print(f"\nRelatório  -> {REPORT.relative_to(ROOT)}")
    print(f"Figuras    -> {FIG_DIR.relative_to(ROOT)}/ ({len(list(FIG_DIR.glob('*.png')))} PNGs)")
    print(f"CSVs       -> {CSV_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
