# Axorvian AI Business Assistant — shell

Working scaffold: auth + SQLite history + LLM abstraction + one live module (AI Chat).

## Run it

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in GEMINI_API_KEY
streamlit run app.py
```

Sign up on the landing page, log in, then open **AI Chat** from the sidebar.

## Project layout