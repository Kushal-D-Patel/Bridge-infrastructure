"""Assignment 2: Bridges

The data used for this assignment is a subset of the data found in:
https://data.ontario.ca/dataset/bridge-conditions

This code is provided solely for the personal and private use of
students taking the CSCA08 course at the University of Toronto
Scarborough. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Anya Tafliovich, Mario Badr, Tom Fairgrieve, Sadia
Sharmin, and Jacqueline Smith

"""

import csv
from copy import deepcopy
from math import sin, cos, asin, radians, sqrt, inf
from typing import TextIO

from constants import (
    ID_INDEX, NAME_INDEX, HIGHWAY_INDEX, LAT_INDEX,
    LON_INDEX, YEAR_INDEX, LAST_MAJOR_INDEX,
    LAST_MINOR_INDEX, NUM_SPANS_INDEX,
    SPAN_DETAILS_INDEX, LENGTH_INDEX,
    LAST_INSPECTED_INDEX, BCIS_INDEX, FROM_SEP, TO_SEP,
    HIGH_PRIORITY_BCI, MEDIUM_PRIORITY_BCI,
    LOW_PRIORITY_BCI, HIGH_PRIORITY_RADIUS,
    MEDIUM_PRIORITY_RADIUS, LOW_PRIORITY_RADIUS,
    EARTH_RADIUS)
EPSILON = 0.01


# We provide this function for you to use as a helper.
def read_data(csv_file: TextIO) -> list[list[str]]:
    """Read and return the contents of the open CSV file csv_file as a
    list of lists, where each inner list contains the values from one
    line of csv_file.

    Docstring examples not given since the function reads from a file.

    """

    lines = csv.reader(csv_file)
    return list(lines)[2:]


# We provide this function for you to use as a helper.  This function
# uses the haversine function to find the distance between two
# locations. You do not need to understand why it works. You will just
# need to call this function and work with what it returns.  Based on
# https://en.wikipedia.org/wiki/Haversine_formula
# Notice how we use the built-in function abs and the constant EPSILON
# defined above to constuct example calls for the function that
# returns a float. We do not test with ==; instead, we check that the
# return value is "close enough" to the expected result.
def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """Return the distance in kilometers between the two locations defined by
    (lat1, lon1) and (lat2, lon2), rounded to the nearest meter.

    >>> abs(calculate_distance(43.659777, -79.397383, 43.657129, -79.399439)
    ...     - 0.338) < EPSILON
    True
    >>> abs(calculate_distance(43.42, -79.24, 53.32, -113.30)
    ...     - 2713.226) < EPSILON
    True
    """

    lat1, lon1, lat2, lon2 = (radians(lat1), radians(lon1),
                              radians(lat2), radians(lon2))

    haversine = (sin((lat2 - lat1) / 2) ** 2
                 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2)

    return round(2 * EARTH_RADIUS * asin(sqrt(haversine)), 3)


# We provide this sample data to help you set up example calls.
THREE_BRIDGES_UNCLEANED = [
    ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', '43.167233',
     '-80.275567', '1965', '2014', '2009', '4',
     'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012', '72.3', '',
     '72.3', '', '69.5', '', '70', '', '70.3', '', '70.5', '', '70.7', '72.9',
     ''],
    ['1 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', '-80.251582',
     '1963', '2014', '2007', '4',
     'Total=60.4  (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61', '04/13/2012',
     '71.5', '', '71.5', '', '68.1', '', '69', '', '69.4', '', '69.4', '',
     '70.3', '73.3', ''],
    ['2 -   4/', 'STOKES RIVER BRIDGE', '6', '45.036739', '-81.33579', '1958',
     '2013', '', '1', 'Total=16  (1)=16;', '18.4', '08/28/2013', '85.1',
     '85.1', '', '67.8', '', '67.4', '', '69.2', '70', '70.5', '', '75.1', '',
     '90.1', '']
]

