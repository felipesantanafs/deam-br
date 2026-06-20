"""
modelo_causal_brasil.py
Avaliação de impacto NACIONAL da conversão de DEAMs para o regime 24h.

Estimador principal: Callaway & Sant'Anna (2021) — staggered DiD — via lib `diff_diff`.
Robustez: Sun & Abraham (2021) e Borusyak et al. (BJS Imputation).

Painel de entrada: dados/consolidado/painel_deam_anual.csv
  unit  = id_municipio        time = ano        coorte = first_treat (0 = nunca tratado)
  grupo = '24h' (tratado) / 'comercial' (controle nunca convertido)

----------------------------------------------------------------------------------
SOBRE O PSM (Propensity Score Matching) — resposta à pergunta de desenho:

NÃO é necessário rodar um PSM separado ANTES do Callaway & Sant'Anna. O estimador
CS já incorpora o ajuste por covariáveis internamente:
  - estimation_method='dr'  -> doubly-robust (regressão de resultado + escore de
                               propensão); robusto a má especificação de um dos dois.
  - estimation_method='ipw' -> só escore de propensão (inverse prob. weighting).
  - estimation_method='reg' -> só regressão de resultado.
O parâmetro `pscore_trim` confirma que o próprio CS estima o escore de propensão e
apara unidades fora do suporte comum. Logo, passar `COVARIATES` com 'dr' já entrega
a "identificação condicional" que um PSM buscaria — sem o passo extra.

Um PSM separado só agrega valor para (a) PRÉ-SELECIONAR/aparar o pool de controles
quando ele é muito maior que o de tratados (aqui: 247 controles vs 38 tratados) ou
(b) garantir overlap antes de estimar. É complementar, não obrigatório.

LIMITAÇÃO ATUAL: o painel ainda NÃO tem covariáveis socioeconômicas (população, IDH,
renda...). Sem elas, roda-se o CS sob tendências paralelas INCONDICIONAIS (COVARIATES
vazio). Quando essas covariáveis forem anexadas, basta preencher COVARIATES e usar
estimation_method='dr' — e o PSM continua dispensável.
----------------------------------------------------------------------------------
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from diff_diff import CallawaySantAnna, SunAbraham, ImputationDiD

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
PATH_PAINEL = ROOT / "dados/consolidado/painel_deam_anual.csv"

# Resultados (acesso) e letalidade, estimados em TAXA por 100 mil habitantes para
# neutralizar a heterogeneidade de porte populacional entre tratados e controles.
# chave (compatível com o Streamlit) -> coluna do painel, rótulo e direção esperada.
OUTCOMES = {
    "notificacoes": {"col": "taxa_notificacoes", "label": "Acesso (SINAN) /100k",   "esperado": "alta"},
    "feminicidios": {"col": "taxa_feminicidios", "label": "Letalidade (SIM) /100k",  "esperado": "baixa"},
}

# Covariável de violência basal: taxa de homicídios MASCULINOS /100k.
# Proxy de violência estrutural ambiente (crime organizado, tráfico, letalidade
# policial) que motiva a adoção reativa da DEAM 24h, sem ser plausivelmente afetada
# por ela. Usamos o recorte masculino (não "geral") porque o outcome de letalidade
# (taxa_feminicidios) é o subconjunto feminino dos mesmos CIDs X85-Y09: condicionar
# em homicídios gerais controlaria parcialmente pelo próprio outcome (containment).
#
# Embora a coluna seja anual (time-varying), o CS da lib `diff_diff` recupera a
# covariável no BASE PERIOD de cada coorte (g-1), nunca no valor pós-tratamento
# (staggered.py:730) — funciona como baseline pré-tratamento cohort-specific, sem
# risco de bad control. A coorte 2009 (sem g-1 no painel) é descartada pelo estimador.
COVARIATES: list[str] = ["taxa_homicidios_masc"]
EST_METHOD = "dr" if COVARIATES else "reg"

N_BOOTSTRAP = 999
SEED = 42


def carregar_painel() -> pd.DataFrame:
    df = pd.read_csv(PATH_PAINEL)
    # A lib usa a coluna de coorte como 'first_treat' (0 = nunca tratado).
    df = df.rename(columns={"coorte": "first_treat"})
    return df


def _eff_to_dict(eff) -> dict:
    """Normaliza uma entrada de efeito (dict ou escalar) para {effect, se}."""
    if isinstance(eff, dict):
        e = eff.get("effect")
        s = eff.get("se")
    else:
        e, s = float(eff), None
    if s is not None and not np.isfinite(s):
        s = None
    return {
        "effect": round(float(e), 4) if e is not None else None,
        "se": round(float(s), 4) if s is not None else None,
    }


def estimar_outcome(df: pd.DataFrame, outcome: str) -> None:
    """Roda CS DiD (ATT global + event study) e robustez (SA, BJS) para um resultado."""
    col = OUTCOMES[outcome]["col"]
    label = OUTCOMES[outcome]["label"]
    print(f"\n>>> {label}  ({col})")

    cs = CallawaySantAnna(
        control_group="never_treated",
        estimation_method=EST_METHOD,
        n_bootstrap=N_BOOTSTRAP,
        cluster="id_municipio",
        seed=SEED,
    )
    cov = COVARIATES or None

    # ATT global
    cs_global = cs.fit(df, outcome=col, unit="id_municipio", time="ano",
                       first_treat="first_treat", aggregate="simple", covariates=cov)
    # Event study (efeitos dinâmicos por tempo relativo ao tratamento)
    cs_es = cs.fit(df, outcome=col, unit="id_municipio", time="ano",
                   first_treat="first_treat", aggregate="event_study", covariates=cov)

    att = float(cs_global.overall_att)
    se = float(cs_global.overall_se)
    pval = float(cs_global.overall_p_value)
    ci = cs_global.overall_conf_int

    print(f"    CS  ATT = {att:+.4f}  SE = {se:.4f}  IC95% = [{float(ci[0]):+.4f}, {float(ci[1]):+.4f}]  p = {pval:.4f}")

    def _finite(x):
        """nan/inf -> None (alguns estimadores retornam nan sem levantar exceção)."""
        return float(x) if (x is not None and np.isfinite(x)) else None

    # Sun & Abraham
    try:
        sa = SunAbraham().fit(df, outcome=col, unit="id_municipio", time="ano",
                              first_treat="first_treat", covariates=cov)
        sa_att, sa_se = _finite(sa.overall_att), _finite(sa.overall_se)
        if sa_att is None:
            print("    [SA] retornou nan (provável colinearidade/posto deficiente) -> None")
        else:
            print(f"    SA  ATT = {sa_att:+.4f}  SE = {sa_se:.4f}")
    except Exception as e:
        print(f"    [SA] falhou: {e}")

    # Borusyak et al. (BJS Imputation)
    try:
        bjs = ImputationDiD().fit(df, outcome=col, unit="id_municipio", time="ano",
                                  first_treat="first_treat", covariates=cov)
        bjs_att, bjs_se = _finite(bjs.overall_att), _finite(bjs.overall_se)
        if bjs_att is None:
            print("    [BJS] retornou nan -> None")
        else:
            print(f"    BJS ATT = {bjs_att:+.4f}  SE = {bjs_se:.4f}")
    except Exception as e:
        print(f"    [BJS] falhou: {e}")

    # Event study — coeficientes por tempo relativo
    print(f"\n    Event study ({label}):")
    print(f"    {'t':>4}  {'ATT':>8}  {'SE':>8}")
    for rel_t, eff in sorted((cs_es.event_study_effects or {}).items()):
        d = _eff_to_dict(eff)
        e_str = f"{d['effect']:+.4f}" if d["effect"] is not None else "    None"
        s_str = f"{d['se']:.4f}"      if d["se"]     is not None else "    None"
        print(f"    {int(rel_t):>4}  {e_str:>8}  {s_str:>8}")


def main() -> None:
    df = carregar_painel()
    n_trat = df.loc[df["first_treat"] > 0, "id_municipio"].nunique()
    n_ctrl = df.loc[df["first_treat"] == 0, "id_municipio"].nunique()
    print(f"Painel: {df['id_municipio'].nunique()} municípios x "
          f"{df['ano'].nunique()} anos | {n_trat} tratados (24h), {n_ctrl} controles")
    print(f"Método de estimação: {EST_METHOD}  | covariáveis: {COVARIATES or 'nenhuma (TP incondicional)'}")

    for outcome in OUTCOMES:
        estimar_outcome(df, outcome)

    print("\nFim do pipeline causal nacional.")


if __name__ == "__main__":
    main()
