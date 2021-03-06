import numpy as np
import cv2
import pandas as pd
import coranking
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from coranking.metrics import trustworthiness, continuity
from constants import MEAN, MAX_BRIGHTNESS, NUMBER_OF_PIXELS


# Load in train data
df = pd.read_csv("../Data/sign_mnist_train.csv")
X_train = df.iloc[:, 1:].values
y_train = df.iloc[:, 0].values

# Load in embedding from deep autoencoders on train data
df_ae_deep = pd.read_csv("../Data/Final_train_ae.csv", header=None)
X_train_ae_deep = df_ae_deep.iloc[:, 0:].values

# Load in embedding from denoised autoencoders on train data
df_ae_denoised = pd.read_csv("../Data/Final_train_denoising_ae.csv", header=None)
X_train_ae_denoised = df_ae_denoised.iloc[:, 0:].values

# Load in test data
df_test = pd.read_csv("../Data/sign_mnist_test.csv")[1500:]
X_test = df_test.iloc[:, 1:].values
y_test = df_test.iloc[:, 0].values

# Load in embedding from deep autoencoders on test data
df_test_ae_deep = pd.read_csv("../Data/Final_test_ae.csv", header=None)
X_test_ae_deep = df_test_ae_deep.iloc[:, 0:].values

# Load in embedding from denoised autoencoders on test data
df_test_ae_denoised = pd.read_csv("../Data/Final_test_denoising_ae.csv", header=None)
X_test_ae_denoised = df_test_ae_denoised.iloc[:, 0:].values

# Contrast train data
X_contrast = np.zeros(np.shape(X_train))
for i in range(len(X_contrast)):
    image = X_train[i, :]
    image = image.astype(np.uint8)
    X_contrast[i] = cv2.equalizeHist(image).reshape(1, NUMBER_OF_PIXELS)

# Normalize train data
X_contrast = X_contrast.astype('float32') / MAX_BRIGHTNESS - MEAN
X_train = X_train.astype('float32') / MAX_BRIGHTNESS - MEAN

# Contrast test data
X_contrast_test = np.zeros(np.shape(X_test))
for i in range(len(X_contrast_test)):
    image = X_test[i, :]
    image = image.astype(np.uint8)
    X_contrast_test[i] = cv2.equalizeHist(image).reshape(1, NUMBER_OF_PIXELS)

# normalize test data
X_contrast_test = X_contrast_test.astype('float32') / MAX_BRIGHTNESS - MEAN
X_test = X_test.astype('float32') / MAX_BRIGHTNESS - MEAN

# Run PCA with n=13 principal components
pca = PCA(n_components=13)
princa = pca.fit_transform(X_contrast)
princa_test = pca.fit_transform(X_contrast_test)

# Pick random subsample to calculate the Measures for for the train data
# we first create numpy arrays with the original data and embeddings together
new_data = np.hstack((X_contrast, princa))
new_data_ae_deep = np.hstack((X_contrast, X_train_ae_deep))
new_data_ae_denoised = np.hstack((X_contrast, X_train_ae_denoised))
n_train = new_data.shape[0]
n_train_ae_deep = new_data_ae_deep.shape[0]
n_train_ae_denoised = new_data_ae_denoised.shape[0]

# Fix a random seed and get a list of random indices with size equal to half the train data size
np.random.seed(0)
random_indices = np.random.choice(n_train, size=13727, replace=False)
random_indices_ae = np.random.choice(n_train_ae_deep, size=13727, replace=False)
random_indices_ae_denoised = np.random.choice(n_train_ae_denoised, size=13727, replace=False)

# Create the random subsample for the pca Measures
random_sample = new_data[random_indices, :]
full_random = random_sample[:, 13:]
pca_random = random_sample[:, :12]

# Create the random subsample for the deep autoencoders Measures
random_ae_sample = new_data_ae_deep[random_indices_ae, :]
full_random_2 = random_ae_sample[:, 13:]
ae_random = random_ae_sample[:, :12]

# Create the random subsample for the denoised autoencoders Measures
random_ae_sample_denoised = new_data_ae_denoised[random_indices_ae_denoised, :]
full_random_3 = random_ae_sample_denoised[:, 13:]
ae_random_denoised = random_ae_sample_denoised[:, :12]

# Calculate coranking matrices
Q = coranking.coranking_matrix(full_random, pca_random)
Q_test = coranking.coranking_matrix(X_contrast_test, princa_test)
Q_ae = coranking.coranking_matrix(full_random_2, ae_random)
Q_ae_test = coranking.coranking_matrix(X_contrast_test, X_test_ae_deep)
Q_ae_denoised = coranking.coranking_matrix(full_random_3, ae_random_denoised)
Q_ae_test_denoised = coranking.coranking_matrix(X_contrast_test, X_test_ae_denoised)

