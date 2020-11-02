# -*- coding:utf-8 -*-
def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("new a path with {path}".format(path=path))
        pass
    pass

if __name__ == "__main__":
    import threading
    import queue
    from cv2 import cv2
    import numpy as np
    import os
    import argparse
    cap = []
    qu = []
    needToRotate = []
    writers = []
    # thr = []
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    isOpened = threading.Event()
    globalSize = None

    parser = argparse.ArgumentParser()
    parser.add_argument("-dn", "--datasetName",
                        help="This dataset creater will create to this dataset name path (default is 'dataset')",
                        default="dataset")
    parser.add_argument(
        "type", help="This is set which type of dataset will be created")
    parser.add_argument("-n", "--camNumber",
                        help="This is number of camera will be opened (default is 1)",
                        type=int, default=1)

    args = parser.parse_args()
    try:
        # initialize the camera to cap list
        for i in range(args.camNumber):
            cap.append(cv2.VideoCapture(i + cv2.CAP_DSHOW))
            # 如果上面程式無法正常執行就用下面這個
            # cap.append(cv2.VideoCapture(i))
            print(cv2.CAP_DSHOW)
            qu.append(queue.Queue())
            pass

        # set cap list to same size (globalSize)
        for i, c in enumerate(cap):
            # 1920 1080
            c.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            c.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
            width = c.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = c.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print("width: ", width, "\nheight: ", height)
            globalSize = (int(width), int(height))

        while not isOpened.is_set():
            frame = []
            # Get frame
            for i, c in enumerate(cap):
                success, fr = c.read()
                if success:
                    frame.append(fr)
                else:
                    frame.append(
                        np.zeros((globalSize[1], globalSize[0], 3), dtype=np.uint8))
                    print("Error reading camera from {i}".format(i=i))
                    pass
                pass

            # Rotate Specified frame
            for ne in needToRotate:
                frame[ne] = np.rot90(frame[ne])
                frame[ne] = cv2.resize(frame[ne], globalSize)
                pass

            # Write frame to file
            for i, w in enumerate(writers):
                w.write(frame[i])
                cv2.putText(frame[i], "Recording", (100, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2, cv2.LINE_AA)
                pass

            # Show the frame
            for f in range(0, len(frame)):
                cv2.imshow("frame"+str(f), frame[f])
                pass

            # keyborad handler with opencv
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                isOpened.set()
                for ca in cap:
                    ca.release()
                break
            elif key == ord('n'):
                """透過 python input 指定要旋轉的 frames"""
                selected_camera = input("Input Rotate Camera>>")
                needToRotate.append(int(selected_camera))
            elif key == ord('r'):
                """開始錄影"""
                DIR = "{datasetName}/{type}".format(
                    datasetName=args.datasetName, type=args.type)
                mkdir(args.datasetName)
                mkdir(DIR)
                counter = len([name for name in os.listdir(DIR)
                               if os.path.isfile(os.path.join(DIR, name))
                               and name[-4:] == ".avi"])
                print("目前有的資料量", counter)
                for i in range(len(cap)):
                    writer = cv2.VideoWriter(DIR + '/' + str(1 + i+counter) + '.avi',
                                             fourcc, 30.0, globalSize)
                    writers.append(writer)
                pass
            elif key == ord('e'):
                """結束錄影"""
                writers = []
                print("Record Done")
                pass
            pass
        pass
    
    # Control + C handler
    except KeyboardInterrupt:
        isOpened.set()
        for c in cap:
            c.release()
    pass
