# remo-cli

> A smart sticky note for your terminal because your memory is garbage and you know it.

Let's be real. You clone a repo you haven't touched in 8 months. You type `npm run dev`. It crashes. You type `python manage.py runserver`. It crashes. You realize you forgot to activate the virtual environment, you're on Node 14 instead of 18, and your `.env` file is missing. You just lost 30 minutes of your life to "environment setup" again.

Enter `remo`. 

`remo` is a lightweight, zero-dependency, project-aware CLI companion. It sits in your project root, silently judging you until you type `remo`. Then it slaps you with the exact startup checklist, environment warnings, and shortcuts you need to actually write code instead of fighting your terminal.

## What does it actually do?

1. **The Startup Checklist:** Tells you exactly what to run so you don't have to scroll through an outdated `README.md` trying to figure out how to boot the frontend.
2. **Environment Checks:** Validates your `.env` variables and checks your tool versions (like Python or Node) *before* you run anything, preventing cryptic stack traces.
3. **Task Reminders:** Set a one-off timer to remind you to check on a deployment, or leave a breadcrumb for your future self before you log off on Friday ("Fix the auth bug next") so you aren't completely lost on Monday morning.
4. **Project Shortcuts:** `remo run test` is way faster to type out than `pytest tests/ --cov=app -v`.

---

## Installation

Use `pipx` (highly recommended so it installs globally without polluting your system Python):
```bash
pipx install remo-cli
```
*Or just `pip install remo-cli` if you like living dangerously.*

Verify it didn't break:
```bash
remo --version
```

---

## How to use this thing

### 1. Initialize a Project
Navigate to your messy codebase and run:
```bash
remo init
```
Follow the interactive wizard. It will create a `.remo` file (commit this to git so your teammates stop asking you how to run the app) and a `.remo.local` file (for your private, local settings. We put this in your `.gitignore`).

### 2. Open a Project Session
Just type `remo` in your terminal.
```bash
remo
```
You'll instantly see your project's checklist, available shortcuts, and whether your environment passes the basic checks you configured.

### 3. Run a Shortcut
Instead of typing out massive Docker or Pytest commands, define them in your `.remo` file's `"shortcuts"` block and just run:
```bash
remo run dev
```

### 4. Leave a Breadcrumb
Quitting for the day? Leave a note for yourself:
```bash
remo log "I think the memory leak is in the Redis worker. Don't forget to check it."
```
Next time you type `remo`, it will be sitting right there waiting for you.

### 5. Set a Reminder
Kick off a long deployment or build script, and tell `remo` to yell at you when it's done so you can go browse Reddit in peace:
```bash
remo remind 10m "Check if the build failed again"
```
*(On Windows, this uses native PowerShell toasts so it actually works, unlike 90% of Python notification libraries).*

---

## Configuration

`remo` is completely driven by a simple JSON file. Put this `.remo` file in your project root:

```json
{
    "project": "My Over-Engineered SaaS",
    "startup": [
        "source .venv/bin/activate",
        "remo run dev"
    ],
    "reminders": [
        { "after": "60m", "message": "Drink water & stretch your goblin spine" }
    ],
    "checks": [
        { "type": "env", "file": ".env.example" },
        { "type": "version", "tool": "node", "min": "18.0" }
    ],
    "shortcuts": {
        "dev": "npm run dev",
        "test": "pytest tests/ -v"
    }
}
```

If you want to add personal shortcuts or local reminders without annoying your team, just put them in a `.remo.local` file instead. `remo` merges them automatically.

## License

MIT License. Do whatever you want with it, just don't blame me if you still forget how to start your own projects.
