""" Analyzes the webcam feed to find parts. """

# 3rd party imports
import cv2
import time
import math
import numpy as np
from fastai.vision import Image, pil2tensor
from typing import List     # add support for list type hints
from sys import exit
from datetime import datetime


# 1st party imports
from shape_sifter_tools.shape_sifter_tools import create_logger
from ss_classes import ClientParams, PartInstance


# Todo: Add color detection via opencv


class TaxiParams:
    """ Parameters for configuring the taxidermist"""
    def __init__(self, init_params: ClientParams):

        # create logger
        self.logger = create_logger(init_params.log_fname_const, init_params.log_level, "Taxidermist")

        # path to google drive and pipes
        self.pipe_recv = init_params.pipe_recv
        self.pipe_send = init_params.pipe_send
        self.google_path = init_params.google_path

        # openCV Object detection properties
        self.min_contour_size = 1000                                   # the minimum contour size that will be included in the crop
        self.fg_bg = cv2.createBackgroundSubtractorMOG2()             # setup the background subtractor
        self.fg_learningRate = 0.002                                  # background subtractor learning rate
        self.dilate_kernel = cv2.getStructuringElement(2, (4, 7))     # Dilation kernel
        self.font = cv2.FONT_HERSHEY_SIMPLEX                          # Font for drawing part numbers on camera feed

        # Edge mask for conveyor belt. Used to eliminate detection of the belt edges.
        mask = cv2.imread(init_params.belt_mask, cv2.IMREAD_GRAYSCALE)                  # load image
        belt_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        self.belt_mask = np.int8(belt_mask)

        # path to video file, if we are not using the camera.
        # TODO: move this to settings.ini
        self.vid_file = self.google_path + "\\assets\\taxidermist\\video\\multi.flv"

        # Setup video feed
        self.video_source = init_params.video_source
        self.view_video = init_params.view_video
        if init_params.video_source == "cam":
            self.logger.info("params.video_source == cam")
            self.video, self.video_shape = configure_webcam()
        elif init_params.video_source == "vid":
            self.logger.info("params.video_source == vid")
            self.video, self.video_shape = self.configure_video_file()
        else:
            self.logger.critical("Invalid 'video_source' in parameter object. Expected 'cam' or 'vid', got {}. Check settings.ini".format(params.video_source))
            exit(2)

        # log that we're finished
        self.logger.debug("taxi params created successfully")


    def configure_video_file(self):

        video = cv2.VideoCapture(self.vid_file, cv2.CAP_FFMPEG)
        ret, frame = video.read()
        height, width, depth = frame.shape
        shape = [height, width, depth]
        return video, shape


class PartParams:
    """ parameters for each currently visible part on the belt. X and Y coordinates
    taken retrieved from opencv contours, plus the objects center X and Y.

    Part numbers identify and track the parts from one frame to the next by mapping
    the previous parts' center to the nearest center in this frame.
    """

    index = 0

    def __init__(self, center_x=-1, center_y=-1, min_x=-1, min_y=-1, max_x=-1, max_y=-1, status='unknown', part_count=-1):
        # Coordinates
        self.center = (center_x, center_y)
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

        # old/new part list status
        self.status = status

        # Unique index number
        self.index = __class__.index
        __class__.index += 1


def configure_webcam():
    """ Initialize webcam """
    # cv2.ocl.setUseOpenCL(0)
    # video = cv2.VideoCapture(cv2.CAP_DSHOW)  # opens video capture
    video = cv2.VideoCapture(0)  # opens video capture

    # camera settings
    video.set(39, 0)    # auto focus
    video.set(3, 1280)  # width
    video.set(4, 720)   # height
    video.set(5, 10)    # frame rate
    video.set(10, 155)  # brightness min: 0 , max: 255 , increment:1
    video.set(11, 125)  # contrast min: 0 , max: 255 , increment:1
    video.set(12, 140)  # saturation min: 0 , max: 255 , increment:1 video.set(13, 0 ) # hue
    video.set(14, 40)   # gain min: 0 , max: 127 , increment:1
    video.set(15, -10)  # exposure min: -7 , max: -1 , increment:1
    video.set(22, 255)  # might be gamma?
    video.set(26, 3500) # white_balance min: 4000, max: 7000, increment:1
    video.set(28, 20)   # focus min: 0 , max: 255 , increment:5

    width = video.get(3)
    height = video.get(4)
    depth = -1
    shape = [height, width, depth]
    return video, shape


