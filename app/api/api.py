from fastapi import FastAPI
from app.database.database import get_championship_probabilities

app = FastAPI()

@app.get('/probabilities')
def get_probabilities(season: str = '2025-26'):
    results = get_championship_probabilities(season)
    http://localhost:8000/probabilities
    # convert to dictionary with percentages
    total = sum(count for _, count in results)
    probabilities = {}
    for champion, count in results:
        probabilities[champion] = round(count / total * 100, 1)
    
    return probabilities