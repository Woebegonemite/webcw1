from django.shortcuts import render

import json
import datetime

from django.http import HttpResponse, HttpRequest, QueryDict
from django.views.decorators.csrf import csrf_exempt

from news_agency.models import Author, NewsStory
from django.contrib.auth import authenticate, login, logout


# Logs the user into the server by validating their account details
@csrf_exempt
def user_login_in(request: HttpRequest):
    server_response = HttpResponse()

    if request.user.is_authenticated:
        server_response.status_code = 403
        server_response.content = "User is already logged in"
        return server_response

    # Checks that method is post
    if request.method != "POST":
        server_response.content = "This resource only expects POST requests with accompanying username and password"
        server_response.status_code = 405
        return server_response

    # Extracts post data
    content: QueryDict = request.POST.copy()

    # Returns username and password
    user_name = content.get(key="username", default=None)
    password = content.get(key="password", default=None)

    # Checks that user name and password were correctly extracted
    if not (user_name and password):
        server_response.content = "This resource expects valid 'username' and 'password' parameters"
        server_response.status_code = 400
        return server_response

    user_name = user_name.strip()
    password = password.strip()

    # Returns author from database with the username and password, if it does not exist then return error, else
    # Log the user in
    returned_author = authenticate(request, username=user_name, password=password)
    if returned_author is not None:
        try:
            login(request, returned_author)
        except:
            server_response.status_code = 500
            server_response.content = f"Failed to login user"
        else:
            server_response.status_code = 200
            server_response.content = f"Welcome, {returned_author.name}, you are logged in"
    else:
        server_response.status_code = 406
        server_response.content = f"Could not return user with username ({user_name}) and password ({password})"

    return server_response


# Logs the user out
@csrf_exempt
def user_log_out(request: HttpRequest):
    server_response = HttpResponse()

    # Checks that user is not already logged in
    if not request.user.is_authenticated:
        server_response.status_code = 401
        server_response.content = "User is not logged in"
        return server_response

    # Checks that method is post
    if request.method != "POST":
        server_response.content = "This resource only expects POST requests with accompanying username and password"
        server_response.status_code = 405
        return server_response

    try:
        logout(request)
    except:
        server_response.status_code = 500
        server_response.content = "Failed to log user out"
        return server_response

    server_response.content = "User successfully logged out"
    server_response.status_code = 200
    return server_response


# Lets the user post a news story
@csrf_exempt
def post_story(request: HttpRequest):

    server_response = HttpResponse()

    # Checks that user is logged in
    if not request.user.is_authenticated:
        server_response.status_code = 401
        server_response.content = "User must be logged in to add a news story"
        return server_response

    # Checks that method is post
    if request.method != "POST":
        server_response.status_code = 405
        server_response.content = "Resource only expects POST requests"
        return server_response

    user_id = request.user.id

    # Attempts to load JSON data from request
    try:
        json_data = json.loads(request.body)
    except BaseException:
        server_response.content = "This resource only expects JSON content requests"
        server_response.status_code = 400
        return server_response

    # Keys to return from JSON
    keys = ["headline", "category", "region", "details"]

    # Checks that the payload includes all correct JSON values
    for key in keys:
        if key not in json_data.keys():
            server_response.status_code = 400
            server_response.content = f"Request must include json request containing {key}"
            return server_response
        else:
            try:
                temp = str(json_data[key])
            except:
                server_response.status_code = 400
                server_response.content = f"Request must include string convertible JSON field {key}"
                return server_response

    # Extract correct JSON values
    headline = str(json_data["headline"]).strip()
    category = str(json_data["category"]).strip().lower()
    region = str(json_data["region"]).strip().lower()
    details = str(json_data["details"]).strip()

    # Checks that the category is of the correct choice
    if category not in dict(NewsStory.available_categories):
        server_response.status_code = 400
        server_response.content = f"Category: {category} is not a valid database field"
        return server_response

    # Checks that the region is of the correct choice
    if region not in dict(NewsStory.available_regions):
        server_response.status_code = 400
        server_response.content = f"Region: {region} is not a valid database field"
        return server_response

    # Checks that the headline is of the correct length
    if len(headline) > 64 or len(headline) < 1:
        server_response.status_code = 400
        server_response.content = f"Headline length cannot be larger than 64 and larger than 0"
        return server_response

    # Checks that the details is of the correct length
    if len(details) > 512 or len(details) < 1:
        server_response.status_code = 400
        server_response.content = f"Details length cannot be larger than 512 and larger than 0"
        return server_response

    # Attempts to create a news story for logged in user, if this fails then an error message is sent back
    try:
        NewsStory.objects.create(headline=headline, category=category, region=region,
                                 details=details, author_id=user_id)
    except:
        server_response.status_code = 500
        server_response.content = f"Unable to add story to database"

    # News story successfully added to database
    server_response.status_code = 201
    server_response.content = f"News story successfully added to account"

    return server_response


