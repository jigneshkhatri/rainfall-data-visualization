import argparse
import json
import pandas as pd
from haversine import haversine
import operator as op
import math

import requests


def calc_coordinates(north_lat, east_lon, south_lat, west_lon, sq_km):

    # Lat-lon for the grid layout for whole area
    border_df = pd.DataFrame(columns=['name','lat','lon'])

    # Lat-lon for the actual data points where rainfall needs to be calculated (mid of point of each box in the grid)
    inner_df = pd.DataFrame(columns=['name','lat','lon'])

    data = []
    inner_data_points = []

    # Total horizontal distance (horizontal side length) of the whole area
    horizontal_distance = haversine((north_lat, west_lon), (north_lat, east_lon))

    # Total vertical distance (vertical side length) of the whole area
    vertical_distance = haversine((north_lat, west_lon), (south_lat, west_lon))

    print(f'horizontal_distance: {horizontal_distance}')
    print(f'vertical_distance: {vertical_distance}')

    print(f'sq_km: {sq_km}')
    side_ratio = horizontal_distance / vertical_distance

    # The vertical distance (vertical side length) of single grid box
    required_vertical_side = math.sqrt(sq_km / side_ratio)

    # The horizontal distance (horizontal side length) of the single grid box
    required_horizontal_side = sq_km / required_vertical_side

    # How many divisions need to be made of horizontal_distance to suffice the sq_km grid box
    horizontal_divisions = int(horizontal_distance / required_horizontal_side)

    # How many divisions need to be made of vertical_distance to suffice the sq_km grid box
    vertical_divisions = int(vertical_distance / required_vertical_side)

    print(f'horizontal_divisions: {horizontal_divisions}')
    print(f'vertical_divisions: {vertical_divisions}')

    if east_lon > 0 and west_lon < 0:
        _east_lon = east_lon if east_lon <= 90 else east_lon-180
        _west_lon = west_lon if west_lon >= -90 else 180+west_lon
    else:
        _east_lon = east_lon
        _west_lon = west_lon

    # The amount to be added in the latitude to lay out the grid from top to bottom
    lat_increments = (south_lat - north_lat) / vertical_divisions

    # The amount to be subtracted in the longitude to lay out the grid from top to bottom
    lon_increments = (_west_lon - _east_lon) / horizontal_divisions
    

    print(f'lat_increments: {lat_increments}')
    print(f'lon_increments: {lon_increments}')

    for i in range(vertical_divisions+1):
        for j in range(horizontal_divisions+1):
            # Calculate the grid data points
            data.append(pd.Series([f'LatLon{i}-{j}', north_lat+lat_increments*j, calc_lon_point(west_lon, lon_increments, i, op.sub)], index=border_df.columns))

    border_df = border_df.append(data, ignore_index=True)

    # For the actual data points where rainfall needs to be caculated (mid point of each grid box)
    inner_north_lat = north_lat + (lat_increments/2)
    inner_west_lon = west_lon - (lon_increments/2)

    for i in range(vertical_divisions):
        for j in range(horizontal_divisions):
            inner_data_points.append(pd.Series([f'LatLon{i}-{j}', inner_north_lat+lat_increments*j, calc_lon_point(inner_west_lon, lon_increments, i, op.sub)], index=border_df.columns))

    inner_df =  inner_df.append(inner_data_points, ignore_index=True)

    return border_df, inner_df


def calc_lon_point(lon, increment, iteration, op):
    val = op(lon, increment*iteration) 
    if val > 180:
        return (val - 180) - 180
    if val < -180:
        return 180 - (-180 - val)
    if val == -180:
        return 180
    return val


def set_rainfall_data(df, api_key, start_date, end_date):
    # Fetch and set the rainfall for each lat-lon from the weather API
    df['rainfall'] = df.apply(lambda row: fetch_rainfall_data_by_world_weather_online(row, api_key, start_date, end_date), axis = 1)


def fetch_rainfall_data_by_visual_crossing(row, api_key, start_date, end_date):
    api_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history"
    lat_lon = f"{row['lat']},{row['lon']}"
    params = {
        "aggregateHours": 24,
        "startDateTime": start_date,
        "endDateTime": end_date,
        "unitGroup": "uk",
        "contentType": "json",
        "dayStartTime": "0:0:00",
        "dayEndTime": "0:0:00",
        "location": lat_lon,
        "key": api_key
    }
    
    print("Calling weather API with following params")
    print(params)

    resp = requests.get(api_url, params=params)
    if not resp.status_code == 200:
        print(f"Error fetching the rainfall data with status: {resp.status_code}")
        print(resp)
        return 0
    
    resp_json = json.loads(resp.text)
    temp_df = pd.DataFrame(resp_json["locations"][lat_lon]["values"], columns=["precip"])
    return temp_df["precip"].sum()


def fetch_rainfall_data_by_world_weather_online(row, api_key, start_date, end_date):
    api_url = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
    lat_lon = f"{row['lat']},{row['lon']}"
    params = {
        "date": start_date,
        "enddate": end_date,
        "includelocation": "yes",
        "format": "json",
        "q": lat_lon,
        "key": api_key
    }
    
    print("Calling weather API with following params")
    print(params)

    resp = requests.get(api_url, params=params)
    if not resp.status_code == 200:
        print(f"Error fetching the rainfall data with status: {resp.status_code}")
        print(resp)
        return 0
    
    resp_json = json.loads(resp.text)
    total_rainfall = 0
    for single_date in resp_json['data']['weather']:
        for single_hour in single_date['hourly']:
            total_rainfall += float(single_hour['precipMM'])
    
    return total_rainfall


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Northern most latitude of the area for which rainfall needs to be visualized
    parser.add_argument("--north_lat", required=True, help='Northern most latitude', type=float)

    # Easterm most longitude of the area for which rainfall needs to be visualized
    parser.add_argument("--east_lon", required=True, help='Eastern most longitude', type=float)

    # Southern most latitude of the area for which rainfall needs to be visualized
    parser.add_argument("--south_lat", required=True, help='Southern most latitude', type=float)

    # Western most longitude of the area for which rainfall needs to be visualized
    parser.add_argument("--west_lon", required=True, help='Western most longitude', type=float)

    # Area of single zone (in sqkm) (single cell of grid) in which whole large area needs to be divided
    parser.add_argument("--sq_km", required=False, help='Single zone area', type=float, default=5)

    parser.add_argument("--api_key", required=True, help='Weather data provider API key', type=str)
    parser.add_argument("--start_date", required=True, help='Start date from when rainfall data needs to be fetched', type=str)
    parser.add_argument("--end_date", required=True, help='End date till when rainfall data needs to be fetched', type=str)
    args = vars(parser.parse_args())

    # Get the lat and lon for whole area grid and the actual data points where rainfall needs to be calculated
    # Actual data points are the mid point of each grid box
    border_df, inner_df = calc_coordinates(args["north_lat"], args["east_lon"], args["south_lat"], args["west_lon"], args["sq_km"])

    # Call the weather API and set the rainfall data for each of the actual data point
    set_rainfall_data(inner_df, args["api_key"], args["start_date"], args["end_date"])

    # Write both the data sets to the csv files
    border_df.to_csv("resources\datasets\grid_points.csv", index=False)
    inner_df.to_csv("resources\datasets\\actual_points.csv", index=False)

    print("Datasets generated successfully")

