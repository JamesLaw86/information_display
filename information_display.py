import service_board
from threading import Thread, Lock
import copy
import time
import weather_receiver
from datetime import datetime

from guizero import App, Picture, Text, Box

class DisplayApp(object):
    """
    Application to display rail times, weather, and whatever else
    """
    def __init__(self, **kwargs):
        """
        first start the thread to read data from the internet, then set up the
        user interface controls
        """
        self.current_rail_services = None
        
        if kwargs:
            if 'rail' in kwargs:
                self.current_rail_services = kwargs['rail']
        
        self.mutex = Lock()
        self.stop_data_read = False
        self.data_read_thread = Thread(target = self.read_data_thread)
        self.data_read_thread.daemon = True
        self.data_read_thread.start()

        self.app = App()
        self.app.repeat(15000, self.update_display)
        
        """Add the various controls / widgets"""
        self.controls_dic = {}
        self.current_controls = []   #currently active controls
        self.temp_controls = []    #stuff that changes, e.g. train times
        
        self.add_fixed_controls()

        self.app.bg = (40, 40, 40)
        
        self.app.display()
        

    def read_data_thread(self):
        """
        Read the keys 
        """
        with open('rail_token.txt', 'r') as csv_file:
            train_key = csv_file.read()
        self.rail_board = service_board.service_board(train_key)
        
        with open('weather_key.txt') as txt_file:
            lines = txt_file.readlines()
            key = lines[0]
            self.weatherID = '7290651'
            self.weather_reciever = weather_receiver.cweather_receiver(key)
        
        while not self.stop_data_read:
            try:
                self.update_weather_data()
                self.update_train_data()
            except Exception as e:
                print('Exception occured int read_data_thread\n', e)
            time.sleep(120000)
        
    def update_train_data(self):
        """Call the server to update the current data"""
        rail_services = self.rail_board.get_services('HRH', 10)
        self.mutex.acquire()
        self.current_rail_services = copy.deepcopy(rail_services)
        now = datetime.now()
        self.update_time = now.strftime("%d, %m, %Y, %H:%M")
        self.mutex.release()
        
 
    def add_fixed_controls(self):
        self.train_txt_col = (255, 165, 0)
        padding_text = Text(self.app, '')
        self.train_heading_text = Text(self.app, text = 'Horsham Trains and Weather', 
                                  color = self.train_txt_col)
        
        

    def update_display(self):
        for temp_control in self.temp_controls:
            temp_control.destroy()
        
        self.update_information_display()
    
    
    def update_information_display(self):
        """
        """
        
        if not self.current_rail_services:
            return
        
        box = Box(self.app, layout = 'grid')
        self.temp_controls.append(box)
        
        update_time_text = f"Updated: {self.update_time}"
        temp_text = Text(box, text = update_time_text, size = 8, grid = [0, 0, 2, 1],
        color = self.train_txt_col)   #some space
        self.temp_controls.append(temp_text)
        
        headings = ['Dept', 'Dest', 'Est', 'Platform']
        column = 0
        for heading in headings:
            temp_text = Text(box, text = heading, align = 'left', 
                             grid = [column, 1], color = self.train_txt_col)
            self.temp_controls.append(temp_text)
            column += 1
        
        temp_text = Text(box, text = '', size = 4, grid = [0, 2])    #some space
        
        self.mutex.acquire()
        row = 3
        

        for service_num in list(self.current_rail_services.keys()):
            service = self.current_rail_services[service_num]
            
            train_info = [service.sch_dept,
                          service.destination,
                          service.est_dept,
                          service.platform]
            column = 0
            for info in train_info:
                temp_text = Text(box, text = info + '        ', align = 'left', 
                                 grid = [column, row], size = 11, 
                                 color = self.train_txt_col)
                self.temp_controls.append(temp_text)
                column += 1
            row += 1
        
        #add the weather
        temp_text = Text(box, text = '', grid=[0, row], size = 11)
        column = 0
        if self.current_forecast:
            row += 1
            for weather_point in self.current_forecast:
                weather_text = weather_point.date_time.strftime("%H:%M")
                weather_text += '\n' + weather_point.main_weather
                degree_symbol = '\u00B0'
                temperature = round(float(weather_point.mainT))
                weather_text += '\n' + str(temperature) + degree_symbol
                temp_text = Text(box, text = weather_text, grid=[column, row],
                                 size = 11, 
                                 color = self.train_txt_col)
                column+=1
                self.temp_controls.append(temp_text)
            
        self.mutex.release()
            
    
    def update_weather_data(self):
        forecast = self.weather_reciever.forecast_byID(self.weatherID)
        if not forecast or len(forecast) < 3:
            return
        self.mutex.acquire()
        self.current_forecast = copy.deepcopy(forecast[0:4])
        self.mutex.release()
        
        
def get_trains_for_test():
    with open('rail_token.txt', 'r') as csv_file:
        train_key = csv_file.read()
        rail_board = service_board.service_board(train_key)
        rail_services = rail_board.get_services('HRH', 8)
    return rail_services
    
test = 0
get_data = 0
if test:
    if get_data:
        test_data = {}
        trains = get_trains_for_test()
        test_data['rail'] = trains
    kwargs = test_data
else:
    kwargs = {}

app = DisplayApp(**kwargs)







#import tkinter as tk
#
#window = tk.Tk()
#label = tk.Label(
#    text="Hello, Tkinter",
#    fg="white",
#    bg="black",
#    width=10,
#    height=10
#)
#label.pack()
#window.mainloop()
