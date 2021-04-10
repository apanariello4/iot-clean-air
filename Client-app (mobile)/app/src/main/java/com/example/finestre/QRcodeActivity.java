package com.example.finestre;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.budiyev.android.codescanner.CodeScanner;
import com.budiyev.android.codescanner.CodeScannerView;
import com.budiyev.android.codescanner.DecodeCallback;
import com.google.zxing.Result;

public class QRcodeActivity extends AppCompatActivity {
    private CodeScanner mCodeScanner;
    public static final String EXTRA_MESSAGE = "Ha letto qualcosa?";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.qrcode);


        CodeScannerView scannerView = findViewById(R.id.scanner_view);
        mCodeScanner = new CodeScanner(this, scannerView);
        mCodeScanner.setDecodeCallback(new DecodeCallback() {
            @Override
            public void onDecoded(@NonNull final Result result) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                       //Toast.makeText(QRcodeActivity.this, result.getText(), Toast.LENGTH_SHORT).show();
                       // Toast toast = Toast.makeText(QRcodeActivity.this, result.getText(), Toast.LENGTH_SHORT);
                        Intent intent=new Intent(QRcodeActivity.this, MainActivity.class);
                        intent.putExtra(EXTRA_MESSAGE, result.getText());
                        startActivity(intent);

                    }
                });
            }
        });
        scannerView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                CharSequence text = "Inquadrare il QR Code sul manuale della finestra!";
                Toast toast = Toast.makeText(QRcodeActivity.this, text, Toast.LENGTH_SHORT);
                toast.show();

                //mCodeScanner.startPreview();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        mCodeScanner.startPreview();
    }

    @Override
    protected void onPause() {
        mCodeScanner.releaseResources();
        super.onPause();
    }


}
