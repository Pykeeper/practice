import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation



def load_data(file_name, sequence_length=10, split=0.8):
    df = pd.read_csv(file_name, sep=',', usecols=[1])

    data_all = np.array(df).astype(float)
    scaler = MinMaxScaler()
    data_all = scaler.fit_transform(data_all)
    data = []
    print("len(data_all)={}".format(len(data_all)))
    for i in range(len(data_all) - sequence_length - 1):
        print("i={}, (i + sequence_length + 1)={}".format(i, i + sequence_length + 1))
        data.append(data_all[i: i + sequence_length + 1])
    reshaped_data = np.array(data).astype('float64')
    np.random.shuffle(reshaped_data)#（133，11，1）
    # 对x进行统一归一化，而y则不归一化
    #行全部取，11列中除了最后一列不取（133，10，1）
    x = reshaped_data[:, :-1]
    #行全部取，11列中只取最后一列（133，1）
    y = reshaped_data[:, -1]
    #分割数
    split_boundary = int(reshaped_data.shape[0] * split)
    train_x = x[: split_boundary]
    test_x = x[split_boundary:]

    train_y = y[: split_boundary]
    test_y = y[split_boundary:]
    print("train_x={}, train_y={}, test_x={}, test_y={}".format(train_x.shape, train_y.shape, test_x.shape, test_y.shape,))
    return train_x, train_y, test_x, test_y, scaler


def build_model():
    # input_dim是输入的train_x的最后一个维度，train_x的维度为(n_samples, time_steps, input_dim)
    model = Sequential()
    # model.add(LSTM(input_dim=1, output_dim=50, return_sequences=True))
    #2.2.2 keras
    model.add(LSTM(input_shape=(None, 1), units=100, return_sequences=False))
    print(model.layers)
    # model.add(LSTM(units=100, return_sequences=False))
    # model.add(Dense(output_dim=1))

    model.add(Dense(units=1))
    model.add(Activation('linear'))

    model.compile(loss='mse', optimizer='rmsprop')
    return model


def train_model(train_x, train_y, test_x, test_y):
    model = build_model()

    try:
        # model.fit(train_x, train_y, batch_size=512, nb_epoch=30, validation_split=0.1)
        model.fit(train_x, train_y, batch_size=512, epochs=30, validation_split=0.1)
        predict = model.predict(test_x)
        predict = np.reshape(predict, (predict.size, ))
    except KeyboardInterrupt:
        print(predict)
        print(test_y)
    print("predict={},test_y={}".format(predict,test_y))
    # print(test_y)
    try:
        fig = plt.figure(1)
        plt.plot(predict, 'r:')
        plt.plot(test_y, 'g-')
        plt.legend(['predict', 'true'])
    except Exception as e:
        print(e)
    return predict, test_y


if __name__ == '__main__':
    train_x, train_y, test_x, test_y, scaler = load_data('international-airline-passengers.csv')
    train_x = np.reshape(train_x, (train_x.shape[0], train_x.shape[1], 1))
    test_x = np.reshape(test_x, (test_x.shape[0], test_x.shape[1], 1))
    print("train_x.shape={},test_x.shape={}".format(train_x.shape,test_x.shape))
    predict_y, test_y = train_model(train_x, train_y, test_x, test_y)
    #返回原来的对应的预测数值
    predict_y = scaler.inverse_transform([[i] for i in predict_y])
    test_y = scaler.inverse_transform(test_y)
    fig2 = plt.figure(2)
    plt.plot(predict_y, 'g:')
    plt.plot(test_y, 'r-')
    plt.show()