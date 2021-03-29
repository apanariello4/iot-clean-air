package com.example.finestre;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class CommandArduino extends AppCompatActivity {

    TextView tv, qrcode;
    Button btn1, btn2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.command_arduino);

        btn1=(Button)findViewById(R.id.button_open);
        btn2=(Button)findViewById(R.id.button_close);
        tv = (TextView)findViewById(R.id.WindowState);
        Intent intent = getIntent();
        final String message = intent.getStringExtra(QRcodeActivity.EXTRA_MESSAGE);
        qrcode = (TextView)findViewById(R.id.qrcode_id);
        qrcode.setText(message);
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
        final PyObject pyobj = py.getModule("apri_finestra");
        final PyObject pyobj_mqtt = py.getModule("chiudi_finestra");

        btn1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                PyObject obj = pyobj.callAttr("main", message);
                tv.setText(obj.toString());
            }
        });

        btn2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                PyObject obj2 = pyobj_mqtt.callAttr("main",message);
                tv.setText(obj2.toString());
            }
        });

    }
}