# Calculate and print Measures for PCA on train data
trust_pca = trustworthiness(Q, min_k=1, max_k=25)
cont_pca = continuity(Q, min_k=1, max_k=25)
print('Trustworthiness measure PCA train data set{}'. format(trust_pca))
print('Continuity measure measure PCA train data set{}'. format(cont_pca))

# Calculate and print Measures for pca on test data
trust_pca_test = trustworthiness(Q_test, min_k=1, max_k=25)
cont_pca_test = continuity(Q_test, min_k=1, max_k=25)
print('Trustworthiness measure PCA test data set{}'. format(trust_pca_test))
print('Continuity measure PCA test data set{}'. format(cont_pca_test))

# Calculate and print Measures for deep ae on train data
trust_ae = trustworthiness(Q_ae, min_k=1, max_k=25)
cont_ae = continuity(Q_ae, min_k=1, max_k=25)
print('Trustworthiness measure deep AE train data set{}'. format(trust_ae))
print('Continuity measure deep AE train data set{}'. format(cont_ae))

# Calculate and print Measures for deep ae on test data
trust_ae_test = trustworthiness(Q_ae_test, min_k=1, max_k=25)
cont_ae_test = continuity(Q_ae_test, min_k=1, max_k=25)
print('Trustworthiness measure deep AE test data set{}'. format(trust_ae_test))
print('Continuity measure deep AE test data set{}'. format(cont_ae_test))

# Calculate and print Measures for denoised ae on train data
trust_ae_denoised = trustworthiness(Q_ae_denoised, min_k=1, max_k=25)
cont_ae_denoised = continuity(Q_ae_denoised, min_k=1, max_k=25)
print('Trustworthiness measure denoised AE train data set{}'. format(trust_ae_denoised))
print('Continuity measure denoised AE train data set{}'. format(cont_ae_denoised))

# Calculate and print Measures for denoised ae on test data
trust_ae_test_denoised = trustworthiness(Q_ae_test_denoised, min_k=1, max_k=25)
cont_ae_test_denoised = continuity(Q_ae_test_denoised, min_k=1, max_k=25)
print('Trustworthiness measure denoised AE test data set{}'. format(trust_ae_test_denoised))
print('Continuity measure denoised AE test data set{}'. format(cont_ae_test_denoised))

# Plot Measures for pca on train data
plt.plot(cont_pca, "-m", label="continuity measure")
plt.plot(trust_pca, "-c", label="trustworthiness measure")
plt.legend(loc="upper right")
plt.xlabel('Number of Neighbors')
plt.ylabel('Measure')
plt.title('PCA on training data')
plt.savefig('pca_train_data.png')
plt.show()

# Plot Measures for pca on test data
plt.plot(cont_pca_test, "-m", label="continuity measure")
plt.plot(trust_pca_test, "-c", label="trustworthiness measure")
plt.legend(loc="upper right")
plt.xlabel('Number of Neighbors')
plt.ylabel('Measure')
plt.title('PCA on test data')
plt.savefig('pca_test_data.png')
plt.show()

# Plot Measures for deep AE on train data
plt.plot(cont_ae, "-m", label="continuity measure")
plt.plot(trust_ae, "-c", label="trustworthiness measure")
plt.legend(loc="upper right")
plt.xlabel('Number of Neighbors')
plt.ylabel('Measure')
plt.title('Deep Autoencoder on training data')
plt.savefig('ae_train_data.png')
plt.show()

# Plot Measures for deep AE on test data
plt.plot(cont_ae_test, "-m", label="continuity measure")
plt.plot(trust_ae_test, "-c", label="trustworthiness measure")
plt.legend(loc="upper right")
plt.xlabel('Number of Neighbors')
plt.ylabel('Measure')
plt.title('Deep Autoencoder on test data')
plt.savefig('ae_test_data.png')
plt.show()

# Plot Measures for denoised AE on train data
plt.plot(cont_ae_denoised, "-m", label="continuity measure")
plt.plot(trust_ae_denoised, "-c", label="trustworthiness measure")
plt.legend(loc="upper right")
plt.xlabel('Number of Neighbors')
plt.ylabel('Measure')
plt.title('Denoising Deep Autoencoder on training data')
plt.savefig('ae_train_data_denoised.png')
plt.show()

# Plot Measures for denoised AE on test data
plt.plot(cont_ae_test_denoised, "-m", label="continuity measure")
plt.plot(trust_ae_test_denoised, "-c", label="trustworthiness measure")
plt.legend(loc="upper right")
plt.xlabel('Number of Neighbors')
plt.ylabel('Measure')
plt.title('Denoising Deep Autoencoder on test data')
plt.savefig('ae_test_data_denoised.png')
plt.show()
