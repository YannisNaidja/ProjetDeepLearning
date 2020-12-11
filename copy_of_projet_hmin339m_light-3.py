# -*- coding: utf-8 -*-
"""Copy_of_Projet_HMIN339M_light.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TG9hi_wIOsHTzQQExzcocEK4qMb91aGs

# **Préparer les données**

### **Monter le dossier dans Drive**
"""

from google.colab import drive
drive.mount('/content/drive')

import os
os.chdir('/content/drive/My Drive/Projet_HMIN339M')

"""### **Importation de quelques librairies**"""

import numpy as np
import tifffile
import glob
from pathlib import Path
import pandas as pd

"""### **Lecture de la série temporelle d'images et Normalisation par bande sur la série temporelle entre 0 et 1**

#### **Lecture des images et création des séries temporelles de bandes**
"""

# Récupérer la liste des images
lst_img = glob.glob ('Images/*.tif')
lst_img.sort() # ordonner par date si ce n'est pas le cas
lst_img

# Lecture de la bande du rouge (B1) pour toute la série temporelle
red_ts = []
for img in lst_img:
  red_ts.append( tifffile.imread(img)[:,:,0]) # Rouge
red_ts = np.dstack(red_ts)
red_ts.shape

# Lecture de la bande du vert (B2) pour toute la série temporelle
green_ts = []
for img in lst_img:
  green_ts.append( tifffile.imread(img)[:,:,1]) # Vert
green_ts = np.dstack(green_ts)
green_ts.shape

# Lecture de la bande du bleu (B3) pour toute la série temporelle
blue_ts = []
for img in lst_img:
  blue_ts.append( tifffile.imread(img)[:,:,2]) # Bleu
blue_ts = np.dstack(blue_ts)
blue_ts.shape

# Lecture de la bande du proche infrarouge (B4) pour toute la série temporelle
nir_ts = []
for img in lst_img:
  nir_ts.append( tifffile.imread(img)[:,:,3]) # Proche infra rouge
nir_ts = np.dstack(nir_ts)
nir_ts.shape

# Calculer des indices spectraux comme le NDVI

"""#### **Normalisation en utilisant le min et le max des bandes sur les séries temporelles**"""

# Normalisation des séries temporelles par bande: Rouge
red_ts_norm = ( red_ts - red_ts.min() ) / ( red_ts.max() - red_ts.min() ).astype(np.float32)
red_ts_norm.min() , red_ts_norm.max(), red_ts_norm.shape, red_ts_norm.dtype

# Normalisation des séries temporelles par bande: Vert
green_ts_norm = ( green_ts - green_ts.min() ) / ( green_ts.max() - green_ts.min() ).astype(np.float32)
green_ts = None
green_ts_norm.min() , green_ts_norm.max(), green_ts_norm.shape, green_ts_norm.dtype

# Normalisation des séries temporelles par bande: Bleu
blue_ts_norm = ( blue_ts - blue_ts.min() ) / ( blue_ts.max() - blue_ts.min() ).astype(np.float32)
blue_ts = None
blue_ts_norm.min() , blue_ts_norm.max(), blue_ts_norm.shape, blue_ts_norm.dtype

# Normalisation des séries temporelles par bande: Proche infrarouge
nir_ts_norm = ( nir_ts - nir_ts.min() ) / ( nir_ts.max() - nir_ts.min() ).astype(np.float32)
nir_ts_norm.min() , nir_ts_norm.max(), nir_ts_norm.shape, nir_ts_norm.dtype

# Normaliser les indices spectraux que vous aurez calculé

"""### **Lecture de la vérité terrain et récupération des positions des pixels du jeu d'entraînement et de test**

#### **Lecture des fichiers de la vérité terrain**
"""

# Lire le fichier correspondant aux classes d'occupation du sol
gt_class = tifffile.imread ('Verite_terrain/DORDOGNE_VT_CLASS.tif')
gt_class.shape , gt_class.dtype

# Lire le fichier correspondant aux identifiants
gt_id = tifffile.imread ('Verite_terrain/DORDOGNE_VT_ID.tif')
gt_id.shape, gt_id.dtype

