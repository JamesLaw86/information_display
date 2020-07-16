import service_board
from threading import Thread, Lock
import copy
import time

from guizero import App, Picture, Text, Box
from enum import Enum

class CurrentDisplay(Enum):
    TRAINS = 1
    WEATHER = 2

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
        self.app.repeat(5000, self.update_display)
        
        """Add the various controls / widgets"""
        self.controls_dic = {}
        self.current_controls = []   #currently active controls
        self.temp_controls = []    #stuff that changes, e.g. train times
        
        self.add_train_controls()
        self.current_display = CurrentDisplay.TRAINS
        
        self.add_weather_controls()

        self.app.bg = (40, 40, 40)
        
        self.set_display()
        self.app.display()
        

    def read_data_thread(self):
        """
        Read the keys 
        """
        with open('rail_token.txt', 'r') as csv_file:
            train_key = csv_file.read()
        self.rail_board = service_board.service_board(train_key)
        while not self.stop_data_read:
            try:
                pass
                #self.update_train_data()
            except:
                print('Exception occured int read_data_thread')
            time.sleep(10000)
        
    def update_train_data(self):
        """Call the server to update the current data"""
        rail_services = self.rail_board.get_services('VIC', 8)
        self.mutex.acquire()
        self.current_rail_services = copy.deepcopy(rail_services)
        self.mutex.release()
        
 
    def add_train_controls(self):
        self.train_txt_col = (255, 165, 0)
        train_heading_text = Text(self.app, text = 'Horsham Trains', 
                                  color = self.train_txt_col)
        
        
        self.horsham_pic = Picture(self.app, image='horsham_station.jpg')
        self.horsham_pic.height = int(self.horsham_pic.height /4)
        self.horsham_pic.width = int(self.horsham_pic.width /4)
        
        self.controls_dic[CurrentDisplay.TRAINS] = [train_heading_text, self.horsham_pic]
        


    def add_weather_controls(self):
        weather_heading_text = Text(self.app, text = 'Horsham Weather')
        
        self.weather_pic = Picture(self.app, image='horsham_weather.jpg')
        self.weather_pic.height = int(self.horsham_pic.height )
        self.weather_pic.width = int(self.horsham_pic.width)
        
        weather_heading_text.hide()
        self.weather_pic.hide()
        self.controls_dic[CurrentDisplay.WEATHER] = [weather_heading_text, self.weather_pic]
        
    def update_display(self):
        """
        
        """
        if self.current_display is CurrentDisplay.TRAINS and False:
            self.current_display = CurrentDisplay.WEATHER
        elif self.current_display is CurrentDisplay.WEATHER:
            self.current_display = CurrentDisplay.TRAINS
        self.set_display()
    
    
    def set_display(self):
        """
        Set the currently active display. Need to destroy temporary controls,
        hide the previous current controls and show the new current controls
        """
        for temp_control in self.temp_controls:
            temp_control.destroy()
        
        self.temp_controls = []
        
        for control in self.current_controls: #hide the current set of controls
            control.hide()
            
        self.current_controls = self.controls_dic[self.current_display]  #show the new set
        for control in self.current_controls:
            control.show()
        
        if self.current_display is CurrentDisplay.TRAINS:
            self.set_train_display()
        else:
            self.set_weather_display()
    
    def set_train_display(self):
        """
        """
        
        if not self.current_rail_services:
            return
        
        text_color = (255,165,0)
        box = Box(self.app, layout = 'grid')
        self.temp_controls.append(box)
        
        temp_text = Text(box, text = '', size = 8, grid = [0, 0])   #some space
        
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
        for service_num in reversed(list(self.current_rail_services.keys())):
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
            
        self.mutex.release()
            
        
    def set_weather_display(self):
        pass
        
def get_trains_for_test():
    with open('rail_token.txt', 'r') as csv_file:
        train_key = csv_file.read()
        rail_board = service_board.service_board(train_key)
        rail_services = rail_board.get_services('VIC', 8)
    return rail_services
    

test = 0
if test:
    kwargs = {}
    trains = get_trains_for_test()
    kwargs['rail'] = trains

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
