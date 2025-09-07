# 📄 DoxTract - Professional Document Extraction

✨ Features

- 📄 **Multi-format Support**: PDF, TXT, DOCX files
- 🔒 **Enterprise Security**: Rate limiting, CORS protection, input validation
- 📊 **Large File Support**: Up to 50MB file processing
- 🚀 **Serverless Architecture**: Auto-scaling on Vercel + Cloud Run
- 🌐 **Global CDN**: Fast access worldwide via Vercel
- 📱 **Responsive UI**: Modern, professional interface
- 🔍 **Detailed Extraction**: Text, tables, metadata, and document structure
- ⚡ **Real-time Processing**: Live progress updates and instant downloads

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- Node.js (for Vercel CLI)
- Google Cloud CLI

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/doxtract.git
cd doxtract

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend
python app.py
```

```bash
# Setup frontend (new terminal)
cd frontend
python -m http.server 3000
```

Open http://localhost:3000 in your browser.

## 🔒 Security Features

- ✅ **Rate Limiting**: 10 requests/minute per IP
- ✅ **Input Validation**: File type and size checks
- ✅ **CORS Protection**: Restricted origins
- ✅ **Security Headers**: XSS, clickjacking protection
- ✅ **Error Sanitization**: No internal details exposed
- ✅ **Production Mode**: Debug endpoints disabled

## 📈 Performance

| Metric                     | Value                         |
| -------------------------- | ----------------------------- |
| **File Size Limit**  | 50MB                          |
| **Processing Speed** | ~2-10s for typical documents  |
| **Concurrent Users** | Auto-scaling (0-10 instances) |
| **Global Latency**   | <100ms via Vercel CDN         |
| **Uptime**           | 99.9%+ (serverless)           |

## 📁 Project Structure

```
doxtract/
├── backend/
│   ├── app.py              # FastAPI backend
│   ├── docparse.py         # Document processing engine
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Container configuration
│   └── cloudbuild.yaml     # Cloud Run deployment
├── frontend/
│   ├── index.html          # Web interface
│   └── vercel.json         # Vercel configuration
├── deploy-backend.sh       # Backend deployment script
├── deploy-frontend.sh      # Frontend deployment script
├── configure.py            # Configuration helper
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run security checks: `safety check`
5. Submit a pull request

## 🆘 Support

- 📖 **Documentation**: [VERCEL-CLOUDRUN-DEPLOY.md](VERCEL-CLOUDRUN-DEPLOY.md)
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Contact**: [@Shreyas_Pandeyy](https://x.com/Shreyas_Pandeyy)

Made with ❤️ for document processing needs