"""#### **Récupération des positions des pixels d'entraînement et de test**"""

# Récupérer les positions des échantillons d'entraînement et test
idx_train_ = np.where ( (gt_id!=0) & (gt_class!=0) )
idx_test = np.where ( (gt_id!=0) & (gt_class==0) )

# Lecture des identifiants et labels des échantillons d'entraînement
train_id_ = gt_id[idx_train_]
train_y_ = gt_class[idx_train_]
f'échantillons d\'entrainement: {train_y_.shape[0]} pixels, {len(np.unique(train_id_))} objets'

# Lecture des identifiants et labels des échantillons de test
test_id = gt_id[idx_test]
f'échantillons test: {test_id.shape[0]} pixels, {len(np.unique(test_id))} objets'

"""### **Création d'un jeu de validation en prenant une partie du jeu d'entraînement**
Pour cela, on s'assure de faire la division en mettant les pixels ayant le même identifiant dans un seul et même lot
"""

# Dataframe pour créer un jeu de validation
samples = pd.DataFrame({'ID':train_id_,'Class':train_y_})
samples = samples.drop_duplicates(keep='first')
samples.head(5)

# 30% des échantillons de chaque classe affecté au jeu de validation
train_id = []
valid_id = []
for c in np.unique(samples.Class.values) :
    samples_c = samples.loc[samples.Class==c]
    samples_frac = samples_c.sample(frac=0.7,random_state=1234) 
    train_id.extend( samples_frac.ID.values )
    valid_id.extend( samples_c.drop(samples_frac.index).ID.values )
len(train_id),len(valid_id)

"""### **Récupération des positions des nouveaux échantillons d'entraînement et de validation**"""

# Récupérer les positions des nouveaux échantillons d'entraînement et validation
idx_train = np.where ( np.isin(gt_id,train_id) )
idx_valid = np.where ( np.isin(gt_id,valid_id) )

"""### **Lire finalement les labels correspondant aux nouveaux échantillons d'entraînement, de validation et test**"""

train_y = gt_class[idx_train]
valid_y = gt_class[idx_valid]
test_y = gt_class[idx_test]
train_y.shape, valid_y.shape, test_y.shape

"""### **Lire finalement les identifiants correspondant aux nouveaux échantillons d'entraînement, de validation et test**"""

# utile pour les aggrégations au niveau objet
# train_id_array = gt_id[idx_train] # Pas vraiment nécessaire pour les échantillons d'entraînements
valid_id_array = gt_id[idx_valid]
test_id_array = gt_id[idx_test]
#train_id_array.shape, 
valid_id_array.shape, test_id_array.shape

"""### **Lire finalement les valeurs des séries temporelles correspondant aux nouveaux échantillons d'entraînement, de validation et test**

#### **Pour un Perceptron multi-couche**
"""

# Un perceptron multi-couche ou un algo classique de machine learning requiert un tableau 2D du type 
# (nombre d'échantillons, nombre de features=(nombre de dates x nombre de bandes))
# Vous pouvez rajouter au stack les indices spectraux normalisés que vous aurez calculé

train_X = np.column_stack ( ( blue_ts_norm[idx_train], green_ts_norm[idx_train], red_ts_norm[idx_train], nir_ts_norm[idx_train] ) )

valid_X = np.column_stack ( ( blue_ts_norm[idx_valid], green_ts_norm[idx_valid], red_ts_norm[idx_valid], nir_ts_norm[idx_valid] ) )

test_X = np.column_stack ( ( blue_ts_norm[idx_test], green_ts_norm[idx_test], red_ts_norm[idx_test], nir_ts_norm[idx_test] ) )

train_X.shape, valid_X.shape, test_X.shape

"""#### **Pour un CNN 1D ou temporel**"""

# Un CNN 1D ou temporel requiert un tableau 3D du type (nombre d'échantillons, nombre de dates, nombre de bandes)
# Vous pouvez rajouter à la liste des bandes les indices spectraux normalisés que vous aurez calculé
train_X = []
for band in [blue_ts_norm,green_ts_norm,red_ts_norm,nir_ts_norm]:
    train_X.append( band[idx_train] ) 