# Returns all stories with requested parameters
def get_story(request: HttpRequest):
    server_response = HttpResponse()

    # Checks that method is GET
    if request.method != "GET":
        server_response.status_code = 405
        server_response.content = "Resource only expects GET requests"
        return server_response

    # Converts request to UTF-8 JSON dictionary
    content = request.body

    try:
        content = content.decode("utf8")
        json_data = json.loads(content)
    except Exception:
        server_response.content = "Resource must be in UTF-8 JSON format"
        server_response.status_code = 400
        return server_response

    keys = ["story_cat", "story_region", "story_date"]

    # Checks that the payload includes all correct JSON values
    for key in keys:
        if key not in json_data.keys():
            server_response.status_code = 400
            server_response.content = f"Request must include json request containing {key}"
            return server_response
        else:
            try:
                temp = str(json_data[key])
            except:
                server_response.status_code = 400
                server_response.content = f"Request must include string convertible JSON field {key}"
                return server_response

    # Extract correct JSON values
    category = str(json_data["story_cat"]).strip()
    region = str(json_data["story_region"]).strip()
    raw_date = str(json_data["story_date"]).strip()

    if raw_date != "*":
        # Checks that date is of the correct format
        try:
            day, month, year = raw_date.split('/')
            search_date = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            server_response.content = "Resource expects valid date in form day/month/year"
            server_response.status_code = 400
            return server_response

        # Checks that the date is earlier or equal to the current date
        if search_date > datetime.datetime.now():
            server_response.content = "Search data cannot be later than the current date"
            server_response.status_code = 400
            return server_response

    # Checks that the category is of the correct choice
    if category not in dict(NewsStory.available_categories) and category != "*":
        server_response.status_code = 400
        server_response.content = f"Category: {category} is not a valid database field"
        return server_response

    # Checks that the region is of the correct choice
    if region not in dict(NewsStory.available_regions) and region != "*":
        server_response.status_code = 400
        server_response.content = f"Region: {region} is not a valid database field"
        return server_response

    # Returns all news stories in the database
    all_news_stories = NewsStory.objects.all()

    # If each of the fields is a 'return all' operator, then each set is narrowed down
    if category != "*":
        all_news_stories = all_news_stories.filter(category=category)

    if region != "*":
        all_news_stories = all_news_stories.filter(region=region)

    if raw_date != "*":
        all_news_stories = all_news_stories.filter(creation_date__gte=search_date)

    # If no news objects remain in the queryset, then an appropriate message is returned
    if len(all_news_stories) == 0:
        server_response.status_code = 404
        server_response.content = "No news stories with those search fields were returned"
        return server_response

    # Iterates through each news story and adds appropriate fields to a JSON dictionary
    stories_dict = []

    for story in all_news_stories:
        current_story = {"key": story.id, "headline": story.headline, "story_cat": story.category,
                         "story_region": story.region, "author": story.author.name,
                         "story_date": story.creation_date.strftime("%d/%m/%Y"), "story_details": story.details}

        stories_dict.append(current_story)

    response_json = {"stories": stories_dict}

    response_json = json.dumps(response_json)

    # JSON news objects are returned
    server_response.status_code = 200
    server_response.content = response_json

    return server_response


# Allows the user to delete a news story they have made
@csrf_exempt
def delete_story(request: HttpRequest):
    server_response = HttpResponse()

    # Checks that user is actually logged in
    if not request.user.is_authenticated:
        server_response.status_code = 401
        server_response.content = "User must be logged in to delete a news story"
        return server_response

    # Checks that request method is POST
    if request.method != "POST":
        server_response.status_code = 405
        server_response.content = "Resource only expects GET requests"
        return server_response

    user_id = request.user.id

    # Converts request payload to JSON, otherwise produces error message
    try:
        json_data = json.loads(request.body)
    except BaseException:
        server_response.content = "This resource only expects JSON content requests"
        server_response.status_code = 400
        return server_response

    # Checks that the story key is in the JSON payload
    if "story_key" not in json_data.keys():
        server_response.content = "Resource must accept a story key to delete"
        server_response.status_code = 400
        return server_response

    # Attempts to convert story key to integer format
    try:
        story_key = int(json_data["story_key"])
    except ValueError:
        server_response.content = "Story key must be in Integer format"
        server_response.status_code = 400
        return server_response

    # Returns news story with key, if no news story is returned then an error is returned
    try:
        news_story = NewsStory.objects.get(id=story_key)
    except:
        server_response.content = f"News Story with key {story_key} does not exist"
        server_response.status_code = 400
        return server_response

    # Checks that the news story author matches the current logged in user ID, or that the user is not a superuser
    if news_story.author_id != user_id and not request.user.is_superuser:
        server_response.content = f"Could not delete story with key {story_key}; you are not the valid owner"
        server_response.status_code = 400
        return server_response

    # Deletes the news story
    try:
        news_story.delete()
    except:
        server_response.content = f"Failed to delete story with key {story_key}"
        server_response.status_code = 500
        return server_response

    # Returns successful deletion result
    server_response.content = f"News story successfully deleted"
    server_response.status_code = 201
    return server_response
