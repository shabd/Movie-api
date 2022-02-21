# Movie-api

A Movie Api created with Django and Django-rest framework
- the application makes use of travis CI
- As well as Docker



<!-- Running the appliction  -->
- docker-compose up 


<!-- To Run tests -->
- docker-compose run app sh -c "python manage.py test"

<!-- End points -->
1. Post /movies
- A movie title must be surplied .eg
{
    "movie_title" : "godzilla"
}
- movie data recieved from api is saved to the database and returned 



2. GET /movies
- If no parms is given, it will return all movies in the application database
- `order_by=title`, or `order_by=rating` can be used as parms
- `desc=true` parameter can be given to reverse the order
- if `desc` parameter is given without the `order_by` parameter, then will return all movies without ordering

3. POST /comments
- Request body should contain imdbID of movie already present in database, and a comment text body
for example 
{ "movie_id":"tt0112573",
 "comment"="example comment"
 }
- Comment is saved and returned in request response

4. GET /comments
- Fetches  all comments in db
- By passing movie imdbID, allows filtering comments. for eg `movie_id=tt0112573` 

5. GET /top
- Returns top movies already in the database ranking based on a number of comments added to the movie
 in the specified date range. The response includes the ID of the movie(DB id), rank and total number of comments (in the specified date range)
 - Date range is specified like this example --> `start_date=2020-03-10` and `end_date=2020-03-15`.