train_X = np.stack(train_X,axis=-1)

valid_X = []
for band in [blue_ts_norm,green_ts_norm,red_ts_norm,nir_ts_norm]:
    valid_X.append( band[idx_valid] ) 
valid_X = np.stack(valid_X,axis=-1)

test_X = []
for band in [blue_ts_norm,green_ts_norm,red_ts_norm,nir_ts_norm]:
    test_X.append( band[idx_test] ) 
test_X = np.stack(test_X,axis=-1)

train_X.shape, valid_X.shape, test_X.shape

"""#### **Pour un CNN2D ou spatial avec exemple d'imagettes ou patchs de 5 sur 5 en largeur et hauteur** 

Des patchs de 9 sur 9 sur l'ensemble des échantillons sont un peu trop gourmands en RAM pour Google Colab
"""

# Un CNN 2D ou spatial requiert un tableau 3D du type (nombre d'échantillons, largeur, hauteur, nombre de features= (nombre de dates x nombre de bandes) )
# Vous pouvez rajouter à la liste des bandes les indices spectraux normalisés que vous aurez calculé

# Training
# 1- précaution pour ne pas considérer les pixels dont on ne peut extraire des patchs car trop près du bord
idx_col = idx_train[0]
idx_row = idx_train[1]
coords = np.column_stack((idx_col,idx_row))
coords = coords[np.where( ( np.isin(coords[:,0],np.arange(2,blue_ts_norm.shape[0]-2,1)) ) & ( np.isin(coords[:,1],np.arange(2,blue_ts_norm.shape[1]-2,1)) ) ) ]
# len(coords)
# 2- créer un tableau avec les patchs
train_X = []
for coord in coords :
  lst = []
  for band in [blue_ts_norm,green_ts_norm,red_ts_norm,nir_ts_norm]:
    lst.append( band[coord[0]-2:coord[0]+3,coord[1]-2:coord[1]+3] )
  train_X.append(np.stack(lst,axis=-1).reshape(5,5,-1))
train_X = np.stack(train_X,axis=0)
train_X.shape

train_X[:,2,2,:,:].reshape(train_X.shape[0],-1).shape, train_X[:,2,2,:,:].shape, train_X.reshape(train_X.shape[0],5,5,-1).shape

train_y.shape, np.unique(train_y)

train_X[:,1:4,1:4,:,:].shape

# Validation
# 1- précaution pour ne pas considérer les pixels dont on ne peut extraire des patchs car trop près du bord
idx_col = idx_valid[0]
idx_row = idx_valid[1]
coords = np.column_stack((idx_col,idx_row))
coords = coords[np.where( ( np.isin(coords[:,0],np.arange(2,blue_ts_norm.shape[0]-2,1)) ) & ( np.isin(coords[:,1],np.arange(2,blue_ts_norm.shape[1]-2,1)) ) ) ]
# len(coords)
# 2- créer un tableau avec les patchs
valid_X = []
for coord in coords :
  lst = []
  for band in [blue_ts_norm,green_ts_norm,red_ts_norm,nir_ts_norm]:
    lst.append( band[coord[0]-2:coord[0]+3,coord[1]-2:coord[1]+3] )
  valid_X.append(np.stack(lst,axis=-1).reshape(5,5,-1))
valid_X = np.stack(valid_X,axis=0)
valid_X.shape

# Test
# 1- précaution pour ne pas considérer les pixels dont on ne peut extraire des patchs car trop près du bord
idx_col = idx_test[0]
idx_row = idx_test[1]
coords = np.column_stack((idx_col,idx_row))
coords = coords[np.where( ( np.isin(coords[:,0],np.arange(2,blue_ts_norm.shape[0]-2,1)) ) & ( np.isin(coords[:,1],np.arange(2,blue_ts_norm.shape[1]-2,1)) ) ) ]
# len(coords)
# 2- créer un tableau avec les patchs
test_X = []
for coord in coords :
  lst = []
  for band in [blue_ts_norm,green_ts_norm,red_ts_norm,nir_ts_norm]:
    lst.append( band[coord[0]-2:coord[0]+3,coord[1]-2:coord[1]+3] )
  test_X.append(np.stack(lst,axis=-1).reshape(5,5,-1))
