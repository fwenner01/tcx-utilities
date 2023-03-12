import os
import datetime
import json
import argparse
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)
import tcx_parser


def login(username, password):
    """Use username and password to log into Garmin api"""
    try:
        api = Garmin(username, password)
        api.login()
        with open("session.json", "w", encoding="utf-8") as f:
            json.dump(api.session_data, f, ensure_ascii=False, indent=4)
        return api

    except (GarminConnectConnectionError, GarminConnectAuthenticationError, GarminConnectTooManyRequestsError) as err:
        print(err)
        return False


def login_without_credentials():
    """Use last session to log into Garmin api"""
    try:
        with open("session.json") as f:
            session = json.load(f)
            api = Garmin(session_data=session)
            api.login()
            return api

    except (FileNotFoundError, GarminConnectAuthenticationError) as err:
        print(err)
        return False
    

def get_month_name(month_num):
    months = ["", "January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return months[int(month_num)]


def download_activities(api, start_date, end_date):
    activities = api.get_activities_by_date(start_date, end_date)
    for activity in activities:
        start_time = activity['startTimeLocal']
        start_time = start_time.split(" ")[0]
        start_time = start_time.split("-")
        year = start_time[0]
        month = start_time[1]
        month = get_month_name(month)
        day = start_time[2]

        id = activity['activityId']

        if not os.path.exists(f"activities\\{year}\\{month}"):
            os.makedirs(f"activities\\{year}\\{month}")

        data = api.download_activity(id, dl_fmt=api.ActivityDownloadFormat.TCX)
        with open(f"activities\\{year}\\{month}\\{day}-{id}.tcx", "wb") as fb:
            fb.write(data)


def tcx(filename):
    points_data = tcx_parser.get_all_data_points(filename)
    #print(points_data)

    tcx_parser.search_point_time(points_data)

    #time = tcx_parser.get_total_time(points_data)
    #print(time)

    # times = tcx_parser.create_list_of_point_times(points_data)
    # print(times)


def get_args():
    """Parse all of the user arguments"""
    parser = argparse.ArgumentParser(description='Process garmin requests')
    parser.add_argument('--username', dest='username', action='store', required=False)
    parser.add_argument('--password', dest='password', action='store', required=False)
    parser.add_argument('--start_date', dest='start_date', action='store', required=False)
    parser.add_argument('--end_date', dest='end_date', action='store', default=f"{datetime.date.today()}", required=False)
    parser.add_argument('--list_activities', dest="list_activities", action='store_true', required=False)
    parser.add_argument('--download_activities', dest="download_activities", action='store_true', required=False)
    parser.add_argument('--tcx', dest="tcx", action='store_true', required=False)
    args = parser.parse_args()
    return args


def main():

    args = get_args()

    # login with credentials if the arguments were used
    if args.username and args.password and not args.tcx:
        print("logging in with credentials...")
        api = login(args.username, args.password)
        if not api:
            return
        
    # login without credentials
    elif not args.tcx:
        print("logging in without credentials...")
        api = login_without_credentials()
        if not api:
            return
        
    
    if args.download_activities:
        if not args.start_date:
            print("Need --start_date to download activities")
            return
        download_activities(api, args.start_date, args.end_date)
    

    if args.list_activities:
        activities = api.get_activities_by_date('2022-03-06', '2023-03-11')
        for a in activities:
            print(a['startTimeLocal'])
    

    if args.tcx:
        tcx("run.tcx")






if __name__ == "__main__":
    main()