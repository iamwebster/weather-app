from django.shortcuts import render
import requests
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()
API_KEY = os.getenv("API_KEY")


def index(request):
    if request.method == "POST":
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}&units=metric"
        weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"
        city = request.POST["city"]
        try:
            today = get_today_weather(weather_url, city, API_KEY)
            forecast = get_forecast(forecast_url, city, API_KEY)
            hourly = get_hourly_forecast(forecast_url, city, API_KEY)
            context = {"today": today, "forecast": forecast, "hourly": hourly}
        except KeyError:
            context = {"message": "City not found!"}
    else:
        context = {}

    return render(request, "weather_page.html", context=context)


def get_today_weather(url: str, city: str, api_key: str) -> dict:
    get_weather_url = url.format(city, api_key)
    weather_data_json = requests.get(get_weather_url).json()
    weather_dict = {}
    weather_dict["city"] = weather_data_json["name"]
    weather_dict["country"] = weather_data_json["sys"]["country"]
    weather_dict["temp"] = round(weather_data_json["main"]["temp"], 1)
    weather_dict["feels_like"] = round(weather_data_json["main"]["feels_like"], 1)
    weather_dict['wind'] = weather_data_json['wind']['speed']
    weather_dict['pressure'] = weather_data_json['main']['pressure']
    weather_dict['humidity'] = weather_data_json['main']['humidity']
    weather_dict["desc"] = weather_data_json["weather"][0]["description"]
    weather_dict["icon"] = weather_data_json["weather"][0]["icon"]

    return weather_dict


def get_hourly_forecast(url: str, city: str, api_key: str) -> list:
    get_hourly_url = url.format(city, api_key)
    hourly_data_json = requests.get(get_hourly_url).json()

    hourly_data = []
    for hour in hourly_data_json["list"][1:6]:
        hourly_dict = {}
        hourly_time = datetime.strptime(hour["dt_txt"].split()[1], "%H:%M:%S")
        hourly_dict["time"] = hourly_time.strftime("%H:%M")
        hourly_dict["temp"] = round(hour["main"]["temp"])
        hourly_dict["desc"] = hour["weather"][0]["description"]
        hourly_dict["icon"] = hour["weather"][0]["icon"]
        hourly_data.append(hourly_dict)

    return hourly_data


def get_forecast(url: str, city: str, api_key: str) -> list:
    get_forecast_url = url.format(city, api_key)
    forecast_data_json = requests.get(get_forecast_url).json()

    forecast_data = []
    for forecast in forecast_data_json["list"]:
        if forecast["dt_txt"].split()[1] == "15:00:00":
            forecast_dict = {}
            date = datetime.strptime(forecast["dt_txt"].split()[0], "%Y-%m-%d")
            forecast_dict["day"] = date.strftime("%a")
            forecast_dict["temp"] = round(forecast["main"]["temp"])
            forecast_dict["desc"] = forecast["weather"][0]["description"]
            forecast_dict["icon"] = forecast["weather"][0]["icon"]
            forecast_data.append(forecast_dict)

    return forecast_data
