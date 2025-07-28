import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api.api:app", reload=True)
    # reload=True -> auto-reloads server if a code is changed