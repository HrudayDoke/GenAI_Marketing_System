# ⚡ GenAI Product Marketing Automation System

> Multi-modal AI pipeline for brand-consistent marketing copy and product image generation — powered by **Claude API** (Anthropic) and **DALL-E 3** (OpenAI), deployed as a full-stack **Streamlit** application.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)
![Claude](https://img.shields.io/badge/Claude-claude--opus--4--5-purple?style=flat-square)
![DALL·E](https://img.shields.io/badge/DALL·E-3-green?style=flat-square&logo=openai)

---

## 🚀 Features

- **Multi-modal GenAI pipeline** — Claude generates structured copy; DALL-E 3 generates brand-aligned product visuals from Claude's own prompts
- **Prompt engineering framework** — System + user prompts engineered for brand-consistent, conversion-optimized output
- **5+ product categories** — Tech, Fashion, Food, Beauty, Home, Sports
- **5 brand tones** — Bold & Punchy, Luxury, Playful, Professional, Minimalist
- **5 output formats** — Social Post, Product Description, Ad Copy, Email, Campaign Brief
- **Batch mode** — Runs all 6 categories in parallel with a single click
- **Session state management** — Full generation history within a session
- **JSON export** — Every result exportable as structured JSON
- **API key management** — Secure in-session key handling (never stored)

---

## 🏗 Architecture

```
User Input (product, category, tone, format)
        │
        ▼
┌───────────────────┐
│   Claude claude-opus-4-5     │  ← Prompt Engineering Framework
│  (Anthropic API)  │     System prompt: brand-aware copywriter
└────────┬──────────┘     User prompt: structured JSON schema
         │
         │  JSON output:
         │  { headline, subheadline, body, cta,
         │    hashtags, imagePrompt, brandVoiceNote }
         │
         ▼
┌───────────────────┐
│    DALL-E 3       │  ← imagePrompt from Claude
│  (OpenAI API)     │     1024×1024, standard quality
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Streamlit UI    │  ← Session state, history, export
│   (Full-stack)    │
└───────────────────┘
```

---

## 🛠 Setup

### 1. Clone the repo
```bash
git clone https://github.com/HrudayDoke/genai-marketing-system.git
cd genai-marketing-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
```bash
cp .env.example .env
# Edit .env and add your keys:
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
```
Or enter keys directly in the app's sidebar (session-only, never stored).

### 4. Run
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
genai-marketing-system/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```

---

## 💡 Prompt Engineering Design

The system uses a **two-layer prompt architecture**:

**System prompt** — Establishes the AI persona as a world-class brand copywriter, emphasizes brand-consistency, conversion focus, and JSON-only output.

**User prompt** — Dynamically injects: product name, category, tone, format, and keywords. Defines a strict JSON schema so output is always parseable and structured.

Claude's `imagePrompt` field is then passed verbatim to DALL-E 3 — creating a closed-loop where the copy model also directs the vision model.

---

## 🧑‍💻 Author

**Hrudaynath Doke**  
MCA Graduate · Data & AI Engineer  
[GitHub](https://github.com/HrudayDoke) · [LinkedIn](https://linkedin.com/in/hrudaynath-doke)

---

## 📄 License

MIT License — free to use, modify, and distribute.
