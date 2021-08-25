"""This module contains the JSON graph converter class, which is used
to convert various graph descriptor formats into a unified .json structure"""

from src.graphs._functions import json_dict_from_gml
from src.graphs._functions import json_dict_from_lgf
from src.graphs._functions import json_dict_from_graphml
from src.graphs._functions import convert_lat_long_to_x_y

""" Supported formats: if a new format is introduced,
append it to the _function module of the package, 
and import it into the dict for easier use. 
"""
_SUPPORTED_FORMATS = {
    "lgf": json_dict_from_lgf,
    "gml": json_dict_from_gml,
    "graphml": json_dict_from_graphml
}


class JsonGraphGenerator:
    """Class made for generating usable .json data from various input graph formats."""
    def __init__(self, file):
        """ Initializes raw data from input file."""
        ext = file.split('.')[-1]
        if ext not in _SUPPORTED_FORMATS:
            raise Exception("Not supported file format!")
        self._dump = _SUPPORTED_FORMATS[ext](file)

    def gen_json(self, auto_convert=True):
        """ Returns json compatible data of converted graph.
        :param auto_convert: If true, detects if input is in lat-long format,
        and projects it to a 2D plane
        :return: a JSON object containing graph information
        """
        if not auto_convert:
            return self._dump
        else:
            for n in self._dump['nodes']:
                lon_ovr = n['coords'][0] < -180 or 180 < n['coords'][0]
                lat_ovr = n['coords'][1] < -90 or 90 < n['coords'][1]
                if lon_ovr or lat_ovr:
                    return self._dump
            convert_lat_long_to_x_y(self._dump, sensitivity=4)
            return self._dump
