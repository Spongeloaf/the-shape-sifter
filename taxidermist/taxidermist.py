import cv2
import time
import math
from shape_sifter_tools import part_instance
from typing import List     # add support for list type hints
from sys import exit
from datetime import datetime
# Todo: Add color detection via opencv


class TaxiParams:
    """ Parameters for configuring the taxidermist"""
    def __init__(self, mode="1", feed="1", vid_file="video\\multi.flv", mask="newmask.bmp"):
        # adjustable parameters
        self.mode = mode
        self.min_contour_size = 700  # the minimum contour size that will be included in the crop
        self.fg_bg = cv2.createBackgroundSubtractorMOG2()  # setup the background subtractor.
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.dilate_kernel = cv2.getStructuringElement(2, (8, 8))
        self.belt_mask = cv2.imread(mask)
        self.belt_mask = cv2.cvtColor(self.belt_mask, cv2.COLOR_BGR2GRAY)  # gray scale the image
        self.feed = feed
        self.vid_file = vid_file
        self.count = 0
        self.pipe_to_bb = ""


class PartParams:
    """ parameters for each currently visible part on the belt. X and Y coordinates
    taken retrieved from opencv contours, plus the objects center X and Y.

    Valid statuses are: !!! ALL OUTDATED!!!!

    # TODO: UPDATE THIS LIST!!!

    'new': will begin tracking and dispatch a message to the Belt Buckle
    'known': Part has been dispatched, and we're waiting for it to leave the camera
    'ignore': part is either moving off the bottom of the screen, or still entering from the top(meaning we don't have a full picture of it yet).

    Part numbers are a simple int, starting from zero. They're used to identify and
    track the parts from one frame to the next by mapping the previous parts' center
    to the nearest center in this frame.
    """

    index = 0

    def __init__(self, center_x=-1, center_y=-1, min_x=-1, min_y=-1, max_x=-1, max_y=-1, status='unknown', part_count=-1):

        self.center = (center_x, center_y)
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.status = status
        self.part_count = part_count
        self.index = __class__.index
        __class__.index += 1
        # TODO: Figure out how to implement this properly:
        # self.image = []


def dilate_image(image, kernel):

    image = cv2.dilate(image, kernel)
    return image


def get_fg_mask(frame, params):
    frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # grayscale the image
    frame_grayscale = cv2.blur(frame_grayscale, (7, 7))  # blur the image to remove noise
    fg_mask = params.fg_bg.apply(frame_grayscale, learningRate=0.002) # foreground subtractor this gets the B/W image while moving

    return fg_mask


def find_contours(fg_mask, params):
    # finds contours in the masked frame taken at the same time as the middle frame of the array
    contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = fg_mask.shape
    min_x, min_y = width, height
    max_x = max_y = 0

    # compares each contour to the minimum set size and ignores it if smaller
    lego_contours = []
    if len(contours) != 0:
        # find the biggest area
        for c in contours:
            area = cv2.contourArea(c)
            if area > params.min_contour_size:
                lego_contours.append(c)

    return lego_contours


def get_rects_and_centers(image, contours):
    """Returns a list of part_param objects for each set of contours."""

    height, width, depth = image.shape
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

        # # flags deletion for parts about to leave the frame
        # if max_y > (height * 0.97):
        #     part.status = "gone"

        parts_list.append(part)

    return parts_list


def draw_rects_and_centers(image, part_list: List[PartParams], params):

    for part in part_list:
        # draw rect
        cv2.rectangle(image, (part.min_x, part.min_y), (part.max_x, part.max_y), (255, 0, 0), 2)
        cv2.putText(image, str(part.part_count), part.center, params.font, 1, (0, 0, 255), 3)


def get_center_y(part: PartParams):
    return part.center[1]


def configure_webcam():

    video = cv2.VideoCapture(0)  # opens video capture

    # camera settings
    video.set(39, 0)    # auto focus
    video.set(3, 1280)  # width
    video.set(4, 720)   # height
    video.set(5, 10)    # framerate
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


def configure_video_file(params: TaxiParams):
    video = cv2.VideoCapture(params.vid_file, cv2.CAP_FFMPEG)
    ret, frame = video.read()
    height, width, depth = frame.shape
    shape = [height, width, depth]
    return video, shape


def create_test_data():
    parts_list = []
    parts_list.append(PartParams(15, 15, 10, 10, 20, 20))
    parts_list.append(PartParams(75, 75, 70, 70, 80, 80))
    parts_list.append(PartParams(125, 125, 120, 120, 130, 130))

    new_list = []
    new_list.append(PartParams(125, 145, 120, 140, 130, 150))
    new_list.append(PartParams(75, 95, 70, 90, 80, 100))
    new_list.append(PartParams(15, 35, 10, 30, 20, 40))

    return parts_list, new_list


def update_part_list(new_parts_list: List[PartParams], old_parts_list: List[PartParams], frame, params: TaxiParams):

    try:
        # we are going to move backwards through the list of parts, chopping out any unwanted ones.
        # This is done in reverse because if we remove an item while going forward,
        # all future items have their positions changed.
        i = len(new_parts_list) - 1

        while i > -1:
            # dispatches parts to the BB when they are first seen
            if new_parts_list[i].status == "unknown":
                new_parts_list[i].status = "mapped"
                new_parts_list[i].part_count = params.count

                old_parts_list.append(new_parts_list[i])
                cropped_part_image = crop_image(new_parts_list[i], frame)
                new_part = make_new_part(cropped_part_image)
                save_image(new_part, params.count)
                params.count += 1

                # Dispatch to server and BB, but not when running stand alone.
                if __name__ != '__main__':
                    dispatch_part(new_part, params.pipe_to_bb)
                    print("Part dispatched to BB")

            # decrement i, so we move backwards through the list
            i -= 1

    except TypeError:
        pass

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
    except TypeError:
        pass


