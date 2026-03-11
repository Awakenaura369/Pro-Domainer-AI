import streamlit as st
from groq import Groq
import pandas as pd
import re
import io
from datetime import datetime

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
# 6. دالة Score
# ============================================================
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

    return f"""Act as a professional domain investor (Domainer) and branding expert.

Target Niche: {niche}
Required Extensions: {ext_str}
Style: {style_instruction}
Number of domains: {num}

For each domain generate:
DOMAIN|SCORE(1-10)|EST_VALUE|CATEGORY|REASON

Rules:
- No hyphens, no numbers
- SCORE: investment potential 1-10
- EST_VALUE: realistic resale value in USD (e.g. $500, $2,000, $15,000)
- CATEGORY: one of [Brandable, Keyword, Short, Geo, Tech]
- REASON: 1 short sentence why it's valuable
- Only return the pipe-separated data, no headers, no extra text
- Generate exactly {num} domains

Example format:
petsmart.com|9|$12,000|Keyword|Strong exact-match keyword with huge search volume
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

                est_value  = parts[2] if len(parts) > 2 else "N/A"
                category   = parts[3] if len(parts) > 3 else "General"
                reason     = parts[4] if len(parts) > 4 else ""

                new_data.append({
                    "domain":     domain_name,
                    "score_raw":  score_raw,
                    "score_num":  score_num,
                    "est_value":  est_value,
                    "category":   category,
                    "reason":     reason,
                    "niche":      niche,
                    "timestamp":  datetime.now().strftime("%H:%M"),
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
            <td style="color:#8892a4;font-size:0.82rem">{d['reason'][:60]}...</td>
            <td>
                <a href="{nc_link}" target="_blank" style="color:#58a6ff;text-decoration:none;margin-right:8px">NC</a>
                <a href="{gd_link}" target="_blank" style="color:#3fb950;text-decoration:none;margin-right:8px">GD</a>
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
                <th>💬 السبب</th>
                <th>🔗 شيك</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>"""

    st.markdown(table_html, unsafe_allow_html=True)

    # --- تحميل Excel ---
    st.markdown("<br>", unsafe_allow_html=True)
    dl_col1, dl_col2 = st.columns([1, 3])
    with dl_col1:
        export_data = []
        for d in filtered:
            export_data.append({
                "Domain":     d["domain"],
                "Score":      d["score_raw"],
                "Est. Value": d["est_value"],
                "Category":   d["category"],
                "Reason":     d["reason"],
                "Niche":      d["niche"],
                "Namecheap":  f"https://www.namecheap.com/domains/registration/results/?domain={d['domain']}",
                "GoDaddy":    f"https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={d['domain']}",
                "Afternic":   f"https://www.afternic.com/search?keywords={d['domain']}",
            })
        df_export = pd.DataFrame(export_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Domains')
            workbook  = writer.book
            worksheet = writer.sheets['Domains']
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#0d1117', 'font_color': '#00d4ff', 'border': 1})
            for col_num, col_name in enumerate(df_export.columns):
                worksheet.write(0, col_num, col_name, header_fmt)
                worksheet.set_column(col_num, col_num, 20)

        st.download_button(
            label="📥 تحميل Excel",
            data=output.getvalue(),
            file_name=f"domains_{niche.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ============================================================
# 11. Footer
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#4a5568;font-size:0.82rem;padding:1rem">
    🌐 <b>Pro Domainer AI v3.0</b> — Developed by Mouhcine Digital Systems<br>
    Powered by <b>Groq</b> & <b>Llama 3</b> | Links: NC=Namecheap · GD=GoDaddy · AN=Afternic
</div>
""", unsafe_allow_html=True)
