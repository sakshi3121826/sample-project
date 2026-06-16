# Multi-format Extraction Agent

A Flask web application for ingesting and normalizing data from multiple sources:
- Video files
- Free-form text
- Excel spreadsheets (`.xlsx`, `.xls`)

The app presents a dynamic frontend with 10 pages and a backend that supports uploads, extraction flows, and result previews.

## Project structure

- `app.py` - Flask backend with routes for all pages and upload endpoints.
- `templates/` - Jinja HTML templates built from a shared `base.html` layout.
- `static/css/style.css` - styling for the site, hero section, cards, and forms.
- `static/js/app.js` - frontend behavior for tabs and navigation highlighting.
- `static/images/hero-visual.svg` - branding illustration used on the homepage and upload page.
- `requirements.txt` - Python dependencies.

## Pages included

- Home
- Upload
- Video
- Text
- Excel
- Transactions
- Images
- Results
- Settings
- About

## Features

- Upload and process video, text, and Excel files.
- Extract transaction records from text and spreadsheet data.
- Display normalized results in JSON format.
- View transaction lists and frame/image extraction previews.
- Clean modern UI with gradient backgrounds and illustrations.

## Azure integration guidance

This project includes local placeholder logic for video processing. For full production behavior, connect these Azure services:

1. **Azure AI Video Indexer** or **Azure AI Video Analyzer**
   - Process videos
   - Extract speech transcripts
   - Detect frames and objects
   - Pull image metadata
2. **Azure Computer Vision**
   - OCR text from extracted frames
   - Detect printed or handwritten text
3. **Azure Document Intelligence**
   - Extract structured data from receipts, invoices, and forms
   - Use prebuilt or custom models for transactions
4. **Azure OpenAI**
   - Normalize free-form text into a consistent JSON schema
   - Extract entities and transaction fields from unstructured input

## Run locally

1. Create a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open your browser:
   ```text
   http://127.0.0.1:5000
   ```

## Developer notes

- `process_video_file()` in `app.py` is stubbed with placeholder results.
- Add Azure SDK logic and secret configuration for a production pipeline.
- The app saves uploads to a local `uploads/` folder created automatically.
- Use `pandas` and `openpyxl` for spreadsheet processing.

## Future improvements

- Add real Azure Video Indexer integration.
- Add user authentication and file history.
- Add schema mapping for different transaction formats.
- Store results in a database or Azure Blob Storage.
