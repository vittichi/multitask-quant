import keras
from keras.models import Model
from keras import layers
from keras.layers import Input, Dense, Flatten, merge, Dropout
from keras.optimizers import Adam, Adadelta, Nadam, SGD
from keras.applications.inception_v3 import InceptionV3
from keras.layers.wrappers import TimeDistributed
from keras.layers.pooling import GlobalAveragePooling2D
from keras.layers import LSTM
from keras.layers import Reshape
from keras.layers import Lambda
import tensorflow as tf
from keras import backend as K
from keras.regularizers import l2

class RatioInc:
    def __init__(self, input_shape = (203,203, 3), act_f = "relu", batch_size = 100):
        """
        intialization of hyperparameters
        """
        self.act_f = act_f
        self.batch_size = batch_size
        self.input_shape = input_shape
        self.ratio_classes = 17
        self.l2reg = 1e-8
        self.dropout = 0.5

    def build(self):
        """
        loads the inception network,
        contains the fully connected layers,
        predicts the class
        """
        model_inception = InceptionV3(weights = None, include_top = False)
        inp = Input(self.input_shape, name = 'more_input')

        out_inc = model_inception(inp)
        print out_inc.get_shape()
        out_res = Reshape((25,2048))(out_inc)


        td_dense = TimeDistributed(Dense(1024, W_regularizer = l2(self.l2reg), activation = 'relu'))
        drop_td_dense = Dropout(self.dropout)
        l_td_dense = td_dense(out_res)
        drop_l_td_dense = drop_td_dense(l_td_dense)

        td_dense2 = TimeDistributed(Dense(512, W_regularizer = l2(self.l2reg), activation = 'relu'))
        drop_td_dense2 = Dropout(self.dropout)
        l_td_dense2 = td_dense2(drop_l_td_dense)
        drop_l_td_dense2 = drop_td_dense2(l_td_dense2)

        ratio_flat = Flatten()(drop_l_td_dense2)
        hidden_ratio = Dense(32, W_regularizer = l2(self.l2reg), activation = 'relu')(ratio_flat)
        drop_hidden_ratio = Dropout(self.dropout)(hidden_ratio)
        out_ratio = Dense(self.ratio_classes,  activation = 'softmax', name = 'pred3')(drop_hidden_ratio)
        model = Model(inputs = inp, outputs = out_ratio)
        model.compile(loss = 'categorical_crossentropy', optimizer = 'sgd', metrics = ['accuracy'])
        return model
