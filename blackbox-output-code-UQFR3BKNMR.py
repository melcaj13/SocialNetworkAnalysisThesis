import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import textblob
from textblob import TextBlob
import io

# Streamlit sayfa konfigürasyonu
st.set_page_config(
    page_title="Hibrit Dijital İtibar Risk Modeli",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri - Modern kurumsal tasarım
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .kpi-card {
        background: linear-gradient(145deg, #f0f2f6, #e2e8f0);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 5px solid #3b82f6;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #64748b;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    .warning-card {
        background: linear-gradient(145deg, #fef3c7, #fde68a);
        border-left-color: #f59e0b !important;
    }
    .danger-card {
        background: linear-gradient(145deg, #fee2e2, #fecaca);
        border-left-color: #ef4444 !important;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_sample_data():
    """Tez için örnek Philadelphia Yelp Restoran verisi"""
    np.random.seed(42)
    n_users = 100
    
    user_ids = [f"USER_{i:04d}" for i in range(n_users)]
    
    # Rastgele yorum metinleri (Türkçe)
    comments = [
        "Servis çok yavaş, garsonlar ilgisiz", "Yemekler harikaydı, tekrar geleceğim",
        "Fiyatlar çok yüksek kaliteye göre", "Hijyen sorunları var, bir daha gelmem",
        "Personel çok güler yüzlü", "Mekan çok kalabalık, rezervasyon alınmalı",
        "Lezzetli yemekler, uygun fiyatlar", "Siparişler karışık geldi, düzeltilmeli"
    ]
    
    data = {
        'Kullanıcı_ID': user_ids,
        'Yorum_Metni': np.random.choice(comments, n_users),
        'Arkadaş_Sayısı': np.random.randint(5, 500, n_users),
        'Yorum_Puanı': np.random.randint(1, 6, n_users),
        'Yorum_Tarihi': pd.date_range('2023-01-01', periods=n_users, freq='D').strftime('%Y-%m-%d')
    }
    
    df = pd.DataFrame(data)
    return df

def analyze_sentiment(text):
    """TextBlob ile Türkçe duygu analizi"""
    try:
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        return polarity
    except:
        return 0.0

def calculate_risk_score(df):
    """Risk skoru hesaplama"""
    # NLP: Duygu analizi
    df['Duygu_Skoru'] = df['Yorum_Metni'].apply(analyze_sentiment)
    df['Duygu_Siddeti'] = np.abs(df['Duygu_Skoru'])
    
    # SNA: Ağ merkeziliği (normalize edilmiş)
    max_friends = df['Arkadaş_Sayısı'].max()
    df['Merkezilik_Skoru'] = df['Arkadaş_Sayısı'] / max_friends
    
    # Risk Skoru: |Polarity| * Merkezilik
    df['Risk_Skoru'] = df['Duygu_Siddeti'] * df['Merkezilik_Skoru']
    
    # Negatif yorum filtreleme
    df['Negatif_Yorum'] = df['Duygu_Skoru'] < -0.1
    
    return df

# Ana başlık
st.markdown('<h1 class="main-header">🛡️ Hibrit Dijital İtibar Risk Modeli</h1>', unsafe_allow_html=True)
st.markdown("### İşletmenizin e-WOM verilerinden gizli kanaat önderlerini tespit edin ve risk skorlarınızı yönetin")

# Sidebar - Dosya yükleme
st.sidebar.markdown("## 📁 Veri Yükleme")
uploaded_file = st.sidebar.file_uploader(
    "Excel (.xlsx) veya CSV (.csv) dosyanızı yükleyin:",
    type=['xlsx', 'csv'],
    help="Dosyada 'Kullanıcı_ID', 'Yorum_Metni', 'Arkadaş_Sayısı' sütunları olmalı"
)

# Örnek veri veya yüklenen veri
if uploaded_file is not None:
    # Kullanıcı dosyası yüklendi
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.sidebar.success("✅ Dosya başarıyla yüklendi!")
        st.session_state['use_sample'] = False
    except Exception as e:
        st.error(f"Dosya okuma hatası: {str(e)}")
        st.info("Lütfen doğru formatta dosya yükleyin.")
        df = generate_sample_data()
        st.session_state['use_sample'] = True
else:
    # Örnek veri kullan
    df = generate_sample_data()
    st.session_state['use_sample'] = True

# Analiz yap
with st.spinner("Analiz ediliyor... NLP + SNA hibrit model çalışıyor..."):
    df_analyzed = calculate_risk_score(df.copy())

# KPI Kartları
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="metric-value">{}</div>
        <p class="metric-label">Toplam Yorum</p>
    </div>
    """.format(len(df_analyzed)), unsafe_allow_html=True)

with col2:
    avg_sentiment = df_analyzed['Duygu_Skoru'].mean()
    color_class = "warning-card" if avg_sentiment < 0 else "kpi-card"
    st.markdown(f"""
    <div class="kpi-card {color_class}">
        <div class="metric-value">{avg_sentiment:.3f}</div>
        <p class="metric-label">Ort. Duygu Skoru</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    high_risk_count = len(df_analyzed[df_analyzed['Risk_Skoru'] > df_analyzed['Risk_Skoru'].quantile(0.9)])
    st.markdown("""
    <div class="kpi-card danger-card">
        <div class="metric-value">{}</div>
        <p class="metric-label">Yüksek Riskli Müşteri</p>
    </div>
    """.format(high_risk_count), unsafe_allow_html=True)

# Risk Matrisi - Scatter Plot
st.markdown("### 📊 Risk Matrisi - İnteraktif Görselleştirme")

# Kritik bölge threshold'ları
high_centrality_threshold = df_analyzed['Merkezilik_Skoru'].quantile(0.8)
high_risk_threshold = df_analyzed['Duygu_Siddeti'].quantile(0.8)

fig = px.scatter(
    df_analyzed, 
    x='Merkezilik_Skoru', 
    y='Duygu_Siddeti',
    size='Risk_Skoru',
    color='Risk_Skoru',
    hover_data=['Kullanıcı_ID', 'Yorum_Metni', 'Arkadaş_Sayısı'],
    color_continuous_scale='RdYlGn_r',
    title="Kritik Riskli Bölge (Sağ Üst Çeyrek)",
    labels={
        'Merkezilik_Skoru': 'Ağ Merkeziliği (0-1)',
        'Duygu_Siddeti': 'Duygu Şiddeti',
        'Risk_Skoru': 'Risk Skoru'
    }
)

# Kritik bölgeyi vurgula
fig.add_vrect(
    x0=high_centrality_threshold, x1=1,
    y0=high_risk_threshold, y1=1,
    fillcolor="red", opacity=0.2,
    line_width=0,
    annotation_text="🚨 KRİTİK RİSK BÖLGESİ", 
    annotation_position="top right"
)

fig.update_layout(
    height=600,
    showlegend=False,
    title_font_size=20,
    font=dict(size=12)
)

st.plotly_chart(fig, use_container_width=True)

# Acil müdahale tablosu
st.markdown("### 🚨 Acil Müdahale Gerektirenler (Risk Skoruna Göre)")
high_risk_users = df_analyzed.nlargest(10, 'Risk_Skoru')[['Kullanıcı_ID', 'Yorum_Metni', 
                                                         'Duygu_Skoru', 'Merkezilik_Skoru', 
                                                         'Risk_Skoru', 'Arkadaş_Sayısı']]

st.dataframe(
    high_risk_users.style.format({
        'Duygu_Skoru': '{:.3f}',
        'Merkezilik_Skoru': '{:.3f}',
        'Risk_Skoru': '{:.4f}'
    }).background_gradient(cmap='Reds', subset=['Risk_Skoru']),
    use_container_width=True,
    height=400
)

# Alt bilgi
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b;'>
    <p>💡 <strong>Hibrit Dijital İtibar Risk Modeli</strong> | Yüksek Lisans Tezi Projesi</p>
    <p>NLP (TextBlob) + SNA (Ağ Merkeziliği) ile geliştirilmiştir.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar info
if st.session_state.get('use_sample', True):
    st.sidebar.info("🔥 Örnek veri kullanılıyor. Kendi verinizi yükleyerek analiz yapabilirsiniz.")
else:
    st.sidebar.markdown("### 📈 Analiz İstatistikleri")
    st.sidebar.metric("İşlenen Kayıt", len(df_analyzed))
    st.sidebar.metric("Ort. Risk Skoru", f"{df_analyzed['Risk_Skoru'].mean():.4f}")