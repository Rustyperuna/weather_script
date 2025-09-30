# -*- coding: utf-8 -*-
# Copyright (c) 2025 Tony Lindholm
# Licensed under the MIT License. See LICENSE file for details.

"""
Script for getting daily weather data for a given location.

DISCLAIMER: Some bugs might exist.

NOTE: 27.9.2025
    - Requires python v3.12 or lower. Geopy doesn't support v3.13 yet.
    - Python v3.12.9 was used for this program.
"""

import sys
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime as dt
#from pprint import pprint   # Used to make JSON data readable in console.

 
BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_DAYS = 3


def weather_data(location="", days=DEFAULT_DAYS):
    """
    Fetch weather data for a given location and forecast period.
    
    Makes a GET request to the Open-Meteo API and passes the result to
    "create_table()" for formatting and printing.

    Args:
        location (str): Name of the requested location.
        days (int): Number of days (1-7). If out of range, defaults to 3.

    Returns:
        None
    """

    locate = Nominatim(user_agent="get_weather_script")
    get_location = locate.geocode(location).raw

    params = {
        "latitude": get_location["lat"],
        "longitude": get_location["lon"],
        "daily": [
            "temperature_2m_max", 
            "temperature_2m_min", 
            "apparent_temperature_max",
            "apparent_temperature_min",
            "sunrise", 
            "sunset",
            "rain_sum"
        ],
        "timezone": "auto",
        "forecast_days": days,
        "temperature_unit": "celsius"   # Use "fahrenheit" for freedom-units.
    }

    responses = requests.get(BASE_URL, params=params)
    data = responses.json()

    if data:
        create_table(location, days, data)
    else:
        print("No data from query.")


def how_to_message():
    """
    Display how-to instructions for running the script.
    
    Returns:
        None
    """

    print(
        "<" + 20 * "-" + "> USAGE <" + 20 * "-" + ">\n" \
        "Accepts 2 parameters:\n" \
        "<location (str)> [required] : Target location to get weather forecast for.\n" \
        "<days (int)> [optional] : Weather forecast for 1-7 days. Default: 3.\n\n" \
        "If an argument contains spaces, it should be enclosed in quotes.\n" \
        'Example usage: Kotka 5 | "New York" 5' \
    )


def create_table(location, days, data):
    """
    Create a dataframe from request data passed from weather_data(). 
    
    Args:
        location (str): Name of the location used in the query.
        days (int): Number of days displayed in the table.
        data (dict): API response containing daily weather data.
    
    Side Effects:
        - Creates a pandas DataFrame.
        - Prints the formatted forecast table to the console.

    Returns:
        None
    """

    # Daily weather data.
    daily = data["daily"]

    # Separate daily data lists to variables. 
    day = daily["time"]
    daily_temp_max = daily["temperature_2m_max"]
    daily_temp_min = daily["temperature_2m_min"]
    daily_apparent_temp_max = daily["apparent_temperature_max"]
    daily_apparent_temp_min = daily["apparent_temperature_min"]
    daily_sunrise = daily["sunrise"]
    daily_sunset = daily["sunset"]
    daily_rain = daily["rain_sum"]

    # Format date and time data to dd.mm.yy and hh:mm format.
    day = [dt.fromisoformat(d).strftime("%d.%m.%Y") for d in day]
    daily_sunrise = [dt.fromisoformat(dsr).strftime("%H:%M") for dsr in daily_sunrise]
    daily_sunset = [dt.fromisoformat(dss).strftime("%H:%M") for dss in daily_sunset]

    # Create rows from list data.
    rows = zip(
        day,
        daily_temp_max,
        daily_temp_min,
        daily_apparent_temp_max,
        daily_apparent_temp_min,
        daily_sunrise,
        daily_sunset,
        daily_rain
    )
    
    # Create complete dataframe with custom column names.
    df = pd.DataFrame(rows, columns=[
        "Day",
        "Highest °C",
        "Lowest °C",
        "Apparent (Max, °C)",
        "Apparent (Min, °C)",
        "Sunrise",
        "Sunset",
        "Rain (mm)"
    ])

    plural = "s" if days > 1 else ""

    print(f"Weather forecast for {days} day{plural} in {location.capitalize()} " \
          f"[Latitude: {data['latitude']}, Longitude: {data['longitude']}]")
    print()
    print(df)


def error_handler(user_args):
    """
    Validate and sanitize command-line arguments.

    Ensures that:
        - At least one argument (location) is provided.
        - No more than two arguments are given.
        - The first argument is a string (location).
        - The second argument, if given, is an integer (days).

    Args:
        user_args (list[str]): Raw command-line arguments (excluding script name).

    Side Effects:
        - Prints error messages to the console.
        - Exits the program early in case of invalid arguments.

    Returns:
        user_args (list[str] or None): A list of validated arguments if checks pass;
        otherwise None (the function may call exit on error).
    """

    if not user_args:
        print("Input Error: Location not provided.")
        return None
    
    elif len(user_args) > 2:
        print(f"Input Error: Too many arguments. Expected 2, got {len(user_args)}.")
        return None

    elif len(user_args) == 1:
        location = user_args[0]

        try:
            if float(location):
                raise TypeError("First argument must be a string.")
        except TypeError as e:
            print(f"Error: {e}")
        except ValueError:
            return user_args

    elif len(user_args) == 2:
        valid = False
        
        for index, arg in enumerate(user_args):

            if index == 0:
                # Convert input to float or if input is 0.
                # If ValueError is triggered, input is valid.
                try:
                    if float(arg) or arg.isnumeric():
                        raise TypeError("The first argument should be a string.")
                except TypeError as e:
                    print(f"Error: {e}")
                    break
                except ValueError:
                    continue

            if index == 1:
                try:
                    if int(arg):
                        valid = True
                except ValueError:
                    print("Error: The second argument should be an integer.")
        if valid:
            return user_args
         

def main():
    """
    Entry point of the script.

    Parses command-line arguments, validates them with "error_handler()",
    and calls "weather_data()" to fetch and display the forecast.

    Side Effects:
        - Reads command-line arguments from sys.argv.
        - Prints how-to instructions and error messages (if any).
        - Prints the weather forecast to the console.

    Returns:
        None
    """

    try:
        user_args = sys.argv[1:]
        args = error_handler(user_args)

        if len(args) == 1:
            location_user = args[0]
            weather_data(location_user)

        elif len(args) == 2:
            location_user = args[0]
            days_user = int(args[1])

            if days_user <= 0 or days_user > 7:
                days_user = DEFAULT_DAYS

            weather_data(location_user, days_user)
    except:
        how_to_message()
    

if __name__ == "__main__":
    main()