# Practical Exercise, Emma Lovato
Set up a FastAPI web service centred on Pydantic validation. For those looking to go the extra mile, incorporate data scraping to fetch reviews from JustEat. Take the Excel file as the data source.

## 1. Set Up FastAPI
First, I create a FastAPI application structure, which will serve as the "backbone" of my web service.

## 2. Create a Pydantic Model
I create a model called RestaurantReview that describes what a review should look like, making sure the data is correct, like checking that ratings are within a certain range and comments aren't too long.

STEP:
1. Define a RestaurantReview Pydantic model with fields for reviewer, text, sentiment, and vote.
2. Implement validation to ensure voto (rating) is between 0 and 5, and testo (review text) isn't too long.

## 3. Load Existing Reviews from Excel
Loading and examining the Excel file to see what data it contains. 

## 4. Create API Endpoints
- Add Review Endpoint: Accepts a review and saves it.
This part of my application will let people add a new restaurant review. 
They’ll need to follow the structure I set in the RestaurantReview model.
- Fetch Reviews Endpoint: Returns all stored reviews.
This will allow people to see all the reviews that have been added so far.

## Bonus: Scrape Reviews from JustEat
I try to set up an endpoint that can fetch reviews from the JustEat website when you give it a restaurant name.

## 5. Access the API:
Open your browser and go to http://localhost:8000/docs to view the API documentation and test the endpoints.
