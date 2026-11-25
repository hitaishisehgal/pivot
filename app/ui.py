"""Shared PIVOT design system, chart palette, and theme-aware components."""
import streamlit as st

SLATE_BLUE = "#2F4454"
DEEP_BURGUNDY = "#2E151B"
DUSTY_ROSE = "#DA7B93"
MUTED_TEAL = "#376E6F"
DEEP_TEAL = "#1C3334"

LIGHT_CHART_COLORS = [SLATE_BLUE, DUSTY_ROSE, MUTED_TEAL, "#9A7A86", "#75908D", "#B58E74"]
DARK_CHART_COLORS = ["#A9C2D0", DUSTY_ROSE, "#79AAA4", "#D3B8C2", "#D8C4A7", "#9BB0C0"]


def chart_colors():
    return DARK_CHART_COLORS if st.session_state.get("pivot_theme", "light") == "dark" else LIGHT_CHART_COLORS


def inject_theme(theme="light"):
    """Inject the single PIVOT component stylesheet for the active mode."""
    dark = theme == "dark"
    tokens = (
        "--pivot-bg:#172226;--pivot-surface:#202F33;--pivot-card:#26383C;--pivot-raised:#31464A;"
        "--pivot-primary:#2E151B;--pivot-sidebar:#21171B;--pivot-rose:#DA7B93;--pivot-teal:#79AAA4;"
        "--pivot-deep-teal:#F4F0EA;--pivot-text:#F4F0EA;--pivot-muted:#C1CCCD;--pivot-border:#45595D;"
        "--pivot-input:#202F33;--pivot-placeholder:#C1CCCD;--pivot-hover:#34494D;--pivot-focus:rgba(218,123,147,.3);--pivot-shadow:rgba(0,0,0,.18)"
        if dark else
        "--pivot-bg:#F5F3EE;--pivot-surface:#FCFBF8;--pivot-card:#FFFFFF;--pivot-raised:#EEEAE4;"
        "--pivot-primary:#2E151B;--pivot-sidebar:#2E151B;--pivot-rose:#DA7B93;--pivot-teal:#376E6F;"
        "--pivot-deep-teal:#1C3334;--pivot-text:#1C3334;--pivot-muted:#53666B;--pivot-border:#D6DCD9;"
        "--pivot-input:#FFFFFF;--pivot-placeholder:#53666B;--pivot-hover:#F3E8E9;--pivot-focus:rgba(218,123,147,.24);--pivot-shadow:rgba(28,51,52,.07)"
    )
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Manrope:wght@500;600;700;800&display=swap');
:root{{{tokens}}}
html,body,[data-testid="stAppViewContainer"],.stApp{{background:var(--pivot-bg)!important;color:var(--pivot-text)!important;font-family:Inter,system-ui,sans-serif}}
[data-testid="stMain"]{{background:var(--pivot-bg)}}
header[data-testid="stHeader"],.stAppHeader{{background:var(--pivot-bg)!important}}
[data-testid="stToolbar"]{{background:transparent!important}}
.block-container{{max-width:1380px;padding:1.25rem clamp(1.2rem,3vw,2.8rem) 3.2rem}}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{{font-family:Manrope,Inter,sans-serif!important;color:var(--pivot-deep-teal)!important;letter-spacing:-.025em}}
.stApp h1{{font-size:clamp(2rem,3vw,2.55rem)!important;line-height:1.14!important}}
.stApp p,.stApp li,.stApp [data-testid="stCaptionContainer"] p{{color:var(--pivot-muted)}}
.stApp [data-testid="stMarkdownContainer"] a{{color:var(--pivot-teal)!important}}
[data-testid="stSidebar"]{{background:var(--pivot-sidebar)!important;border-right:1px solid #563940;min-width:17rem!important;max-width:17rem!important}}
[data-testid="stSidebar"] > div:first-child{{padding:1.25rem .85rem 1.6rem}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{{margin:.25rem 0 .4rem}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong{{display:block;padding:.85rem .6rem .32rem;color:#EACBD2!important;font:600 .67rem 'IBM Plex Mono',monospace;letter-spacing:.11em}}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{{color:#E3DADD!important;font-size:.72rem;letter-spacing:.055em;font-weight:600}}
.pivot-brand{{display:flex;align-items:center;gap:.7rem;margin:.1rem 0 .45rem}}
.pivot-brand-mark{{display:grid;place-items:center;width:38px;height:38px;border:1px solid #9A7780;border-radius:11px;background:#42252D;color:#FFF!important;font:700 1rem 'IBM Plex Mono',monospace}}
.pivot-brand strong{{color:#FFF!important;font:800 1.47rem Manrope,sans-serif;letter-spacing:-.05em}}
[data-testid="stSidebar"] [data-testid="stButton"]{{margin:0 0 4px}}
[data-testid="stSidebar"] [data-testid="stButton"] button{{width:100%;min-height:42px;justify-content:flex-start;text-align:left;padding:.5rem .72rem;font-size:.87rem;font-weight:550;white-space:nowrap}}
[data-testid="stSidebar"] hr{{border-color:rgba(255,255,255,.22)!important}}
[data-testid="stMetric"]{{height:100%;padding:1rem 1.15rem;background:var(--pivot-card);border:1px solid var(--pivot-border);border-radius:12px;box-shadow:0 5px 18px var(--pivot-shadow)}}
[data-testid="stMetricLabel"] p{{color:var(--pivot-muted)!important;font-size:.81rem!important;font-weight:600}}
[data-testid="stMetricValue"]{{font-family:Manrope,Inter,sans-serif!important;color:var(--pivot-deep-teal)!important;font-size:1.55rem!important;line-height:1.15;white-space:normal;overflow-wrap:anywhere;font-weight:700}}
[data-testid="stForm"]{{padding:.1rem 0 .25rem;background:transparent;border:0;border-radius:0;box-shadow:none}}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{{color:var(--pivot-text)!important;font-size:.87rem!important;font-weight:600!important;line-height:1.35}}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]>div{{background:var(--pivot-input)!important;color:var(--pivot-text)!important;border:1px solid var(--pivot-border)!important;border-radius:7px!important;min-height:44px}}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{{padding:.55rem .75rem}}
[data-baseweb="select"]>div{{padding-left:.55rem}}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{{color:var(--pivot-placeholder)!important;opacity:1}}
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stTextArea"] textarea:focus,[data-baseweb="select"]>div:focus-within{{border-color:var(--pivot-teal)!important;box-shadow:0 0 0 3px var(--pivot-focus)!important}}
[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{{min-height:32px;color:var(--pivot-text)!important}}
input[type="checkbox"],input[type="radio"]{{accent-color:var(--pivot-rose)}}
[data-baseweb="popover"] ul,[data-baseweb="popover"] [role="listbox"]{{background:var(--pivot-card)!important}}
[data-baseweb="popover"] [role="option"]{{background:var(--pivot-card)!important;color:var(--pivot-text)!important}}
[data-baseweb="popover"] [role="option"]:hover{{background:var(--pivot-hover)!important}}
[data-baseweb="select"] svg,[data-testid="stNumberInput"] button svg{{color:var(--pivot-text)!important;fill:var(--pivot-text)!important}}
[role="tooltip"]{{background:var(--pivot-deep-teal)!important;color:#FFFFFF!important;border:1px solid var(--pivot-border)!important;border-radius:7px!important}}
[data-testid="stTabs"] [data-baseweb="tab-list"]{{gap:.3rem;border-bottom:1px solid var(--pivot-border)}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{{height:3px;background:var(--pivot-rose)!important}}
[data-testid="stTabs"] [data-baseweb="tab-border"]{{background:var(--pivot-border)!important}}
.pivot-form-section{{margin:1rem 0 .35rem;padding:0 0 .45rem;border-bottom:1px solid var(--pivot-border);background:transparent;color:var(--pivot-muted);font:600 .72rem 'IBM Plex Mono',monospace;letter-spacing:.07em;text-transform:uppercase}}
.pivot-hero{{position:relative;display:flex;align-items:center;justify-content:space-between;gap:2rem;overflow:hidden;padding:1.6rem 1.9rem;margin:0 0 1.5rem;border:1px solid var(--pivot-border);border-radius:16px;background:linear-gradient(112deg,var(--pivot-card),var(--pivot-surface) 74%);box-shadow:0 8px 26px var(--pivot-shadow)}}
.pivot-hero:before{{content:'';position:absolute;left:0;top:18px;bottom:18px;width:4px;background:var(--pivot-rose)}}
.pivot-hero.compact{{min-height:130px;padding:1.35rem 1.65rem;margin-bottom:1.35rem}}
.pivot-hero:after{{content:'';position:absolute;right:12%;top:-132px;width:260px;height:260px;border:1px solid color-mix(in srgb,var(--pivot-primary) 25%,transparent);border-radius:50%;box-shadow:0 0 0 28px color-mix(in srgb,var(--pivot-primary) 5%,transparent),0 0 0 56px color-mix(in srgb,var(--pivot-rose) 6%,transparent);pointer-events:none}}
.pivot-hero-copy{{position:relative;z-index:1;max-width:850px}}
.stApp .pivot-eyebrow,.stApp .pivot-section-kicker{{color:var(--pivot-teal)!important;font:600 .72rem 'IBM Plex Mono',monospace;letter-spacing:.09em;text-transform:uppercase}}
.pivot-hero h1{{margin:.4rem 0 .55rem;font-size:clamp(2rem,3vw,2.5rem)!important}}
.pivot-hero.compact h1{{font-size:clamp(1.75rem,2.5vw,2.15rem)!important}}
.pivot-hero p{{max-width:760px;margin:0;color:var(--pivot-muted)!important;font-size:.96rem;line-height:1.6}}
.pivot-hero-art{{position:relative;z-index:1;flex:0 0 205px;height:120px;margin-right:1.5%}}
.pivot-hero.compact .pivot-hero-art{{transform:scale(.86);transform-origin:right center}}
.pivot-orbit{{position:absolute;border:1px solid color-mix(in srgb,var(--pivot-primary) 30%,transparent);border-radius:50%;transform:rotate(-24deg)}}
.pivot-orbit.one{{width:158px;height:75px;right:8px;top:27px}}.pivot-orbit.two{{width:116px;height:116px;right:28px;top:7px;border-color:color-mix(in srgb,var(--pivot-rose) 48%,transparent)}}
.pivot-orbit-dot{{position:absolute;width:11px;height:11px;right:34px;top:26px;background:var(--pivot-rose);border:3px solid var(--pivot-card);border-radius:50%}}
.pivot-signal-card{{position:absolute;left:2px;top:24px;width:135px;padding:11px 13px;border:1px solid var(--pivot-border);border-radius:10px;background:var(--pivot-card);box-shadow:0 7px 18px var(--pivot-shadow);transform:rotate(-2deg)}}
.pivot-signal-card strong{{display:block;color:var(--pivot-deep-teal);font:700 1.1rem Manrope,sans-serif}}
.pivot-signal-card small{{display:block;margin-top:3px;color:var(--pivot-muted);font:500 .65rem 'IBM Plex Mono',monospace;letter-spacing:.06em}}
.pivot-signal-bars{{display:flex;align-items:end;gap:5px;height:22px;margin-top:9px}}
.pivot-signal-bars i{{display:block;width:10px;border-radius:2px 2px 0 0;background:#A8B8BA}}
.pivot-signal-bars i:nth-child(1){{height:9px}}.pivot-signal-bars i:nth-child(2){{height:16px;background:var(--pivot-teal)}}.pivot-signal-bars i:nth-child(3){{height:12px;background:var(--pivot-rose)}}.pivot-signal-bars i:nth-child(4){{height:21px;background:var(--pivot-primary)}}
.pivot-signal-bars span{{margin-left:auto;color:var(--pivot-muted);font:500 .55rem 'IBM Plex Mono',monospace;align-self:center}}
.stApp .pivot-section-kicker{{display:flex;align-items:center;gap:.65rem;margin:.4rem 0 .35rem;letter-spacing:.1em}}
.pivot-section-kicker:after{{content:'';height:1px;flex:1;max-width:180px;background:linear-gradient(90deg,var(--pivot-border),transparent)}}
[data-testid="stVerticalBlockBorderWrapper"]{{background:var(--pivot-card)!important;border-color:var(--pivot-border)!important;border-radius:12px}}
[data-testid="stExpander"]{{background:var(--pivot-card);border:1px solid var(--pivot-border);border-radius:10px}}
[data-testid="stDataFrame"]{{border:1px solid var(--pivot-border);border-radius:9px;overflow:hidden}}
[data-testid="stFileUploader"] section{{background:var(--pivot-card);border:1px dashed #82989C;border-radius:10px}}
[data-testid="stFileUploader"] section:hover{{border-color:var(--pivot-rose)}}
[data-testid="stAlert"]{{border-radius:10px}}
[data-testid="stCaptionContainer"] p{{color:var(--pivot-muted)!important}}
[data-testid="stSidebar"] .st-key-pivot-dark-mode{{position:sticky;top:.5rem;z-index:5;margin:.65rem 0 1rem;padding:.65rem .7rem;border:1px solid rgba(255,255,255,.16);border-radius:9px;background:rgba(46,21,27,.96)}}
[data-testid="stSidebar"] .st-key-pivot-dark-mode [data-testid="stWidgetLabel"] p{{color:#F6F0F1!important;font-weight:600}}
[data-testid="stMain"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]{{background:var(--pivot-primary)!important;color:#FFFFFF!important;border:1px solid var(--pivot-primary)!important;border-radius:8px!important;min-height:42px;padding:.55rem 1.05rem;font-weight:700!important;transition:background .16s ease,border-color .16s ease,transform .16s ease}}
[data-testid="stMain"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover{{background:#48242E!important;border-color:var(--pivot-rose)!important;transform:translateY(-1px)}}
[data-testid="stMain"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"] *{{color:#FFFFFF!important}}
[data-testid="stMain"] [data-testid="stForm"] button,[data-testid="stMain"] [data-testid="stFormSubmitButton"] button{{background:var(--pivot-primary)!important;color:#FFFFFF!important;border:1px solid var(--pivot-primary)!important;border-radius:8px!important;min-height:42px;padding:.55rem 1.05rem;font-weight:700!important}}
[data-testid="stMain"] [data-testid="stForm"] button p,[data-testid="stMain"] [data-testid="stFormSubmitButton"] button p{{color:#FFFFFF!important}}
[data-testid="stMain"] [data-testid="stButton"] button[data-testid="stBaseButton-secondary"]{{background:var(--pivot-card)!important;color:var(--pivot-text)!important;border:1px solid var(--pivot-border)!important}}
[data-testid="stMain"] [data-testid="stButton"] button[data-testid="stBaseButton-secondary"] *{{color:var(--pivot-text)!important}}
[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]{{background:transparent!important;color:#F6F0F1!important;border-color:transparent!important}}
[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] *{{color:#F6F0F1!important}}
[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover{{background:rgba(255,255,255,.09)!important;border-color:rgba(255,255,255,.13)!important}}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]{{background:var(--pivot-rose)!important;color:#2E151B!important;border-color:#E796AA!important;box-shadow:inset 3px 0 #FFFFFF!important}}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] *{{color:#2E151B!important}}
html body .stApp [data-testid="stTabs"] button[role="tab"]{{min-height:46px;padding:0 1rem;color:var(--pivot-muted)!important;background-color:var(--pivot-surface)!important;font-size:.88rem;font-weight:600;border-radius:8px 8px 0 0}}
html body .stApp [data-testid="stTabs"] button[role="tab"] *{{color:inherit!important}}
html body .stApp [data-testid="stTabs"] button[role="tab"][aria-selected="true"]{{color:var(--pivot-deep-teal)!important;background-color:var(--pivot-hover)!important}}
html body .stApp [data-testid="stTabs"] button[role="tab"]:hover{{color:var(--pivot-deep-teal)!important;background-color:var(--pivot-hover)!important}}
html body .stApp [data-testid="stNumberInput"] button{{background:var(--pivot-raised)!important;color:var(--pivot-text)!important;border:1px solid #9DAEAD!important;min-width:38px}}
html body .stApp [data-testid="stNumberInput"] button:hover{{background:var(--pivot-hover)!important}}
html body .stApp [data-testid="stNumberInput"] button:disabled{{background:var(--pivot-raised)!important;color:var(--pivot-muted)!important}}
html body .stApp [data-testid="stNumberInput"] button svg{{color:var(--pivot-text)!important;fill:var(--pivot-text)!important}}
.stApp button:disabled,[data-testid="stDownloadButton"] button:disabled{{opacity:1!important;background:var(--pivot-raised)!important;border-color:var(--pivot-border)!important;color:var(--pivot-muted)!important}}
.stApp button:disabled *{{color:var(--pivot-muted)!important}}
.stApp button,.stApp [data-testid="stDownloadButton"] button{{border-radius:8px;transition:background .16s ease,border-color .16s ease}}
hr{{border-color:var(--pivot-border)!important}}
*:focus-visible{{outline:2px solid var(--pivot-rose)!important;outline-offset:2px}}
@media(max-width:850px){{.block-container{{padding:1.2rem 1rem 2rem}}.pivot-hero{{padding:1.35rem}}.pivot-hero-art{{flex-basis:170px;transform:scale(.85);transform-origin:right center}}}}
@media(max-width:600px){{[data-testid="stSidebar"]{{width:min(17rem,85vw)!important;min-width:min(17rem,85vw)!important;max-width:min(17rem,85vw)!important}}.pivot-hero{{padding:1.1rem;min-height:0}}.pivot-hero-art{{display:none}}.block-container{{padding:1rem .75rem 1.5rem}}[data-testid="stMetric"]{{padding:.75rem}}.pivot-hero h1{{font-size:1.75rem!important}}[data-testid="stTabs"] [role="tab"]{{padding:0 .5rem;font-size:.78rem}}}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{scroll-behavior:auto!important;transition:none!important;animation:none!important}}}}
</style>""", unsafe_allow_html=True)


def render_hero(eyebrow, title, description, compact=False):
    size = " compact" if compact else ""
    st.markdown(
        f'<section class="pivot-hero{size}" aria-label="{eyebrow}"><div class="pivot-hero-copy">'
        f'<div class="pivot-eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>'
        '<div class="pivot-hero-art" aria-hidden="true"><div class="pivot-orbit one"></div>'
        '<div class="pivot-orbit two"></div><div class="pivot-orbit-dot"></div>'
        '<div class="pivot-signal-card"><strong>G3</strong><small>STUDENT SIGNAL</small>'
        '<div class="pivot-signal-bars"><i></i><i></i><i></i><i></i><span>GRADE / 20</span></div>'
        '</div></div></section>',
        unsafe_allow_html=True,
    )


def section_heading(title, description=None, eyebrow=None):
    if eyebrow:
        st.markdown(f'<div class="pivot-section-kicker">{eyebrow}</div>', unsafe_allow_html=True)
    st.subheader(title)
    if description:
        st.caption(description)


def chart_theme(fig, height=360):
    """Apply the active brand palette and readable chart typography."""
    dark = st.session_state.get("pivot_theme", "light") == "dark"
    bg = "#1C3334" if dark else "#FFFFFF"
    text = "#F8F6F1" if dark else "#1C3334"
    muted = "#C4D0D2" if dark else "#53666B"
    grid = "#385258" if dark else "#E0E5E4"
    border = "#526A70" if dark else "#C6D1D2"
    fig.update_layout(
        template="plotly_dark" if dark else "plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=bg,
        font={"family": "Inter, sans-serif", "size": 13, "color": text},
        title_text=fig.layout.title.text or "",
        title_font={"family": "Manrope, sans-serif", "size": 18, "color": text},
        margin={"l": 28, "r": 24, "t": 58, "b": 34},
        hoverlabel={"bgcolor": bg, "bordercolor": border, "font": {"color": text, "family": "Inter, sans-serif", "size": 13}},
        legend={"bgcolor": "rgba(0,0,0,0)", "font": {"color": muted, "size": 12}},
    )
    fig.update_xaxes(gridcolor=grid, zerolinecolor=border, linecolor=border, tickfont={"color": muted, "size": 12}, title_font={"color": text})
    fig.update_yaxes(gridcolor=grid, zerolinecolor=border, linecolor=border, tickfont={"color": muted, "size": 12}, title_font={"color": text})
    return fig


def render_table(data, **kwargs):
    """Render a styled dataframe with contrast matching the active app theme."""
    dark = st.session_state.get("pivot_theme", "light") == "dark"
    surface = "#1C3334" if dark else "#FFFFFF"
    text = "#F8F6F1" if dark else "#1C3334"
    alternate = "#233C3D" if dark else "#F5F7F6"
    border = "#385258" if dark else "#D8DFDF"
    styler = data.style.set_properties(**{
        "background-color": surface,
        "color": text,
        "border-color": border,
        "font-size": "13px",
    }).set_table_styles([
        {"selector": "th", "props": [("background-color", alternate), ("color", text), ("font-weight", "600"), ("border-bottom", f"1px solid {border}")]},
        {"selector": "td", "props": [("color", text), ("border-bottom", f"1px solid {border}")]},
        {"selector": "tr:hover td", "props": [("background-color", alternate)]},
    ], overwrite=False)
    st.dataframe(styler, **kwargs)


def empty_state(title, description, icon="—"):
    st.markdown(
        f'<div style="padding:20px;border:1px solid var(--pivot-border);border-radius:9px;background:var(--pivot-card)">'
        f'<div style="font:650 1rem Manrope,sans-serif;color:var(--pivot-text)">{icon}&nbsp; {title}</div>'
        f'<div style="margin-top:6px;color:var(--pivot-muted);font-size:.92rem;line-height:1.5">{description}</div></div>',
        unsafe_allow_html=True,
    )
