from django.shortcuts import render, redirect
import requests
import json
from django.urls import reverse
from .headers import all_headers

main_url = "https://imdb8.p.rapidapi.com/v2/search"
details_url = "https://imdb8.p.rapidapi.com/title/get-overview-details"
genres_url = "https://imdb8.p.rapidapi.com/title/v2/get-genres"
cast_url = "https://imdb8.p.rapidapi.com/title/v2/get-top-cast-and-crew"
popular_url = "https://imdb8.p.rapidapi.com/title/v2/get-popular"
videos_url = "https://imdb8.p.rapidapi.com/title/get-videos"

# for headers look in base/headers.py

def Home(request):
    popular_movies = []

    popular_querystring = {"first":"27","country":"US","language":"en-US"}
    
    for header in all_headers:
        popular_response = requests.get(popular_url, headers=header, params=popular_querystring) 
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
            break
    
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
    
    for header in all_headers:
        main_response = requests.get(main_url, headers=header, params=main_querystring) 
        if main_response.status_code == 200:
            now_headers = header
            break

    if main_response.status_code == 200:
        main_data = main_response.json()
        movie_id = main_data["data"]["mainSearch"]["edges"][0]["node"]["entity"]["id"]
    else:
        print(main_response.status_code)

    details_querystring = {"tconst": movie_id}
    
    details_response = requests.get(details_url, headers=now_headers, params=details_querystring)
    genres_response = requests.get(genres_url, headers=now_headers, params=details_querystring)
    cast_response = requests.get(cast_url, headers=now_headers, params=details_querystring)
    videos_response = requests.get(videos_url, headers=now_headers, params=details_querystring)

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

    if videos_response.status_code == 200:
        data = videos_response.json()
        image = data["resource"]["videos"][0]["image"]
        if image["width"] > 1900:
            movie["image"] = image["url"]

    context = {
        "movie": movie
    }
    
    return render(request, 'base/movie.html', context)