import datetime
import lxml.etree
import dateutil.parser as dp

NAMESPACES = {
    'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
    'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
    'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
}


def get_tcx_point_data(point: lxml.etree._Element):
    """
    Get data from a Trackpoint XML element
    Return it as a dictionary
    """
    
    data = {}
    
    time_str = point.find('ns:Time', NAMESPACES).text
    data['time'] = dp.parse(time_str)
        
    elevation_elem = point.find('ns:AltitudeMeters', NAMESPACES)
    if elevation_elem is not None:
        data['elevation'] = float(elevation_elem.text)
    
    hr_elem = point.find('ns:HeartRateBpm', NAMESPACES)
    if hr_elem is not None:
        data['heart_rate'] = int(hr_elem.find('ns:Value', NAMESPACES).text)
        
    cad_elem = point.find('ns:Cadence', NAMESPACES)
    if cad_elem is not None:
        data['cadence'] = int(cad_elem.text)
    
    speed_elem = point.find('.//ns3:Speed', NAMESPACES)
    if speed_elem is not None:
        data['speed'] = float(speed_elem.text)

    distance_elem = point.find('ns:DistanceMeters', NAMESPACES)
    if distance_elem is not None:
        data['distance'] = float(distance_elem.text)
    
    return data
    

def get_all_data_points(fname: str):
    """
    Takes a string of the path to a TCX file and returns a list of dictionaries
    Where each dictionary is a Trackpoint
    """  
    tree = lxml.etree.parse(fname)
    root = tree.getroot()
    activity = root.find('ns:Activities', NAMESPACES)[0]
    points_data = []
    lap_no = 1
    for lap in activity.findall('ns:Lap', NAMESPACES):
        track = lap.find('ns:Track', NAMESPACES) 
        for point in track.findall('ns:Trackpoint', NAMESPACES):
            single_point_data = get_tcx_point_data(point)
            if single_point_data:
                single_point_data['lap'] = lap_no
                points_data.append(single_point_data)
        lap_no += 1
    
    return points_data


def get_total_time(points_data):
    start_time = points_data[0]["time"]
    end_time = points_data[-1]["time"]

    return (end_time - start_time)


def create_list_of_point_times(points_data):
    times = []
    for point in points_data:
        times.append(point["time"].time())
    return times


def search_point_time(points_data):
    times = create_list_of_point_times(points_data) #datetime.time(12, 29, 22), datetime.time(12, 29, 24)
    #print(times)
    search_closest_time(times, datetime.time(12, 29, 44))
    #print(times[6])
    #print(times[7])

    #print(get_time_difference(times[6], times[7]))

    #print(times[6] - times[7])


def get_time_difference(time1, time2):
    """Returns difference between two datetime.time objects in seconds"""
    dateTime1 = datetime.datetime.combine(datetime.date.today(), time1)
    dateTime2 = datetime.datetime.combine(datetime.date.today(), time2)
    return abs((dateTime1 - dateTime2).total_seconds())


def search_closest_time(v, to_find):
    lo = 0
    hi = len(v) - 1
    closest = 9999#get_time_difference(v[mid], to_find)
    #closestIndex = mid
 
    # This below check covers all cases , so need to check
    # for mid=lo-(hi-lo)/2
    while hi - lo > 0:
        mid = (hi + lo) // 2
        difference = get_time_difference(v[mid], to_find)
        if difference < closest:
            closest = difference
            closestIndex = mid
        if v[mid] < to_find:
            lo = mid + 1
        else:
            hi = mid
 
    if v[lo] == to_find:
        print("Found At Index", lo)
    elif v[hi] == to_find:
        print("Found At Index", hi)
    else:
        print("Not Found. Closest Index", closestIndex, closest)
