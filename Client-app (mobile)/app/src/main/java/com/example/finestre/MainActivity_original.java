package com.example.finestre;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CursorAdapter;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity_original extends AppCompatActivity {
    private static final int REQUEST_CAMERA_RESULT = 1;
    TextView tv;
    Button btn1;

    private DbManager db = null;
    private CursorAdapter adapter;
    private ListView listview = null;

    private View.OnClickListener clickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            int position = listview.getPositionForView(v);
            long id = adapter.getItemId(position);
            if (db.delete(id))
                adapter.changeCursor(db.query());
        }
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);

        btn1 = (Button) findViewById(R.id.button1);
        tv = (TextView) findViewById(R.id.initialtext);


        //--------------------------------------------------------------------------------------------------


        db = new DbManager(this);
        listview = (ListView) findViewById(R.id.listview);
        Cursor crs = db.query();
        adapter = new CursorAdapter(this, crs, 0) {
            @Override
            public View newView(Context ctx, Cursor arg1, ViewGroup arg2) {
                View v = getLayoutInflater().inflate(R.layout.listactivity_row, null);
                return v;
            }

            @Override
            public void bindView(View v, Context arg1, Cursor crs) {
                String oggetto = crs.getString(crs.getColumnIndex(DatabaseStrings.FIELD_SUBJECT));
                TextView txt = (TextView) v.findViewById(R.id.txt_subject);
                txt.setText(oggetto);
                txt = (TextView) v.findViewById(R.id.txt_date);
                ImageButton imgbtn = (ImageButton) v.findViewById(R.id.btn_delete);
                imgbtn.setOnClickListener(clickListener);
            }

            @Override
            public long getItemId(int position) {
                Cursor crs = adapter.getCursor();
                crs.moveToPosition(position);
                return crs.getLong(crs.getColumnIndex(DatabaseStrings.FIELD_ID));
            }
        };
        listview.setAdapter(adapter);

        btn1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(ContextCompat.checkSelfPermission(MainActivity_original.this,
                        Manifest.permission.CAMERA)== PackageManager.PERMISSION_GRANTED){
                    Intent intent=new Intent(MainActivity_original.this, QRcodeActivity.class);
                    startActivity(intent);
                }
                else{
                    requestCameraPermission();
                }


            }
        });

    }

    public void salva(View v) {
        EditText location = (EditText) findViewById(R.id.luogo);
        EditText sub = (EditText) findViewById(R.id.oggetto);
        if (sub.length() > 0 && location.length() > 0) {
            db.save(sub.getEditableText().toString(), location.getEditableText().toString());
            adapter.changeCursor(db.query());
            sub.setText("");
            location.setText("");
        }
    }

// --------------------------------------------------------------------------------------------------------------------------------------------


    // Funzione per la richiesta del permesso dell'uso della fotocamera
    private void requestCameraPermission(){
        if(ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)){
            new AlertDialog.Builder(this)
                    .setTitle("Richiesta Fotocamera")
                    .setMessage("Accetta per poter utilizzare il lettore QR Code")
                    .setPositiveButton("Ok", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            ActivityCompat.requestPermissions(MainActivity_original.this,new String[]{Manifest.permission.CAMERA},
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
