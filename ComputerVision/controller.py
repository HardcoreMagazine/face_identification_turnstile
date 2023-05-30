from personface_ident.personface_ident_alg1 import ComputerVisionController
from personface_ident.personface_ident_alg2 import ComputerVisionControllerAlt
import sys

"""
Second controller handle, does calls based on user input in main.py
"""

args = sys.argv[1:]  # read all run arguments except script name (self)
if args.__contains__('-FA'):
    if args.__contains__('-T'):  # only train model
        cvc = ComputerVisionController()
        cvc.TrainModel()
        exit(0)
    elif args.__contains__('-U'):  # update model and run script as usual
        cvc = ComputerVisionController()
        #cvc.home_path = "" # full project path
        cvc.cam_id = 0 # camera id (0-255)
        cvc.UpdateModel()
        cvc.Start()
elif args.__contains__('-SA'):
    cvcAlt = ComputerVisionControllerAlt()
    #cvcAlt.home_path = "" # full project path
    cvcAlt.cam_id = 0 # camera id (0-255)
    cvcAlt.Start()

