import os
import time
import cv2
import pickle
import utilities.ExternalHttpRequestHandle as _http
import numpy as np
from os.path import exists
from pathlib import Path
from utilities.ExternalHttpClientHandle import CVHttpClient as cvhc

"""
LBPH algorithm is faster than face_recognition ("alt" algorithm/based on "dlib"), 
but require a lot more samples for good detection (20-40 pictures for each user)
It is highly recommended that samples evenly distributed, i.e. "40 samples of user1, 40 samples of user2",
and not "40 samples of user1, 6 samples of user2".
"""

class ComputerVisionController:
    def __init__(self):
        """
        Called when the class is instantiated.
        It sets up all of the variables that are needed for other functions in the class to run.
        :param self: Represent the instance of the class
        """
        ## Full path to project folder
        self.home_path = 'D:/Files/UNI/DIPLOMA/opencv_scripts/release'
        ## Full path to project resources folder
        self.res_path = f'{self.home_path}/resources'
        ## Haar cascade model (.xml) path
        self.haar_model_path = f'{self.res_path}/models/haarcascade/haarcascade_frontalface_default.xml'
        ## System camera ID (default - 0)
        self.cam_id = 0
        ## Local/private variables for CV/HTTP_SRV/HTTP_CLIENT use
        self.__haarCfr = cv2.CascadeClassifier(self.haar_model_path)
        self.__faceRec = cv2.face.LBPHFaceRecognizer_create()
        self.__labels = {}
        self.__file_index = []
        self.__t_start = time.time()
        self.__lastUser = ''
        self.loc_ip = "192.168.1.6"
        self.loc_port = 8080
        self.ext_ip = "192.168.1.5"
        self.ext_port = 9090
        self.db_ip = "192.168.1.5"

    def __createUserDir(self, user_name):
        """
        Creates a user directory in the images folder.
        The function takes one argument, which is the username of the user who uploaded an image.
        It then creates a path to that users folder using their username and returns it.
        :param user_name
        :return: user path
        """
        user_path = f'{self.res_path}/images/{user_name.lower()}'
        ## Create user folder
        #@ Note: function does not override folder & its contents
        #@ if folder already exists
        Path(user_path).mkdir(exist_ok=True)
        return user_path

    def __seekNextFilename(self, user_dir):
        """
        Used to find the next available filename for a user's profile picture.
        It takes in one argument, which is the directory of the user's folder.
        It then checks if there are any files in that
        directory and returns '0.jpg' if there aren't any files,
        or int+1 from the highest int value found within all
        filenames ending with '.png' or '.jpg'.
        :param user_dir: walk through the user's directory and find all of their files
        :return: Next user's filename available in form of string
        """
        u_files = next(os.walk(user_dir), (None, None, []))[2]
        if not u_files:
            return '1.jpg'
        else:
            temp = []
            for i in range(0, len(u_files)):
                if u_files[i].endswith('png') or u_files[i].endswith('jpg'):
                    temp.append(u_files[i].split('.')[0])
            return f'{int(max(temp)) + 1}.jpg'

    def __checkTimer(self):
        """
        <Helper> function that checks to see if the timer has expired.
        :return: True if timer has expired, else False
        """
        if time.time() - self.__t_start < 12:
            return False
        else:
            return True

    def __triggerGates(self, name):
        """
        [robust]
        Triggers the gates to open.
        Checks if this user was not previously recognized -
        if they are different, triggers
        the gates to open and updates lastUser with new value.
        Else -  it will check if enough time has passed
        since their previous recognition using __checkTimer(). If True,
        it will trigger the gates again
        :param name: User name to log
        """
        if self.__lastUser != name:
            cvhc(self.ext_ip, self.ext_port, self.db_ip).LaunchAndRequest(name)
            self.__lastUser = name
            self.__t_start = time.time()
        elif self.__checkTimer():
            cvhc(self.ext_ip, self.ext_port, self.db_ip).LaunchAndRequest(name)
            self.__t_start = time.time()

    def TrainModel(self):
        """
        Used to train the model.
        It takes no arguments, but it does require a folder structure like this:
            images/person_name_folder (ex.: 'John')/[image files] ('1.png', '2.jpg', etc)
        Tracks time used to train model.
        """
        # Timer mark 1
        t1 = time.time()
        # Create new model
        curr_label_id = 1
        label_ids = {}  ## creates an empty dict
        img_labels = []  ## creates an empty list
        faces_img_list = []
        ## Read files and directories
        for root, dirs, files in os.walk(f'{self.res_path}/images'):
            for file in files:
                ### for each file, folder inside root directory:
                ### if file has image ext:
                #@ Note: this also allows to ignore empty folders
                if file.endswith('png') or file.endswith('jpg'):
                    self.__file_index.append(root.replace('\\', '/') + f'/{file}')
                    #@ Note: label == object/person's name (folder name)
                    label = os.path.basename(root).replace(" ", "-").upper()
                    if label not in label_ids:
                        label_ids[label] = curr_label_id
                        curr_label_id += 1
                    _id = label_ids[label]
                    img_gray = cv2.imread(os.path.join(root, file), flags=cv2.IMREAD_GRAYSCALE)
                    faces = self.__haarCfr.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
                    for (x, y, w, h) in faces:
                        face = img_gray[y:y + h, x:x + w]
                        faces_img_list.append(face)
                        img_labels.append(_id)
        ## Save file index for later use
        with open(f'{self.res_path}/models/lbph/file_index', 'w', encoding='utf-8') as file_i:
            file_i.writelines('\n'.join(self.__file_index))
            file_i.writelines('\n')
        ## Save labels file for later use
        with open(f'{self.res_path}/models/lbph/labels', 'wb') as file_w:
            pickle.dump(label_ids, file_w)
        ## Train model based on detected samples
        self.__faceRec.train(faces_img_list, np.array(img_labels))
        ## Save model (for later use)
        self.__faceRec.save(f'{self.res_path}/models/lbph/trainee.xml')
        # Timer mark 2
        t2 = time.time()
        print(f'CV> Training completed in {round(t2 - t1, 3)} s')

    def UpdateModel(self):
        """
        Used to update the model with new samples (images).
        It will iterate over all folders and files in the 'images' folder,
        and add any new images it finds to the training set.
        It will also create a label for each image, based on its parent
        folder name (the name of that person). If a label already exists for that person,
        it will use that one instead of creating a new one.
        Tracks time used to re-train model.
        """
        ## Check if model already loaded
        if not self.__file_index:
            ## Load model if possible, else - exit with code 1 (error)
            if not self.LoadModel():
                print('CV> No pre-trained model(s) found, unable to update')
                exit(1)
        t1 = time.time()
        curr_cl_id = max(self.__labels) + 1
        label_ids = {val: key for key, val in self.__labels.items()}  ## invert labels dict back to original state
        faces_img_list = []
        img_labels = []
        ## Iterate over images and folders (labels)
        for root, dirs, files in os.walk(f'{self.res_path}/images'):
            for file in files:
                if file.endswith('png') or file.endswith('jpg'):
                    file_str = root.replace('\\', '/') + f'/{file}'
                    if file_str not in self.__file_index:
                        self.__file_index.append(file_str)
                        label = os.path.basename(root).replace(" ", "-").upper()
                        if label not in label_ids:
                            label_ids[label] = curr_cl_id
                            curr_cl_id += 1
                        _id = label_ids[label]
                        img_gray = cv2.imread(os.path.join(root, file), flags=cv2.IMREAD_GRAYSCALE)
                        faces = self.__haarCfr.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=4)
                        for (x, y, w, h) in faces:
                            face = img_gray[y:y + h, x:x + w]
                            faces_img_list.append(face)
                            img_labels.append(_id)
        # Save updated file index
        with open(f'{self.res_path}/models/lbph/file_index', 'w', encoding='utf-8') as file_i:
            file_i.truncate(0)  ### Remove file contents
            file_i.writelines('\n'.join(self.__file_index))
        # Save updated labels in binary file
        with open(f'{self.res_path}/models/lbph/labels', 'wb') as file_l:
            file_l.truncate(0)  ### Remove file contents
            pickle.dump(label_ids, file_l)
        # Update and save model
        self.__faceRec.update(faces_img_list, np.array(img_labels))
        self.__faceRec.save(f'{self.res_path}/models/lbph/trainee.xml')
        t2 = time.time()
        print(f'CV> Update-training completed in {round(t2 - t1, 3)} s')

    def LoadModel(self):
        """
        Used to load the LBPH model from a file.
        :return: True if load successful, else - False
        """
        if exists(f'{self.res_path}/models/lbph/labels') \
                and exists(f'{self.res_path}/models/lbph/trainee.xml') \
                and exists(f'{self.res_path}/models/lbph/file_index'):
            with open(f'{self.res_path}/models/lbph/labels', 'rb') as f_l:
                self.__labels = pickle.load(f_l)  ## read labels file
                self.__labels = {val: key for key, val in self.__labels.items()}  ## invert labels dict
            with open(f'{self.res_path}/models/lbph/file_index', 'r', encoding='utf-8') as f_i:
                self.__file_index = f_i.read().splitlines()
            self.__faceRec.read(f'{self.res_path}/models/lbph/trainee.xml')
            return True
        else:
            return False

    def Start(self):
        """
        Main function of this module.
        It starts a http server on local_IP:8080, loads the
        pre-trained model and begins reading camera feed.
        If no pre-trained model(s) are found, it will
        train one using all images in ./data/faces directory.
        """
        # Launch http server
        _http.HttpServer(self.loc_ip, self.loc_port, self.db_ip).StartInThread()
        # Load local model OR train one if not found
        if not self.LoadModel():
            print('CV> No pre-trained model(s) found, unable to start CV')
            exit(1)
        # Begin reading camera feed
        feed = cv2.VideoCapture(self.cam_id)
        ## check if camera works properly
        if not feed.isOpened():
            print('CV> Unable to access camera')
            exit(1)
        # Parse video feed data
        while cv2.waitKey(1) & 0xFF != ord('q'):
            v_available, frame = feed.read()
            if not v_available:
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.__haarCfr.detectMultiScale(frame_gray, scaleFactor=1.3, minNeighbors=5)
            for (x, y, w, h) in faces:
                try:
                    u_id, confidence = self.__faceRec.predict(frame_gray[y:y + h, x:x + w])
                    if 85 <= confidence < 100:
                        print(f'CV> User: {self.__labels[u_id]}, Confidence: {round(confidence, 5)}%')
                        print(f'CV> User label: {u_id}')
                        # Trigger gates
                        self.__triggerGates(self.__labels[u_id])
                    elif _http.take_frame:
                        u_dir = self.__createUserDir(_http.user)
                        next_filename = self.__seekNextFilename(u_dir)
                        cv2.imwrite(f'{u_dir}/{next_filename}', frame[y:y + h, x:x + w])
                        print(f'CV> Taken photo of \"{_http.user}\"')
                        ## Trigger gates
                        self.__triggerGates(_http.user)
                        ## Reset http-cv variables
                        _http.take_frame = False
                        _http.user = ''
                except Exception as exc:
                    print(f'CV> Unknown error\n{exc}')
                #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.imshow('Live feed', frame)
        # Safe exit
        feed.release()
        #cv2.destroyAllWindows()
