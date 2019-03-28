import torch
from fastai import *
from fastai.vision import *


def main():
    path = "C:\\google_drive\\software_dev\\the_shape_sifter\\mtMind\\categories"
    data = ImageDataBunch.from_folder(path, num_workers=0)

    learn = create_cnn(data, models.resnet50(bs=16), metrics=accuracy)

    learn.fit(1)


if __name__ == '__main__':
    main()
