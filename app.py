import streamlit as st
from groq import Groq
import pandas as pd
import re

# إعداد الصفحة باش تبان احترافية
st.set_page_config(
    page_title="Pro Domainer AI", 
    page_icon="💰", 
    layout="wide"
)

# جلب الـ API Key من secrets (الموجود في Streamlit Cloud أو ملف .streamlit/secrets.toml)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("⚠️ خاصك تزيد GROQ_API_KEY فـ Secrets!")
    st.stop()

# تصميم الواجهة
st.title("🚀 Pro Domainer AI Generator")
st.markdown("---")

# القائمة الجانبية للإعدادات
with st.sidebar:
    st.header("⚙️ إعدادات البحث")
    niche = st.text_input("النيش المستهدف", value="Pet Tech", help="مثلاً: AI, Crypto, Pets...")
    num_ideas = st.slider("عدد الأفكار", 5, 20, 10)
    st.info("💡 نصيحة: استعمل الكوبون NEWCOM679 فـ Namecheap باش توفر الصولد!")

# الزر الرئيسي
if st.button("ابحث عن الهميزات! 🔥"):
    with st.spinner('الحاج Groq جالس كيقبض فـ الدومينات...'):
        
        # البرومبت اللي كيخلي الذكاء الاصطناعي يفكر بحال "سماسرية" الدومينات
        prompt = f"""
        Act as a professional domain investor (Domainer). 
        Target Niche: {niche}
        Task: Generate {num_ideas} high-value .com domain names.
        
        Rules:
        1. Only .com extensions. No hyphens or numbers.
        2. High commercial intent.
        3. For each domain, provide a predicted 'Resell Value' based on current market trends.
        
        Format the output EXACTLY like this (one per line):
        DOMAIN|VALUE|DESCRIPTION
        example.com|$1,500|Short and brandable
        """

        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            
            raw_output = completion.choices[0].message.content.strip().split('\n')
            
            # معالجة البيانات وعرضها في جدول
            data = []
            for line in raw_output:
                if '|' in line and not line.startswith('DOMAIN'):
                    parts = line.split('|')
                    if len(parts) == 3:
                        domain_name = parts[0].strip().lower()
                        # تنظيف الدومين من أي زيادات
                        domain_name = re.sub(r'^[0-9\.\-\s]+', '', domain_name)
                        
                        data.append({
                            "Domain Name": domain_name,
                            "Est. Value": parts[1].strip(),
                            "Reason": parts[2].strip(),
                            "Check": f"https://www.namecheap.com/domains/registration/results/?domain={domain_name}"
                        })

            if data:
                df = pd.DataFrame(data)
                
                # عرض الجدول بشكل أنيق
                st.subheader(f"✅ مقترحات لـ نيش {niche}")
                
                # تحويل الجدول لـ HTML باش نزيدو روابط قابلة للضغط
                def make_clickable(link):
                    return f'<a target="_blank" href="{link}">شيك فـ Namecheap</a>'
                
                df['Check'] = df['Check'].apply(make_clickable)
                
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                st.success(f"لقينا ليك {len(df)} دومين فيهم إمكانيات كبيرة!")
            else:
                st.warning("الـ API عطانا فورماط غريبة، عاود كليكي على الزر.")

        except Exception as e:
            st.error(f"وقع مشكل تقني: {e}")

st.markdown("---")
st.caption("مطور بواسطة Mouhcine Digital Systems 🛠️ - استثمر بذكاء.")
