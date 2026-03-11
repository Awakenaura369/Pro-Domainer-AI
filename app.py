import streamlit as st
from groq import Groq
import pandas as pd
import re
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ============================================================
# 1. إعداد الصفحة
# ============================================================
st.set_page_config(
    page_title="Pro Domainer AI 🚀",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS احترافي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0d1b2a 100%);
        padding: 2rem;
        border-radius: 14px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid #00d4ff;
        box-shadow: 0 0 30px rgba(0,212,255,0.15);
    }
    .main-header h1 { color: #00d4ff; font-size: 2.4rem; margin: 0; letter-spacing: -1px; }
    .main-header p  { color: #8892a4; margin: 0.5rem 0 0; font-size: 1rem; }

    .stat-card {
        background: #0d1117;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        transition: border-color 0.3s;
    }
    .stat-card:hover { border-color: #00d4ff; }
    .stat-card .number { font-size: 2rem; font-weight: 700; color: #00d4ff; }
    .stat-card .label  { color: #8892a4; font-size: 0.82rem; margin-top: 0.2rem; }

    .domain-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    .domain-table th {
        background: #0d1117;
        color: #00d4ff;
        padding: 0.8rem 1rem;
        text-align: left;
        border-bottom: 2px solid #21262d;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .domain-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #21262d;
        color: #c9d1d9;
        font-size: 0.9rem;
    }
    .domain-table tr:hover td { background: #161b22; }

    .score-high   { color: #3fb950; font-weight: 700; }
    .score-medium { color: #d29922; font-weight: 700; }
    .score-low    { color: #f85149; font-weight: 700; }

    .ext-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .ext-com  { background: #1f6feb33; color: #58a6ff; border: 1px solid #1f6feb; }
    .ext-io   { background: #3fb95033; color: #3fb950; border: 1px solid #3fb950; }
    .ext-ai   { background: #d2992233; color: #d29922; border: 1px solid #d29922; }
    .ext-net  { background: #8957e533; color: #bc8cff; border: 1px solid #8957e5; }

    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #0077b6) !important;
        color: #0a0a0a !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(0,212,255,0.4) !important;
    }

    .success-banner {
        background: linear-gradient(135deg, #0d4429, #196d35);
        border: 1px solid #3fb950;
        color: #3fb950;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .section-title {
        color: #c9d1d9;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #21262d;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. API Client
# ============================================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ خطأ: تأكد من إضافة GROQ_API_KEY في Streamlit Secrets!")
    st.stop()

# ============================================================
# 3. Header
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🌐 Pro Domainer AI</h1>
    <p>اكتشف دومينات بقيمة عالية بذكاء اصطناعي — Powered by Groq & Llama 3</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 4. Session State
# ============================================================
if "all_results" not in st.session_state:
    st.session_state.all_results = []
if "search_count" not in st.session_state:
    st.session_state.search_count = 0

# ============================================================
# 5. Sidebar
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ إعدادات البحث")

    st.markdown("### 🎯 النيش")
    niche = st.text_input("النيش المستهدف:", "Pet Care")
    niche_examples = st.expander("💡 أمثلة على النيشات")
    with niche_examples:
        examples = ["AI Tools", "Health Tech", "E-commerce", "Real Estate",
                    "Crypto", "EdTech", "Fitness", "Travel", "Food Delivery", "Legal Tech"]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                niche = ex

    st.markdown("---")
    st.markdown("### 🔧 إعدادات الدومين")
    num_ideas = st.slider("عدد الأفكار:", 5, 25, 10)

    extensions = st.multiselect(
        "الامتدادات المطلوبة:",
        [".com", ".io", ".ai", ".net", ".co", ".app"],
        default=[".com"],
        help="اختر واحد أو أكثر"
    )

    domain_style = st.selectbox(
        "أسلوب الدومين:",
        ["Mixed (brandable + keywords)", "Brandable only", "Keyword-rich only", "Short (under 8 chars)"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🤖 النموذج")
    model_choice = st.selectbox(
        "النموذج:",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        index=0
    )

    st.markdown("---")
    if st.button("🗑️ مسح كل النتائج", use_container_width=True):
        st.session_state.all_results = []
        st.session_state.search_count = 0
        st.rerun()

# ============================================================
# 6. دالة توليد PDF احترافي
# ============================================================
def generate_pdf_report(domains, niche):
    buffer = io.BytesIO()

    # ألوان
    DARK      = colors.HexColor("#0d1117")
    CYAN      = colors.HexColor("#00d4ff")
    GREEN     = colors.HexColor("#3fb950")
    YELLOW    = colors.HexColor("#d29922")
    RED       = colors.HexColor("#f85149")
    LIGHT     = colors.HexColor("#c9d1d9")
    GRAY      = colors.HexColor("#8892a4")
    DARKGRAY  = colors.HexColor("#21262d")
    WHITE     = colors.white

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # --- عنوان الرابورت ---
    title_style = ParagraphStyle(
        "title", fontSize=26, fontName="Helvetica-Bold",
        textColor=CYAN, alignment=TA_CENTER, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "sub", fontSize=11, fontName="Helvetica",
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=2
    )
    story.append(Paragraph("Pro Domainer AI", title_style))
    story.append(Paragraph(f"Domain Research Report — Niche: {niche}", sub_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        sub_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN))
    story.append(Spacer(1, 0.4*cm))

    # --- ملخص إحصائي ---
    total      = len(domains)
    high_v     = sum(1 for d in domains if d.get("score_num", 0) >= 8)
    med_v      = sum(1 for d in domains if 5 <= d.get("score_num", 0) < 8)
    low_v      = sum(1 for d in domains if d.get("score_num", 0) < 5)
    avg_sc     = sum(d.get("score_num", 0) for d in domains) / total if total else 0

    section_style = ParagraphStyle(
        "section", fontSize=13, fontName="Helvetica-Bold",
        textColor=CYAN, spaceBefore=8, spaceAfter=6
    )
    story.append(Paragraph("Executive Summary", section_style))

    summary_data = [
        ["Metric", "Value"],
        ["Total Domains Analyzed", str(total)],
        ["High Value (Score 8-10)", f"{high_v} domains"],
        ["Medium Value (Score 5-7)", f"{med_v} domains"],
        ["Low Value (Score 1-4)", f"{low_v} domains"],
        ["Average Investment Score", f"{avg_sc:.1f} / 10"],
        ["Target Niche", niche],
        ["Report Date", datetime.now().strftime("%Y-%m-%d")],
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  CYAN),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  DARK),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  10),
        ("BACKGROUND",   (0, 1), (-1, -1), DARK),
        ("TEXTCOLOR",    (0, 1), (0, -1),  LIGHT),
        ("TEXTCOLOR",    (1, 1), (1, -1),  GREEN),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [DARK, colors.HexColor("#161b22")]),
        ("GRID",         (0, 0), (-1, -1), 0.5, DARKGRAY),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [4, 4, 4, 4]),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=DARKGRAY))
    story.append(Spacer(1, 0.3*cm))

    # --- جدول الدومينات ---
    story.append(Paragraph("Domain Investment Opportunities", section_style))

    cell_style = ParagraphStyle(
        "cell", fontSize=8, fontName="Helvetica", textColor=LIGHT
    )
    domain_style_p = ParagraphStyle(
        "domain_p", fontSize=9, fontName="Helvetica-Bold", textColor=CYAN
    )
    reason_style = ParagraphStyle(
        "reason_p", fontSize=7.5, fontName="Helvetica", textColor=GRAY
    )

    headers = ["#", "Domain", "Score", "Value", "Search Vol", "CPC", "Comp.", "Category"]
    table_data = [headers]

    for i, d in enumerate(domains, 1):
        sc = d.get("score_num", 0)
        score_hex = "#3fb950" if sc >= 8 else ("#d29922" if sc >= 5 else "#f85149")
        comp      = d.get("competition", "N/A")
        comp_hex  = "#3fb950" if comp == "Low" else ("#d29922" if comp == "Medium" else "#f85149")

        table_data.append([
            Paragraph(str(i), cell_style),
            Paragraph(d["domain"], domain_style_p),
            Paragraph(f'<font color="{score_hex}"><b>{d["score_raw"]}/10</b></font>', cell_style),
            Paragraph(d["est_value"], ParagraphStyle("val", fontSize=8, fontName="Helvetica-Bold", textColor=GREEN)),
            Paragraph(d.get("search_vol", "N/A"), ParagraphStyle("sv",  fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#58a6ff"))),
            Paragraph(d.get("cpc", "N/A"),        ParagraphStyle("cpc", fontSize=8, fontName="Helvetica", textColor=YELLOW)),
            Paragraph(f'<font color="{comp_hex}">{comp}</font>', cell_style),
            Paragraph(d["category"], cell_style),
        ])

    col_widths = [0.7*cm, 4.2*cm, 1.6*cm, 2.2*cm, 2.0*cm, 1.8*cm, 1.8*cm, 2.0*cm]
    domain_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    domain_table.setStyle(TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  CYAN),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  DARK),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        # Rows
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [DARK, colors.HexColor("#161b22")]),
        ("GRID",          (0, 0), (-1, -1), 0.3, DARKGRAY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(domain_table)
    story.append(Spacer(1, 0.5*cm))

    # --- Top 3 picks ---
    top3 = sorted(domains, key=lambda x: x.get("score_num", 0), reverse=True)[:3]
    if top3:
        story.append(HRFlowable(width="100%", thickness=0.5, color=DARKGRAY))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Top 3 Investment Picks", section_style))

        for rank, d in enumerate(top3, 1):
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            pick_data = [
                [f"{medals[rank]} #{rank} — {d['domain']}", f"Score: {d['score_raw']}/10", f"Value: {d['est_value']}"],
                [d["reason"], "", ""],
                [f"Namecheap: namecheap.com/domains/registration/results/?domain={d['domain']}", "", ""],
            ]
            pick_table = Table(pick_data, colWidths=[10*cm, 3*cm, 4*cm])
            sc = d.get("score_num", 0)
            border_color = GREEN if sc >= 8 else YELLOW
            pick_table.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), DARK),
                ("TEXTCOLOR",    (0, 0), (0, 0),   CYAN),
                ("FONTNAME",     (0, 0), (0, 0),   "Helvetica-Bold"),
                ("FONTSIZE",     (0, 0), (0, 0),   10),
                ("TEXTCOLOR",    (1, 0), (1, 0),   YELLOW),
                ("TEXTCOLOR",    (2, 0), (2, 0),   GREEN),
                ("FONTNAME",     (1, 0), (2, 0),   "Helvetica-Bold"),
                ("FONTSIZE",     (1, 0), (-1, -1), 8),
                ("TEXTCOLOR",    (0, 1), (-1, -1), GRAY),
                ("FONTSIZE",     (0, 1), (-1, -1), 7.5),
                ("SPAN",         (0, 1), (-1, 1)),
                ("SPAN",         (0, 2), (-1, 2)),
                ("BOX",          (0, 0), (-1, -1), 1, border_color),
                ("LEFTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",   (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ]))
            story.append(pick_table)
            story.append(Spacer(1, 0.3*cm))

    # --- Footer ---
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=DARKGRAY))
    footer_style = ParagraphStyle(
        "footer", fontSize=7.5, fontName="Helvetica",
        textColor=GRAY, alignment=TA_CENTER, spaceBefore=6
    )
    story.append(Paragraph(
        "Generated by Pro Domainer AI v3.0 | Mouhcine Digital Systems | Powered by Groq & Llama 3",
        footer_style
    ))
    story.append(Paragraph(
        "Disclaimer: Domain valuations are AI estimates for research purposes only.",
        footer_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ============================================================
# 6. دالة Score
# ============================================================
def comp_badge(level):
    colors_map = {
        "Low":    ("color:#3fb950", "🟢"),
        "Medium": ("color:#d29922", "🟡"),
        "High":   ("color:#f85149", "🔴"),
    }
    style, emoji = colors_map.get(level, ("color:#8892a4", "⚪"))
    return f'<span style="{style};font-weight:600;font-size:0.82rem">{emoji} {level}</span>'

def get_score_html(score_str):
    try:
        score = int(re.sub(r"[^\d]", "", score_str))
        if score >= 8:
            return f'<span class="score-high">⭐ {score}/10</span>'
        elif score >= 5:
            return f'<span class="score-medium">🔶 {score}/10</span>'
        else:
            return f'<span class="score-low">🔻 {score}/10</span>'
    except Exception:
        return f'<span class="score-medium">{score_str}</span>'

def get_ext_badge(domain):
    for ext in [".com", ".io", ".ai", ".net", ".co", ".app"]:
        if domain.endswith(ext):
            cls = f"ext-{ext[1:]}" if ext[1:] in ["com","io","ai","net"] else "ext-com"
            return f'<span class="ext-badge {cls}">{ext}</span>'
    return ""

# ============================================================
# 7. دالة بناء الـ Prompt
# ============================================================
def build_prompt(niche, num, extensions, style):
    ext_str = ", ".join(extensions) if extensions else ".com"
    style_map = {
        "Mixed (brandable + keywords)": "Mix brandable creative names with keyword-rich names",
        "Brandable only": "Focus on creative, brandable, memorable names (not keyword-based)",
        "Keyword-rich only": "Focus on keyword-rich descriptive domain names for SEO value",
        "Short (under 8 chars)": "All domains must be under 8 characters — short and punchy",
    }
    style_instruction = style_map.get(style, "")

    return f"""Act as a professional domain investor (Domainer), SEO expert, and branding consultant.

Target Niche: {niche}
Required Extensions: {ext_str}
Style: {style_instruction}
Number of domains: {num}

For each domain generate exactly this pipe-separated format:
DOMAIN|SCORE|EST_VALUE|CATEGORY|SEARCH_VOL|CPC|COMPETITION|REASON

Field definitions:
- DOMAIN: the full domain name (e.g. petcare.com)
- SCORE: investment potential 1-10
- EST_VALUE: realistic resale value in USD (e.g. $500, $2,000, $15,000)
- CATEGORY: one of [Brandable, Keyword, Short, Geo, Tech]
- SEARCH_VOL: estimated monthly searches for main keyword (e.g. 12K, 45K, 200K)
- CPC: estimated cost-per-click in USD (e.g. $1.20, $4.50, $12.00)
- COMPETITION: SEO competition level — Low / Medium / High
- REASON: 1 short sentence why it's a good investment

Rules:
- No hyphens, no numbers in domain name
- Only return the pipe-separated lines, no headers, no extra text
- Generate exactly {num} lines

Example:
petcare.com|9|$15,000|Keyword|45K|$3.20|High|Exact-match keyword with massive search demand in booming pet industry
"""

# ============================================================
# 8. إحصائيات
# ============================================================
col1, col2, col3, col4 = st.columns(4)
total_domains = len(st.session_state.all_results)
high_value = sum(1 for d in st.session_state.all_results if d.get("score_num", 0) >= 8)
avg_score = (sum(d.get("score_num", 0) for d in st.session_state.all_results) / total_domains) if total_domains else 0

with col1:
    st.markdown(f'<div class="stat-card"><div class="number">{total_domains}</div><div class="label">دومين مقترح</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="number">{high_value}</div><div class="label">قيمة عالية ⭐</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="number">{avg_score:.1f}</div><div class="label">متوسط الـ Score</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="number">{st.session_state.search_count}</div><div class="label">عمليات بحث</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 9. زر البحث
# ============================================================
btn_col1, btn_col2 = st.columns([2, 4])
with btn_col1:
    search_btn = st.button("🔍 ابحث عن الدومينات! 🔥", use_container_width=True)

if search_btn:
    if not niche.strip():
        st.warning("⚠️ دخل النيش من فضلك!")
        st.stop()
    if not extensions:
        st.warning("⚠️ اختر امتداد واحد على الأقل!")
        st.stop()

    with st.spinner(f"🤖 جاري تحليل نيش '{niche}' بذكاء Llama 3..."):
        try:
            prompt = build_prompt(niche, num_ideas, extensions, domain_style)
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional domain investor. Always respond with ONLY pipe-separated data, no extra text."},
                    {"role": "user", "content": prompt}
                ],
                model=model_choice,
                temperature=0.7,
                max_tokens=2000,
            )

            raw_output = completion.choices[0].message.content.strip().split('\n')
            new_data = []

            for line in raw_output:
                line = line.strip()
                if '|' not in line:
                    continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) < 4:
                    continue

                domain_name = re.sub(r'^[0-9\.\-\*\s]+', '', parts[0].lower()).strip()
                if not domain_name:
                    continue

                # استخرج رقم الـ score
                score_raw = parts[1] if len(parts) > 1 else "5"
                score_num = 0
                try:
                    score_num = int(re.sub(r"[^\d]", "", score_raw))
                except Exception:
                    pass

                est_value   = parts[2] if len(parts) > 2 else "N/A"
                category    = parts[3] if len(parts) > 3 else "General"
                search_vol  = parts[4] if len(parts) > 4 else "N/A"
                cpc         = parts[5] if len(parts) > 5 else "N/A"
                competition = parts[6] if len(parts) > 6 else "N/A"
                reason      = parts[7] if len(parts) > 7 else (parts[4] if len(parts) > 4 else "")

                new_data.append({
                    "domain":      domain_name,
                    "score_raw":   score_raw,
                    "score_num":   score_num,
                    "est_value":   est_value,
                    "category":    category,
                    "search_vol":  search_vol,
                    "cpc":         cpc,
                    "competition": competition,
                    "reason":      reason,
                    "niche":       niche,
                    "timestamp":   datetime.now().strftime("%H:%M"),
                })

            if new_data:
                # ترتيب حسب الـ score
                new_data.sort(key=lambda x: x["score_num"], reverse=True)
                st.session_state.all_results = new_data + st.session_state.all_results
                st.session_state.search_count += 1
                st.markdown(f'<div class="success-banner">✅ تم! وجدنا <b>{len(new_data)}</b> دومين لنيش <b>{niche}</b></div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ ما لقيناش نتائج، حاول مرة أخرى.")

        except Exception as e:
            st.error(f"❌ خطأ: {str(e)}")

# ============================================================
# 10. عرض النتائج
# ============================================================
if st.session_state.all_results:
    st.markdown('<div class="section-title">📊 الدومينات المقترحة</div>', unsafe_allow_html=True)

    # --- فلتر ---
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        min_score = st.slider("الـ Score الأدنى:", 1, 10, 1)
    with filter_col2:
        filter_cat = st.multiselect("الفئة:", ["Brandable", "Keyword", "Short", "Geo", "Tech", "General"], default=[])
    with filter_col3:
        filter_ext = st.multiselect("الامتداد:", [".com", ".io", ".ai", ".net", ".co", ".app"], default=[])

    # تطبيق الفلتر
    filtered = st.session_state.all_results
    filtered = [d for d in filtered if d["score_num"] >= min_score]
    if filter_cat:
        filtered = [d for d in filtered if d["category"] in filter_cat]
    if filter_ext:
        filtered = [d for d in filtered if any(d["domain"].endswith(ext) for ext in filter_ext)]

    st.markdown(f"**{len(filtered)}** دومين بعد الفلتر")

    # --- جدول HTML ---
    rows_html = ""
    for d in filtered:
        ext_badge   = get_ext_badge(d["domain"])
        score_html  = get_score_html(d["score_raw"])
        nc_link  = f"https://www.namecheap.com/domains/registration/results/?domain={d['domain']}"
        gd_link  = f"https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={d['domain']}"
        an_link  = f"https://www.afternic.com/search?keywords={d['domain']}"

        rows_html += f"""
        <tr>
            <td><b style="color:#c9d1d9">{d['domain']}</b> {ext_badge}</td>
            <td>{score_html}</td>
            <td style="color:#3fb950;font-weight:600">{d['est_value']}</td>
            <td><span style="color:#8892a4;font-size:0.82rem">{d['category']}</span></td>
            <td style="color:#58a6ff;font-weight:600">{d.get('search_vol','N/A')}</td>
            <td style="color:#d29922;font-weight:600">{d.get('cpc','N/A')}</td>
            <td>{comp_badge(d.get('competition','N/A'))}</td>
            <td style="color:#8892a4;font-size:0.82rem">{d['reason'][:55]}...</td>
            <td>
                <a href="{nc_link}" target="_blank" style="color:#58a6ff;text-decoration:none;margin-right:6px">NC</a>
                <a href="{gd_link}" target="_blank" style="color:#3fb950;text-decoration:none;margin-right:6px">GD</a>
                <a href="{an_link}" target="_blank" style="color:#d29922;text-decoration:none">AN</a>
            </td>
        </tr>"""

    table_html = f"""
    <table class="domain-table">
        <thead>
            <tr>
                <th>🌐 الدومين</th>
                <th>📊 Score</th>
                <th>💰 القيمة</th>
                <th>📁 الفئة</th>
                <th>🔍 Search Vol</th>
                <th>💲 CPC</th>
                <th>⚔️ Competition</th>
                <th>💬 السبب</th>
                <th>🔗 شيك</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>"""

    st.markdown(table_html, unsafe_allow_html=True)

    # --- Chart ديال Top Domains ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Top Domains — Investment Score Chart</div>', unsafe_allow_html=True)
    top_chart = sorted(filtered, key=lambda x: x.get("score_num", 0), reverse=True)[:10]
    if top_chart:
        chart_df = pd.DataFrame({
            "Domain":  [d["domain"] for d in top_chart],
            "Score":   [d.get("score_num", 0) for d in top_chart],
        }).set_index("Domain")
        st.bar_chart(chart_df, color="#00d4ff", height=300)

    # --- تحميل Excel + PDF ---
    st.markdown("<br>", unsafe_allow_html=True)
    dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 2])

    # بناء بيانات التصدير
    export_data = []
    for d in filtered:
        export_data.append({
            "Domain":      d["domain"],
            "Score":       d["score_raw"],
            "Est. Value":  d["est_value"],
            "Category":    d["category"],
            "Search Vol":  d.get("search_vol", "N/A"),
            "CPC":         d.get("cpc", "N/A"),
            "Competition": d.get("competition", "N/A"),
            "Reason":      d["reason"],
            "Niche":       d["niche"],
            "Namecheap":   f"https://www.namecheap.com/domains/registration/results/?domain={d['domain']}",
            "GoDaddy":     f"https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={d['domain']}",
            "Afternic":    f"https://www.afternic.com/search?keywords={d['domain']}",
        })
    df_export = pd.DataFrame(export_data)

    # --- Excel ---
    with dl_col1:
        output_xl = io.BytesIO()
        with pd.ExcelWriter(output_xl, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Domains')
            workbook  = writer.book
            worksheet = writer.sheets['Domains']
            header_fmt = workbook.add_format({
                'bold': True, 'bg_color': '#0d1117',
                'font_color': '#00d4ff', 'border': 1
            })
            green_fmt = workbook.add_format({'font_color': '#3fb950', 'bold': True})
            for col_num, col_name in enumerate(df_export.columns):
                worksheet.write(0, col_num, col_name, header_fmt)
                worksheet.set_column(col_num, col_num, 22)

        st.download_button(
            label="📥 Excel",
            data=output_xl.getvalue(),
            file_name=f"domains_{niche.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # --- PDF ---
    with dl_col2:
        pdf_buffer = generate_pdf_report(filtered, niche)
        st.download_button(
            label="📄 PDF Report",
            data=pdf_buffer,
            file_name=f"domain_report_{niche.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ============================================================
# 11. Footer
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#4a5568;font-size:0.82rem;padding:1rem">
    🌐 <b>Pro Domainer AI v3.1</b> — Developed by Mouhcine Digital Systems<br>
    Powered by <b>Groq</b> & <b>Llama 3</b> | Links: NC=Namecheap · GD=GoDaddy · AN=Afternic
</div>
""", unsafe_allow_html=True)
