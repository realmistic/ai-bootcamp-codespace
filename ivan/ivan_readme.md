# Ivan's Fork Setup and Management Guide

## ⚙️ My Fork Details

**Original repo:** https://github.com/alexeygrigorev/ai-bootcamp-codespace
**My fork:** https://github.com/realmistic/ai-bootcamp-codespace

## 🪜 Step-by-step setup (local + remote)

### 1. Clone your fork (your copy)
```bash
git clone https://github.com/realmistic/ai-bootcamp-codespace.git
cd ai-bootcamp-codespace
```

### 2. Add the original repo as an "upstream" remote
```bash
git remote add upstream https://github.com/alexeygrigorev/ai-bootcamp-codespace.git
```
This lets you pull in updates from the original project later.

### 3. Verify your remotes
```bash
git remote -v
```
You should see something like:
```
origin    https://github.com/realmistic/ai-bootcamp-codespace.git (fetch)
origin    https://github.com/realmistic/ai-bootcamp-codespace.git (push)
upstream  https://github.com/alexeygrigorev/ai-bootcamp-codespace.git (fetch)
upstream  https://github.com/alexeygrigorev/ai-bootcamp-codespace.git (push)
```

## 📦 Project Dependencies Setup

### Install all dependencies
This project uses [uv](https://github.com/astral-sh/uv) for fast Python dependency management. All dependencies are defined in `pyproject.toml`.

```bash
uv sync
```

This command will:
- Create a virtual environment (`.venv`) if it doesn't exist
- Install all required dependencies including:
  - `elasticsearch` - Search and analytics engine
  - `jupyter` - Interactive computing environment
  - `minsearch` - Minimal search functionality
  - `openai-agents` - AI agent framework
  - `qdrant-client` - Vector database client
  - `sentence-transformers` - Text embeddings
  - `toyaikit` - AI toolkit
  - `youtube-transcript-api` - YouTube transcript extraction
  - And many more supporting packages

### Activate the virtual environment
```bash
source .venv/bin/activate
```

### Verify installation
You can verify the installation by checking if key packages are available:
```bash
python -c "import openai, qdrant_client, sentence_transformers, elasticsearch, jupyter, minsearch; print('All key dependencies verified successfully')"
```

### Run Jupyter notebooks
To work with the course notebooks, you can use `uv run` to automatically use the correct environment:

```bash
# Start Jupyter Lab (recommended) - uv handles the environment
uv run jupyter lab

# Or use classic Jupyter Notebook interface
uv run jupyter notebook
```

**What happens:**
- Jupyter Lab will start on `http://localhost:8888`
- A browser window should open automatically with the interface
- If not, copy the URL with the token from the terminal output
- Your environment variables (like `OPENAI_API_KEY`) are automatically available thanks to direnv

**To stop the server:**
- Press `Ctrl+C` in the terminal

### Managing Jupyter Servers

**List running Jupyter servers:**
```bash
jupyter server list
```

**Stop a specific server by port:**
```bash
jupyter server stop 8888
```

**Kill all Jupyter processes:**
```bash
pkill -f jupyter
```

**Force kill servers on a specific port:**
```bash
lsof -ti:8888 | xargs kill -9
```

**Clean up stale Jupyter runtime files (if servers show as running but aren't):**
```bash
# On macOS
find ~/Library/Jupyter/runtime -name "*.json" -delete

# On Linux
rm -rf ~/.local/share/jupyter/runtime/*.json
```

**Verify all servers are stopped:**
```bash
jupyter server list
# Should show: "Currently running servers:"
```

## 🔑 Environment Variables

This project uses [direnv](https://direnv.net/) to manage environment variables securely.

### Setup
Environment variables (like API keys) are stored in `.envrc` file in the project root:
```bash
export OPENAI_API_KEY='your-key-here'
```

The `.envrc` file is already in `.gitignore` to prevent accidentally committing secrets.

### How it works
- When you `cd` into the project directory, direnv automatically loads environment variables from `.envrc`
- When you leave the directory, the variables are automatically unloaded
- direnv is already configured in your shell (`.zshrc`)

### First-time setup
If you haven't already:
1. Install direnv: `brew install direnv`
2. Add to your shell config (`.zshrc`): `eval "$(direnv hook zsh)"`
3. Allow direnv in this project: `direnv allow .`

You should see this message when entering the project directory:
```
direnv: loading ~/Documents/ai-bootcamp-codespace/.envrc
direnv: export +OPENAI_API_KEY
```

### 4. Keep your fork updated
Periodically, get new commits from the original repo:
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

Or, to rebase (a cleaner history):
```bash
git fetch upstream
git rebase upstream/main
```

### 5. Work on your own extensions
Create branches, commit, push — everything goes to your fork:
```bash
git checkout -b my-feature
# ...edit files...
git commit -am "Add my extension"
git push origin my-feature
```

✅ The original repo remains untouched.

## Visual Diagram

```
 ┌───────────────────────────────┐
 │     Original Repository       │
 │   github.com/original/project │
 └──────────────┬────────────────┘
                │  (you fork)
                ▼
 ┌───────────────────────────────┐
 │          Your Fork            │
 │   github.com/realmistic/      │
 │   ai-bootcamp-codespace       │
 └──────────────┬────────────────┘
                │  (you clone)
                ▼
 ┌───────────────────────────────┐
 │       Your Local Repo         │
 │   (on your computer)          │
 └───────────────────────────────┘

 Remotes in your local repo:

   origin   →  your fork (your GitHub copy)
   upstream →  original repo (someone else's)
```

## Sync Flow Summary

```
   ┌─────────────┐          ┌─────────────┐
   │  upstream   │◄─────────┤  your local │
   │ (original)  │          │   repo      │
   └──────┬──────┘          └──────┬──────┘
          │                         │
          │ git fetch/merge         │ git push
          ▼                         ▼
   ┌─────────────┐          ┌─────────────┐
   │   updates   │          │   your fork │
   │ (original)  │          │ (your copy) │
   └─────────────┘          └─────────────┘
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Clone your fork | `git clone https://github.com/realmistic/ai-bootcamp-codespace.git` |
| Add original as upstream | `git remote add upstream <original-url>` |
| Check remotes | `git remote -v` |
| Pull updates from original | `git fetch upstream && git merge upstream/main` |
| Push your work | `git push origin <branch-name>` |

## 💡 Bonus: Contributing Back

If you ever want to contribute back:
- You can open a Pull Request (PR) from your fork to the original repo.
- If you don't want to — no problem, your fork can remain independent forever.

---

**TL;DR:**
- You pull new changes down from upstream (the original repo).
- You push your own commits up to origin (your fork).
- The two can stay connected, but independent.
