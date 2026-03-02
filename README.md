# Compass AI

## Product Vision

**Compass AI** is a conversational web agent that helps UC Davis students make informed decisions about professor selection during course planning. Students can chat to discover, compare, and get personalized recommendations for professors based on Rate My Professor data.

## CLI (local)

This repo also includes a simple CLI agent (LangChain + OpenAI) that queries the Supabase database and uses fuzzy matching for professor / department / course names.

### Setup

1. Install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file in the repo root with:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY` (or `SUPABASE_SERVICE_KEY` / `SUPABASE_KEY`)
- `OPENAI_API_KEY`
- Optional: `OPENAI_MODEL` (defaults to `gpt-4.1-mini`)

### Run

Interactive mode:

```bash
python -m compass_cli.cli
```

Single question:

```bash
python -m compass_cli.cli --once "Who's the best professor for ECS 36C?"
```

### Example Requests

The following is a list of example requests that Compass can handle:

- "Who's the best professor for ECS 36C?"
- "I need to take a computer science elective, who should I take it with?"
- "Compare Professor Johnson and Professor Martinez for ECS 50"
- "I want an easy A for my GE requirement"
- "Who are the top-rated biology professors?"
- "I learn best from professors who use lots of real-world examples"
- "Which math professor has the lightest workload?"
- "Tell me about Professor Sarah Chen"
- "I want a challenging upper-division course, who should I look for?"
- "Are there any really engaging lecturers in the psychology department?"
- "Who teaches MAT 21A and how are they rated?"
- "I need a professor who's good at explaining complex topics clearly"

## Branching strategy

1. Create an issue describing what you are gonna do (if I haven't already).
2. Create a new branch called `name/brief-description-[ISSUE#]`.
   - Example: `sohan/define-end-product-13`
3. Make your changes with detailed commit messages
4. Create a PR with a descriptive title and description
5. Apply and respond to feedback
