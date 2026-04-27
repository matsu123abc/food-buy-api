from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "food-buy-api is running"}
