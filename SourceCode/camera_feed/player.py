import threading
from camera_feed.exceptions import BadVideoFile
from camera_feed.logger import logger
import cv2


class Loop:
    def __init__(self, file_path: str, control: list = None) -> None:
        if not control == None:
            logger.warning("Please Pass a list variable")
            logger.warning("Boolean Values will not work")
            self.__control = control

        self.__file_path = file_path
        self.thread = None

    def play(self):
        logger.debug("Loop : \tStarting the thread ")
        try:
            cap = cv2.VideoCapture(self.__file_path)
        except Exception as e:
            logger.critical("Failed to load the file")
            logger.error(str(e))
            raise BadVideoFile

        while cap.isOpened() and self.__control[0]:
            ret, frame = cap.read()
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(
                "window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )

            if ret:
                cv2.imshow("window", frame)
            else:
                logger.warning("No Video")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    # def play(self):
    #     logger.debug("Loop Play thread is created")
    #     self.thread = threading.Thread(target=self.__thread)
    #     self.thread.start()
