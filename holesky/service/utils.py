import os
import json
from datetime import datetime

from data.parser import parse_kml
from data.client import retrieve_from_ipfs


def allowed_file(filename):
    # KML files only
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'kml'


def parse_file(file_path: str):
    # KML files only
    if file_path.endswith('.kml'):
        kwargs = parse_kml(file_path)
        polygon_kwargs = kwargs['polygon_kwargs']
        spatial_agg_kwargs = kwargs['spatial_agg_kwargs']
        temporal_agg_kwargs = kwargs['temporal_agg_kwargs']
        return polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs
    else:
        raise ValueError("Invalid file type")


def download_file(cid: str):
    return retrieve_from_ipfs(cid)


def cleanup_file(file: str):
    os.remove(file)


def convert_to_datetime(date_str: str):
    if isinstance(date_str, datetime):
        return date_str
    try:
        timestamp = int(date_str)
        if timestamp > 1e10:
            result = datetime.fromtimestamp(timestamp / 1e3)
        else:
            result = datetime.fromtimestamp(timestamp)
    except ValueError:
        result = datetime.strptime(date_str, '%Y-%m-%d')
    return result


def filter_to_date(data: str, date: datetime):
    data = json.loads(data)
    timestamps = data['result']['timestamps_ms']
    date_timestamp = date.timestamp() * 1e3
    for i in range(len(timestamps)):
        # ordered oldest to newest
        if timestamps[i] > date_timestamp:
            index = i - 1
            result = {
                "agb": {
                    "data": data['result']['agb']['data'][index],
                    "unit": data['result']['agb']['unit']
                },
                "deforestation": {
                    "data": data['result']['deforestation']['data'][index],
                    "unit": data['result']['deforestation']['unit']
                },
                "sequestration": {
                    "data": data['result']['sequestration']['data'][index],
                    "unit": data['result']['sequestration']['unit']
                }
            }
            break
    return result

    

