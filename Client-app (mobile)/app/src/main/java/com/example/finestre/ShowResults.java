package com.example.finestre;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class ShowResults extends AppCompatActivity {


    TextView qrcode;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.risultato);


        // Get the Intent that started this activity and extract the string
        Intent intent = getIntent();
        String message = intent.getStringExtra(QRcodeActivity.EXTRA_MESSAGE);

        // Capture the layout's TextView and set the string as its text
        qrcode = (TextView)findViewById(R.id.textqrcode);
        qrcode.setText(message);

    }
}