def create_test_data():
    """ Creates fake data for algorithm testing. """
    parts_list = []
    parts_list.append(PartParams(15, 15, 10, 10, 20, 20))
    parts_list.append(PartParams(75, 75, 70, 70, 80, 80))
    parts_list.append(PartParams(125, 125, 120, 120, 130, 130))

    new_list = []
    new_list.append(PartParams(125, 145, 120, 140, 130, 150))
    new_list.append(PartParams(75, 95, 70, 90, 80, 100))
    new_list.append(PartParams(15, 35, 10, 30, 20, 40))

    return parts_list, new_list


def get_fg_mask(frame, params):
    """ Use a background subtractor to get a black and white image of just the moving parts. """
    frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)               # gray scale the image
    frame_grayscale = cv2.blur(frame_grayscale, (7, 7))                     # blur the image to remove noise
    fg_mask = params.fg_bg.apply(frame_grayscale, params.fg_learningRate)   # foreground subtractor gets the B/W image
    return fg_mask


def find_contours(fg_mask, taxi):
    """ finds contours in the masked frame taken at the same time as the middle frame of the array """
    contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width, depth = taxi.video_shape
    min_x, min_y = width, height
    max_x = max_y = 0

    # compares each contour to the minimum set size and ignores it if smaller
    lego_contours = []
    if len(contours) != 0:
        # find the biggest area
        for c in contours:
            area = cv2.contourArea(c)
            if area > taxi.min_contour_size:
                lego_contours.append(c)

    return lego_contours


def get_rects_and_centers(contours, taxi):
    """Returns a list of part_param objects for each set of contours."""

    height, width, depth = taxi.video_shape
    parts_list = []

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        min_x, min_y = width, height
        max_x = max_y = 0
        center_x, center_y = 0,0
        min_x, max_x = min(x, min_x), max(x + w, max_x)
        min_y, max_y = min(y, min_y), max(y + h, max_y)

        # filters out any part still entering the frame
        if min_y < (height * 0.05):
            continue
        # filters out parts leaving the frame
        if max_y > (height * 0.99):
            continue

        # get center
        center_x, center_y = x + int(w / 2), y + int(h / 2)

        # add centers to a list
        part = PartParams(center_x, center_y, min_x, min_y, max_x, max_y)
        parts_list.append(part)

    return parts_list


def draw_rects_and_centers(image, part_list: List[PartParams], params):
    """ Draws bounding rects and index numbers on all parts visible in the frame """
    for part in part_list:
        # draw rect
        cv2.rectangle(image, (part.min_x, part.min_y), (part.max_x, part.max_y), (255, 0, 0), 2)
        cv2.putText(image, str(part.index), part.center, params.font, 1, (0, 0, 255), 3)


def get_center_y(part: PartParams):
    """ Sorting function for map_centers()"""
    return part.center[1]


def update_part_list(new_parts_list: List[PartParams], old_parts_list: List[PartParams], frame, params: TaxiParams):
    """ This function checks the part list and creates newp arts or discards gone parts as necessary.
     It's a hot mess, but it works. """
    try:
        # we are going to move backwards through the list of parts, chopping out any unwanted ones.
        # This is done in reverse because if we remove an item while going forward,
        # all future items have their positions changed.
        i = len(new_parts_list) - 1

        while i > -1:
            # dispatches parts to the BB when they are first seen
            if new_parts_list[i].status == "unknown":

                if new_parts_list[i].center[1] > (params.video_shape[0] * 0.55):
                    new_parts_list[i].status = 'gone'
                    print("ignored")
                    continue

                new_parts_list[i].status = "mapped"
                # new_parts_list[i].part_count = params.count Possibly depreciated
                old_parts_list.append(new_parts_list[i])

                new_part = make_new_part()

                cropped_image = crop_image(new_parts_list[i], frame)
                fastai_image = convert_to_fastai(cropped_image)
                new_part.part_image = fastai_image
                new_part.camera_offset = camera_offset(new_parts_list[i].center[1])

                # Dispatch to server and BB, but not when running stand alone.
                if __name__ != '__main__':
                    dispatch_part(params, new_part)
                    save_image(cropped_image, new_part.instance_id, params)
                else:
                    print("__main__: not dispatched part")
                    params.logger.debug("__main__: not dispatched part")

            # decrement i, so we move backwards through the list
            i -= 1

    except TypeError as e:
        params.logger.debug("Type error in update part list: {}".format(e))

    try:
        i = len(old_parts_list) - 1
        while i > -1:
            if old_parts_list[i].status == 'gone':
                del old_parts_list[i]
                i -= 1
                continue

            if old_parts_list[i].status == 'mapped':
                old_parts_list[i].status = 'gone'
            i -= 1
    except TypeError as e:
        params.logger.debug("Type error in update part list: {}".format(e))


