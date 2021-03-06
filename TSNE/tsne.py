import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE

# load in train data set
df = pd.read_csv("../Data/sign_mnist_train.csv")
X_train = df.iloc[:, 1:].values
y_train = df.iloc[:, 0].values

# load in embedding from autoencoders on train data
df_ae = pd.read_csv("../Data/Final_train_ae.csv", header=None)
X_train_ae = df_ae.iloc[:, 0:].values

# run t-SNE on autoencoders output
TSNE = TSNE(n_components=2, perplexity=5, learning_rate=100)
TSNE_output = TSNE.fit_transform(X_train_ae)

# make dataframe of t-SNE results
tsneDf = pd.DataFrame(data=TSNE_output)
finalDf = pd.concat([tsneDf, df[['label']]], axis=1)

# Get the two components
finalDf['tsne1'] = finalDf.loc[:, 0].values
finalDf['tsne2'] = finalDf.loc[:, 1].values

# create a two-dimensional plot of the t-SNE results
plt.figure(figsize=(18, 8))
plt.title("2-component t-SNE")
sns.scatterplot(x="tsne1", y="tsne2", hue=y_train, palette=sns.color_palette("hls", 24), data=finalDf, legend="full")
plt.show()
