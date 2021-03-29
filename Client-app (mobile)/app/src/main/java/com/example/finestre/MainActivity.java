package com.example.finestre;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_CAMERA_RESULT = 1;
    TextView tv;
    Button btn1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        btn1=(Button)findViewById(R.id.button1);
        tv = (TextView)findViewById(R.id.initialtext);

        btn1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
            if(ContextCompat.checkSelfPermission(MainActivity.this,
                        Manifest.permission.CAMERA)== PackageManager.PERMISSION_GRANTED){
                Intent intent=new Intent(MainActivity.this, QRcodeActivity.class);
                startActivity(intent);
            }
            else{
                requestCameraPermission();
            }


            }
        });
    }

    // Funzione per la richiesta del permesso dell'uso della fotocamera
    private void requestCameraPermission(){
        if(ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)){
            new AlertDialog.Builder(this)
                    .setTitle("Richiesta Fotocamera")
                    .setMessage("Accetta per poter utilizzare il lettore QR Code")
                    .setPositiveButton("Ok", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            ActivityCompat.requestPermissions(MainActivity.this,new String[]{Manifest.permission.CAMERA},
                                    REQUEST_CAMERA_RESULT);
                        }
                    })
                    .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            dialog.dismiss();
                        }
                    })
                    .create().show();
        }
        else{
            ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.CAMERA},
                    REQUEST_CAMERA_RESULT);
        }

    }

    //Result of our permissions

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        if(requestCode == REQUEST_CAMERA_RESULT){
            if(grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Permesso Concesso", Toast.LENGTH_SHORT).show();
            }
            else{
                Toast.makeText(this, "Permesso Negato", Toast.LENGTH_SHORT).show();
            }
            }
        }
}
