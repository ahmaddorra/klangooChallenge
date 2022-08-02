import os
from pyvirtualdisplay import Display
os.environ["DISPLAY"] = ":1"
display = Display(visible=0, size=(1920,1080))
display.start()