THREE_BRIDGES = [
    [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233, -80.275567,
     '1965', '2014', '2009', 4, [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
     [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, '04/13/2012',
     [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
     '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
     [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]
]


# We provide the header and doctring for this function to help get you
# started.
def get_bridge(bridge_data: list[list], bridge_id: int) -> list:
    """Return the data for the bridge with id bridge_id from bridge data
    bridge_data. If there is no bridge with id bridge_id, return [].

    >>> result = get_bridge(THREE_BRIDGES, 1)
    >>> result == [
    ...    1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...    -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ...    [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True
    >>> get_bridge(THREE_BRIDGES, 42)
    []

    """

    if bridge_id - 1 < len(bridge_data):
        return bridge_data[bridge_id - 1]

    return []


def get_average_bci(bridge_data: list[list], bridge_id: int) -> float:
    """ Return the average BCI of the bridge with id bridge_id from bridge data
    bridge_data. If there is no bridge with the id bridge_id or if there are no
    BCIs for the bridge with id bridge_id, return 0.

    >>> get_average_bci (THREE_BRIDGES, 1)
    70.88571428571429

    >>> get_average_bci (THREE_BRIDGES, 42)
    0
    """
    if (bridge_id - 1 < len(bridge_data)
            and isinstance(bridge_data[bridge_id - 1][BCIS_INDEX], list)):
        total = 0
        num_bci = 0
        for num in bridge_data[bridge_id - 1][BCIS_INDEX]:
            total += num
            num_bci += 1
        return total / num_bci

    return 0


def get_total_length_on_hwy(bridge_data: list[list], highway: str) -> float:
    """Return the total length of bridges on the highway highway from bridge
    data bridge_data. If there are no bridges on the highway highway, return 0.

    >>> get_total_length_on_hwy(THREE_BRIDGES, '403')
    126.0

    >>> get_total_length_on_hwy(THREE_BRIDGES, '6')
    18.4

    >>> get_total_length_on_hwy(THREE_BRIDGES, '407')
    0
    """
    total = 0
    for bridge in bridge_data:
        if bridge[HIGHWAY_INDEX] == highway:
            total += bridge[LENGTH_INDEX]

    return total


def get_distance_between(bridge1: list, bridge2: list) -> float:
    """Return the distance between bridges bridge1 and bridge2 in kilometers
    rounded to 3 decimal places using the function round().

    Precondition: bridge 1 and bridge 2 are valid.

    >>> get_distance_between([1, 'Highway 24 Underpass at Highway 403', '403',
    ... 43.167233, -80.275567, '1965', '2014', '2009', 4,
    ... [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ... [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ... [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582, '1963',
    ... '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, '04/13/2012',
    ... [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]])
    1.968

    >>> get_distance_between([3, 'STOKES RIVER BRIDGE', '6', 45.036739,
    ... -81.33579, '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ... [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]],
    ... [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233, -80.275567,
    ... '1965', '2014', '2009', 4, [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ... [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]])
    224.451
    """
    return round(calculate_distance(bridge1[LAT_INDEX], bridge1[LON_INDEX],
                 bridge2[LAT_INDEX], bridge2[LON_INDEX]), 3)


def get_closest_bridge(bridge_data: list[list], bridge_id: int) -> int:
    """Return the id of the bridge which is closest to the bridge with id
    bridge_id from bridge data bridge_data.

    Precondition: Bridge with id bridge_id is present in the bridge data
    bridge_data and there are atleast two bridges in bridge data bridge_data.

    >>> get_closest_bridge(THREE_BRIDGES, 2)
    1

    >>> get_closest_bridge(THREE_BRIDGES, 1)
    2
    """
    if bridge_data[bridge_id - 1] != bridge_data[0]:
        closest_bridge = bridge_data[0]
    else:
        closest_bridge = bridge_data[1]

    for bridge in bridge_data:
        if (bridge != bridge_data[bridge_id - 1]
            and get_distance_between(closest_bridge,
                                     bridge_data[bridge_id - 1])
                > get_distance_between(bridge, bridge_data[bridge_id - 1])):
            closest_bridge = bridge

    return closest_bridge[ID_INDEX]


def get_bridges_in_radius(bridge_data: list[list], latitude: float,
                          longitude: float, radius: float) -> list[int]:
    """Return a list of ids of all bridges within radius radius of the location
    with latitude and longitude latitude and longitude in the bridge data
    bridge_data.

    Precondition: Valid bridge data.

    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, 50)
    [1, 2]

    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, 0)
    []

    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, 250)
    [1, 2, 3]
    """
    id_list = []
    for bridge in bridge_data:
        if calculate_distance(latitude, longitude, bridge[LAT_INDEX],
                              bridge[LON_INDEX]) <= radius:
            id_list.append(bridge[ID_INDEX])

    return id_list


def get_bridges_with_bci_below(bridge_data: list[list],
                               bridge_id: list[int], bci: float) -> list[int]:
    """Return a list of ids of all bridges within bridge data bridge_data
    whose id is within bridge_id and whose BCI is less than or equal to the
    given BCI bci.

    Precondition: Valid bridge data.

    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2], 72)
    [2]

    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2, 3], 85.2)
    [1, 2, 3]

    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2, 3], 0)
    []

    >>> get_bridges_with_bci_below(THREE_BRIDGES, [], 85.2)
    []
    """
    bci_below = []
    for bridge in bridge_data:
        if bridge[ID_INDEX] in bridge_id and bridge[BCIS_INDEX][0] <= bci:
            bci_below.append(bridge[ID_INDEX])

    return bci_below


def get_bridges_containing(bridge_data: list[list], search: str) -> list[int]:
    """Return a list of ids of all bridges within bridge data bridge_data
    whose names contain the search string search. The search is
    case-insensitive.

    Precondition: Valid bridge data

    >>> get_bridges_containing(THREE_BRIDGES, 'underpass')
    [1, 2]
    >>> get_bridges_containing(THREE_BRIDGES, 'pAss')
    [1, 2]
    >>> get_bridges_containing(THREE_BRIDGES, 'mouse')
    []
    """
    bridge_id = []
    for bridge in bridge_data:
        if search.lower() in bridge[NAME_INDEX].lower():
            bridge_id.append(bridge[ID_INDEX])

    return bridge_id


# We provide the header and doctring for this function to help get you started.
def assign_inspectors(bridge_data: list[list], inspectors: list[list[float]],
                      max_bridges: int) -> list[list[int]]:
    """Return a list of bridge IDs from bridge data bridge_data, to be
    assigned to each inspector in inspectors. inspectors is a list
    containing (latitude, longitude) pairs representing each
    inspector's location. At most max_bridges are assigned to each
    inspector, and each bridge is assigned once (to the first
    inspector that can inspect that bridge).

    See the "Assigning Inspectors" section of the handout for more details.

    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15], [42.10, -81.15]], 0)
    [[], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 1)
    [[1]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 2)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 3)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 1)
    [[1], [2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 2)
    [[1, 2], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [45.0368, -81.34]],
    ...                   2)
    [[1, 2], [3]]
    >>> assign_inspectors(THREE_BRIDGES, [[38.691, -80.85], [43.20, -80.35]],
    ...                   2)
    [[], [1, 2]]

    """

    id_lst = [bridge[ID_INDEX] for bridge in bridge_data]

    assignment = []
    for inspector in inspectors:
        assign_inspector = []
        count = 0
        for bridge_id in id_lst:
            is_high = (bridge_id in get_bridges_in_radius(bridge_data,
                                                          inspector[0],
                                                          inspector[1],
                                                          HIGH_PRIORITY_RADIUS)
                       and bridge_id
                       in get_bridges_with_bci_below(bridge_data,
                                                     id_lst, HIGH_PRIORITY_BCI))
            is_medium = (bridge_id
                         in get_bridges_in_radius(bridge_data, inspector[0],
                                                  inspector[1],
                                                  MEDIUM_PRIORITY_RADIUS)
                         and bridge_id
                         in get_bridges_with_bci_below(bridge_data, id_lst,
                                                       MEDIUM_PRIORITY_BCI))
            is_low = (bridge_id
                      in get_bridges_in_radius(bridge_data, inspector[0],
                                               inspector[1],
                                               LOW_PRIORITY_RADIUS)
                      and bridge_id
                      in get_bridges_with_bci_below(bridge_data,
                                                    id_lst, LOW_PRIORITY_BCI))

            if count < max_bridges and (is_high or is_medium or is_low):
                assign_inspector.append(bridge_id)
                count += 1

        assignment.append(assign_inspector)

        id_lst = [bid for bid in id_lst if bid not in assign_inspector]

    return assignment


# We provide the header and doctring for this function to help get you
# started. Note the use of the built-in function deepcopy (see
# help(deepcopy)!): since this function modifies its input, we do not
# want to call it with THREE_BRIDGES, which would interfere with the
# use of THREE_BRIDGES in examples for other functions.
def inspect_bridges(bridge_data: list[list], bridge_ids: list[int], date: str,
                    bci: float) -> None:
    """Update the bridges in bridge_data with id in bridge_ids with the new
    date and BCI score for a new inspection.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> inspect_bridges(bridges, [1], '09/15/2018', 71.9)
    >>> bridges == [
    ...   [1, 'Highway 24 Underpass at Highway 403', '403',
    ...    43.167233, -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65, '09/15/2018',
    ...    [71.9, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...   [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...    '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2],
    ...    61, '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...   [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...    '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...    [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True

    """

    for bridge in bridge_data:
        if bridge[ID_INDEX] in bridge_ids:
            bridge[LAST_INSPECTED_INDEX] = date
            bridge[BCIS_INDEX].insert(0, bci)


def add_rehab(bridge_data: list[list], bridge_id: int, date: str,
              major: bool) -> None:
    """Update the bridge with the id bridge_id in bridge data bridge_data with
    new rehab year record from the date date. Will update appropriate rehab year
    record based on the major status major. If there is no bridge with
    id bridge_id in the bridge data bridge_data then the function has no effect.

    Precondition: date should be in the format MM/DD/YYYY. Valid bridge data.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> add_rehab(bridges, 1, '09/15/2018', False)
    >>> bridges == [
    ...         [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...            -80.275567, '1965', '2014', '2018', 4,
    ...            [12.0, 19.0, 21.0, 12.0], 65, '04/13/2012',
    ...            [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...        [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...         '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0,
    ...            '04/13/2012',
    ...         [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...        [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...         '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...         [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> add_rehab(bridges, 2, '09/15/2019', True)
    >>> bridges == [
    ...         [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...            -80.275567, '1965', '2014', '2009', 4,
    ...            [12.0, 19.0, 21.0, 12.0], 65, '04/13/2012',
    ...            [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...        [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...         '1963', '2019', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0,
    ...            '04/13/2012',
    ...         [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...        [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...         '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...         [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> add_rehab(bridges, 42, '09/15/2018', False)
    >>> bridges == [
    ...         [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...            -80.275567, '1965', '2014', '2009', 4,
    ...            [12.0, 19.0, 21.0, 12.0], 65, '04/13/2012',
    ...            [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...        [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...         '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0,
    ...            '04/13/2012',
    ...         [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...        [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...         '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...         [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True

    """
    if major and bridge_id - 1 < len(bridge_data):
        bridge_data[bridge_id - 1][LAST_MAJOR_INDEX] = date[6:]
    elif bridge_id - 1 < len(bridge_data):
        bridge_data[bridge_id - 1][LAST_MINOR_INDEX] = date[6:]


# We provide the header and doctring for this function to help get you started.
def format_data(data: list[list[str]]) -> None:
    """Modify the uncleaned bridge data data, so that it contains proper
    bridge data, i.e., follows the format outlined in the 'Data
    formatting' section of the assignment handout.

    >>> d = THREE_BRIDGES_UNCLEANED
    >>> format_data(d)
    >>> d == THREE_BRIDGES
    True

    """

    for i in range(len(data)):
        format_bcis(data[i])
        format_spans(data[i])
        format_location(data[i])
        format_length(data[i])
        data[i][ID_INDEX] = i + 1


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_location(bridge_record: list) -> None:
    """Format latitude and longitude data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_location(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           43.167233, -80.275567, '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    True
    """

    bridge_record[LON_INDEX] = float(bridge_record[LON_INDEX])
    bridge_record[LAT_INDEX] = float(bridge_record[LAT_INDEX])


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_spans(bridge_record: list) -> None:
    """Format the bridge spans data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_spans(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', 4,
    ...           [12.0, 19.0, 21.0, 12.0], '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    True

    """
    bridge_record[NUM_SPANS_INDEX] = int(bridge_record[NUM_SPANS_INDEX])
    span_lst = []
    details = bridge_record[SPAN_DETAILS_INDEX]
    i = 0

    while i < len(details):
        if details[i] == ')':
            num = ''
            i += 2
            while i < len(details) and details[i] != ';':
                num += details[i]
                i += 1
            span_lst.append(float(num))
        else:
            i += 1

    bridge_record[SPAN_DETAILS_INDEX] = span_lst


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_length(bridge_record: list) -> None:
    """Format the bridge length data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_length(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...            '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...            'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', 65, '04/13/2012',
    ...            '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...            '70.5', '', '70.7', '72.9', '']
    True

    """

    bridge_record[LENGTH_INDEX] = float(bridge_record[LENGTH_INDEX])


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_bcis(bridge_record: list) -> None:
    """Format the bridge BCI data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_bcis(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True

    """

    bci_lst = []

    for string in bridge_record[BCIS_INDEX:]:
        if len(string) != 0:
            bci_lst.append(float(string))

    bridge_record[BCIS_INDEX] = bci_lst[1:]
    del bridge_record[BCIS_INDEX + 1:]


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # To test your code with larger lists, you can uncomment the code below to
    # read data from the provided CSV file.
    # with open('bridge_data.csv', encoding='utf-8') as bridge_data_file:
    #     BRIDGES = read_data(bridge_data_file)
    # format_data(BRIDGES)

    # For example:
    # print(get_bridge(BRIDGES, 3))
    # EXPECTED = [3, 'NORTH PARK STEET UNDERPASS', '403', 43.165918, -80.263791,
    #             '1962', '2013', '2009', 4, [12.2, 18.0, 18.0, 12.2], 60.8,
    #             '04/13/2012', [71.4, 69.9, 67.7, 68.9, 69.1, 69.9, 72.8]]
    # print('Testing get_bridge: ', get_bridge(BRIDGES, 3) == EXPECTED)
