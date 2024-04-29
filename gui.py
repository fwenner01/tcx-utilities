from datetime import timedelta
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

import requests
from garth.exc import GarthHTTPError
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)



class TCXUtilitiesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TCX Utilities")
        photo = tk.PhotoImage(file = 'icons/runner-icon.png')
        self.wm_iconphoto(False, photo)
        self.geometry("800x600")

        self.logged_in = False
        self.api = None

        self.pages = {}
        self.current_page = tk.StringVar()
        self.current_page.set("Welcome")

        self.sidebar = tk.Frame(self, bg="gray", width=200)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self.create_sidebar_buttons()
        self.create_welcome_page()
        #self.create_analyze_page()
        #self.create_synchronize_page()

    def create_sidebar_buttons(self):
        buttons = [
            ("Welcome", "icons/welcome-icon.png", 7, self.create_welcome_page),
            ("Analyze", "icons/analyze-icon.png", 5, self.create_analyze_page),
            ("Synchronize", "icons/synchronize-icon.png", 5, self.create_synchronize_page),
            ("Export", "icons/export-icon.png", 13, self.create_export_page),
            ("Settings", "icons/settings-icon.png", 13, self.create_settings_page)
        ]
        for text, icon_path, icon_size, command in buttons:
            icon = tk.PhotoImage(file=icon_path)
            icon = icon.subsample(icon_size, icon_size)
            btn = ttk.Button(self.sidebar, text=text, image=icon, compound="top",
                            command=lambda c=command: self.change_page(c), width=20)
            btn.image = icon  # To prevent garbage collection
            btn.pack(fill="x", padx=5, pady=5)

    def change_page(self, command):
        self.content.destroy()
        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)
        command()

    def create_welcome_page(self):
        self.pages["Welcome"] = tk.Label(self.content, text="Welcome to TCX Utilities!", font=("Helvetica", 24))
        self.pages["Welcome"].pack(pady=50)
    
    def create_export_page(self):
        self.pages["Export"] = tk.Label(self.content, text="Export Page", font=("Helvetica", 24))
        self.pages["Export"].pack(pady=50)

    def create_settings_page(self):
        self.pages["Settings"] = tk.Label(self.content, text="Settings Page", font=("Helvetica", 24))
        self.pages["Settings"].pack(pady=50)

    def create_analyze_page(self):
        self.pages["Analyze"] = tk.Frame(self.content)
        self.pages["Analyze"].pack(fill="both", expand=True)

        #calendar_label = tk.Label(self.pages["Analyze"], text="Calendar")
        #calendar_label.pack()

        # # Add Calendar widget
        # self.calendar = Calendar(self.pages["Analyze"])
        # self.calendar.pack(side="left", padx=(50,0), pady=(30,0), anchor='nw')
        # self.calendar.bind("<<CalendarSelected>>", self.on_frequency_entry_changed)

        # x = [1, 2, 3, 4, 5]
        # y = [2, 3, 5, 7, 11]

        # # Create a new figure
        # fig, ax = plt.subplots(figsize=(1,1))

        # # Plot the data
        # ax.plot(x, y)
        # ax.set_xlabel('X-axis')
        # ax.set_ylabel('Y-axis')
        # ax.set_title('Sample Graph')

        # # Embed the Matplotlib graph into the Tkinter window
        # canvas = FigureCanvasTkAgg(fig, master=self.pages["Analyze"])
        # canvas.draw()
        # canvas.get_tk_widget().pack(side="bottom", padx=(0,0), pady=(0,0), anchor="nw")

        self.calendar = Calendar(self.pages["Analyze"])
        self.calendar.pack(side="left", padx=(50,0), pady=(30,0), anchor='nw')
        self.calendar.bind("<<CalendarSelected>>", self.on_frequency_entry_changed)


        # time_range_label = tk.Label(self.pages["Analyze"], text=time)
        # time_range_label.pack(side="top", padx=(0, 0), pady=(120, 0))

        # Label for frequency dropdown
        frequency_label = tk.Label(self.pages["Analyze"], text="Days:")
        frequency_label.pack(side="top", padx=(0, 10), pady=(80, 0))

        # Dropdown for frequency
        #dropdown1_label = tk.Label(self.pages["Analyze"], text="Time Range")
        #dropdown1_label.pack(side="left", padx=(10, 10), pady=(60, 0), anchor='nw')
        # frequency_options = ["Day", "Week", "Month", "Year"]
        # self.frequency_var = tk.StringVar()
        # self.frequency_dropdown = ttk.Combobox(self.pages["Analyze"], textvariable=self.frequency_var,
        #                                     values=frequency_options)
        # self.frequency_dropdown.pack(side="top", padx=(10, 10), pady=(10, 0))
        self.frequency_var = tk.StringVar()
        self.frequency_entry = tk.Entry(self.pages["Analyze"], textvariable=self.frequency_var)
        self.frequency_entry.pack(side="top", padx=(10, 10), pady=(10, 0))
        self.frequency_entry.bind("<KeyRelease>", self.on_frequency_entry_changed)

        self.time_range_label = tk.Label(self.pages["Analyze"])
        self.time_range_label.pack(side="top", padx=(0, 0), pady=(10, 0))


        # Create a scrollbar
        self.scrollbar = tk.Scrollbar(self.pages["Analyze"], orient=tk.VERTICAL)

        # Create a listbox with scrollbar
        self.listbox = tk.Listbox(self.pages["Analyze"], selectmode=tk.MULTIPLE, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="top", padx=(0, 0), pady=(60, 0))

        # # Add some sample items
        # for i in range(50):
        #     self.listbox.insert(tk.END, f"Item {i+1}")

        self.select_all_button = tk.Button(self.pages["Analyze"], text="Select All", command=self.select_all)
        self.select_all_button.pack(side="top", padx=(0, 0), pady=(20, 0))

        self.stats_button = tk.Button(self.pages["Analyze"], text="View Stats", command=self.select_all)
        self.stats_button.pack(side="top", padx=(0, 0), pady=(20, 0))

        # time = "3/1/2024 - 3/3/2024"

        # # Label for time range
        # time_range_label = tk.Label(self.pages["Analyze"], text=time)
        # time_range_label.pack(side="left", padx=(0, 0), pady=(120, 0), anchor='nw')

        # Dropdown for type
        #dropdown2_label = tk.Label(self.pages["Analyze"], text="Type")
        #dropdown2_label.pack(side="left", padx=(10,5))
        # type_options = ["Statistics", "Graphs", "Splitter"]
        # self.type_var = tk.StringVar()
        # self.type_dropdown = ttk.Combobox(self.pages["Analyze"], textvariable=self.type_var, values=type_options)
        # self.type_dropdown.pack(side="left", padx=(20, 0), pady=(60, 0), anchor='nw')

        # Space to display statistics and graphs
        #display_space = tk.Label(self.pages["Analyze"], text="Space to display statistics and graphs")
        #display_space.pack()
    
    def select_all(self):
        if len(self.listbox.curselection()) == len(self.listbox.get(0, tk.END)):
            self.listbox.selection_clear(0, tk.END)  # Deselect all items
        else:
            self.listbox.select_set(0, tk.END)  # Select all items


    def get_month_num(self, month_name):
        months = ["", "January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        return int(months.index(month_name))
    
    def find_activity_files(self, start_date, end_date):
        folder = "activities"
        if not os.path.exists(folder):
            return []
        
        all_items = os.listdir(folder)
        
        file_list = []
        year_folders = [item for item in all_items if os.path.isdir(os.path.join(folder, item))]
        for year_dirs in year_folders:
            year = year_dirs
            if int(year) >= start_date.year and int(year) <= end_date.year:
                month_folders = [item for item in os.listdir(os.path.join(folder, year)) if os.path.isdir(os.path.join(folder, year, item))]
                for month_dirs in month_folders:
                    month = self.get_month_num(month_dirs)
                    if month >= start_date.month and month <= end_date.month:
                        file_paths = [item for item in os.listdir(os.path.join(folder, year, month_dirs)) if os.path.isfile(os.path.join(folder, year, month_dirs, item))]
                        for file in file_paths:
                            day = file.split("-")[0]
                            if not day.isdigit():
                                continue
                            date = datetime.date(int(year), month, int(day))
                            if date >= start_date and date <= end_date:
                                file_list.append(file)
        
        return file_list


    
    def on_frequency_entry_changed(self, event):
        # This function is called whenever the content of the frequency entry changes
        new_value = self.frequency_var.get()
        if new_value.isdigit() == False:
            return
        # print("Entry changed to:", new_value)

        start_date = self.calendar.selection_get()
        if start_date == None:
            return
        
        end_date = start_date + datetime.timedelta(days = (int(new_value)-1))

        time_range = start_date.strftime("%m/%d/%Y") + " - " + end_date.strftime("%m/%d/%Y")

        self.time_range_label.config(text=time_range)

        activity_list = self.find_activity_files(start_date, end_date)
        
        self.listbox.delete(0, tk.END)
        for activity in activity_list:
            self.listbox.insert(tk.END, activity)
            #args.start_date = today - datetime.timedelta(days = 14)
        #print(f"Downloading activities from {args.start_date} to {args.end_date}")
        # You can perform any actions you want here based on the new value
            
    def create_synchronize_page2(self):
        self.pages["Synchronize2"] = tk.Frame(self.content)
        self.pages["Synchronize2"].pack(fill="both", expand=True)

        self.days_label = tk.Label(self.pages["Synchronize2"], text="Look back days:")
        self.days_label.grid(row=0, column=0, padx=(200, 10), pady=(150,10), sticky="w")
        
        self.days_var = tk.StringVar()
        self.days_entry = tk.Entry(self.pages["Synchronize2"], textvariable=self.days_var)
        self.days_entry.grid(row=0, column=1, padx=(0, 20), pady=(150,10), sticky="w")

        self.download_button = ttk.Button(self.pages["Synchronize2"], text="Download", command=self.download)
        self.download_button.grid(row=1, column=1, columnspan=2, padx=0, pady=10, sticky="w")


    def download(self):
        num_days = self.days_var.get()

        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days = int(num_days))
        print(f"Downloading activities from {start_date} to {today}")
        output = download_activities(self.api, start_date, today, overwrite=True)

        self.activities_label = tk.Label(self.pages["Synchronize2"], text=f"Activities Downloaded: \n{output}")
        self.activities_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="e")


    def create_synchronize_page(self):

        if self.logged_in:
            self.change_page(self.create_synchronize_page2)
            return

        self.pages["Synchronize"] = tk.Frame(self.content)
        self.pages["Synchronize"].pack(fill="both", expand=True)
        
        self.username_label = tk.Label(self.pages["Synchronize"], text="Email:")
        self.username_label.grid(row=0, column=0, padx=(200, 10), pady=(150,10), sticky="e")
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.pages["Synchronize"], textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, padx=(0, 20), pady=(150,10), sticky="w")
        
        self.password_label = tk.Label(self.pages["Synchronize"], text="Password:")
        self.password_label.grid(row=1, column=0, padx=(200, 10), pady=10, sticky="e")
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.pages["Synchronize"], textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="w")
        
        self.login_button = ttk.Button(self.pages["Synchronize"], text="Login", command=self.login)
        self.login_button.grid(row=2, column=1, columnspan=2, padx=0, pady=10, sticky="w")

    def login(self):
        # Implement your login logic here
        username = self.username_var.get()
        password = self.password_var.get()
        print("Username:", username)
        print("Password:", password)

        tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
        tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"

        self.api = init_api(username, password, tokenstore, tokenstore_base64)

        if self.api:
            self.logged_in = True
            self.change_page(self.create_synchronize_page2)
        else:
            print("ERROR LOGGING IN")


def get_month_name(month_num):
    months = ["", "January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return months[int(month_num)]


def download_activities(api, start_date, end_date, overwrite):
    activities = api.get_activities_by_date(start_date, end_date)
    output = ""
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
                output += f"{file_path}\n"
                print(f"Downloaded activity: {file_path}")
    
    return output


def init_api(email, password, tokenstore, tokenstore_base64):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        garmin = Garmin()
        garmin.login(tokenstore) #tokenstore

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
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
            return None

    return garmin


if __name__ == "__main__":
    app = TCXUtilitiesApp()
    app.mainloop()