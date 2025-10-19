# Chat‑SQL

Chat with your SQL databases using an LLM-powered Streamlit app. Point it at a local SQLite database (included) or connect to your own MySQL instance, then ask questions in natural language.

## Features
- Chat UI built with Streamlit
- SQLite demo database (`student.db`) ready to use
- Optional MySQL connection (host/user/password/db)
- Uses LangChain with Groq Llama 3 for SQL agent reasoning
- Caches DB configuration for faster reloads

## Demo database
This repo includes a `student.db` SQLite database prepopulated with a `STUDENT` table (NAME, CLASS, SECTION, MARKS) for quick testing. You can also create your own database.

## Quickstart

### Prerequisites
- Python 3.10+
- A Groq API key

### Install

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Then in the app sidebar:
- Enter your Groq API key
- Choose one:
  - "Use SQLLite 3 Database- Student.db" to use the bundled SQLite DB (read‑only)
  - "Connect to your MySQL Database" and provide host/user/password/db

Ask questions like:
- "Show top 3 students by MARKS"
- "Average MARKS per CLASS"

## Configuration notes
- The SQLite database is opened read‑only. To modify data, connect to MySQL or replace `student.db` and adjust the code accordingly.
- The LLM is configured via `ChatGroq` with `model_name="Llama3-8b-8192"`. Set your key in the sidebar each run.

## Project structure

```text
app.py          # Streamlit app (UI, agent, DB selection)
sqlite.py       # Helper to create a sample SQLite DB (not required at runtime)
student.db      # Sample SQLite DB used by default
requirements.txt
tests/          # Test files
  test_db_connectivity.py  # Database connectivity tests
.github/        # GitHub Actions and issue templates
  workflows/test.yml       # CI workflow (example)
  ISSUE_TEMPLATE/          # Issue templates
```

## Development

### Create/refresh the sample SQLite database (optional)
Running `sqlite.py` will recreate and populate the `STUDENT` table:

```bash
python sqlite.py
```

### Linting & formatting
This project does not enforce a specific linter yet. Contributors may use `ruff`/`black` locally if preferred.

### Testing
Basic database connectivity tests are available using pytest:

```bash
pip install pytest
pytest tests/ -v
```

The tests verify:
- SQLite database file exists
- Database connection works
- STUDENT table exists with correct structure
- Table contains sample data

See `.github/ISSUE_TEMPLATE/add-ci-pipeline.md` for adding CI/CD automation.

## Contributing
We welcome contributions! Please read CONTRIBUTING.md for guidelines, local setup, and the pull request process.

## Security
If you discover a security issue, please follow the instructions in SECURITY.md rather than opening a public issue.

## License
This project is licensed under the MIT License. See LICENSE for details.

## Acknowledgements
- Streamlit
- LangChain
- Groq Llama 3 models
