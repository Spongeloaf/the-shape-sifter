# from fastai.imports import *
# from fastai.transforms import *
# from fastai.fastai.conv_learner import *
# from fastai.model import *
# from fastai.fastai.dataset import *
# from fastai.sgdr import *
# from fastai.fastai.plots import *
# import shutil

from fastai.vision import *
from fastai import *

##############
# BEGIN INIT #
##############

# root data path
PATH = "C:\\Users\\peter\\Google Drive\\peter\\python projects\\machine learning\\lego_v3\\"

# image size
sz = 224

#batch size
bs = 128

# Uncomment the below if you need to reset your precomputed activations
#shutil.rmtree(f'{PATH}tmp', ignore_errors=True)

#architecture
arch = resnet34

# fast.ai data object contains all of our data, structured by the fast.ai library
# according to from_paths
data = ImageClassifierData.from_paths(PATH, bs=bs, tfms=tfms_from_model(arch, sz))
learn = ConvLearner.pretrained(arch, data, precompute=False)
learn.load('mtmind_99_percent')


print("CUDA enabled: {0}".format(torch.cuda.is_available()))
# print(torch.backends.cudnn.enabled)
print(os.listdir(PATH))


# xforms, _ = tfms_from_model(arch, sz)
# im = xforms(open_image("E:\\data\\lego_v3\\test\\3003_1.jpg"))
# preds = to_np(learn.models.model(V(T(im[None]).cuda())))
# print(np.argmax(preds, axis=1))

# this gives prediction for validation set. Predictions are in log scale
log_preds = learn.predict()
print(log_preds.shape)

print(log_preds[:10])

preds = np.argmax(log_preds, axis=1)  # from log probabilities to 0 or 1
probs = np.exp(log_preds[:,1])        # pr(dog)

