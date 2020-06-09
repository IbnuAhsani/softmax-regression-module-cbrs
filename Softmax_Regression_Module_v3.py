# -*- coding: utf-8 -*-
"""ScikitLearn - Multinomial Logistic Regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EKf8fGhgNolOaCy2QRD1t9sZJh9s4oA3

[**The link for the tutorial**](https://www.youtube.com/watch?v=2JiXktBn_2M)

**Import Dependencies**
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import sys
import pickle
import numpy as np
import pandas as pd
import seaborn as sn
import sklearn
from sklearn import metrics 
from imblearn.under_sampling import NearMiss
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

np.set_printoptions(threshold=sys.maxsize)

# %matplotlib inline

"""**Data Preprocessing**"""

data_frame = pd.read_csv('/content/drive/My Drive/Colab Notebooks/Content-Based Recommender System Data/Hypothesis Data/data-23-tf-idf.csv', header=None, sep=',')
data_frame.shape

header = []

for i in range(len(data_frame.columns)-1):
  header.append(str(i))

header.append('target')

data_frame.columns = header
print(data_frame.columns)

ax = data_frame['target'].value_counts().plot(kind='bar', figsize=(7,5), fontsize=12);
ax.set_alpha(0.8)

totals = []

for i in ax.patches:
    totals.append(i.get_height())

total = sum(totals)

for i in ax.patches:
    ax.text(i.get_x()-.03, i.get_height()+.5, i.get_height(), fontsize=10)

data_labels = data_frame['target']
data_features = data_frame.drop('target',axis=1)

near_miss = NearMiss(random_state=42)
x_undersampled, y_undersampled = near_miss.fit_sample(data_features, data_labels)

print(x_undersampled.shape)
print(y_undersampled.shape)

data_features_df = pd.DataFrame(data = x_undersampled[0:,0:], 
                                index = [i for i in range(x_undersampled.shape[0])],
                                columns = [str(i) for i in range(x_undersampled.shape[1])])

data_labels_df = pd.DataFrame(data = y_undersampled[0:], 
                                index = [i for i in range(y_undersampled.shape[0])],
                                columns = ['target'])

data_frame_undersampled = data_features_df.join(data_labels_df)

ax = data_frame_undersampled['target'].value_counts().plot(kind='bar', figsize=(7,5), fontsize=12);
ax.set_alpha(0.8)

totals = []

for i in ax.patches:
    totals.append(i.get_height())

total = sum(totals)

for i in ax.patches:
    ax.text(i.get_x()-.03, i.get_height()+.5, i.get_height(), fontsize=10)

data_frame_shuffled_once = data_frame_undersampled.sample(frac=1)
data_frame_shuffled_twice = data_frame_shuffled_once.sample(frac=1)
data_frame_shuffled_twice.sample(3)

target_counts = data_frame['target'].value_counts()
batch_size = 32
beta = .001
learning_rate = 0.001
num_epoch = 101
num_k_splits = 10
num_features = data_frame.shape[1] - 1
num_labels = target_counts.shape[0]

"""**Helper Functions**"""

def to_onehot(y):
  data = np.zeros((num_labels))
  data[y] = 1
  return data

def to_label_list(results):
  label_list = []

  for result in results:
    prediction_label = np.argmax(result)
    label_list.append(prediction_label)
  
  return label_list

def get_accuracy(labels, predictions):
  test_batch_size = predictions.shape[0]
  total_correct_prediction = np.sum(np.argmax(predictions, axis=1) == np.argmax(labels, axis=1))
  accuracy = 100.0 * total_correct_prediction / test_batch_size  
  
  return accuracy

def get_fmeasure(labels, predictions):
  
  fmeasures = {}

  for i in range(num_labels):
    fmeasure_data_dict = {
      "gi": 0,
      "pi_intersect_gi": 0,
    }

    fmeasures[str(i)] = fmeasure_data_dict 
    fmeasure_data_dict = {}

  for i in range(len(labels)):
    label = labels[i]
    prediction = predictions[i]
    fmeasures[str(label)]['gi'] += 1

    if prediction == label:
      fmeasures[str(label)]['pi_intersect_gi'] += 1
  
  total_fmeasure_score = 0

  for i in range(num_labels):
    fmeasure_data = fmeasures[str(i)]
    
    gi = fmeasure_data['gi']
    pi_intersect_gi = fmeasure_data['pi_intersect_gi']
    
    fmeasure_score = (2 * pi_intersect_gi)/(2 * gi)
    total_fmeasure_score += fmeasure_score

  fmeasure_score = total_fmeasure_score / num_labels

  return fmeasure_score

data_labels = data_frame_shuffled_twice['target'].to_numpy()
data_features = data_frame_shuffled_twice.drop('target',axis=1).to_numpy()

fold_counter = 1
strat_kfold = StratifiedKFold(n_splits= num_k_splits)

for train_index, test_index in strat_kfold.split(data_features, data_labels):

  print("\n==================================\n")
  print("Fold: %d" % fold_counter)
  print("\n")
  
  kfold_train_features = data_features[train_index]
  kfold_train_labels = data_labels[train_index]

  kfold_test_features = data_features[test_index]
  kfold_test_labels = data_labels[test_index]
  kfold_test_labels_onehot_encoded = np.array([to_onehot(label) for label in kfold_test_labels])

  classifier = LogisticRegression(random_state=0, multi_class='multinomial', solver='newton-cg')
  model = classifier.fit(kfold_train_features, kfold_train_labels)
  
  test_prediction = model.predict(kfold_test_features)
  test_prediction_proba = model.predict_proba(kfold_test_features)

  test_accuracy = get_accuracy(kfold_test_labels_onehot_encoded, test_prediction_proba)
  print('test_accuracy: ', test_accuracy)

  data_test_label_list = to_label_list(kfold_test_labels_onehot_encoded)
  test_predictions_label_list = to_label_list(test_prediction_proba)
  test_fmeasure = get_fmeasure(data_test_label_list, test_predictions_label_list)
  print('test_fmeasure: ', test_fmeasure)
  print("\n")
  
  # classification report
  # test_classification_report = classification_report(kfold_test_labels, test_prediction)
  # print('classification report')
  # print(test_classification_report)

  test_confusion_matrix = confusion_matrix(kfold_test_labels, test_prediction)
  confusion_matrix_df = pd.DataFrame(test_confusion_matrix, range(num_labels), range(num_labels))
  
  plt.figure(figsize=(8,5))
  sn.set(font_scale=1.0)
  sn.heatmap(confusion_matrix_df, annot=True, fmt='g', cmap="BuPu", annot_kws={"size": 8}) 

  print('confusion matrix')
  plt.show()

  # model_name = 'model_sastrawi_{}.pkl'.format(fold_counter)

  # pickle.dump(model, open(model_name,'wb'))

  fold_counter += 1

# near_miss = SMOTE()
# x_undersampled, y_undersampled = near_miss.fit_sample(data_features, data_labels)

# print(x_undersampled.shape)
# print(y_undersampled.shape)

# smk = SMOTETomek(random_state=42)
# x_undersampled, y_undersampled = smk.fit_sample(data_features, data_labels)

# print(x_undersampled.shape)
# print(y_undersampled.shape)