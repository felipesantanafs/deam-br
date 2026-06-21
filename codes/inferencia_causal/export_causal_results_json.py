"""
export_causal_results_json.py
Roda o modelo causal NACIONAL na especificação final (duplamente robusta, DR, com
covariáveis) e exporta dados/consolidado/causal_results.json no formato consumido
pelo dashboard Streamlit (pages/7_Modelo_Causal.py).

Especificação idêntica a modelo_causal_brasil.py e diagnostico_callaway_santanna.py:
  estimador Callaway & Sant'Anna (2021), controle = nunca-tratados, 999 bootstrap,
  estimation_method='dr' com COVARIATES (homicídios masc., log pop., log PIB pc,
  delta homicídios masc.). Robustez: Sun & Abraham e BJS Imputation.
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from diff_diff import CallawaySantAnna, SunAbraham, ImputationDiD

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"
OUT_JSON = ROOT / "dados/consolidado/causal_results.json"

OUTCOMES = {
    "notificacoes": {"col": "taxa_notificacoes", "label": "Acesso (SINAN) /100k"},
    "feminicidios": {"col": "taxa_feminicidios", "label": "Letalidade (SIM) /100k"},
}
COVARIATES = ["taxa_homicidios_masc", "log_populacao",
              "log_pib_per_capita", "delta_homicidios_masc"]
EST_METHOD = "dr"
N_BOOTSTRAP = 999
SEED = 42
TREAT_KW = dict(unit="id_municipio", time="ano", first_treat="first_treat")


def _finite(x):
    return float(x) if (x is not None and np.isfinite(x)) else None


def _round(x, n=4):
    v = _finite(x)
    return round(v, n) if v is not None else None


def _cs():
    return CallawaySantAnna(control_group="never_treated", estimation_method=EST_METHOD,
                            n_bootstrap=N_BOOTSTRAP, cluster="id_municipio", seed=SEED)


def event_study(res) -> dict:
    out = {}
    for t, eff in sorted((res.event_study_effects or {}).items()):
        e = eff.get("effect") if isinstance(eff, dict) else float(eff)
        s = eff.get("se") if isinstance(eff, dict) else None
        out[str(int(t))] = {"effect": _round(e), "se": _round(s)}
    return out


def group_effects(res) -> dict:
    out = {}
    for g, eff in (res.group_effects or {}).items():
        e = eff.get("effect") if isinstance(eff, dict) else float(eff)
        s = eff.get("se") if isinstance(eff, dict) else None
        out[str(int(g))] = {"effect": _round(e), "se": _round(s)}
    return out


def estimar(df, outcome) -> dict:
    col = OUTCOMES[outcome]["col"]
    print(f"\n>>> {OUTCOMES[outcome]['label']} ({col})")
    cov = COVARIATES or None

    g = _cs().fit(df, outcome=col, aggregate="simple", covariates=cov, **TREAT_KW)
    es = _cs().fit(df, outcome=col, aggregate="event_study", covariates=cov, **TREAT_KW)
    gr = _cs().fit(df, outcome=col, aggregate="group", covariates=cov, **TREAT_KW)
    ci = g.overall_conf_int

    sa_att = sa_se = bjs_att = bjs_se = None
    try:
        sa = SunAbraham().fit(df, outcome=col, covariates=cov, **TREAT_KW)
        sa_att, sa_se = _finite(sa.overall_att), _finite(sa.overall_se)
    except Exception as e:
        print(f"    [SA] {e}")
    try:
        bjs = ImputationDiD().fit(df, outcome=col, covariates=cov, **TREAT_KW)
        bjs_att, bjs_se = _finite(bjs.overall_att), _finite(bjs.overall_se)
    except Exception as e:
        print(f"    [BJS] {e}")

    print(f"    CS ATT = {g.overall_att:+.4f} (SE {g.overall_se:.4f}) "
          f"IC95% [{float(ci[0]):+.4f}, {float(ci[1]):+.4f}] p={g.overall_p_value:.4f}")
    print(f"    SA = {sa_att} | BJS = {bjs_att}")

    return {
        "cs_att": _round(g.overall_att),
        "cs_se": _round(g.overall_se),
        "cs_p_value": _round(g.overall_p_value),
        "cs_ci_lower": _round(ci[0]),
        "cs_ci_upper": _round(ci[1]),
        "sa_att": _round(sa_att), "sa_se": _round(sa_se),
        "bjs_att": _round(bjs_att), "bjs_se": _round(bjs_se),
        "event_study": event_study(es),
        "group_effects": group_effects(gr),
        "n_treated_units": int(g.n_treated_units),
        "n_control_units": int(g.n_control_units),
    }


def main():
    df = pd.read_csv(PATH_PAINEL).rename(columns={"coorte": "first_treat"})
    trat = df[df["first_treat"] > 0].drop_duplicates("id_municipio")
    coortes = {str(int(k)): int(v) for k, v in
               trat.groupby("first_treat").size().items()}
    n_trat = trat["id_municipio"].nunique()
    n_ctrl = df.loc[df["first_treat"] == 0, "id_municipio"].nunique()

    cs_did = {o: estimar(df, o) for o in OUTCOMES}

    out = {
        "metadata": {
            "escopo": "Nacional (municípios brasileiros)",
            "periodo": "2009-2019",
            "hipotese": "Impacto causal da conversão de DEAMs para o regime 24h",
            "metodo_principal": "Callaway & Sant'Anna (2021) via diff-diff",
            "estimation_method": EST_METHOD,
            "covariaveis": COVARIATES,
            "contrafactual": "DEAMs de horário comercial (nunca convertidas para 24h)",
            "control_group": "never_treated",
            "coortes": coortes,
            "n_municipios_tratados": n_trat,
            "n_municipios_controle": n_ctrl,
            "robustez": "Sun & Abraham (2021), Borusyak et al. (2024)",
            "nota_covariaveis": ("Estimação duplamente robusta (DR): regressão de "
                                 "resultado + escore de propensão sobre as covariáveis. "
                                 "A covariável delta_homicidios_masc corrige a adoção "
                                 "reativa que violava as tendências paralelas do "
                                 "feminicídio sob especificação só de nível."),
        },
        "cs_did_24h": cs_did,
    }

    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"\nJSON -> {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
