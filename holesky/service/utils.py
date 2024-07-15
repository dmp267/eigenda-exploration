import os
import datetime

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
    try:
        timestamp = int(date_str)
        return datetime.datetime.fromtimestamp(timestamp)
    except ValueError:
        return datetime.strptime(date_str, '%Y-%m-%d')