def convert_to_fastai(frame):
    """ Makes an opencv::mat image into a fastai compatible image. """
    swapped_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_fastai = Image(pil2tensor(swapped_image, dtype=np.float32).div_(255))

    # using Umat. I found it to be slow, but I'm leaving it here for posterity.
    # mat_image = cv2.UMat.get(swapped_image)
    # img_fastai = Image(pil2tensor(mat_image, dtype=np.float32).div_(255))

    return img_fastai


def map_centers(old: List[PartParams], new: List[PartParams]):
    """ Expects two lists of part params. Both lists will have their centers extracted
    and the new object centers will be mapped to the closest (without going backwards)
    object center in the new list. """

    # TODO: try and improve/remove this
    try:
        if len(old) == 0 and len(new) == 0:
            return
    except TypeError:
        return

    new.sort(key=get_center_y)
    old.sort(key=get_center_y)

    lo = len(old) - 1

    # true when there are no current parts, return since there's nothing to map
    if lo == -1:
        return

    # will be skipped if the old list is empty
    for lo in range(len(old)):
        dl = []
        for ln in range(len(new)):

            # does not allow mapping to any part that has been claimed by another part.
            if new[ln].status != 'unknown':
                dl.append(99999)
                continue

            # does not allow mapping to parts closer to the top edge of the screen
            if new[ln].center[1] < (old[lo].center[1] - 5):
                dl.append(99999)
                continue

            # get distance between centers using pythagorean theorem and append it to array dl
            dx = new[ln].center[0] - old[lo].center[0]
            dy = new[ln].center[1] - old[lo].center[1]
            dl.append(math.sqrt((dx * dx) + (dy * dy)))

        # find the closest match by distance
        try:
            match = dl.index(min(dl))

            # when the part is leaving the screen, it will not be in the new parts list.
            # This if statement will abort mapping if all the new parts are claimed
            # which will leave the status of this parts at 'gone'. It will be removed from the list next update.
            if new[match].status == 'mapped':
                continue

            if dl[match] > 1000:
                continue

            old[lo].center = new[match].center
            old[lo].min_x = new[match].min_x
            old[lo].min_y = new[match].min_y
            old[lo].max_x = new[match].max_x
            old[lo].max_y = new[match].max_y
            old[lo].status = 'mapped'
            new[match].status = 'mapped'

        except ValueError:
            pass

    return


def crop_image(part_param: PartParams, frame):
    """ Crops a raw frame to just the image of a desired part. """
    cropped_part_image = frame[part_param.min_y:part_param.max_y, part_param.min_x:part_param.max_x]
    return cropped_part_image


def crop_image_umat(part_param: PartParams, frame):
    """ An attempt at using Umat instead of regular cv2 mat images.
    It didn't save any time, but I'm leaving it here for posterity."""

    cropped_part_image = cv2.UMat(frame, [[part_param.min_y, part_param.max_y], [part_param.min_x, part_param.max_x]])
    return cropped_part_image


def save_image(image, name, params: TaxiParams):
    """ Saves the part image to the disk"""
    cv2.imwrite(params.google_path + "\\assets\\taxidermist\\new_part_images\\{0}.png".format(name), image)  # writes image to disk
    params.logger.debug("saved image")


def make_new_part():
    """ Creates a new PartInstance object """

    now = datetime.now()
    instance_id = now.strftime("%H%M%S%f")
    # instance_id = time.strftime("%H%M%S")
    part_color = ''
    part_number = ''
    category_number = ''
    category_name = ''
    server_status = 'new'
    bb_status = 'new'

    part = PartInstance(
        instance_id=instance_id,
        part_number=part_number,
        category_number=category_number,
        part_color=part_color,
        category_name=category_name,
        server_status=server_status,
        bb_status=bb_status,
        serial_string='',
    )
    return part


def camera_offset(y_coord: int):
    return 4.080101 * y_coord + 675.1549


def dispatch_part(params: TaxiParams, part: PartInstance):
    """ Sends a part to the server """
    params.logger.debug("Part dispatched to server")
    params.pipe_send.send(part)


