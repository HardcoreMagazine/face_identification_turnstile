import cv2
import os
from pathlib import Path


class ComputerVisionCamera:
    def __init__(self):
        """
        Called when the class is instantiated.
        Sets up the instance variables.
        Folder in which program running in must have similar to this example structure.
        :param self: represent the instance of the class
        :param proj_path: path to project folder
        :param res_path: path to resources subfolder
        :param camera_id: id of camera to use. Default value is 0,
        which means there is only 1 camera connected to computer
        """
        self.proj_path = 'D:/Files/UNI/DIPLOMA/opencv_scripts/release'
        self.res_path = f'{self.proj_path}/resources'
        self.net_model = f'{self.res_path}/models/haarcascade/haarcascade_frontalface_default.xml'
        self.camera_id = 0

    def __createUserDir(self):
        """
        Creates a new user directory in the 'images' folder if folder is not present,
        else - returns value without overriding folder or its contents.
        :return: path string OR False when no label is provided
        """
        # Get user input
        user_label = input('@ Enter user label (name): ').lower()
        if not user_label or user_label.isspace():
            print('@ Empty label entered')
            return False
        user_dir = f'{self.res_path}/images/{user_label}'
        ## Create user folder, no override if already present
        # @ Note: throws exception if 'proj_path' incorrect
        # @ (locked for R/W or does not exists)
        Path(user_dir).mkdir(exist_ok=True)
        return user_dir

    def __seekNextFilename(self, user_dir):
        """
        <Helper> function that takes in the user's directory as an argument.
        It then checks to see if there are any files in the directory,
        and if not, returns '0.jpg' as the next filename.
        If there are files present, it will iterate through them and find which
        one has the highest index number (the first part of the filename before '.jpg'/'.png').
        It will then return a string with that index + 1 followed by '.jpg'. This ensures that no two
        files have identical names.
        :param user_dir: user's directory
        :return: The next filename in the sequence as string
        """
        u_files = next(os.walk(user_dir), (None, None, []))[2]
        if not u_files:
            return '1.jpg'
        else:
            maxIndex = 1
            for i in range(0, len(u_files)):
                if u_files[i].endswith('png') or u_files[i].endswith('jpg'):
                    temp = int(u_files[i].split('.')[0])
                    if temp > maxIndex:
                        maxIndex = temp
            return f'{maxIndex + 1}.jpg'

    def Start(self):
        """
        Main function of this class. It creates a directory for the user,
        and then begins reading from the camera feed.
        If it detects a face, it will draw a green rectangle around
        that face on screen.
        When user presses 'p' key, program will save that image to disk in selected user directory.
        """
        save = False
        next_filename = None
        u_dir = self.__createUserDir()
        if not u_dir:
            exit(1)
        ## Begin reading camera feed
        feed = cv2.VideoCapture(self.camera_id)
        ## Check if camera works properly
        if not feed.isOpened():
            print('@ Unable to access camera')
            exit(1)
        ## Read selected model:
        haarClassifier = cv2.CascadeClassifier(self.net_model)
        ## Parse video feed data
        while cv2.waitKey(1) & 0xFF != ord('q'):
            video_available, frame = feed.read()
            if not video_available:
                break
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_faces = haarClassifier.detectMultiScale(gray_frame, 1.3, 5)
            if cv2.waitKey(1) & 0xFF == ord('p'):
                next_filename = self.__seekNextFilename(u_dir)
                save = True
            for (x, y, w, h) in detected_faces:
                if save:
                    cv2.imwrite(f'{u_dir}/{next_filename}', frame[y:y + h, x:x + w])
                    print(f'@> Saved image as {u_dir}/{next_filename}')
                    save = False
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow('Live feed', frame)
        # Exit
        feed.release()
        cv2.destroyAllWindows()