def map_centers(old: List[PartParams], new: List[PartParams], shape):
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
            print("value error in map centers()")

    return


def crop_image(part_param: PartParams, frame):

    cropped_part_image = frame[part_param.min_y:part_param.max_y, part_param.min_x:part_param.max_x]

    return cropped_part_image


def save_image(part: part_instance, count):
    """ Saves the part image to the disk"""
    cv2.imwrite("images\{0}.png".format(part.instance_id), part.part_image)  # writes image to disk
    print("saved images: {0}".format(count))


def make_new_part(cropped_part_image):

    # create a part object and send it to the server
    now = datetime.now()
    instance_id = now.strftime("%H%M%S%f")
    # instance_id = time.strftime("%H%M%S")
    part_color = ''
    part_number = ''
    category_number = ''
    category_name = ''
    server_status = 'wait_mtm'
    bb_status = 'new'

    part = part_instance(
        instance_id=instance_id,
        part_image=cropped_part_image,
        part_number=part_number,
        category_number=category_number,
        part_color=part_color,
        category_name=category_name,
        server_status=server_status,
        bb_status=bb_status,
        serial_string='',
    )
    return part


def dispatch_part(part_instance: part_instance):
    # TODO: make it work!
    pass


def main_client(mode, feed, vid_file=""):

    # initialize
    params = TaxiParams(mode, feed, vid_file)

    if params.mode is "1":
        video, video_shape = configure_webcam()

    elif params.mode is "2":
        video, video_shape = configure_video_file(params.vid_file)
    else:
        exit(2)

    old_list, new_list = [], []


    while video.isOpened:

        t_start = time.perf_counter()

        # grab a frame and render it
        ret, frame = video.read()
        t_frame_start = time.perf_counter()

        fg_mask = get_fg_mask(frame, params)
        fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=params.belt_mask)     # Applies a bitmask to the image which removes
        fg_dilated = dilate_image(fg_mask, params.dilate_kernel)
        contours = find_contours(fg_dilated, params)

        new_list = get_rects_and_centers(frame, contours)
        map_centers(old_list, new_list, video_shape)
        update_part_list(new_list, old_list, frame)

        if params.feed == "1":
            draw_rects_and_centers(frame, old_list, params)

            t_frame_stop = time.perf_counter()
            t_frame_time = t_frame_stop - t_frame_start

            cv2.putText(frame, 'process time: {0:3.3f}'.format(t_frame_time), (10, 700), params.font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('raw_frame', frame)
            cv2.imshow('fg_mask', fg_mask)

            # create a window for live viewing of frames
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # keeps the taxidermist ticking at 30hz. Measures the duration from the start of the loop (t_start) and waits until 17ms have passed.
        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.032:
            time.sleep(0.032 - t_duration)

    video.release()
    cv2.destroyAllWindows()


def main_standalone():
    """ Runs the taxidermist without the server. Will not attempt to dispatch parts to the server or belt buckle """

    mode_str = input("Choose your operating mode (default = camera:\ncamera = 1\nvideo file = 2\n")
    if mode_str is not ("2" or "1"):
        mode_str = "1"

    cam_str = input("Choose your output mode (default = view camera feed:\nview camera feed = 1\nhide camera feed = 2\n")
    if cam_str is not ("2" or "1"):
        cam_str = "1"

    # initialize
    params = TaxiParams(mode_str, cam_str)

    if params.mode is "1":
        video, video_shape = configure_webcam()

    elif params.mode is "2":
        video, video_shape = configure_video_file(params)
    else:
        exit(2)

    assert video_shape != False
    assert video != False

    old_list, new_list = [], []

    while video.isOpened:

        t_start = time.perf_counter()

        # grab a frame and render it
        ret, frame = video.read()

        t_frame_start = time.perf_counter()

        fg_mask = get_fg_mask(frame, params)
        fg_mask = cv2.bitwise_and(fg_mask, fg_mask, mask=params.belt_mask)     # Applies a bitmask to the image which removes
        fg_dilated = dilate_image(fg_mask, params.dilate_kernel)
        contours = find_contours(fg_dilated, params)

        new_list = get_rects_and_centers(frame, contours)
        map_centers(old_list, new_list, video_shape)
        update_part_list(new_list, old_list, frame, params)

        if params.feed == "1":

            draw_rects_and_centers(frame, old_list, params)
            t_frame_stop = time.perf_counter()
            t_frame_time = t_frame_stop - t_frame_start
            cv2.putText(frame, 'process time: {0:3.3f}'.format(t_frame_time), (10, 700), params.font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('raw_frame', frame)
            cv2.imshow('fg_mask', fg_mask)

            # create a window for live viewing of frames
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # keeps the taxidermist ticking at 30hz. Measures the duration from the start of the loop (t_start) and waits until 17ms have passed.
        t_stop = time.perf_counter()
        t_duration = t_stop - t_start
        if t_duration < 0.032:
            time.sleep(0.032 - t_duration)

    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main_standalone()