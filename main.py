from fastapi import FastAPI
from routers import teams, users, prs

app = FastAPI(title="PR Reviewer Assignment Service", version="1.0.0")

app.include_router(teams.router)
app.include_router(users.router)
app.include_router(prs.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
