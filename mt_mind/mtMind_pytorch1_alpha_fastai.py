import fastai.vision as vision
import time



if __name__ == '__main__':
    # path = "C:\\google_drive\\software_dev\\the_shape_sifter\\mtMind\\lego_v3\\"
    learn = vision.load_learner('C:\\google_drive\\software_dev\\the_shape_sifter\\mtMind\\lego_v3\\', "shitty_first_attempt")


    img = vision.open_image('C:\\google_drive\\software_dev\\the_shape_sifter\\mtMind\\lego_v3\\image.png')

    start = time.perf_counter()
    learner = learn.predict(img)
    stop = time.perf_counter()

    print("{}\n\rThis process took {}".format(learner, (stop - start)))

    start = time.perf_counter()
    learner = learn.predict(img)
    stop = time.perf_counter()

    print("{}\n\rThis process took {}".format(learner, (stop - start)))

    start = time.perf_counter()
    learner = learn.predict(img)
    stop = time.perf_counter()

    print("{}\n\rThis process took {}".format(learner, (stop - start)))

    start = time.perf_counter()
    learner = learn.predict(img)
    stop = time.perf_counter()

    print("{}\n\rThis process took {}".format(learner, (stop - start)))

    start = time.perf_counter()
    learner = learn.predict(img)
    stop = time.perf_counter()

    print("{}\n\rThis process took {}".format(learner, (stop - start)))

    start = time.perf_counter()
    learner = learn.predict(img)
    stop = time.perf_counter()

    print("{}\n\rThis process took {}".format(learner, (stop - start)))