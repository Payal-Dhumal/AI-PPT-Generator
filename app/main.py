"""FastAPI application entry point."""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.models.image import ImageMetadata
from app.models.presentation import GenerationResult, PresentationRequest
from app.services.groq_service import GroqService
from app.services.image_service import ImageManager
from app.services.ppt_service import PPTGenerator
from app.utils.constants import (
    DEFAULT_SLIDE_COUNT,
    GENERATED_DIR,
    PRESENTATION_TYPES,
    TEMPLATE_NAMES,
    UPLOADS_DIR,
)
from app.utils.validators import ValidationError

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="AI PPT Generator", version="1.0.0")

image_manager = ImageManager(uploads_dir=str(BASE_DIR / UPLOADS_DIR))
ppt_generator = PPTGenerator(
    image_manager=image_manager,
    generated_dir=str(BASE_DIR / GENERATED_DIR),
)

os.makedirs(BASE_DIR / UPLOADS_DIR, exist_ok=True)
os.makedirs(BASE_DIR / GENERATED_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "assets", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=_get_html_ui())


@app.get("/api/templates")
async def list_templates():
    return {"templates": TEMPLATE_NAMES}


@app.get("/api/presentation-types")
async def list_presentation_types():
    return {"types": PRESENTATION_TYPES}


@app.get("/api/images", response_model=List[ImageMetadata])
async def list_images():
    return image_manager.list_images()


@app.post("/api/images/upload", response_model=ImageMetadata)
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return image_manager.upload_image(content, file.filename or "image.png")
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/api/images/{image_name}")
async def delete_image(image_name: str):
    if not image_manager.delete_image(image_name):
        raise HTTPException(status_code=404, detail="Image not found")
    return {"success": True}