test_X = np.stack(test_X,axis=0)
test_X.shape

"""### **Sauvegarde des données d'entraînement, de validation et test en fichier numpy**"""

# Ainsi de cette façon vous pourrez continuer directement avec la création des modèles et en libérant la mémoire de tout ce qui a été fait précédemment
Path('data').mkdir(exist_ok=True, parents=True)
np.save('data/train_X.npy',train_X)
np.save('data/train_y.npy',train_y)
# np.save('data/train_id.npy',train_id_array)

np.save('data/valid_X.npy',valid_X)
np.save('data/valid_y.npy',valid_y)
np.save('data/valid_id.npy',valid_id_array)

np.save('data/test_X.npy',test_X)
np.save('data/test_id.npy',test_id_array)

"""Videz la mémoire en redémarrant l'environnement d'exécution

# **Votre modèle de deep learning**

### **Remontage de Drive et Importation de quelques librairies**
"""

from google.colab import drive
drive.mount('/content/drive')

import os
os.chdir('/content/drive/My Drive/Projet_HMIN339M')
import numpy as np
import pandas as pd
import tifffile
from pathlib import Path
from sklearn.metrics import f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, Conv1D, GlobalAveragePooling1D, GlobalAveragePooling2D, BatchNormalization, MaxPooling2D
from tensorflow.keras.models import Sequential

"""### **Recharger les données d'entraînement, de validation et test en fichier numpy**"""

# Recharger les données après avoir vidé la mémoire
train_X = np.load('data/train_X.npy')
train_y = np.load('data/train_y.npy')

valid_X = np.load('data/valid_X.npy')
valid_y = np.load('data/valid_y.npy')
valid_id = np.load('data/valid_id.npy')

test_X = np.load('data/test_X.npy')
test_id = np.load('data/test_id.npy')
train_X.shape, train_y.shape, valid_X.shape, valid_y.shape, valid_id.shape, test_X.shape, test_id.shape

"""### **Encoder les labels entre 0 et 4 de sorte à matcher les prédictions des réseaux de neurones**"""

encoder = LabelEncoder()
encoder.fit(train_y)
train_y_enc = encoder.transform(train_y)
valid_y_enc = encoder.transform(valid_y)
np.unique(train_y), np.unique(train_y_enc), np.unique(valid_y), np.unique(valid_y_enc)

"""### **Définition séquentielle de votre modèle avec Keras**

N'oubliez pas de spécifier l'input shape qui varie en fonction des types d'architectures, le nombre de neurones de la couche de sortie qui équivaut au nombre de classes que vous avez et de l'activer avec une fonction Softmax

mlp
"""

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

from tensorflow.keras.layers import Dropout, Activation, Flatten, Conv1D, MaxPooling1D, GlobalAveragePooling1D

model = tf.keras.models.Sequential([
  tf.keras.Input(shape=(32)),
  tf.keras.layers.Dense(1024, activation='relu'),
  #tf.keras.layers.Dropout(0.5),
  tf.keras.layers.Dense(512,activation='relu'),
  tf.keras.layers.Dense(5,activation="softmax")
])

"""cnn1d"""

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

from tensorflow.keras.layers import Dropout, Activation, Flatten, Conv1D, MaxPooling1D, GlobalAveragePooling1D

model = Sequential()

model.add(Conv1D(filters=64, kernel_size=3, padding='same', activation='relu',input_shape=(8,4)))
model.add(Conv1D(filters=128, kernel_size=3, padding='same', activation='relu',input_shape=(8,4)))
model.add(Conv1D(filters=256, kernel_size=3, padding='same', activation='relu',input_shape=(8,4)))

model.add(GlobalAveragePooling1D())
model.add(Dropout(0.5))

model.add(Dense(256,activation='relu'))

model.add(Dropout(0.5))

model.add(Dense(256,activation='relu'))


model.add(Dense(5))
model.add(Activation('softmax'))

