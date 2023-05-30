import os
import time
import cv2
import re
import face_recognition as fr
import numpy as np
import utilities.ExternalHttpRequestHandle as _http
from utilities.ExternalHttpClientHandle import CVHttpClient as cvhc

class ComputerVisionControllerAlt:
    def __convertToRGB(self, images_arr):
        """
        Converts imageset from BGR to RGB.
        This is necessary because OpenCV reads images as BGR,
        but face_recognition displays them as RGB.
        :param images_arr: list of BGR images
        :return: list of RGB images
        """
        converted_images_arr = []
        for img in images_arr:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            converted_images_arr.append(img)
        return converted_images_arr

    def __findEncodings(self, images_arr):
        """
        Extracts encodings from list of converted RGB images.
        :param images_arr: list of RGB images
        :return: A list of encodings
        """
        encoding_arr = []
        images_arr = self.__convertToRGB(images_arr)
        for img in images_arr:
            encoding = fr.face_encodings(img)[0]
            encoding_arr.append(encoding)
        return encoding_arr

    def __checkTimer(self):
        if time.time() - self.__t_start < 12:
            return False
        else:
            return True

    def __triggerGates(self, name):
        if self.__lastUser != name:
            cvhc(self.ext_ip, self.ext_port, self.db_ip).LaunchAndRequest(name)
            self.__lastUser = name
            self.__t_start = time.time()
        elif self.__checkTimer():
            cvhc(self.ext_ip, self.ext_port, self.db_ip).LaunchAndRequest(name)
            self.__t_start = time.time()

    def __init__(self):
        # Define global variables
        self.proj_path = 'D:/Files/UNI/DIPLOMA/opencv_scripts/release'
        self.res_path = f'{self.proj_path}/resources'
        self.cam_id = 0
        self.__images = []  # image bytes array
        self.__class_names = []  # figure names
        self.__t_start = time.time()
        self.__lastUser = ''
        # Read image files
        __dir_files = os.listdir(f'{self.res_path}/images_alt')  # get list of directory files
        for file in __dir_files:  # process listed files
            current_image = cv2.imread(f'{self.res_path}/images_alt/{file}')
            self.__images.append(current_image)
            # removes number, '.ext' from file name
            # and adds resulting name classifier in array
            self.__class_names.append(re.sub("\d+", " ", os.path.splitext(file)[0].upper()))
        self.__known_encodings = self.__findEncodings(self.__images)
        self.loc_ip = "192.168.1.6"
        self.loc_port = 8080
        self.ext_ip = "192.168.1.5"
        self.ext_port = 9090
        self.db_ip = "192.168.1.5"

    def Start(self):
        """
        Main function of this module. It initializes
        HTTP server and begins reading the camera feed.
        The video feed is then parsed for faces, which are then
        compared to known encodings in order to
        determine if *this* person is known to the system.
        If it has, the gates will be triggered (opened); otherwise, an image
        of that person's face will be saved for
        later processing (only if user has & used special plastic card).
        """
        _http.HttpServer(self.loc_ip, self.loc_port, self.db_ip).StartInThread()
        # Begin reading camera feed
        feed = cv2.VideoCapture(self.cam_id)
        # Check if camera works properly
        if not feed.isOpened():
            print('CV_FR> Unable to access camera')
            exit(1)
        # Parse video feed data
        while cv2.waitKey(1) & 0xFF != ord('q'):
            video_continue, frame = feed.read()
            if not video_continue:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = fr.face_locations(frame_rgb)
            encodings = fr.face_encodings(frame_rgb, faces)
            for encoded_face, face_location in zip(encodings, faces):
                match = fr.compare_faces(self.__known_encodings, encoded_face)
                face_distance = fr.face_distance(self.__known_encodings, encoded_face)
                match_index = np.argmin(face_distance)
                if match[match_index]:
                    name = self.__class_names[match_index].upper()
                    print(f'CV_FR> Detected: {name} @ Distance = {1-face_distance[match_index]}')
                    ## Trigger gates
                    self.__triggerGates(name)
                else:
                    #print('CV_FR> Detected: UNKNOWN')
                    if _http.take_frame:
                        x, y = face_location[3], face_location[0]
                        h, w = face_location[1] - face_location[3], face_location[2] - face_location[0]
                        cv2.imwrite(f'{self.res_path}/images_alt/{_http.user}.jpg', frame[y:y+h, x:x+w])
                        print(f'CV_FR> Taken photo of \"{_http.user}\"')
                        ## Trigger gates
                        self.__triggerGates(_http.user)
                        ## Reset http-cv variables
                        _http.take_frame = False
                        _http.user = ''
                #cv2.rectangle(frame, (face_location[3], face_location[0]),
                #              (face_location[1], face_location[2]), (0, 255, 0), 2)
            #cv2.imshow('Live feed', frame)
        # Safe exit
        feed.release()
        #cv2.destroyAllWindows()
