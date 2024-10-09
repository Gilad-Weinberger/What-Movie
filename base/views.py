from django.shortcuts import render, redirect
import requests
import json
from django.urls import reverse

main_url = "https://imdb8.p.rapidapi.com/v2/search"
details_url = "https://imdb8.p.rapidapi.com/title/get-overview-details"
genres_url = "https://imdb8.p.rapidapi.com/title/v2/get-genres"
cast_url = "https://imdb8.p.rapidapi.com/title/v2/get-top-cast-and-crew"
popular_url = "https://imdb8.p.rapidapi.com/title/v2/get-popular"

# 21 headers:
# headers = {
#     "x-rapidapi-key": "9ddb0ab3fdmshd38e2a337759cc3p1af9b8jsnde847bad7fa1",
#     "x-rapidapi-host": "imdb8.p.rapidapi.com"
# }

# 321 headers:
headers = {
	"x-rapidapi-key": "51cc4ca6d6msh5996fc999faf8b9p173fe6jsn1f15abc92647",
	"x-rapidapi-host": "imdb8.p.rapidapi.com"
}

def Home(request):
    popular_movies = []

    popular_querystring = {"first":"27","country":"US","language":"en-US"}
    popular_response = requests.get(popular_url, headers=headers, params=popular_querystring) 
   
    if popular_response.status_code == 200:
        data = popular_response.json()
        movies = data['data']['movies']['edges']
        for movie in movies[:27]:
            movie_info = movie['node']
            movie_dict = {
                'id': movie_info['id'],
                'name': movie_info['titleText']['text'],
                'image': movie_info['primaryImage']['url'] if movie_info['primaryImage'] else None
            }
            popular_movies.append(movie_dict)
    
    if request.method == 'POST':
        movie_name_search = request.POST.get('movie_name_search', '').strip()
        print(movie_name_search)
        if movie_name_search:
            return redirect(reverse('movie', args=[movie_name_search]))

    context = {
        'movies': popular_movies
    }

    return render(request, 'base/home.html', context)

def Movie(request, movie_name):
    main_querystring = {"searchTerm": movie_name,"type":"title","first":"1"}
    main_response = requests.get(main_url, headers=headers, params=main_querystring) 

    if main_response.status_code == 200:
        main_data = main_response.json()
        movie_id = main_data["data"]["mainSearch"]["edges"][0]["node"]["entity"]["id"]
    
    details_querystring = {"tconst": movie_id}
    
    details_response = requests.get(details_url, headers=headers, params=details_querystring)
    genres_response = requests.get(genres_url, headers=headers, params=details_querystring)
    cast_response = requests.get(cast_url, headers=headers, params=details_querystring)

    movie = {}
    
    if details_response.status_code == 200:
        data = details_response.json()
        
        if data["title"]["runningTimeInMinutes"]:
            total_minutes = data["title"]["runningTimeInMinutes"]
        else:
            total_minutes = data["title"]["runtime"]["seconds"]
        hours, minutes = divmod(total_minutes, 60)
        
        movie.update({
            "name": data["title"]["title"],
            "image": data["title"]["image"]["url"],
            "rating": data["ratings"]["rating"],
            "description": data["plotOutline"]["text"],
            "duration": {
                "hours": hours,
                "minutes": minutes,
                "total_minutes": total_minutes
            },
            "year_released": data["title"]["year"]
        })
    
    if genres_response.status_code == 200:
        data = genres_response.json()
        genres = [genre["genre"]["text"] for genre in data["data"]["title"]["titleGenres"]["genres"]]
        movie["genres"] = genres

    if cast_response.status_code == 200:
        data = cast_response.json()
        top_characters = []
        for credit in data["data"]["title"]["principalCredits"][2]["credits"][:3]:
            if credit["__typename"] == "Cast":
                character = {
                    "actor_name": credit["name"]["nameText"]["text"],
                    "character_name": credit["characters"][0]["name"],
                    "image": credit["name"]["primaryImage"]["url"] if credit["name"]["primaryImage"] else None
                }
                top_characters.append(character)
        movie["top_characters"] = top_characters

    context = {
        "movie": movie
    }
    
    return render(request, 'base/movie.html', context)