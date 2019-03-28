import numpy as np
import cv2
import time


def dilate_image(image, kernel):

    image = cv2.dilate(image, kernel)
    return image


def get_fg_mask(frame):
    frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # grayscale the image
    frame_grayscale = cv2.blur(frame_grayscale, (4, 4))  # blur the image to remove noise
    fg_mask = fg_bg.apply(frame_grayscale, learningRate=0.007) # foreground subtractor this gets the B/W image while moving

    return fg_mask


def find_contours(fg_mask):
    # finds contours in the masked frame taken at the same time as the middle frame of the array
    __, contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = fg_mask.shape
    min_x, min_y = width, height
    max_x = max_y = 0

    # compares each contour to the minimum set size and ignores it if smaller
    lego_contours = []
    if len(contours) != 0:
        # find the biggest area
        for c in contours:
            area = cv2.contourArea(c)
            if area > min_contour_size:
                lego_contours.append(c)

    return lego_contours


def get_bounding_rect(image, contours):
    #cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

    height, width, depth = image.shape

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        min_x, min_y = width, height
        max_x = max_y = 0
        min_x, max_x = min(x, min_x), max(x + w, max_x)
        min_y, max_y = min(y, min_y), max(y + h, max_y)
        cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)


    return


def configure_webcam():

    video = cv2.VideoCapture(0)  # opens video capture

    # camera settings
    video.set(39, 0)    # auto focus
    video.set(3, 1920)  # width
    video.set(4, 1080)  # height
    video.set(5, 10)    # framerate
    video.set(10, 150)  # brightness min: 0 , max: 255 , increment:1
    video.set(11, 130)  # contrast min: 0 , max: 255 , increment:1
    video.set(12, 156)  # saturation min: 0 , max: 255 , increment:1 video.set(13, 0 ) # hue
    video.set(14, 15)   # gain min: 0 , max: 127 , increment:1
    video.set(15, -9)   # exposure min: -7 , max: -1 , increment:1
    video.set(22, 255)  # might be gamma?
    video.set(26, 4800) # white_balance min: 4000, max: 7000, increment:1
    video.set(28, 15)   # focus min: 0 , max: 255 , increment:5

    return video


def configure_video_file():
    video = cv2.VideoCapture("video\\one_odd.flv", cv2.CAP_FFMPEG)
    return video


def configure_image():
    frame = cv2.imread("images\\mbg.png")
    fg_mask = get_fg_mask(frame)
    frame = cv2.imread("images\\mfg.png")

    t_frame_start = time.perf_counter()

    fg_mask = get_fg_mask(frame)
    fg_dilated = dilate_image(fg_mask, dilate_kernel)
    contours = find_contours(fg_dilated)
    get_bounding_rect(frame, contours)

    t_frame_stop = time.perf_counter()
    t_frame_time = t_frame_stop - t_frame_start

    # cv2.putText(frame, 'process time: {0:3.3f}'.format(t_frame_time), (10, 100), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('raw_frame', frame)
    cv2.imshow('fg_mask', fg_dilated)
    #cv2.imshow('fg_dilated', fg_dilated)
    wait = True
    while wait:
        # create a window for live viewing of frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return


#########################
#    BEGIN
#########################

# tweakable options
min_contour_size = 500  # the minimum contour size that will be included in the crop
fg_bg = cv2.createBackgroundSubtractorMOG2()  # setup the background subtractor.
image_dump = False
count = 0
font = cv2.FONT_HERSHEY_SIMPLEX
dilate_kernel = cv2.getStructuringElement(2, (8,8))
belt_mask = cv2.imread("mask.bmp")
belt_mask = cv2.cvtColor(belt_mask, cv2.COLOR_BGR2GRAY)  # grayscale the image

video = configure_video_file()
# video = configure_webcam()
# video = configure_image()




while(video.isOpened()):
    t_start = time.perf_counter()

    # grab a frame and render it
    ret, frame = video.read()

    t_frame_start = time.perf_counter()

    fg_mask = get_fg_mask(frame)
    fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=belt_mask)     # Applies a bitmask to the image which removes
    fg_dilated = dilate_image(fg_mask, dilate_kernel)
    contours = find_contours(fg_dilated)
    get_bounding_rect(frame, contours)

    t_frame_stop = time.perf_counter()
    t_frame_time = t_frame_stop - t_frame_start

    cv2.putText(frame, 'process time: {0:3.3f}'.format(t_frame_time), (10, 700), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('raw_frame', frame)
    cv2.imshow('fg_mask', fg_mask)

    # create a window for live viewing of frames
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

        # create a window for live viewing of frames
    if cv2.waitKey(5) & 0xFF == ord('s'):
        image_dump = True

    # keeps the server ticking at 60hz. Measures the duration from the start of the loop (t_start) and waits until 17ms have passed.
    t_stop = time.perf_counter()
    t_duration = t_stop - t_start
    if t_duration < 0.020:
        time.sleep(0.020 - t_duration)

video.release()
cv2.destroyAllWindows()

