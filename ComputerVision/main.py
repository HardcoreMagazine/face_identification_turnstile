import subprocess
import time
from datetime import datetime


"""
First and primary (program) controller handle, interacts with user in order to work
#@ Remember to edit CV configuration (paths, ips, port numbers) in 'controller.py'!!
"""
# Brief: check if script is running as main program or as a module, block "module" run
if __name__ == "__main__":
    default_delay = 20  # positive integer, 1-72
    print(f'@> Select restart delay, hours (enter a number between 1 and 48) [default - {default_delay}h]: ')
    delay = input()
    try:
        delay = float(delay)
        if 0 >= delay > 48:
            print(f'@> Incorrect input, setting restart delay to default value of {default_delay}h')
            delay = default_delay * 60 * 60
        else:
            print(f'@ Setting restart delay to {delay} hours ({delay*60*60} seconds)')
            delay = delay * 60 * 60
    except:
        print(f'@> Incorrect input, setting restart delay to default value of {default_delay}h')
        delay = default_delay * 60 * 60

    print('@> Select algorithm to use (1 - LBPH+HaarCascade, 2 - face_recognition,CNN) [default - 1]: ')
    user_algo = input()

    # case if algo == '1' OR any other number/string, i.e. DEFAULT case
    if user_algo == '1' and user_algo != '2':
        args = ['-FA', '-T']
        # run subprocess to train model (no manual control over process)
        proc_out = subprocess.run(['python', 'controller.py'] + args, capture_output=True, text=True)
        print(proc_out.stdout)
        # begin main script - regular timed update/restart
        while True:
            proc = subprocess.Popen(['python', 'controller.py'] + ['-FA', '-U'])
            time.sleep(delay)  # put this process asleep while CV script is running
            proc.kill() # send SIGKILL signal
            curr_time = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
            print(f"@> SYSTEM RESTART @ {curr_time}")
    else: # case algo == '2'
        while True:
            proc = subprocess.Popen(['python', 'controller.py'] + ['-SA'])
            time.sleep(delay)  # put this process asleep while CV script is running
            proc.kill() # send SIGKILL signal
            curr_time = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
            print(f"@> SYSTEM RESTART @ {curr_time}")


'''
# Alternative path: create photos instead of running face detector
if __name__ == "__main__":
    from utilities.ComputerVisionCamera import ComputerVisionCamera
    cvcam = ComputerVisionCamera()
    cvcam.proj_path = ""
    cvcam.res_path = ""
    cvcam.net_model = ""
    cvcam.camera_id = 0
    cvcam = cvcam.Start()
'''
