"""
GenAI Product Marketing Automation System
Author: Hrudaynath Doke
Stack: Claude API (Anthropic) + DALL-E 3 (OpenAI) + Streamlit
"""

import streamlit as st
import anthropic
import openai
import requests
import json
import os
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Marketing Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600&family=Playfair+Display:wght@700;900&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #0A0A0A; }
.stApp { background: #0A0A0A; color: #fff; }

.header-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #fff 40%, #666);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
}

.metric-card {
    background: #111;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.copy-block {
    background: #111;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}

.tag {
    display: inline-block;
    background: rgba(232,255,71,0.1);
    border: 1px solid rgba(232,255,71,0.3);
    color: #E8FF47;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    margin: 3px;
    letter-spacing: 0.5px;
}

.stButton > button {
    background: linear-gradient(135deg, #E8FF47, #B8FF00) !important;
    color: #000 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(232,255,71,0.25) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #111 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #fff !important;
    border-radius: 8px !important;
}

.stSidebar { background: #0D0D0D !important; }
.stSidebar [data-testid="stSidebarContent"] { background: #0D0D0D !important; }

hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
PRODUCT_CATEGORIES = [
    "Tech & Gadgets",
    "Fashion & Apparel",
    "Food & Beverage",
    "Beauty & Wellness",
    "Home & Living",
    "Sports & Fitness",
]

COPY_TONES = [
    "Bold & Punchy",
    "Luxury & Refined",
    "Playful & Fun",
    "Professional & Trustworthy",
    "Minimalist & Clean",
]

COPY_FORMATS = [
    "Social Media Post",
    "Product Description",
    "Ad Headline + Body",
    "Email Subject + Preview",
    "Full Campaign Brief",
]

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

# ── API clients ───────────────────────────────────────────────────────────────
def get_anthropic_client():
    key = st.session_state.get("anthropic_key") or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        st.error("⚠ Anthropic API key not set. Add it in the sidebar.")
        st.stop()
    return anthropic.Anthropic(api_key=key)

def get_openai_client():
    key = st.session_state.get("openai_key") or os.getenv("OPENAI_API_KEY", "")
    if not key:
        return None
    return openai.OpenAI(api_key=key)

# ── Core pipeline ─────────────────────────────────────────────────────────────
def generate_copy(product_name: str, category: str, tone: str, fmt: str, keywords: str) -> dict:
    """Call Claude API to generate structured marketing copy."""
    client = get_anthropic_client()

    system = (
        "You are a world-class brand copywriter and marketing strategist. "
        "You create compelling, conversion-optimized marketing copy that is "
        "brand-consistent, audience-aware, and emotionally resonant. "
        "Always respond with ONLY a JSON object — no markdown, no backticks, no explanation."
    )

    prompt = f"""Generate marketing copy for this product:

Product: {product_name}
Category: {category}
Brand Tone: {tone}
Output Format: {fmt}
Keywords to include: {keywords or 'none specified'}

Return ONLY this JSON:
{{
  "headline": "Main attention-grabbing headline",
  "subheadline": "Supporting subheadline",
  "body": "Full copy body (2-4 sentences)",
  "cta": "Call to action text",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "imagePrompt": "Detailed DALL-E 3 prompt: realistic, studio-lit, brand-aligned product photo",
  "brandVoiceNote": "1 sentence on why this tone works for this category"
}}"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_image(dalle_prompt: str) -> Image.Image | None:
    """Call DALL-E 3 to generate a product image."""
    client = get_openai_client()
    if client is None:
        return None

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        url = response.data[0].url
        img_bytes = requests.get(url, timeout=30).content
        return Image.open(BytesIO(img_bytes))
    except Exception as e:
        st.warning(f"Image generation failed: {e}")
        return None


def run_pipeline(product_name, category, tone, fmt, keywords, gen_image=True):
    """Full multi-modal pipeline: copy + image."""
    with st.spinner("⚡ Generating copy with Claude..."):
        copy_data = generate_copy(product_name, category, tone, fmt, keywords)

    image = None
    if gen_image:
        with st.spinner("🎨 Generating image with DALL-E 3..."):
            image = generate_image(copy_data.get("imagePrompt", ""))

    result = {
        "product": product_name,
        "category": category,
        "tone": tone,
        "format": fmt,
        "copy": copy_data,
        "image": image,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    st.session_state.history.insert(0, result)
    st.session_state.generation_count += 1
    return result

# ── Render result ─────────────────────────────────────────────────────────────
def render_result(result: dict):
    copy = result["copy"]
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### 📣 Headline")
        st.markdown(f"**{copy.get('headline', '')}**")
        st.markdown(f"*{copy.get('subheadline', '')}*")
        st.divider()

        st.markdown("### 📝 Body Copy")
        st.write(copy.get("body", ""))
        st.divider()

        st.markdown("### 🎯 Call to Action")
        st.code(copy.get("cta", ""), language=None)

        st.markdown("### 🏷 Hashtags")
        tags_html = " ".join(f'<span class="tag">#{t}</span>' for t in copy.get("hashtags", []))
        st.markdown(tags_html, unsafe_allow_html=True)
        st.divider()

        st.markdown("### 🎨 DALL-E 3 Image Prompt")
        st.text_area("Copy this into DALL-E 3", copy.get("imagePrompt", ""), height=100, key=f"prompt_{result['timestamp']}")

        st.markdown("### 💡 Brand Voice Note")
        st.info(copy.get("brandVoiceNote", ""))

    with col2:
        if result.get("image"):
            st.image(result["image"], caption="AI-Generated Product Visual", use_column_width=True)
        else:
            st.markdown("""
            <div style='background:#111;border:1px solid rgba(255,255,255,0.08);
                border-radius:12px;padding:60px 20px;text-align:center;color:#444;'>
                <div style='font-size:2rem;margin-bottom:12px;'>🎨</div>
                <div>Add an OpenAI key in the sidebar<br>to generate product images</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='copy-block' style='margin-top:16px;'>
            <div style='color:#555;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>Session Info</div>
            <div style='color:#888;font-size:0.8rem;'>📦 {result['product']}</div>
            <div style='color:#888;font-size:0.8rem;'>🏷 {result['category']}</div>
            <div style='color:#888;font-size:0.8rem;'>🎭 {result['tone']}</div>
            <div style='color:#888;font-size:0.8rem;'>📄 {result['format']}</div>
            <div style='color:#888;font-size:0.8rem;'>🕐 {result['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Export
        export_json = json.dumps({k: v for k, v in result.items() if k != "image"}, indent=2)
        st.download_button(
            "⬇ Export JSON",
            data=export_json,
            file_name=f"marketing_{result['product'].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ GenAI Marketing Engine")
    st.caption("v2.0 · Hrudaynath Doke")
    st.divider()

    st.markdown("**🔑 API Keys**")
    anthropic_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...", key="anthropic_key")
    openai_key = st.text_input("OpenAI API Key (DALL-E 3)", type="password", placeholder="sk-...", key="openai_key")
    st.caption("Keys stay in session only — never stored.")
    st.divider()

    st.markdown("**📊 Session Stats**")
    st.metric("Generations", st.session_state.generation_count)
    st.metric("History Items", len(st.session_state.history))
    st.divider()

    st.markdown("**🛠 Pipeline**")
    st.markdown("""
    - 🧠 **Claude claude-opus-4-5** — Copy generation
    - 🎨 **DALL-E 3** — Image generation
    - 🏗 **Prompt Engineering** — Brand-consistent output
    - 💾 **Session State** — History management
    - 📤 **JSON Export** — Portability
    """)

    if st.button("🗑 Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.generation_count = 0
        st.rerun()


# ── Main UI ───────────────────────────────────────────────────────────────────
st.markdown('<div class="header-title">Product Marketing<br>Automation System</div>', unsafe_allow_html=True)
st.caption("Multi-modal GenAI pipeline · Claude + DALL-E 3 · 5+ product categories")
st.divider()

# Metrics row
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Claude Model", "claude-opus-4-5")
with m2: st.metric("Image Model", "DALL-E 3")
with m3: st.metric("Categories", "6")
with m4: st.metric("Output Formats", "5")

st.divider()

# Input form
st.markdown("### 🚀 Generate Marketing Copy")
col1, col2 = st.columns([2, 1])

with col1:
    product_name = st.text_input("Product Name *", placeholder="e.g. AuraX Pro Wireless Earbuds")
    keywords = st.text_input("Keywords (optional)", placeholder="premium, eco-friendly, innovative...")

with col2:
    category = st.selectbox("Category", PRODUCT_CATEGORIES)
    tone = st.selectbox("Brand Tone", COPY_TONES)

fmt = st.selectbox("Output Format", COPY_FORMATS)

col_a, col_b, col_c = st.columns([2, 1, 3])
with col_a:
    gen_image = st.checkbox("Generate DALL-E 3 Image", value=True)
with col_b:
    generate_btn = st.button("⚡ Generate", use_container_width=True)

st.divider()

# Batch mode
with st.expander("⚡ Batch Mode — Generate for All Categories"):
    st.caption("Runs the pipeline across all 6 product categories simultaneously.")
    batch_product = st.text_input("Product for batch run", placeholder="e.g. EcoSip Water Bottle", key="batch_product")
    batch_tone = st.selectbox("Tone", COPY_TONES, key="batch_tone")
    batch_fmt = st.selectbox("Format", COPY_FORMATS, key="batch_fmt")
    if st.button("⚡ Run Batch (6 categories)", use_container_width=True):
        if not batch_product.strip():
            st.error("Enter a product name.")
        else:
            batch_results = []
            progress = st.progress(0, "Starting batch generation...")
            for i, cat in enumerate(PRODUCT_CATEGORIES):
                progress.progress((i + 1) / len(PRODUCT_CATEGORIES), f"Generating for {cat}...")
                r = run_pipeline(batch_product, cat, batch_tone, batch_fmt, "", gen_image=False)
                batch_results.append(r)
            progress.empty()
            st.success(f"✅ Generated {len(batch_results)} copy sets!")
            for r in batch_results:
                with st.expander(f"📦 {r['category']}"):
                    render_result(r)

# Single generation
if generate_btn:
    if not product_name.strip():
        st.error("⚠ Product name is required.")
    else:
        result = run_pipeline(product_name, category, tone, fmt, keywords, gen_image)
        st.success("✅ Generated successfully!")
        render_result(result)

# History
if st.session_state.history:
    st.divider()
    st.markdown("### 📂 Session History")
    for i, r in enumerate(st.session_state.history[1:], 1):  # Skip the latest (already shown)
        with st.expander(f"[{r['timestamp']}] {r['product']} · {r['category']} · {r['tone']}"):
            render_result(r)
