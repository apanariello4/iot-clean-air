import pandas as pd
from pandas import read_csv
from pandas import to_datetime
from pandas import DataFrame
from fbprophet import Prophet
from datetime import datetime as dt
import requests
import csv
import os.path


date = []
host_path = "http://151.81.17.207:5000"
dataset_pm25_1 = "./dataset/pm25_modena_parco_ferrari_2019.csv"
dataset_pm25_2 = "./dataset/pm25_modena_parco_ferrari_2020.csv"
dataset_pm25_3 = "./dataset/pm25_modena_parco_ferrari_sensor.csv"
dataset_pm10_1 = "./dataset/pm10_modena_parco_ferrari_2019.csv"
dataset_pm10_2 = "./dataset/pm10_modena_parco_ferrari_2020.csv"
dataset_pm10_3 = "./dataset/pm10_modena_parco_ferrari_sensor.csv"

# sensorValuePM25 = random.uniform(10.0, 100.0)
# sensorValuePM10 = random.uniform(10.0, 100.0)

class Prediction():

	def load_datasets(self):
		df_pm25_1 = read_csv(dataset_pm25_1, sep=',')
		df_pm25_1 = df_pm25_1[['DATA_INIZIO', 'VALORE']]
		df_pm25_2 = read_csv(dataset_pm25_2, sep=',')
		df_pm25_2 = df_pm25_2[['DATA_INIZIO', 'VALORE']]
		df_pm10_1 = read_csv(dataset_pm10_1, sep=',')
		df_pm10_1 = df_pm10_1[['DATA_INIZIO', 'VALORE']]
		df_pm10_2 = read_csv(dataset_pm10_2, sep=',')
		df_pm10_2 = df_pm10_2[['DATA_INIZIO', 'VALORE']]

		return df_pm25_1, df_pm25_2, df_pm10_1, df_pm10_2


	def update_datasets(self, time, sensorValuePM25, sensorValuePM10):
		#Append the values of time and sensorValue in csv files
		with open(dataset_pm25_3, mode='a', newline='') as csv_file:
			fieldnames = ["DATA_INIZIO", "VALORE"]
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

			# if not os.path.isfile(dataset_pm25_3):
			# 	writer.writeheader()
			writer.writerow({"DATA_INIZIO": time,
							 "VALORE": int(round(sensorValuePM25, 0))
							})

		with open(dataset_pm10_3, mode='a', newline='') as csv_file:
			fieldnames = ["DATA_INIZIO", "VALORE"]
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

			# if not os.path.isfile(dataset_pm10_3):
			# 	writer.writeheader()
			writer.writerow({"DATA_INIZIO": time,
							 "VALORE": int(round(sensorValuePM10, 0))
							})


	def make_prediction(self, df, time_dataset):
		df.columns = ['ds', 'y']
		train = df
		# print(train.tail())

		model = Prophet(daily_seasonality=True)
		model.add_country_holidays(country_name='IT')
		model.fit(train)
		future = list()

		for i in range(3):
			date = time_dataset
			future.append([date])
		future = DataFrame(future)
		future.columns = ['ds']
		# use the model to make a forecast
		forecast = model.predict(future)
		forecast[['yhat']] = forecast[['yhat']].round(0).astype('int32')
		pred_df = forecast[['ds', 'yhat']]

		return pred_df


	def prediction(self, sensorValuePM25, sensorValuePM10):
		df_pm25_1, df_pm25_2, df_pm10_1, df_pm10_2 = self.load_datasets()

		timestamp = dt.now()
		time_dataset = timestamp.strftime('%d/%m/%Y')
		self.update_datasets(time_dataset, sensorValuePM25, sensorValuePM10)

		df_pm25_3 = read_csv(dataset_pm25_3, sep=',')
		df_pm25_3 = df_pm25_3[['DATA_INIZIO', 'VALORE']]
		df_pm10_3 = read_csv(dataset_pm10_3, sep=',')
		df_pm10_3 = df_pm10_3[['DATA_INIZIO', 'VALORE']]

		# df_pm25_3[['DATA_INIZIO']] = dt.strptime(df_pm25_3[['DATA_INIZIO']], '%d/%m/%Y')
		# df_pm10_3[['DATA_INIZIO']] = dt.strptime(df_pm10_3[['DATA_INIZIO']], '%d/%m/%Y')


		df_pm25 = pd.concat([df_pm25_1, df_pm25_2, df_pm25_3])
		df_pm10 = pd.concat([df_pm10_1, df_pm10_2, df_pm10_3])
		# print(df.tail())

		pred_df_pm25 = self.make_prediction(df_pm25, time_dataset)
		pred_df_pm10 = self.make_prediction(df_pm10, time_dataset)

		print(pred_df_pm25)
		print(pred_df_pm10)

		time_server = timestamp.strftime('%Y-%m-%d %H:%M:%S')
		pm25 = pred_df_pm25["yhat"].values.tolist()
		pm10 = pred_df_pm10["yhat"].values.tolist()
		pm = pm25 + pm10
		pred_dict = {"region": "Modena", "pm": pm, "timestamp": time_server}
		print(pred_dict)

		#POST values
		r = requests.post(host_path + "/api/v1/predictions", json= pred_dict)
		print(r)

		g = requests.get(host_path + "/api/v1/predictions", json= {"region": "Modena"})
		print(g.json())


# def test():
# 	g = requests.get(host_path + "/api/v1/predictions", json= {"region": "Modena"})
# 	print(g.json())


# if __name__== '__main__':
# 	pr = Prediction()
# 	pr.prediction()