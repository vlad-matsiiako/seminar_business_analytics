import pandas as pd
import cv2
import numpy as np
import skdim

# load in the data
df = pd.read_csv("../Data/sign_mnist_train.csv")
features = df.columns[1:]
X_train = df.loc[:, features].values
y = df.loc[:,['label']].values

#contrast data
X_contrast = np.zeros(np.shape(X_train))
for i in range(len(X_contrast)):
    image = X_train[i,:]
    image = image.astype(np.uint8)
    X_contrast[i] = cv2.equalizeHist(image).reshape(1,784)

X_contrast = X_contrast.astype('float32') / 255.0 - 0.5

CD = skdim.id.CorrInt(k1=10, k2=40, DM=False).fit_predict(X_train)
EigValue = skdim.id.lPCA(ver='FO', alphaRatio=0.1, alphaFO=0.1, verbose=False, fit_explained_variance=False).fit_predict(X_train)
#MLE = skdim.id.MLE(dnoise=None, sigma=0, n=None, integral_approximation='Haro', unbiased=False, neighborhood_based=True, K=10).fit_predict(x)
print(EigValue)
print(CD)
#print(MLE)