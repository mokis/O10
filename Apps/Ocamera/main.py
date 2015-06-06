import time
import cv
import Image
import StringIO

import subpub3
reload(subpub3)


def capture_and_compress(capture, capture_size):
    # capture & color transform
    #img_bgr = capture.read()
    for i in range(0,2):
        img_bgr = cv.QueryFrame(capture)
    #if len(img_bgr) == 0:
    #    return ""

    temp_bgr = cv.CreateMat(capture_size[1], capture_size[0], cv.CV_8UC3)
    cv.Resize(img_bgr, temp_bgr)
    
    #src_rgb = cv.CreateMat(capture_size[1], capture_size[0], cv.CV_8UC1)
    #cv.CvtColor(img_bgr, src_rgb, cv.CV_BGR2RGB)

    # to raw string & to jpeg string
    str_img = Image.fromstring("RGB", capture_size, temp_bgr.tostring(), "raw")
    strio = StringIO.StringIO()
    str_img.save(strio, "JPEG")
    send_str = strio.getvalue()
    return send_str


my_ip = "192.168.2.1"

zmq = subpub3.messanger(my_ip)
zmq.pub("cam1", 10060, 0.1)

capture1 = cv.CreateCameraCapture(0)
#capture1_size = [int(cv2.VideoCapture.get(cv2.CV_CAP_PROP_FRAME_WIDTH)),
#                 int(cv2.VideoCapture.get(cv2.CV_CAP_PROP_FRAME_HEIGHT))]

capture1_size = [160,120]

running = True
while running:
    #time.sleep(0.01)
    zmq.synch()
 
    send_str = capture_and_compress(capture1, capture1_size)

    if len(send_str) > 0:
        zmq.send(str(capture1_size[0]) + send_str, "cam1")


