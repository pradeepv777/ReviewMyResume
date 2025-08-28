# AI Resume Reviewer (Streamlit)

A clean Streamlit port of your resume reviewer. Upload a PDF, get a 100-point score, category breakdown, tier (S–D), and prioritized feedback.

## Quickstart (VS Code)

1. **Open folder**
   - In VS Code: *File → Open Folder…* and select this project.

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   # Activate
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open the app**
   - Your browser should open automatically. If not, copy the provided URL into your browser.

## Notes
- Grammar checks use `language_tool_python`. If it fails (no internet / Java not available), the app falls back to a neutral grammar score.
- Heuristic ATS & Design scores are computed in `parser.py`. Improve them later with layout-aware parsing.
- All scoring weights & thresholds live in `scoring.py`.
