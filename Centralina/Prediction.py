from pandas import read_csv
from pandas import to_datetime
from pandas import DataFrame
from fbprophet import Prophet
from sklearn.metrics import mean_absolute_error
from matplotlib import pyplot as plt

def prediction():
	dataset = "./dataset/pm2.5_modena_parco_ferrari.csv"
	df = read_csv(dataset, sep=',')
	df = df[['DATA_INIZIO', 'VALORE']]
	# print(df.head())

	df.columns = ['ds', 'y']
	df['ds'] = to_datetime(df['ds'])
	train = df.drop(df.index[-10:])
	print(train.tail())

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
	print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
	# plot forecast
	# model.plot(forecast)
	# plt.show()

	# calculate MAE between expected and predicted values for december
	y_true = df['y'][-10:].values
	y_pred = forecast['yhat'].values
	mae = mean_absolute_error(y_true, y_pred)
	print('MAE: %.3f' % mae)
	# plot expected vs actual
	plt.plot(y_true, label='Actual')
	plt.plot(y_pred, label='Predicted')
	plt.legend()
	plt.show()


if __name__== '__main__':
	prediction()