"""cnn2d"""

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

from tensorflow.keras.layers import Dropout, Activation, Flatten, Conv2D, MaxPooling2D, GlobalAveragePooling2D


model = tf.keras.Sequential()

model.add(Conv2D(64, (3, 3), activation='relu', input_shape=(5, 5, 32)))
model.add(MaxPooling2D(pool_size=(2,2)))

model.add(Conv2D(128, (1, 1), activation='relu'))
model.add(MaxPooling2D(pool_size=(1,1)))

model.add(Conv2D(256, (1, 1), activation='relu'))
model.add(MaxPooling2D(pool_size=(1,1)))
 

model.add(Dropout(0.2))

model.add(Dense(256, activation='relu'))
model.add(Dropout(0.1))

model.add(tf.keras.layers.Dense(5, activation='softmax'))

"""hybride mlp cnn2D ( utiliser les données de départ du cnn2D)"""

def MlpModel():
  input = tf.keras.Input(shape=(32))

  couche1 = Dense(64, activation='relu')(input)
  couche2 = Dropout(0.3)(layer1)
  couche3 = Dense(128, activation='relu')(couche2)
  couche4 = Dropout(0.3)(layer3)
  couche5 = Dense(256, activation='relu')(couche4)
  couche6 = Dropout(0.3)(layer5)
 

  return tf.keras.Model(inputs=input, outputs=couche6)

mlp_model = mlpModel()
mlp_model.summary()

def Cnn2dModel():
  input = tf.keras.Input(shape=(5,5,32))

  couche1 = Conv2D(filters=32, kernel_size=(3,3), activation='relu')(input)
  couche2 = MaxPooling2D(2,2)(couche1)
  couche3 = Dropout(0.3)(couche2)
  couche4 = GlobalAveragePooling2D()(couche3)

  return tf.keras.Model(inputs=input, outputs=couche4)

cnn2d_model = cnn2dModel()
cnn2d_model.summary() 
concat = tf.keras.layers.Concatenate()([mlp_model.output, cnn2d_model.output])

layer_c = Dense(256, activation='relu')(concat)
out_layer = Dense(5, activation='softmax')(layer_c)

model = tf.keras.Model(inputs=[mlp_model.input, cnn2d_model.input], outputs=out_layer)

tf.keras.utils.plot_model(new_model)

train_X = [train_X[:,2,2,:].reshape(train_X.shape[0], -1), train_X]
valid_X = [valid_X[:,2,2,:].reshape(valid_X.shape[0], -1), valid_X]
test_X = [test_X[:,2,2,:].reshape(test_X.shape[0], -1), test_X]

# Afficher votre modèle
model.summary()

"""### **Compiler votre modèle en définissant une fonction de côut, un optmiseur et une métrique**

Dans le cas d'une classification multi-classe, votre fonction de coût est la cross entropy catégorique. $Adam$ est un bon optimiseur de départ pour vos projets. Ici vous pouvez surveiller la métrique $Accuracy$. Pour la fonction de coût (loss), je n'utilse pas l'argument $from\_logits=True$ car j'ai déjà activé la couche de sortie avec une fonction Softmax
"""

model.compile(optimizer='adam',loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=['acc'])

"""### **Définir un callback pour sauver les poids de votre modèle sur les meilleures époque c'est à dire les moments où il s'améliorera sur le jeu de validation**"""

Path('my_model').mkdir(exist_ok=True, parents=True)
checkpointpath = os.path.join('my_model','model') # chemin où sauver le modèle
callbacks = [tf.keras.callbacks.ModelCheckpoint(
              checkpointpath,
              verbose=1, # niveau de log
              monitor='val_acc', # nom de la métrique à surveiller
              save_best_only=True, # sauver uniquement le meilleur modèle
              save_weights_only=True)] # sauver uniquement les poids

