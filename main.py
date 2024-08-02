# main.py

# PRACTICAL EXERCISE
# Set up a FastAPI web service centred on Pydantic validation. 
# For those looking to go the extra mile, 
# incorporate data scraping to fetch reviews from JustEat. 
# Take the Excel file as the data source.

# Libraries
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import pandas as pd
import requests
from bs4 import BeautifulSoup

# FastAPI Setup
app = FastAPI()

# Define the Pydantic model
class RestaurantReview(BaseModel):
    reviewer: str
    testo: str = Field(..., max_length=500, description="Review text must not exceed 500 characters.")
    sentiment: Optional[float] = None
    voto: float = Field(..., ge=0, le=5, description="Rating must be between 0 and 5.")

    @validator('voto')
    def validate_voto(cls, value):
        if value < 0 or value > 5:
            raise ValueError('Rating must be between 0 and 5.')
        return value

# Load existing reviews
file_path = 'C:/Users/emmal/Desktop/CALTON/example (1) (1).xlsx'
df = pd.read_excel(file_path)

reviews = []
for _, row in df.iterrows():
    try:
        review = RestaurantReview(
            reviewer=row.get('reviewer', 'Anonymous'),
            testo=row.get('testo', ''),
            voto=row.get('voto', 0)
        )
        reviews.append(review)
    except Exception as e:
        print(f"Error adding review from row: {row} -> {e}")

# API endpoints
# An endpoint to input a review based on the `RestaurantReview` schema.
@app.post("/add_review/", response_model=RestaurantReview)
async def add_review(review: RestaurantReview):
    reviews.append(review)
    return review

# An endpoint to retrieve all stored reviews.
@app.get("/reviews/", response_model=List[RestaurantReview])
async def fetch_reviews():
    return reviews

# Bonus (Optional):
# Scrape JustEat reviews
def scrape_justeat_reviews(restaurant_name: str):
    # Placeholder URL; 
    url = f"https://www.just-eat.co.uk/restaurants-{restaurant_name}/reviews"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    soup = BeautifulSoup(response.content, 'html.parser')
    review_elements = soup.find_all('div', class_='review-text')

    scraped_reviews = []
    for element in review_elements:
        comment = element.get_text(strip=True)
        scraped_reviews.append({
            "reviewer": "Scraped User",
            "testo": comment,
            "voto": 5,  # Example: default rating
            "sentiment": None
        })
    
    return scraped_reviews

@app.get("/scrape_reviews/{restaurant_name}", response_model=List[RestaurantReview])
async def scrape_reviews(restaurant_name: str):
    try:
        scraped_reviews = scrape_justeat_reviews(restaurant_name)
        reviews.extend([RestaurantReview(**rev) for rev in scraped_reviews])
        return scraped_reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))