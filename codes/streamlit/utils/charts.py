"""
Templates de gráficos Plotly reutilizáveis com design premium.
Tema escuro com paleta azul FEA-USP.
"""
import plotly.graph_objects as go
import plotly.express as px

# ─── Paleta de cores FEA-USP (azul dominante) ────────────────────────
COLORS = {
    "primary":     "#1B4F72",   # Azul FEA escuro
    "secondary":   "#2E86C1",   # Azul médio
    "accent":      "#5DADE2",   # Azul claro
    "highlight":   "#85C1E9",   # Azul highlight
    "light":       "#AED6F1",   # Azul pastel
    "warning":     "#F39C12",   # Âmbar
    "danger":      "#E74C3C",   # Vermelho
    "success":     "#27AE60",   # Verde
    "text":        "#ECF0F1",   # Cinza claro
    "text_dim":    "#95A5A6",   # Cinza médio
    "bg_dark":     "#0B1A2E",   # Fundo escuro
    "bg_card":     "#112240",   # Fundo card
    "bg_surface":  "#1A3150",   # Fundo superfície
    "grid":        "#1E3A5F",   # Linhas do grid
}

# Paleta sequencial para gráficos
PALETTE = ["#1B4F72", "#2E86C1", "#5DADE2", "#85C1E9", "#AED6F1",
           "#F39C12", "#E74C3C", "#27AE60", "#8E44AD", "#F1C40F"]

PALETTE_WARM = ["#E74C3C", "#F39C12", "#F1C40F", "#27AE60", "#2E86C1",
                "#8E44AD", "#1ABC9C", "#E67E22", "#3498DB", "#9B59B6"]


def apply_theme(fig: go.Figure, height: int = 450, show_legend: bool = True) -> go.Figure:
    """Aplica o tema premium escuro/azul a qualquer figura Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,26,46,0.6)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=COLORS["text"], size=13),
        title=dict(font=dict(size=18, color=COLORS["text"]), x=0.0, xanchor="left"),
        height=height,
        margin=dict(l=60, r=30, t=60, b=50),
        showlegend=show_legend,
        legend=dict(
            bgcolor="rgba(17,34,64,0.7)",
            bordercolor=COLORS["grid"],
            borderwidth=1,
            font=dict(size=11, color=COLORS["text_dim"]),
        ),
        xaxis=dict(
            gridcolor=COLORS["grid"],
            gridwidth=0.5,
            zerolinecolor=COLORS["grid"],
            title_font=dict(size=12, color=COLORS["text_dim"]),
            tickfont=dict(size=11, color=COLORS["text_dim"]),
        ),
        yaxis=dict(
            gridcolor=COLORS["grid"],
            gridwidth=0.5,
            zerolinecolor=COLORS["grid"],
            title_font=dict(size=12, color=COLORS["text_dim"]),
            tickfont=dict(size=11, color=COLORS["text_dim"]),
        ),
        hoverlabel=dict(
            bgcolor=COLORS["bg_card"],
            bordercolor=COLORS["secondary"],
            font=dict(color=COLORS["text"], size=12),
        ),
    )
    return fig


def metric_card_css() -> str:
    """Retorna CSS para cards de métricas premium."""
    return """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #112240 0%, #1A3150 100%);
        border: 1px solid #1E3A5F;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(46,134,193,0.2);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #5DADE2;
        margin: 4px 0;
        letter-spacing: -1px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #95A5A6;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
    }
    .delta-up { color: #E74C3C; }
    .delta-down { color: #27AE60; }
    .delta-neutral { color: #F39C12; }

    /* Section dividers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #AED6F1;
        border-bottom: 2px solid #1E3A5F;
        padding-bottom: 8px;
        margin: 30px 0 16px 0;
        letter-spacing: 0.5px;
    }

    /* Insight boxes */
    .insight-box {
        background: linear-gradient(135deg, rgba(46,134,193,0.15) 0%, rgba(93,173,226,0.08) 100%);
        border-left: 3px solid #2E86C1;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin: 12px 0;
        font-size: 0.92rem;
        color: #AED6F1;
        line-height: 1.5;
    }

    /* KPI row */
    .kpi-row {
        display: flex;
        gap: 16px;
        margin: 16px 0;
    }
    </style>
    """


def render_metric(label: str, value: str, delta: str = None, delta_dir: str = "neutral") -> str:
    """Renderiza um card de métrica em HTML."""
    delta_html = ""
    if delta:
        css_class = f"delta-{delta_dir}"
        icon = "▲" if delta_dir == "up" else ("▼" if delta_dir == "down" else "●")
        delta_html = f'<div class="metric-delta {css_class}">{icon} {delta}</div>'

    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """


def section_header(text: str) -> str:
    """Renderiza um cabeçalho de seção estilizado."""
    return f'<div class="section-header">{text}</div>'
