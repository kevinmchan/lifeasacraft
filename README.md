# lifeasacraft

Our mission: Learn how to learn, to learn how to live a more intentional life.

## Roadmap

Current feature: Creating a chat client to log conversations locally

Backlog:
- Building collaborative conversations as a graph
- Logging actions
- Logging goals
- Logging measures
- Hosting app on web
- Enabling notifications (push or text)
- Using an event loop and observations to give LLM agents increased agency / influence
- LLM alarm clock

## Development log

### Frontend

The frontend is built using Vue.

1. Initialize vue project.
```bash
npm create vue@latest  # create project named frontend
cd frontend
npm install
npm run format
npm run dev
```

2. Remove boilerplate template files.

3. 

### Backend

The backend is built using fastapi.

1. Initialize project using uv.
```bash
uv init backend
uv add fastapi --extra standard
uv add openapi
```