@app.post("/api/generate", response_model=GenerationResult)
async def generate_presentation(
    topic: str = Form(...),
    prompt: str = Form(""),
    slide_count: int = Form(DEFAULT_SLIDE_COUNT),
    presentation_type: str = Form("Business Presentation"),
    template_name: str = Form("Professional"),
    selected_images: str = Form(""),
):
    try:
        image_list = [img.strip() for img in selected_images.split(",") if img.strip()]
        available = [img.image_name for img in image_manager.list_images()]

        request = PresentationRequest(
            topic=topic,
            prompt=prompt,
            slide_count=slide_count,
            presentation_type=presentation_type,
            template_name=template_name,
            selected_images=image_list,
        )

        groq_service = GroqService()
        presentation_data = groq_service.generate_presentation(request)
        file_path = ppt_generator.generate_presentation(presentation_data, template_name)

        return GenerationResult(
            success=True,
            message="Presentation generated successfully.",
            file_path=os.path.basename(file_path),
            presentation_title=presentation_data.presentation_title,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc


@app.get("/api/download/{filename}")
async def download_presentation(filename: str):
    file_path = BASE_DIR / GENERATED_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


def _get_html_ui() -> str:
    templates_options = "".join(f'<option value="{t}">{t}</option>' for t in TEMPLATE_NAMES)
    types_options = "".join(f'<option value="{t}">{t}</option>' for t in PRESENTATION_TYPES)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI PPT Generator</title>
  <style>
    :root {{
      --bg: #0f1419;
      --surface: #1a2332;
      --surface2: #243044;
      --border: #2d3a4f;
      --text: #e7ecf3;
      --muted: #8b9cb3;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --success: #22c55e;
      --error: #ef4444;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }}
    .container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}
    header {{ text-align: center; margin-bottom: 2.5rem; }}
    header h1 {{
      font-size: 2rem;
      font-weight: 700;
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }}
    header p {{ color: var(--muted); }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    .card h2 {{
      font-size: 1.1rem;
      margin-bottom: 1rem;
      color: var(--text);
    }}
    label {{
      display: block;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 0.35rem;
    }}
    input, select, textarea {{
      width: 100%;
      padding: 0.65rem 0.85rem;
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }}
    input:focus, select:focus, textarea:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    textarea {{ min-height: 80px; resize: vertical; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    @media (max-width: 640px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .upload-zone {{
      border: 2px dashed var(--border);
      border-radius: 8px;
      padding: 2rem;
      text-align: center;
      cursor: pointer;
      transition: border-color 0.2s;
    }}
    .upload-zone:hover {{ border-color: var(--accent); }}
    .upload-zone input {{ display: none; }}
    .image-list {{ display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; }}
    .image-item {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--surface2);
      padding: 0.5rem 0.75rem;
      border-radius: 8px;
      font-size: 0.85rem;
    }}
    .image-item input {{ width: auto; margin: 0; }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .btn-primary {{
      background: var(--accent);
      color: white;
      width: 100%;
      margin-top: 0.5rem;
    }}
    .btn-primary:hover {{ background: var(--accent-hover); }}
    .btn-primary:disabled {{ opacity: 0.6; cursor: not-allowed; }}
    .status {{
      padding: 1rem;
      border-radius: 8px;
      margin-top: 1rem;
      display: none;
    }}
    .status.success {{ display: block; background: rgba(34,197,94,0.15); color: var(--success); }}
    .status.error {{ display: block; background: rgba(239,68,68,0.15); color: var(--error); }}
    .status.loading {{ display: block; background: rgba(59,130,246,0.15); color: var(--accent); }}
    .download-link {{
      display: inline-block;
      margin-top: 0.75rem;
      color: var(--accent);
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>AI PPT Generator</h1>
      <p>Create professional presentations from any topic using Groq AI</p>
    </header>

    <form id="generateForm">
      <div class="card">
        <h2>Presentation Details</h2>
        <label for="topic">Topic *</label>
        <input type="text" id="topic" name="topic" placeholder="e.g. Artificial Intelligence" required>

        <label for="prompt">Detailed Prompt</label>
        <textarea id="prompt" name="prompt" placeholder="Additional instructions for content generation..."></textarea>

        <div class="grid">
          <div>
            <label for="slide_count">Number of Slides</label>
            <input type="number" id="slide_count" name="slide_count" value="10" min="3" max="30">
          </div>
          <div>
            <label for="presentation_type">Presentation Type</label>
            <select id="presentation_type" name="presentation_type">{types_options}</select>
          </div>
        </div>

        <label for="template_name">Template</label>
        <select id="template_name" name="template_name">{templates_options}</select>
      </div>

      <div class="card">
        <h2>Images</h2>
        <div class="upload-zone" id="uploadZone">
          <input type="file" id="imageInput" accept=".png,.jpg,.jpeg,.webp" multiple>
          <p>Click or drag images here (PNG, JPG, WEBP)</p>
        </div>
        <div class="image-list" id="imageList"></div>
      </div>

      <button type="submit" class="btn btn-primary" id="submitBtn">Generate Presentation</button>
      <div class="status" id="status"></div>
    </form>
  </div>

  <script>
    const uploadZone = document.getElementById('uploadZone');
    const imageInput = document.getElementById('imageInput');
    const imageList = document.getElementById('imageList');
    const form = document.getElementById('generateForm');
    const status = document.getElementById('status');
    const submitBtn = document.getElementById('submitBtn');

    let uploadedImages = [];

    uploadZone.addEventListener('click', () => imageInput.click());
    uploadZone.addEventListener('dragover', e => {{ e.preventDefault(); uploadZone.style.borderColor = 'var(--accent)'; }});
    uploadZone.addEventListener('dragleave', () => {{ uploadZone.style.borderColor = 'var(--border)'; }});
    uploadZone.addEventListener('drop', e => {{
      e.preventDefault();
      uploadZone.style.borderColor = 'var(--border)';
      handleFiles(e.dataTransfer.files);
    }});
    imageInput.addEventListener('change', e => handleFiles(e.target.files));

    async function handleFiles(files) {{
      for (const file of files) {{
        const formData = new FormData();
        formData.append('file', file);
        try {{
          const res = await fetch('/api/images/upload', {{ method: 'POST', body: formData }});
          if (!res.ok) throw new Error((await res.json()).detail);
          const data = await res.json();
          uploadedImages.push(data);
          renderImages();
        }} catch (err) {{
          showStatus('error', 'Upload failed: ' + err.message);
        }}
      }}
    }}

    function renderImages() {{
      imageList.innerHTML = uploadedImages.map(img => `
        <label class="image-item">
          <input type="checkbox" value="${{img.image_name}}" checked>
          ${{img.display_name}}
        </label>
      `).join('');
    }}

    function showStatus(type, message, downloadUrl) {{
      status.className = 'status ' + type;
      status.innerHTML = message + (downloadUrl ? `<a class="download-link" href="${{downloadUrl}}" download>Download PPTX</a>` : '');
    }}

    form.addEventListener('submit', async e => {{
      e.preventDefault();
      submitBtn.disabled = true;
      showStatus('loading', 'Generating presentation... This may take a moment.');

      const selected = [...imageList.querySelectorAll('input:checked')].map(cb => cb.value);
      const formData = new FormData(form);
      formData.set('selected_images', selected.join(','));

      try {{
        const res = await fetch('/api/generate', {{ method: 'POST', body: formData }});
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Generation failed');
        showStatus('success', `${{data.presentation_title}} — ready! `, '/api/download/' + data.file_path);
      }} catch (err) {{
        showStatus('error', err.message);
      }} finally {{
        submitBtn.disabled = false;
      }}
    }});

    fetch('/api/images').then(r => r.json()).then(imgs => {{
      uploadedImages = imgs;
      renderImages();
    }});
  </script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
