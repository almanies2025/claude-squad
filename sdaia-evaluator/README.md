# SDAIA National AI Portfolio Evaluator

A professional web-based tool for evaluating AI portfolios and projects against the SDAIA National AI Strategy framework.

## Features

- **Dashboard Overview** — Real-time visualization of portfolio metrics and evaluation status
- **Comprehensive Evaluation** — Assess AI projects against national AI maturity frameworks
- **Bilingual Support** — Full English and Arabic language support
- **PDF Report Generation** — Export detailed evaluation reports
- **Risk Assessment** — Built-in risk scoring and mitigation recommendations
- **Interactive UI** — Modern, responsive interface built with vanilla JavaScript

## Deployment

### One-Click Deploy to Render.com

1. Fork this repository to your GitHub account
2. Go to [render.com](https://render.com) and sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your forked repository
5. Render will auto-detect the `render.yaml` configuration
6. Click "Deploy"

### Local Development

```bash
git clone https://github.com/almanies2025/claude-squad.git
cd claude-squad/sdaia-evaluator
pip install -r requirements.txt
python main.py
```

Then open **http://localhost:8000** in your browser.

### Important: PORT Environment Variable

Render.com sets the `PORT` environment variable automatically. The application uses `os.environ.get("PORT", 8000)` to respect this.

### Temporary Sharing with LocalTunnel

```bash
npx localtunnel --port 8000
```

## Tech Stack

- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend:** Vanilla JavaScript, CSS animations
- **Deployment:** Render.com

## License

MIT
