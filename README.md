# 🤖 Autonomous Multi-Agent AI Workflow Orchestration

An AI-powered research and workflow automation system that uses multiple specialized AI agents to plan, research, analyze data, generate insights, evaluate results, and produce structured research reports.

The project demonstrates how multiple intelligent agents can collaborate to complete a complex research task with minimal human intervention.

---

## 🚀 Project Overview

Traditional research workflows often require users to manually collect information, analyze data, identify patterns, and prepare reports.

This project automates that process using a **six-agent AI architecture**.

A user provides a research topic, and the system coordinates six specialized agents that work together to generate a structured research report.

### Example Research Topic

**The Rise of AI-Powered Cyberattacks and Intelligent Threat Detection (2021–2026)**

The system processes the topic through multiple stages, from planning and research to analysis and final report generation.

---

## ✨ Key Features

- **Multi-Agent Architecture:** Six specialized AI agents collaborate to complete research tasks.
- **Automated Planning:** Creates a structured research plan based on the user's topic.
- **Web Research:** Collects relevant information using web search.
- **Data Analysis:** Processes datasets and identifies useful patterns.
- **Data Visualization:** Generates graphical representations of analytical results.
- **AI-Generated Insights:** Converts research findings into meaningful insights.
- **Quality Evaluation:** Reviews the research output and can request one research retry.
- **Automated Report Generation:** Produces a structured final research report.
- **Web Interface:** Allows users to interact with the system through a browser.
- **CSV Dataset Support:** Supports data analysis using uploaded datasets.

---

## 🧠 Six AI Agents

| Agent | Responsibility |
|---|---|
| 1. Planner Agent | Understands the user's topic and creates a research plan. |
| 2. Researcher Agent | Collects relevant information from web sources. |
| 3. Data Analyst Agent | Processes datasets and performs data analysis. |
| 4. Insight Agent | Identifies trends, patterns, and meaningful findings. |
| 5. Critic Agent | Evaluates output quality and decides whether another research round is needed. |
| 6. Report Agent | Generates the final structured research report. |

### Workflow Architecture

```text
             USER INPUT
                  |
                  v
           PLANNER AGENT
                  |
                  v
          RESEARCHER AGENT
                  |
                  v
         DATA ANALYST AGENT
                  |
                  v
            INSIGHT AGENT
                  |
                  v
            CRITIC AGENT
                  |
          Quality Evaluation
             /       \
            /         \
        Retry        Approved
          |              |
          v              v
     Researcher      REPORT AGENT
          |              |
          +--------------+
                         |
                         v
                 FINAL REPORT
```

The Critic Agent can send the workflow back for one additional research round when improvements are required.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Google Gemini API | AI-powered agent responses |
| Flask | Backend web application |
| HTML | Webpage structure |
| CSS | Website styling |
| JavaScript | Frontend interaction |
| Pandas | Data processing and analysis |
| Matplotlib | Data visualization |
| DuckDuckGo Search | Web research |
| Git & GitHub | Version control and project hosting |

---

## 📂 Project Structure

```text
Autonomous-Multi-Agent-AI/
│
├── agents/
│   ├── planner.py
│   ├── researcher.py
│   ├── data_analyst.py
│   ├── insight.py
│   ├── critic.py
│   ├── report.py
│   └── llm.py
│
├── graph/
│   └── workflow.py
│
├── models/
│   └── state.py
│
├── datasets/
│   └── ev_sales_demo.csv
│
├── website/
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       │
│       └── js/
│           └── app.js
│
├── outputs/
│
├── app.py
├── web_app.py
├── test_gemini.py
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Jeevan05-prog/Autonomous-Multi-Agent-AI.git
```

### 2. Navigate to the Project Folder

```bash
cd Autonomous-Multi-Agent-AI
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Required Libraries

```bash
pip install flask python-dotenv pandas matplotlib duckduckgo-search httpx
```

If additional dependencies are imported by the project, install those as well.

### 6. Configure Gemini API

Create a `.env` file in the root project directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key.

**Important:** Never upload your `.env` file or expose your API key on GitHub.

### 7. Run the Web Application

```bash
python web_app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## 📊 How It Works

1. Enter a research topic through the web interface.
2. The Planner Agent creates a research plan.
3. The Researcher Agent gathers relevant information.
4. The Data Analyst Agent processes available data and generates visualizations.
5. The Insight Agent identifies important findings.
6. The Critic Agent evaluates the generated results.
7. If improvements are needed, the workflow can repeat the research stage once.
8. The Report Agent prepares the final research report.

---

## 🎯 Project Objectives

- Understand multi-agent AI system architecture.
- Explore collaboration between specialized AI agents.
- Implement automated research and analysis workflows.
- Integrate Large Language Models through an API.
- Apply Python-based data analysis and visualization.
- Build an interactive AI-powered web application.
- Explore workflow orchestration, state management, and quality evaluation.

---

## 🔮 Future Enhancements

- Support additional AI models.
- Add more specialized agents.
- Improve source verification and citation handling.
- Add downloadable PDF and DOCX reports.
- Introduce persistent research history.
- Add advanced data visualization options.
- Improve agent performance evaluation.
- Support larger datasets and additional file formats.

---

## 👨‍💻 Author

**Jeevan K M**

Artificial Intelligence and Data Science Engineering Student

GitHub: [Jeevan05-prog](https://github.com/Jeevan05-prog)

### Project Repository

[Autonomous Multi-Agent AI Workflow Orchestration](https://github.com/Jeevan05-prog/Autonomous-Multi-Agent-AI)

---

## 📜 License

This project is developed for educational and learning purposes.
