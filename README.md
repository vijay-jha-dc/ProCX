# 🧠 ProCX — Empathic AI Customer Experience System

Welcome to **ProCX**, an AI-driven customer experience system powered by **LangGraph** and **LangChain**.  
This guide will help every team member set up their local development environment smoothly on **Windows (bash)** and start building intelligent customer experience agents.

---

## 🚀 Tech Stack

| Layer | Tech Used |
|-------|------------|
| **Core Framework** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLM Integration** | [LangChain](https://github.com/langchain-ai/langchain) |
| **Language Models** | OpenAI (default), Anthropic (optional) |
| **Data Handling** | Pandas, NumPy, Scikit-learn |
| **Environment** | Python 3.10+ |
| **IDE** | Visual Studio Code |

---

## ⚙️ Setup Guide (Windows + Bash)

> 💡 Make sure you already have:
> - **Python 3.10+**
> - **Git**
> - **VS Code** (with the **Python extension**)

---

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<your-username>/ProCX.git
cd ProCX
```

### 2️⃣ Create a virtual environment
```bash
python -m venv .venv
```

### 3️⃣ Activate the virtual environment
```bash
source .venv/Scripts/activate
```
✅ You'll know it's activated when your terminal shows:
```
(.venv) user@DESKTOP MINGW64 ~/ProCX (main)
```

### 4️⃣ Upgrade pip and install dependencies
```bash
python -m pip install --upgrade pip setuptools wheel
```
Now install the required packages:
```bash
pip install -r requirements.txt
```
These include:
- `langgraph` → for building agentic workflows
- `langchain` → for LLM orchestration
- `openai` → for LLM calls
- `pandas/numpy/sklearn` → for dataset handling & analytics
- `python-dotenv` → to load environment variables

### 5️⃣ Create a .env file for secrets
```bash
touch .env
```
Add your keys (each member adds their own):
```ini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
LANGCHAIN_API_KEY=xxxxxxxxxxxxxxxxxxxx
```
⚠️ **Never push .env to GitHub!**



### 6️⃣ Create a .gitignore
```bash
touch .gitignore
```
Add this content:
```
.venv/
__pycache__/
.env
```

### 7️⃣ Commit and push
```bash
git add .
git commit -m "Initial project setup with venv and dependencies"
git push origin main
```

---

## 🧩 Folder Structure
```
ProCX/
├─ .venv/
├─ .env
├─ data/
│  ├─ raw/
│  └─ processed/
├─ src/
│  ├─ agents/
│  │  ├─ order_agent.py
│  │  ├─ empathy_agent.py
│  ├─ workflows/
│  ├─ pipelines/
│  └─ app.py
├─ tests/
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 🧠 Running LangGraph

Once dependencies are installed and your `.env` is set:

### 1️⃣ Start LangGraph Dev Server
```bash
langgraph dev
```
This runs your local agent graph service. You can test your agents, call endpoints, and integrate with LangGraph Studio if desired.

### 2️⃣ (Optional) Debug with VS Code
Add a `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to LangGraph Dev",
      "type": "python",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5678 },
      "pathMappings": [
        { "localRoot": "${workspaceFolder}", "remoteRoot": "${workspaceFolder}" }
      ]
    }
  ]
}
```
Then run LangGraph in debug mode:
```bash
langgraph dev --debug-port 5678
```

---

## 💡 Common Commands

| Task | Command |
|------|---------|
| Activate venv | `source .venv/Scripts/activate` |
| Deactivate venv | `deactivate` |
| Install deps | `pip install -r requirements.txt` |
| Update deps | `pip install -U -r requirements.txt` |
| Start LangGraph | `langgraph dev` |
| Debug LangGraph | `langgraph dev --debug-port 5678` |
| Freeze deps | `pip freeze > requirements.txt` |

---

## 🧑‍💻 Development Tips

- Always activate the venv before running Python commands.
- Use VS Code's interpreter selector → choose `.venv`.
- Keep your `.env` local and private.
- If you switch branches or pull new code, re-run:
  ```bash
  pip install -r requirements.txt
  ```
- Add docstrings and small comments — they help with agent logic clarity.
- For any permission errors in PowerShell, run:
  ```bash
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

---

## 🔮 Next Steps

1. Implement your first LangGraph Agent (e.g., Order Event Agent).
2. Store datasets in `/data/raw` and processed versions in `/data/processed`.
3. Add utility functions and workflows in `/src/agents` and `/src/workflows`.
4. Run:
   ```bash
   langgraph dev
   ```
   to test and visualize your agents.

---

## 🤝 Contribution Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/<your-feature-name>
   ```
2. Commit changes:
   ```bash
   git add .
   git commit -m "Add <feature-name>"
   ```
3. Push and open a Pull Request:
   ```bash
   git push origin feature/<your-feature-name>
   ```

---

## ❤️ Made with Empathy by Team ProCX

Building intelligent, human-centered support experiences powered by AI.
