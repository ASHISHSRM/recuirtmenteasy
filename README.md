# RecruitAI - Intelligent Resume Screening Platform

A modern, production-ready resume screening application with **75% skill-based matching** and professional dark UI. **100% local processing - no external APIs required.**

## Features

- ✅ **Skill-Based Scoring (75%)** - Extract and match required technical skills
- ✅ **TF-IDF Similarity (25%)** - Semantic text matching using TF-IDF
- ✅ **Hiring Recommendations** - 🟢 Strong Hire | 🟡 Mid Hire | 🔴 No Hire
- ✅ **Multiple File Formats** - Support for PDF, DOCX, DOC, TXT
- ✅ **Summary Statistics** - Quick overview of candidate pools
- ✅ **Export Options** - CSV and Excel export with full details
- ✅ **Professional Dark UI** - Modern, sleek interface
- ✅ **100% Local Processing** - No external APIs, no internet required
- ✅ **Production Ready** - Deploy on Railway, Vercel, or anywhere

## Scoring Algorithm

```
Combined Score = (Skill Match × 0.75) + (TF-IDF Score × 0.25)

Classification:
  ≥ 75  → 🟢 Strong Hire
  60-75 → 🟡 Mid Hire
  < 60  → 🔴 No Hire
```

## Project Structure

```
RecruitAI-Flat/
├── app.py                 # Flask backend with skill extraction
├── requirements.txt       # Python dependencies
├── railway.toml          # Railway deployment config
├── Procfile              # Process file for deployment
├── runtime.txt           # Python version
├── .gitignore            # Git ignore rules
└── frontend/
    ├── index.html        # Professional dark UI
    ├── app.js            # Screening logic & exports
    └── style.css         # Modern dark theme
```

## Setup

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/ashishsrivastava1712/recuirtmenteasy.git
   cd RecruitAI-Flat
   ```

2. Create Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run locally:
   ```bash
   python app.py
   ```
   
   Visit: `http://localhost:5000`

## How It Works

1. **Upload Job Description** - PDF, DOCX, TXT, or paste text
2. **Upload Resumes** - Select multiple resume files
3. **Click "Start Screening"** - AI analyzes skill match + similarity
4. **View Results** - See scores, recommendations, strengths & gaps
5. **Export** - Download as CSV or Excel

## Technical Details

### Backend (Flask)
- **Skill Extraction** - Matches 50+ technical & soft skills
- **TF-IDF Vectorizer** - scikit-learn based text similarity
- **Hybrid Scoring** - Combines both metrics for better decisions
- **File Parsing** - PyPDF2 for PDFs, python-docx for Word

### Frontend (Bootstrap 5 + Vanilla JS)
- **Dark Theme** - Professional, modern, eye-friendly
- **Responsive Design** - Works on desktop, tablet, mobile
- **Real-time Summary** - Live candidate count by hire category
- **Batch Export** - CSV/Excel with all analysis data

## Skills Database

Automatically detects:
- **Programming**: Python, JavaScript, Java, C++, Go, Rust, etc.
- **Frontend**: React, Angular, Vue, Tailwind, Bootstrap
- **Backend**: Django, Flask, Node.js, Express, Spring, FastAPI
- **Databases**: SQL, MongoDB, PostgreSQL, Firebase, Redis
- **DevOps**: Docker, Kubernetes, AWS, GCP, Azure
- **AI/ML**: TensorFlow, PyTorch, scikit-learn, NLP, Computer Vision
- **Soft Skills**: Communication, Leadership, Teamwork, etc.

## Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect repository to Railway
3. Set Python version in `runtime.txt` ✅ (included)
4. Railway auto-detects `Procfile` and deploys

### Manual Deployment

```bash
# Install gunicorn
pip install gunicorn

# Run production server
gunicorn app:app
```

The app will be available at your deployment URL.

## Environment Variables

No external API keys needed! Everything runs locally.

(Optional .env file shown in `.env.example`)

## Performance

- **Single Resume**: ~100-200ms
- **10 Resumes**: ~1-2s
- **50 Resumes**: ~5-10s

Depends on file size and resume complexity.

## Technologies Used

- **Backend**: Python 3.10+, Flask, scikit-learn
- **Frontend**: HTML5, CSS3 (dark theme), Vanilla JavaScript
- **File Handling**: PyPDF2, python-docx
- **Export**: XLSX library
- **Deployment**: Railway, Gunicorn

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, open a GitHub issue or contact the maintainers.

---

**Built with ❤️ for efficient resume screening**
