import pandas as pd
from pandas import read_csv
from pandas import to_datetime
from pandas import DataFrame
from fbprophet import Prophet
from sklearn.metrics import mean_absolute_error
from matplotlib import pyplot as plt
from datetime import datetime as dt
import requests

date = []
host_path = "http://151.81.17.207:5000"

def prediction():
	dataset1 = "./dataset/pm2.5_modena_parco_ferrari_2019.csv"
	dataset2 = "./dataset/pm2.5_modena_parco_ferrari_2020.csv"
	df1 = read_csv(dataset1, sep=',')
	df1 = df1[['DATA_INIZIO', 'VALORE']]
	df2 = read_csv(dataset2, sep=',')
	df2 = df2[['DATA_INIZIO', 'VALORE']]
	df = pd.concat([df1, df2])
	# print(df.tail())

	df.columns = ['ds', 'y']
	df['ds'] = to_datetime(df['ds'])
	train = df.drop(df.index[-10:])
	# print(train.tail())

	model = Prophet()
	model.fit(train)
	future = list()

	for i in range(22, 32):
		date = '2020-12-%02d' % i
		future.append([date])
	future = DataFrame(future)
	future.columns = ['ds']
	future['ds'] = to_datetime(future['ds'])
	# use the model to make a forecast
	forecast = model.predict(future)
	# print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
	forecast[['yhat', 'yhat_lower', 'yhat_upper']] = forecast[['yhat', 'yhat_lower', 'yhat_upper']].round(0).astype('int32')
	# print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
	# plot forecast
	# model.plot(forecast)
	# plt.show()

	curr_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
	print(curr_time)

	# calculate MAE between expected and predicted values for december
	y_true = df['y'][-10:].values
	# print(y_true)
	y_pred = forecast['yhat'].values
	mae = mean_absolute_error(y_true, y_pred)
	print('MAE: %.3f' % mae)
	# plot expected vs actual
	filt = (future['ds']).dt.strftime('%m/%d')
	# print(filt)
	# plt.plot(filt, y_true, label='Actual')
	# plt.plot(filt, y_pred, label='Predicted')
	# plt.legend()
	# plt.show()

	pred = forecast["yhat"].values.tolist()
	pm25 = pred[:3]
	pm10 = pred[:3]
	pm = pm25 + pm10


	Mario = {"region": "Modena", "pm": pm, "timestamp": curr_time}

	r = requests.post(host_path + "/api/v1/predictions", json= Mario)
	print(r)

	g = requests.get(host_path + "/api/v1/predictions", json= {"region": "Modena"})
	print(g.json())


if __name__== '__main__':
	prediction()