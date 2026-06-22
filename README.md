# AI PPT Generator

Production-grade AI-powered PowerPoint generation tool using the Groq API. Generate professional PPTX presentations from any topic with template support and intelligent image placement.

## Features

- Generate complete presentations from a topic and detailed prompt
- Groq API for content planning and slide generation
- 5 professional templates: Professional, Modern, Academic, Creative, Minimal
- Upload and select images (PNG, JPG, JPEG, WEBP)
- AI decides image placement on slides (left, right, center, top, bottom, background)
- Multiple slide types: title, content, two-column, image focus, comparison, timeline, conclusion, thank you
- Export-ready PPTX files

## Project Structure

```
project_root/
├── app/
│   ├── services/
│   │   ├── groq_service.py
│   │   ├── ppt_service.py
│   │   └── image_service.py
│   ├── templates/
│   │   ├── professional.py
│   │   ├── academic.py
│   │   ├── modern.py
│   │   ├── creative.py
│   │   └── minimal.py
│   ├── models/
│   │   ├── slide.py06+
│   │   ├── image.py
│   │   └── presentation.py
│   ├── utils/
│   │   ├── constants.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── main.py
├── uploads/
├── generated/
├── assets/
├── tests/
└── requirements.txt
```

## Setup

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Groq API key**

   Copy `.env.example` to `.env` and add your key:

   ```bash
   copy .env.example .env
   ```

   Get a free API key at [console.groq.com](https://console.groq.com).

4. **Run the application**

   ```bash
   uvicorn app.main:app --reload
   ```

   Open [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

1. Enter a **topic** and optional detailed prompt
2. Choose slide count, presentation type, and template
3. Upload images and select which ones to include
4. Click **Generate Presentation**
5. Download the generated PPTX file

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/api/templates` | List available templates |
| GET | `/api/images` | List uploaded images |
| POST | `/api/images/upload` | Upload an image |
| POST | `/api/generate` | Generate a presentation |
| GET | `/api/download/{filename}` | Download generated PPTX |

## Running Tests

```bash++
pytest tests/ -v
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (required) |
