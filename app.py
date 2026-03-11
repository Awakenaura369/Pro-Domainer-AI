import streamlit as st
from groq import Groq
import pandas as pd
import re

# إعداد الصفحة
st.set_page_config(
    page_title="Pro Domainer AI v2.0", 
    page_icon="🚀", 
    layout="wide"
)

# محاولة جلب الـ API Key من Secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("⚠️ خطأ: مالقيتش GROQ_API_KEY فـ Streamlit Secrets. تأكد بلي زدتيها!")
    st.stop()

# تصميم الواجهة
st.title("🚀 Pro Domainer AI Generator")
st.markdown("---")

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ إعدادات البحث")
    niche = st.text_input("النيش (مثلاً: Pets, AI, SaaS)", value="Pet Care")
    num_ideas = st.slider("عدد الأفكار", 5, 20, 10)
    st.divider()
    st.info("💡 نصيحة: موديل Llama 3.1 دابا أسرع وأذكى فـ اختيار الدومينات.")

# الزر الرئيسي
if st.button("قلب على الهميزات! 🔥"):
    with st.spinner('الحاج Groq كيشوف ليك أحسن الدومينات المتاحة...'):
        
        # البرومبت المطور
        prompt = f"""
        Act as a professional domain investor (Domainer) with 20 years experience.
        Target Niche: {niche}
        Task: Generate {num_ideas} high-value .com domain names.
        
        Rules:
        1. Only .com extensions. No hyphens or numbers.
        2. High commercial value and easy to brand.
        3. Provide an estimated resale value and a short professional reason.
        
        Format the output EXACTLY like this (no introduction):
        DOMAIN|VALUE|DESCRIPTION
        example.com|$1,500|Short and brandable
        """

        try:
            # استعمال الموديل الجديد llama-3.1-8b-instant
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )
            
            raw_output = completion.choices[0].message.content.strip().split('\n')
            
            data = []
            for line in raw_output:
                if '|' in line and not line.startswith('DOMAIN'):
                    parts = line.split('|')
                    if len(parts) == 3:
                        domain_name = parts[0].strip().lower()
                        # تنظيف الدومين من الأرقام الزايدة اللي كيزيدها الذكاء الاصطناعي بعض المرات
                        domain_name = re.sub(r'^[0-9\.\-\s]+', '', domain_name)
                        
                        data.append({
                            "Domain Name": domain_name,
                            "Est. Value": parts[1].strip(),
                            "Reason": parts[2].strip(),
                            "Check": f"https://www.namecheap.com/domains/registration/results/?domain={domain_name}"
                        })

            if data:
                df = pd.DataFrame(data)
                
                # عرض النتائج فـ جدول أنيق
                st.subheader(f"✅ مقترحات نيش {niche}")
                
                # كود لتحويل الروابط لـ أزرار قابلة للضغط
                def make_clickable(link):
                    return f'<a target="_blank" href="{link}" style="color: #ff4b4b; text-decoration: none; font-weight: bold;">Check Availability 🔍</a>'
                
                df['Check'] = df['Check'].apply(make_clickable)
                
                # عرض الجدول كـ HTML
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                st.success("تم توليد النتائج بنجاح!")
            else:
                st.warning("الـ API رجع استجابة خاوية، حاول مرة أخرى.")

        except Exception as e:
            st.error(f"وقع مشكل تقني: {str(e)}")

st.markdown("---")
st.caption("Developed by Mouhcine Digital Systems 🛠️ | Powered by Groq Llama 3.1")