def main(client_params: ClientParams):
    """ Main Taxidrmist function
    Analyses a video file or camera feed, and dispatches part instance objects as they pass by.
    In theory, each part is tracked from one frame to the next, and is only dispatched once to the server. """

    # initialization
    taxi = TaxiParams(client_params)
    taxi.logger.debug(taxi.video_source)
    old_list, new_list = [], []
    taxi.logger.info("taxidermist started")

    # main loop
    while taxi.video.isOpened:

        t_start = time.perf_counter()

        # TODO: add capability to receive control signals from the server
        # client_params.pipe_recv()

        # grab a frame and render it
        ret, raw_frame = taxi.video.read()
        t_frame_start = time.perf_counter()
        # uframe = cv2.UMat(frame)
        process_frame = np.copy(raw_frame)
        process_frame = cv2.dilate(process_frame, taxi.dilate_kernel)
        fg_mask = get_fg_mask(process_frame, taxi)
        fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=taxi.belt_mask)     # Applies a bitmask to the image which removes
        fg_dilated = cv2.dilate(fg_mask, taxi.dilate_kernel)
        contours = find_contours(fg_dilated, taxi)

        new_list = get_rects_and_centers(contours, taxi)
        map_centers(old_list, new_list)
        update_part_list(new_list, old_list, raw_frame, taxi)

        if taxi.view_video == "1":
            t_frame_stop = time.perf_counter()
            t_frame_time = t_frame_stop - t_frame_start

            draw_rects_and_centers(raw_frame, old_list, taxi)

            cv2.putText(raw_frame, 'process time: {0:3.3f}'.format(t_frame_time), (10, 700), taxi.font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('raw_frame', raw_frame)
            # cv2.imshow('fg_mask', fg_mask)

            # create a window for live viewing of frames
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # keeps the taxidermist ticking at 30hz.
        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.032:
            time.sleep(0.032 - t_duration)

    taxi.video.release()
    cv2.destroyAllWindows()


def taxi_sim(params: ClientParams):
    """Simulates the taxidermist
    Randomly sends PartInstance objects to the server. """

    import random
    while True:
        t_start = time.perf_counter()
        rnjezus = random.randint(1, 3)
        if rnjezus == 1:
            now = datetime.now()
            instance_id = now.strftime("%H%M%S%f")

            part_image = 'some picture'
            part_color = ''
            part_number = ''
            category_number = ''
            category_name = ''
            server_status = 'new'
            bb_status = 'new'


            part = PartInstance(
                part_image=part_image,
                instance_id=instance_id,
                part_number=part_number,
                category_number=category_number,
                part_color=part_color,
                category_name=category_name,
                server_status=server_status,
                bb_status=bb_status,
                serial_string=''
            )
            params.pipe_send.send(part)

        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 1:
            time.sleep(1 - t_duration)


def main_new(taxi: TaxiParams):
    # initialization

    taxi.logger.debug(taxi.video_source)
    old_list, new_list = [], []
    taxi.logger.info("taxidermist started")

    # main loop
    while taxi.video.isOpened:

        t_start = time.perf_counter()
        t_frame_start = time.perf_counter()

        ret, frame = taxi.video.read()

        # Converting the image to grayscale.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Using the Canny filter with different parameters
        edges_high_thresh = cv2.Canny(gray, 20, 50)

        masked = cv2.bitwise_and(edges_high_thresh, edges_high_thresh, mask=taxi.belt_mask)  # Applies a bitmask to the image which removes

        dilated = cv2.dilate(masked, taxi.dilate_kernel)

        contours = find_contours(dilated, taxi)

        new_list = get_rects_and_centers(contours, taxi)
        map_centers(old_list, new_list)
        update_part_list(new_list, old_list, frame, taxi)

        if taxi.view_video == "1":
            t_frame_stop = time.perf_counter()
            t_frame_time = t_frame_stop - t_frame_start

            draw_rects_and_centers(frame, old_list, taxi)

            cv2.putText(frame, 'process time: {0:3.3f}'.format(t_frame_time), (10, 700), taxi.font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # cv2.imshow('raw_frame', frame)
            cv2.imshow('fg_mask', frame)

            # create a window for live viewing of frames
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # keeps the taxidermist ticking at 30hz.
        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.032:
            time.sleep(0.032 - t_duration)




# Running standalone
if __name__ == '__main__':
    from ss_classes import ServerInit, ClientParams, PartInstance

    server_init = ServerInit()
    params = ClientParams(server_init, 'taxi')
    Taxi = TaxiParams(params)
    main_new(Taxi)

