import cv2
from camera_feed.logger import logger
from camera_feed.exceptions import BadCameraInterface
import time
import os
import threading


class LiveFeedback(threading.Thread):
    def __init__(self, uri: str, control: list, windowName: str) -> None:
        threading.Thread.__init__(self)
        self.__uri = uri
        self.__control = control
        self.__windowName = windowName

    def run(self) -> None:
        cap = cv2.VideoCapture(self.__uri)
        logger.debug(f"LiveFeedack: \t capture initialized")
        while cap.isOpened() and self.__control[0]:
            ret, frame = cap.read()
            logger.debug(
                f"LiveFeedback: \tRead from the capture successfully :'\t{ret}"
            )
            cv2.imshow(self.__windowName, frame)
            logger.debug(
                f"LiveFeedback: \tShowed on {self.__windowName} successfully :'\t{ret}"
            )
            cv2.waitKey(1)

        cap.release()
        # cv2.waitKey(1)
        # cv2.destroyWindow(self.__windowName)
        cv2.waitKey(15)

        logger.debug("LiveFeedback : \t Ending the thread target")


class Recorder:
    def __init__(
        self,
        name: str,
        uri: any,
        path: str = os.path.abspath(os.getcwd()),
        frame_rate: int = 24,
    ) -> None:
        self.__uri = uri
        self.__name = f"{name}.avi"
        self.__frame_rate = frame_rate
        self.__path = path

    def record(self, duration_in_sec: int):
        cap = cv2.VideoCapture(self.__uri)

        # Check if camera opened successfully
        if cap.isOpened() == False:
            logger.critical("Unable to read camera feed")
            raise BadCameraInterface

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        logger.debug(f"Resolution of the frame = {(frame_width, frame_height)}")

        out = cv2.VideoWriter(
            f"{self.__path}/{ self.__name}",
            cv2.VideoWriter_fourcc("M", "J", "P", "G"),
            24.0,
            (frame_width, frame_height),
        )
        time1 = round(time.time())
        dur = 0
        while dur < duration_in_sec:
            ret, frame = cap.read()

            if ret == True:

                out.write(frame)

                dur = round(time.time()) - time1

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        logger.info(
            f"File Recorded at {self.__frame_rate} fps and saved at {self.__path}/{ self.__name}"
        )
