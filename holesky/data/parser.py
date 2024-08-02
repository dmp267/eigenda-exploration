import os
# import struct
import geopandas as gpd
from pykml import parser
from shapely import Polygon, MultiPolygon


# def pack_polygon_kwargs(multipolygons):
#     packed = bytearray()
#     packed.extend(struct.pack('I', len(multipolygons)))

#     for multipolygon in multipolygons:
#         packed.extend(struct.pack('I', len(multipolygon)))

#         for polygon in multipolygon:
#             packed.extend(struct.pack('I', len(polygon)))

#             for coord in polygon:
#                 packed.extend(struct.pack('ff', *coord))

#     return packed


# def unpack_polygon_kwargs(packed):
#     unpacked = []
#     offset = 0

#     num_multipolygons = struct.unpack_from('I', packed, offset)[0]
#     offset += struct.calcsize('I')

#     for _ in range(num_multipolygons):
#         multipolygon = []
#         num_polygons = struct.unpack_from('I', packed, offset)[0]
#         offset += struct.calcsize('I')

#         for _ in range(num_polygons):
#             polygon = []
#             num_coords = struct.unpack_from('I', packed, offset)[0]
#             offset += struct.calcsize('I')

#             for _ in range(num_coords):
#                 lon, lat = struct.unpack_from('ff', packed, offset)
#                 offset += struct.calcsize('ff')
#                 polygon.append((lon, lat))

#             multipolygon.append(polygon)

#         unpacked.append(multipolygon)
#     return unpacked


def parse_kml(kml_path):
    """
    Parse the KML file at the provided file path and return the necessary 
    kwargs for the geo_temporal_query function.

    Parameters:
        data str: The KML file path
    
    Returns:    
        dict: The kwargs for the geo_temporal_query function.
    """
    if os.path.exists(kml_path):
        with open(kml_path, 'r', encoding='utf-8') as f:
            root = parser.parse(f).getroot()
            f.close()
    else:
        raise ValueError("Invalid data provided.")
    polygons_mask = []
    # all_placemarks = []
    for folder in root.Document.Folder:
        for placemark in folder.Placemark:
            print(f'Processing {placemark.name.text.strip()}')

            multigeometry = placemark.MultiGeometry
            multipolygons = []
            # all_polygons = []

            for polygon in multigeometry.Polygon:
                coordinates = polygon.outerBoundaryIs.LinearRing.coordinates.text.strip()
                coordinate_pairs = []

                for coord in coordinates.split():
                    lon, lat, alt = coord.split(',')
                    if int(alt) != 0:
                        print(f'Warning: altitude is not zero: {alt}')
                    coordinate_pairs.append((float(lon), float(lat)))
                multipolygons.append(Polygon(coordinate_pairs))
                # all_polygons.append(coordinate_pairs)
            polygons_mask.append(MultiPolygon(multipolygons))
            # all_placemarks.append(all_polygons)

    # print(f'all_placemarks: {all_placemarks}')
    # packed = pack_polygon_kwargs(all_placemarks)
    # print(f'packed: {packed}')
    # print(f'len(packed): {len(packed)}')
    # unpacked = unpack_polygon_kwargs(packed)
    # print(f'unpacked: {unpacked}')
    # print(f'len(unpacked): {len(unpacked)}')


    polygon_kwargs = { "polygons_mask": gpd.array.from_shapely(polygons_mask) }
    spatial_agg_kwargs = { "agg_method": "sum" }
    temporal_agg_kwargs = None

    return {
        "polygon_kwargs": polygon_kwargs,
        "spatial_agg_kwargs": spatial_agg_kwargs,
        "temporal_agg_kwargs": temporal_agg_kwargs
    }
