import datetime
from errno import ETIME
import lxml.etree
import dateutil.parser as dp
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
from matplotlib import cm
from dataclasses import dataclass

NAMESPACES = {
    'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
    'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
    'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
}

@dataclass
class TotalStats:
    total_time: float
    distance: float
    max_speed: float
    calories: int
    average_heartrate: int
    max_heartrate: int

@dataclass
class LapStats:
    total_time: float
    distance: float
    max_speed: float
    calories: int
    average_heartrate: int
    max_heartrate: int

@dataclass
class PointStats:
    lap: int
    time: datetime
    distance: float
    heartrate: int
    speed: float
    altitude: float
    latitude: float
    longitude: float


class Activity():

    def __init__(self, fname):
        tree = lxml.etree.parse(fname)
        root = tree.getroot()
        activity = root.find('ns:Activities', NAMESPACES)[0]
        laps = []
        self.points = []
        lap_num = 0
        for lap in activity.findall('ns:Lap', NAMESPACES):
            
            # set stats for lap
            total_time = lap.find('ns:TotalTimeSeconds', NAMESPACES).text
            distance = lap.find('ns:DistanceMeters', NAMESPACES).text
            max_speed = lap.find('ns:MaximumSpeed', NAMESPACES).text
            average_heartrate = lap.find('ns:AverageHeartRateBpm', NAMESPACES).find('ns:Value', NAMESPACES).text
            max_heartrate = lap.find('ns:MaximumHeartRateBpm', NAMESPACES).find('ns:Value', NAMESPACES).text
            calories = lap.find('ns:Calories', NAMESPACES).text


            lap_stats = LapStats(total_time=float(total_time),
                          distance=float(distance),
                          max_speed=float(max_speed),
                          average_heartrate=int(average_heartrate),
                          max_heartrate=int(max_heartrate),
                          calories=int(calories))

            laps.append(lap_stats)

            # set stats for points in lap
            track = lap.find('ns:Track', NAMESPACES) 
            for point in track.findall('ns:Trackpoint', NAMESPACES):
                time =  dp.parse(point.find('ns:Time', NAMESPACES).text)
                distance = point.find('ns:DistanceMeters', NAMESPACES).text
                heartrate = point.find('ns:HeartRateBpm', NAMESPACES).find('ns:Value', NAMESPACES).text
                speed = point.find('ns:Extensions', NAMESPACES).find('ns3:TPX', NAMESPACES).find('ns3:Speed', NAMESPACES).text
                altitude = point.find('ns:AltitudeMeters', NAMESPACES).text
                latitude = point.find('ns:Position', NAMESPACES).find('ns:LatitudeDegrees', NAMESPACES).text
                longitude = point.find('ns:Position', NAMESPACES).find('ns:LongitudeDegrees', NAMESPACES).text
                point_stats = PointStats(lap=lap_num,
                                         time=time,
                                         distance=float(distance),
                                         heartrate=int(heartrate),
                                         speed=float(speed),
                                         altitude=float(altitude),
                                         latitude=float(latitude),
                                         longitude=float(longitude))
                self.points.append(point_stats)
    
            lap_num += 1
        

        total_stats = self.get_total_stats(laps)

        # create dataframes
        laps_data = [{field.name: getattr(lap, field.name) for field in LapStats.__dataclass_fields__.values()} for lap in laps]
        total_data = [{field.name: getattr(total_stats, field.name) for field in TotalStats.__dataclass_fields__.values()}]
        #points_data = [{field.name: getattr(point, field.name) for field in PointStats.__dataclass_fields__.values()} for point in points]
        points_data_excel = [{**{field.name: getattr(point, field.name) for field in PointStats.__dataclass_fields__.values()}, 'time': point.time.strftime('%Y-%m-%d %H:%M:%S')} for point in self.points]
        points_data = [{field.name: getattr(point, field.name) for field in PointStats.__dataclass_fields__.values()} for point in self.points]
        laps_df = pd.DataFrame(laps_data)
        points_df = pd.DataFrame(points_data)
        points_df_excel = pd.DataFrame(points_data_excel)
        total_df = pd.DataFrame(total_data)
        #total_df.index = ['Totals']
       # laps_df = laps_df.append(total_df)  # Append total_df to laps_df
        #laps_df.index.name = None


        laps_df.to_excel("laps.xlsx")
        points_df_excel.to_excel("points.xlsx")
        total_df.to_excel("total.xlsx")

        time = points_df['time']
        speed = points_df['speed']
        heartrate = points_df['heartrate']
        altitude = points_df['altitude']

        # Step 2: Create a figure and axis objects
        fig, axs = plt.subplots(3, 1, figsize=(10, 8))

        # Step 3: Plot the data
        axs[0].fill_between(time, speed, color="skyblue", alpha=0.4)
        axs[0].plot(time, speed, color="Slateblue", alpha=0.6)
        axs[0].set_title('Speed')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Speed')

        axs[1].fill_between(time, heartrate, color="lightgreen", alpha=0.4)
        axs[1].plot(time, heartrate, color="forestgreen", alpha=0.6)
        axs[1].set_title('Heart Rate')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Heart Rate')

        axs[2].fill_between(time, altitude, color="lightcoral", alpha=0.4)
        axs[2].plot(time, altitude, color="maroon", alpha=0.6)
        axs[2].set_title('Altitude')
        axs[2].set_xlabel('Time')
        axs[2].set_ylabel('Altitude')

        # Step 4: Show the plot
        plt.tight_layout()
        plt.show()

        #plt.plot(points_df['time'], points_df['heartrate'])

        #plt.show()


    def graph_map(self):
        xyz = []
        for p in self.points:
            xyz.append([p.longitude, p.latitude, p.altitude, p.speed])
        
        # Extracting x, y, z coordinates
        x_coords, y_coords, z_coords, speeds = zip(*xyz)

        # Plotting
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot each point with varying colors based on speed
        norm = Normalize(vmin=min(speeds), vmax=max(speeds))
        cmap = cm.plasma
        for x, y, z, speed in zip(x_coords, y_coords, z_coords, speeds):
            color = cmap(norm(speed))
            ax.scatter(x, y, z, color=color)

        # Connecting points with lines with varying colors based on speed
        for i in range(len(xyz) - 1):
            start_point = xyz[i]
            end_point = xyz[i+1]
            speed = start_point[3]
            color = cmap(norm(speed))
            ax.plot([start_point[0], end_point[0]], 
                    [start_point[1], end_point[1]], 
                    [start_point[2], end_point[2]], 
                    color=color)

        # Adding labels
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        z_min = min(z_coords)
        z_max = max(z_coords)
        ax.set_zlim(z_min - 50, z_max + 50)

        ax.view_init(elev=90, azim=0)
        plt.show()

    def get_total_stats(self, laps):
        total_time = 0
        distance = 0
        calories = 0
        max_speed = 0
        max_heartrate = 0
        total_heartrate = 0
        average_heartrate = 0
        
        for lap in laps:
            total_time += lap.total_time
            distance += lap.distance
            calories += lap.calories
            if(lap.max_speed > max_speed): 
                max_speed = lap.max_speed
            if(lap.max_heartrate > max_heartrate):
                max_heartrate = lap.max_heartrate
        
            total_heartrate += (lap.average_heartrate * lap.total_time)

        average_heartrate = total_heartrate / total_time

        total_stats = TotalStats(total_time=total_time,
                                    distance=distance,
                                    calories=calories,
                                    max_speed=max_speed,
                                    max_heartrate=max_heartrate,
                                    average_heartrate=average_heartrate)
        
        return total_stats

                

                



def get_average_heartrate(fname: str):
    tree = lxml.etree.parse(fname)
    root = tree.getroot()
    activity = root.find('ns:Activities', NAMESPACES)[0]
    for lap in activity.findall('ns:Lap', NAMESPACES):
        hr = lap.find('ns:AverageHeartRateBpm', NAMESPACES)
        hr2 = hr.find('ns:Value', NAMESPACES)
    return hr2.text



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
    search_closest_time(times, datetime.time(21, 55, 29))
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
    closestIndex = None
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
