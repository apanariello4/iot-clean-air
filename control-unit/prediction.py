import pandas as pd
from fbprophet import Prophet
from datetime import datetime as dt
import requests
import csv

date = []
host_path = "http://151.81.17.207:5000"
dataset_pm25_1 = "./dataset/pm25_modena_parco_ferrari_2019.csv"
dataset_pm25_2 = "./dataset/pm25_modena_parco_ferrari_2020.csv"
dataset_pm25_3 = "./dataset/pm25_modena_parco_ferrari_sensor.csv"
dataset_pm10_1 = "./dataset/pm10_modena_parco_ferrari_2019.csv"
dataset_pm10_2 = "./dataset/pm10_modena_parco_ferrari_2020.csv"
dataset_pm10_3 = "./dataset/pm10_modena_parco_ferrari_sensor.csv"


class Prediction():

    def load_dataset(self, dataset):
        try:
            with open(dataset) as file:
                df = pd.read_csv(file, sep=',')
                df = df[['DATA_INIZIO', 'VALORE']]
        except FileNotFoundError:
            print("File not found")

        return df


    # Insert the new sensor values
    def update_datasets(self, time, sensorValuePM25, sensorValuePM10):
        # Append the values of time, sensorValuePM25 and sensorValuePM10 in csv files
        with open(dataset_pm25_3, mode='a', newline='') as csv_file:
            fieldnames = ["DATA_INIZIO", "VALORE"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({"DATA_INIZIO": time,
                             "VALORE": int(round(sensorValuePM25, 0))
                             })

        with open(dataset_pm10_3, mode='a', newline='') as csv_file:
            fieldnames = ["DATA_INIZIO", "VALORE"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({"DATA_INIZIO": time,
                             "VALORE": int(round(sensorValuePM10, 0))
                             })


    # Make the prediction with Prophet. Additional variables of daily seasonality and Italian holidays are set.
    def make_prediction(self, df, time_dataset):
        df.columns = ['ds', 'y']
        train = df
        # print(train.tail())

        model = Prophet(daily_seasonality=True)
        model.add_country_holidays(country_name='IT')
        model.fit(train)
        future = list()

        # Predict the next 3 hours values
        for i in range(3):
            date = time_dataset
            future.append([date])
        future = pd.DataFrame(future)
        future.columns = ['ds']

        # use the model to make a forecast
        forecast = model.predict(future)
        forecast[['yhat']] = forecast[['yhat']].round(0).astype('int32')
        pred_df = forecast[['ds', 'yhat']]

        return pred_df


    def post_values(self, dict):
        r = requests.post(host_path + "/api/v1/predictions", json=dict)
        return r

    def get_values(self, region):
        g = requests.get(host_path + "/api/v1/predictions", json={"region": region})
        return g


    def prediction(self, sensorValuePM25, sensorValuePM10):
        # Load the datasets of PM25 and PM10, registered in Modena during 2019-2020
        df_pm25_1 = self.load_dataset(dataset_pm25_1)
        df_pm25_2 = self.load_dataset(dataset_pm25_2)
        df_pm10_1 = self.load_dataset(dataset_pm10_1)
        df_pm10_2 = self.load_dataset(dataset_pm10_2)

        # Get the current time
        timestamp = dt.now()
        time_dataset = timestamp.strftime('%d/%m/%Y')
        self.update_datasets(time_dataset, sensorValuePM25, sensorValuePM10)

        df_pm25_3 = self.load_dataset(dataset_pm25_3)
        df_pm10_3 = self.load_dataset(dataset_pm10_3)

        # df_pm25_3[['DATA_INIZIO']] = dt.strptime(df_pm25_3[['DATA_INIZIO']], '%d/%m/%Y')
        # df_pm10_3[['DATA_INIZIO']] = dt.strptime(df_pm10_3[['DATA_INIZIO']], '%d/%m/%Y')

        df_pm25 = pd.concat([df_pm25_1, df_pm25_2, df_pm25_3])
        df_pm10 = pd.concat([df_pm10_1, df_pm10_2, df_pm10_3])

        pred_df_pm25 = self.make_prediction(df_pm25, time_dataset)
        pred_df_pm10 = self.make_prediction(df_pm10, time_dataset)

        print(pred_df_pm25)
        print(pred_df_pm10)

        # Set the values to be sent to the server (time in the server format, predicted values)
        time_server = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        pm25 = pred_df_pm25["yhat"].values.tolist()
        pm10 = pred_df_pm10["yhat"].values.tolist()
        pm = pm25 + pm10
        pred_dict = {"region": "Modena", "pm": pm, "timestamp": time_server}
        print(pred_dict)

        # POST values
        r = self.post_values(pred_dict)
        print(r)

        # GET values
        g = self.get_values(region="Modena")
        print(g.json())

