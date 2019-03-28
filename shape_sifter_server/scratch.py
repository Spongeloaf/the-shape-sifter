"""
Insert Docstring here

:return: none
"""

import cv2
import numpy as np
import datetime
import time

def draw_rectangle(kept_frame, kept_fgmask, min_contour_size):   # grayscale, find contours, crop to rectangle

    # finds contours in the masked frame taken at the same time as the middle frame of the array
    __, contours, hierarchy = cv2.findContours(kept_fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # compares each contour to the minimum set size and ignores it if smaller
    legoContours = []
    if len(contours) != 0:
        # find the biggest area
        for c in contours:
            area = cv2.contourArea(c)
            if area > min_contour_size:
                legoContours.append(c)

    ####################################################################################
    # gets the largest and smallest X and Y coordinates to draw a rectangle around all of the relevant contours
    try:
        hierarchy = hierarchy[0]
    except:
        hierarchy = []

    height, width = kept_fgmask.shape
    min_x, min_y = width, height
    max_x = max_y = 0

    for contour, hier in zip(legoContours, hierarchy):
        (x, y, w, h) = cv2.boundingRect(contour)
        min_x, max_x = min(x, min_x), max(x + w, max_x)
        min_y, max_y = min(y, min_y), max(y + h, max_y)
        # if w > 80 and h > 80:
        #     cv2.rectangle(kept_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    if max_x - min_x > 0 and max_y - min_y > 0:
        # cv2.rectangle(kept_frame, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)
        cropped = kept_frame[min_y:max_y, min_x:max_x]
        return cropped

# Tweakable variables
min_contour_size = 500  # the minimum contour size that will be included in the crop
background_difference_const = 50  # Used to decide if there is a part in the frame

fgbg = cv2.createBackgroundSubtractorMOG2()  # setup the background subtractor.

# video = cv2.VideoCapture(0)  # opens video capture
video = cv2.VideoCapture("video\\one_at_a_time.flv", cv2.CAP_FFMPEG)

# camera settings
# video.set(39, 0)    # auto focus
# video.set(3, 1920)  # width
# video.set(4, 1080)  # height
# video.set(5, 10)    # framerate
# video.set(10, 150)  # brightness min: 0 , max: 255 , increment:1
# video.set(11, 130)  # contrast min: 0 , max: 255 , increment:1
# video.set(12, 156)  # saturation min: 0 , max: 255 , increment:1 video.set(13, 0 ) # hue
# video.set(14, 15)   # gain min: 0 , max: 127 , increment:1
# video.set(15, -9)   # exposure min: -7 , max: -1 , increment:1
# video.set(22, 255)  # might be gamma?
# video.set(26, 4800) # white_balance min: 4000, max: 7000, increment:1
# video.set(28, 15)   # focus min: 0 , max: 255 , increment:5

# the array that images get popped from
pano_image_list = []
fgmask_image_list = []


# initial background image is all black and the shape of the camera frame
background_img = np.zeros((int(video.get(4)), int(video.get(3))), np.uint8)

# Main Loop
while True:

    # grab the next video frame and process it
    capture_running_status, new_frame = video.read()
    print(capture_running_status)
    # if there isn't a new frame, wait 15ms and start the loop over.
    # if not capture_running_status:
    #     time.sleep(15)
    #     continue

    cv2.imshow('frame', new_frame)

    # grayscale the image and blur it for foreground/background subtractor
    image_grayscale = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)  # grayscale the image
    image_gray_blurred = cv2.blur(image_grayscale, (3, 3))  # blur the image to remove noise
    fg_mask = fgbg.apply(image_gray_blurred, learningRate=0.2) # foreground subtractor this gets the B/W image while moving

    # calculates the Mean Squared Error for image comparison
    mean_squared_err = np.sum((background_img.astype("float") - fg_mask.astype("float")) ** 2)
    mean_squared_err /= float(background_img.shape[0] * fg_mask.shape[1])

    # creates the array of images
    if mean_squared_err > background_difference_const:  # as long as there are frames check if the frame is the same as base
        pano_image_list.append(new_frame)      # appends relevant image to array
        fgmask_image_list.append(fg_mask)   # appends masked image to mask array

    # if there is nothing in the frame then a piece has gone through
    else:
        # If the list has items pop the middle frame and save it
        if pano_image_list:
            # print('if pano image list')
            keep_frame = pano_image_list.pop(int(len(pano_image_list) / 2))  # pops the middle image of the array
            keep_fg_mask = fgmask_image_list.pop(int(len(fgmask_image_list) / 2))  # pops the middle mask of the array
            image_cropped = draw_rectangle(keep_frame, keep_fg_mask, min_contour_size)  # crops image to bounding rect of all contours

            # create a part object and send it to the server
            now = datetime.datetime.now()
            instance_id = now.strftime('%H%M%S%f')

            # bb_packet = ss.bb_packet(command='A', argument='0', payload=instance_id, type='BBC')
            # pipe_to_bb.send(bb_packet)

            capture_time = time.monotonic()
            # make_new_part = ss.part_instance(instance_id=instance_id,part_image=image_cropped, server_status='new', capture_time=capture_time)
            # pipe_me_send.send(make_new_part)
            print("BB packet: {}", instance_id)
            pano_image_list = []    # wipes the array before the loop restarts
            fgmask_image_list = []  # wipes the mask array before the loop restarts

            #  writes image to disk for posterity
            cv2.imwrite("images\image_{0}.png".format(time.process_time()), image_cropped)