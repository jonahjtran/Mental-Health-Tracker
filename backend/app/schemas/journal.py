from backend.app.db import models

def verify_mood(rating : int): 
    if (rating < 0 or rating > 5):
        return "Error: invalid mood rating"
    