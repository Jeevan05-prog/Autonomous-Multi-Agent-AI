RESEARCHFLOW AI WEBSITE - SETUP

This is a website add-on for your existing Autonomous-Multi-Agent-AI project.
It does not replace your existing agents, app.py, or CLI workflow.

1. Extract the ZIP contents into the ROOT of your existing project:
   C:\Users\jeeva\Desktop\JKM\Projects\Autonomous-Multi-Agent-AI

   The files should be placed like this:

   Autonomous-Multi-Agent-AI/
   ├── agents/                  (your existing folder - do not replace)
   ├── graph/                   (your existing folder - do not replace)
   ├── models/                  (your existing folder - do not replace)
   ├── datasets/                (your existing folder)
   ├── outputs/                 (your existing folder)
   ├── website/
   │   ├── templates/
   │   │   └── index.html
   │   └── static/
   │       ├── css/
   │       │   └── style.css
   │       └── js/
   │           └── app.js
   ├── web_app.py
   └── WEBSITE_SETUP_README.txt

2. Open the project folder in VS Code.

3. Activate your existing virtual environment in the VS Code terminal:
   .\venv\Scripts\Activate.ps1

   If your terminal already shows (venv), do not activate it again.

4. Install Flask:
   pip install flask

   Your existing project should already have LangGraph and the agent dependencies
   installed. If not, install your existing requirements:
   pip install -r requirements.txt

5. Start the website:
   python web_app.py

6. Open this address in your browser:
   http://127.0.0.1:5000

HOW TO USE

A. Web Research Only:
   - Open New Research.
   - Enter a research topic.
   - Leave the CSV upload empty.
   - Click Generate research.
   - The six agents run. The Data Analyst extracts numerical evidence found in
     research text; it does not invent figures or create statistical charts
     without structured data.

B. Research + Data Analysis:
   - Enter a research topic.
   - Upload a .csv file.
   - Click Generate research.
   - The existing Data Analyst processes the uploaded dataset and generates
     charts when the dataset is suitable.

IMPORTANT NOTES

- Keep your existing .env file in the project root. Never put your Gemini API key
  in website HTML, CSS, or JavaScript.
- The website uses the same existing agents and Gemini configuration.
- Your original app.py CLI application remains unchanged.
- Existing agents save output to shared outputs/ paths. To avoid overwriting
  reports/charts, the website allows only one active workflow at a time.
- Uploaded CSV files are saved in datasets/uploads/.
- The website binds to 127.0.0.1, so it is intended for local use on your PC.
- If the app reports an import error, confirm that you extracted the files into
  the project root (the same folder that contains agents/, graph/, and models/).
