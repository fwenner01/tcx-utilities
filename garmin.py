import argparse
import datetime
import logging
import os
from getpass import getpass
import requests
from garth.exc import GarthHTTPError
import tkinter
from tkinter import ttk
import sv_ttk

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

import tcx_parser


# setup tkinter
root = tkinter.Tk()
sv_ttk.use_dark_theme()
#sv_ttk.use_light_theme()


# setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    

def get_month_name(month_num):
    months = ["", "January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return months[int(month_num)]


def download_activities(api, start_date, end_date, overwrite):
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

        file_path = f"activities\\{year}\\{month}\\{day}-{id}.tcx"

        if not overwrite and os.path.isfile(file_path):
            pass
        else:
            with open(file_path, "wb") as fb:
                fb.write(data)
                print(f"Downloaded activity: {file_path}")


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
    parser.add_argument('--email', dest='email', action='store', required=False)
    parser.add_argument('--password', dest='password', action='store', required=False)
    parser.add_argument('--start_date', dest='start_date', action='store', required=False)
    parser.add_argument('--end_date', dest='end_date', action='store', default=f"{datetime.date.today()}", required=False)
    parser.add_argument('--list_activities', dest="list_activities", action='store_true', required=False)
    parser.add_argument('--download_activities', dest="download_activities", action='store_true', required=False)
    parser.add_argument('--overwrite', dest="overwrite", action='store_true', required=False)
    parser.add_argument('--synchronize', dest="synchronize", action='store_true', default=False, required=False)
    parser.add_argument('--tcx', dest="tcx", action='store_true', required=False)
    args = parser.parse_args()
    return args


def get_credentials():
    """Get user credentials."""

    email = input("Login e-mail: ")
    password = getpass("Enter password: ")

    return email, password


def init_api(email, password, tokenstore, tokenstore_base64):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            garmin = Garmin(email, password)
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            print(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            )
        except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
            logger.error(err)
            return None

    return garmin


def main():

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
    tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
    api = None

    args = get_args()

    api = init_api(email, password, tokenstore, tokenstore_base64)
    if not api:
        return


    if args.download_activities:
        if not args.start_date:
            today = datetime.datetime.now()
            args.start_date = today - datetime.timedelta(days = 14)
        print(f"Downloading activities from {args.start_date} to {args.end_date}")
        download_activities(api, args.start_date, args.end_date, args.overwrite)
    

    # if args.list_activities:
    #     if not args.start_date:
    #         print("Need --start_date to download activities")
    #         return
    #     activities = api.get_activities_by_date(args.start_date, args.end_date)
    #     for a in activities:
    #         print(a["activityId"])
    

    # if args.synchronize:
    #     today = datetime.datetime.now()
    #     look_back = today - datetime.timedelta(days = 14)
    #     activities = api.get_activities_by_date(look_back, today)
    #     for a in activities:
    #         print(a["activityId"])

    

    if args.tcx:
        tcx("activities/2024/January/test1.tcx")

    #root.mainloop()






if __name__ == "__main__":
    main()