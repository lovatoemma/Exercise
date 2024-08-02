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
from bs4 import BeautifulSoup
import pandas as pd
import requests

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
        review_text = row.get('testo', '')
        if pd.isna(review_text) or review_text.strip() == '':
            review_text = "No comment provided"
        
        review = RestaurantReview(
            reviewer=row.get('reviewer', 'Anonymous'),
            testo=review_text,
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
    # Construct the URL for the restaurant's review page
    url = f"https://www.justeat.it/domicilio-{restaurant_name}/reviews"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        reviews_list = []
        for review_div in soup.find_all('div', class_='review-container'):
            reviewer_name = review_div.find('span', class_='reviewer-name').text.strip()
            review_text = review_div.find('p', class_='review-text').text.strip()
            rating = float(review_div.find('span', class_='review-rating').text.strip())
            
            review = RestaurantReview(
                reviewer=reviewer_name,
                testo=review_text,
                voto=rating
            )
            reviews_list.append(review)
            
        return reviews_list
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching reviews from JustEat: {e}")
        return []

# Create an endpoint for scraping
@app.get("/scrape_reviews/")
async def scrape_reviews(restaurant_name: str):
    scraped_reviews = scrape_justeat_reviews(restaurant_name)
    if not scraped_reviews:
        raise HTTPException(status_code=404, detail="No reviews found or error in scraping.")
    return scraped_reviews