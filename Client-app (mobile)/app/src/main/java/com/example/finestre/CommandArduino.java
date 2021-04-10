package com.example.finestre;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.io.IOException;

import java.io.UnsupportedEncodingException;

import org.jetbrains.annotations.NotNull;
import org.json.*;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;


public class CommandArduino extends AppCompatActivity {

    TextView tv, qrcode;
    Button btn1, btn2;
    private String server = "http://151.81.17.207:5000";
    private String url = "http://151.81.17.207:5000/api/v1/sensor/status?uuid=";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.command_arduino);

        btn1 = (Button) findViewById(R.id.button_open);
        btn2 = (Button) findViewById(R.id.button_close);
        tv = (TextView) findViewById(R.id.WindowState);
        Intent intent = getIntent();
        final String uuid = intent.getStringExtra(MainActivity.EXTRA_UUID);
        final String location = intent.getStringExtra(MainActivity.EXTRA_LOCATION);
        qrcode = (TextView) findViewById(R.id.qrcode_id);
        qrcode.setText(location);

        String clientId = MqttClient.generateClientId();
        final MqttAndroidClient client = new MqttAndroidClient(CommandArduino.this,
                "tcp://151.81.17.207:1883", clientId);


        getStatusWindow(uuid,url);


        checkConnection(client,uuid);



    }

    public void checkConnection(final MqttAndroidClient client, final String uuid){
        try {
            IMqttToken token = client.connect();
            token.setActionCallback(new IMqttActionListener() {


                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    // We are connected

                    Toast.makeText(CommandArduino.this, "Connesso", Toast.LENGTH_SHORT).show();

                        btn1.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View view) {
                                apri(client, uuid);
                            }
                        });

                        btn2.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View view) {
                                chiudi(client, uuid);
                            }
                        });

                        // Faccio una get per aggiornare lo stato della finestra

                        //sendPost(uuid);

                    //Faccio la sub al topic della mia finestra
                        subscribeMqttChannel(client, uuid+"/window");
                    }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    // Something went wrong e.g. connection timeout or firewall problems
                    Toast.makeText(CommandArduino.this, "Non connesso al broker", Toast.LENGTH_SHORT).show();
//                    Intent intent=new Intent(CommandArduino.this, MainActivity_original.class);
//                    startActivity(intent);

                }
            });
        } catch (
                MqttException e) {
            e.printStackTrace();
            Toast.makeText(CommandArduino.this, "Non connesso al broker", Toast.LENGTH_SHORT).show();
        }
    }



    public void getStatusWindow(String uuid, String url) {

        OkHttpClient client_req = new OkHttpClient();
        Request request = new Request.Builder()
                .url(url+uuid)
                .addHeader("Content-Type","application/json")
                .build();
        client_req.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                CommandArduino.this.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {

                        Toast.makeText(CommandArduino.this, "Non sono riuscito a connettermi alla pagina", Toast.LENGTH_SHORT).show();
                    }
                });
                e.printStackTrace();
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                if (response.isSuccessful()){
                    final String myResponse= response.body().string();


                    CommandArduino.this.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {

                            try {

                                JSONObject Jobject = new JSONObject(myResponse);
                                String stato_finestra = Jobject.getString("status");
                                Toast.makeText(CommandArduino.this, stato_finestra,Toast.LENGTH_SHORT).show();
                                tv.setText(stato_finestra);
                            } catch (JSONException e) {
                                e.printStackTrace();
                            }

                        }
                    });
                }
            }
        });
    }


    public void subscribeMqttChannel(MqttAndroidClient client, String uuid) {
        try {

            if (client.isConnected()) {

                client.subscribe(uuid, 0);
                client.setCallback(new MqttCallback() {
                    @Override
                    public void connectionLost(Throwable cause) {
                        Toast.makeText(CommandArduino.this,"Il telefono si è disconnesso",Toast.LENGTH_SHORT).show();
                    }

                    @Override
                    public void messageArrived(String topic, MqttMessage message) throws Exception {

                        String arrivato = message.toString();
                        Toast.makeText(CommandArduino.this, "Nuovo messaggio ricevuto",Toast.LENGTH_SHORT).show();
                        tv.setText(arrivato);
                    }

                    @Override
                    public void deliveryComplete(IMqttDeliveryToken token) {

                    }
                });
            }
        } catch (Exception e) {
            Log.d("tag","Error :" + e);
        }
    }


    public void apri (MqttAndroidClient client, String uuid) {
        String topic = uuid +"/command" ;

        Toast.makeText(CommandArduino.this,"Comando inviato",Toast.LENGTH_SHORT).show();
        String payload = "ON";
        byte[] encodedPayload = new byte[0];
        try {
            encodedPayload = payload.getBytes("UTF-8");
            MqttMessage message = new MqttMessage(encodedPayload);
            message.setRetained(true);
            client.publish(topic, message);
        } catch (UnsupportedEncodingException | MqttException e) {
            e.printStackTrace();
        }
    }


    public void chiudi (MqttAndroidClient client, String uuid) {
        String topic = uuid +"/command" ;

        Toast.makeText(CommandArduino.this,"Comando inviato",Toast.LENGTH_SHORT).show();
        String payload = "OFF";
        byte[] encodedPayload = new byte[0];
        try {
            encodedPayload = payload.getBytes("UTF-8");
            MqttMessage message = new MqttMessage(encodedPayload);
            message.setRetained(true);
            client.publish(topic, message);
        } catch (UnsupportedEncodingException | MqttException e) {
            e.printStackTrace();
        }
    }
}