"""### **Entraîner votre modèle pour un certain nombre d'époques**

Le paramètre $validation\_data$ vous permet de spécifier des données de validation et de votre le comportement de votre modèle sur un jeu indépendant dont il n'a pas la connaissance. 

La taille de batch ($batch\_size$) correspond au nombre d'échantillons sur lesquels le modèle est entraîné à la fois sur une époque. Vous pouvez le mettre à (ex. 32, 64, 128, 256) et plus il est grand ce qui requiert d'avoir de la mémoire plus le temps d'exécution d'une époque sera court

J'utilise les labels encodés entre 0 et 4 car la prédiction sur les distributions de probabilités du modèle est retournée avec un argmax
"""

BATCH_SIZE = 256
EPOCHS = 30

history = model.fit (train_X, train_y_enc, validation_data=(valid_X,valid_y_enc), batch_size=BATCH_SIZE, epochs=EPOCHS, callbacks=callbacks)

"""Evolution de training et validation Loss"""

from matplotlib import pyplot as plt
plt.style.use('dark_background')

loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(loss) + 1)
plt.plot(epochs, loss, 'y', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

"""Evolution de training accuracy et validation accuracy"""

acc = history.history['acc']
val_acc = history.history['val_acc']
plt.plot(epochs, acc, 'y', label='Training acc')
plt.plot(epochs, val_acc, 'r', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

"""### **Restaurer les poids du modèle sur la meilleure époque d'entraînement**"""

model.load_weights(checkpointpath)
# S'assurer que c'est bien le meilleur modèle sur les époques d'entraînement

model.evaluate(valid_X,valid_y_enc,batch_size=256)

"""### **Prédiction des classes sur le jeu de validation et évaluation en aggrégeant au niveau objet**"""

# Récupérer les probabilités prédites sur le jeu de validation
valid_prob = model.predict(valid_X,batch_size=256)
valid_prob.shape

# Retourner la classe correspondant à la probabilité la plus haute
valid_pred = np.argmax(valid_prob,axis=1) # axe 1 car ceci concerne chaque ligne
valid_pred.shape

# Je réencode les prédictions entre 1 et 5
valid_pred_enc = encoder.inverse_transform(valid_pred)
np.unique(valid_pred_enc)

# Aggrégation au niveau objet
out_pred = []
unique_id = np.unique(valid_id)
for ID in unique_id :
    # Récupérer les prédictions des pixels appartenant au même objet
    pred = valid_pred_enc[np.where(valid_id==ID)]
    y_true = valid_y[np.where(valid_id==ID)]
    # Prendre la valeur majoritaire des prédictions sur les pixels
    out_pred.append([ np.bincount(y_true).argmax(), np.bincount(pred).argmax()]) #(Vérité terrain,Prédiction majoritaire)
out_pred = np.vstack(out_pred)
out_pred.shape

# F1 score au niveau objet
f1_score(out_pred[:,0],out_pred[:,1],average='weighted')

"""### **Prédire sur le jeu test et Préparer une soumission**"""

# Récupérer les probabilités prédites sur le jeu test
test_prob = model.predict(test_X,batch_size=256)
test_prob.shape

# Retourner la classe correspondant à la probabilité la plus haute
test_pred = np.argmax(test_prob,axis=1) # axe 1 car ceci concerne chaque ligne
test_pred.shape

# Je réencode les prédictions entre 1 et 5
test_pred_enc = encoder.inverse_transform(test_pred)
np.unique(test_pred_enc)

# Aggrégation au niveau objet
agg_pred = []
unique_id = np.unique(test_id)
for ID in unique_id :
    # Récupérer les prédictions des pixels appartenant au même objet
    pred = test_pred_enc[np.where(test_id==ID)]
    # Prendre la valeur majoritaire des prédictions sur les pixels
    agg_pred.append([ ID, np.bincount(pred).argmax()]) #(ID,Prédiction majoritaire)
agg_pred = np.vstack(agg_pred)
agg_pred.shape

df = pd.DataFrame({'ID':agg_pred[:,0],'Class':agg_pred[:,1]})
df.to_csv('Soumission_NaidjaYoussefDiabateLight2.csv',index=False)
df.head(5)

# F1 Score au niveau objet
df_test = pd.read_csv('Test_ID_Label.csv') # Ce fichier vous sera fourni le 12 Novembre
f1_score(df_test.Class,df.Class,average='weighted')