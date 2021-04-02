package com.example.finestre;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.os.Bundle;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.CursorAdapter;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import static android.provider.AlarmClock.EXTRA_MESSAGE;

public class MainActivity extends Activity {

	public static final String EXTRA_UUID = "Nessun UUID";
	private static final int REQUEST_CAMERA_RESULT = 1;
	private DbManager db=null;
	private CursorAdapter adapter;
	private ListView listview=null;
	Button btn1;



	private OnClickListener clickListener=new OnClickListener() {
		@Override
		public void onClick(View v) 
		{
			int position=listview.getPositionForView(v);
			long id=adapter.getItemId(position);
			if (db.delete(id))
				adapter.changeCursor(db.query());

		}
	};
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

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
				String luogo = crs.getString(crs.getColumnIndex(DatabaseStrings.FIELD_LOCATION));
				String oggetto = crs.getString(crs.getColumnIndex(DatabaseStrings.FIELD_SUBJECT));
				TextView loc = (TextView) v.findViewById(R.id.txt_location);
				TextView txt = (TextView) v.findViewById(R.id.txt_subject);
				loc.setText(luogo);
				txt.setText(oggetto);
				ImageButton imgbtn = (ImageButton) v.findViewById(R.id.btn_delete);
				imgbtn.setFocusable(false);
				imgbtn.setOnClickListener(clickListener);
			}

			@Override
			public long getItemId(int position) {
				Cursor crs = adapter.getCursor();
				crs.moveToPosition(position);
				return crs.getLong(crs.getColumnIndex(DatabaseStrings.FIELD_ID));
			}
		};


		// se sono stati passati dati dal lettore QR code allora accedo qua
		Intent intent = getIntent();
		final String message = intent.getStringExtra(QRcodeActivity.EXTRA_MESSAGE);
		if(message != null){
			EditText sub = (EditText) findViewById(R.id.oggetto);
			sub = (EditText) findViewById(R.id.oggetto);
			sub.setText(message);
		}

		//setta la funzione scansione
		btn1 = (Button) findViewById(R.id.button_scan);

		listview.setAdapter(adapter);


		listview.setOnItemClickListener(new AdapterView.OnItemClickListener() {
			@Override
			public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

				Cursor crs = adapter.getCursor();
				crs.moveToPosition(position);
				String uuid = crs.getString(crs.getColumnIndex(DatabaseStrings.FIELD_SUBJECT));
				Intent intent=new Intent(MainActivity.this, CommandArduino.class);
				intent.putExtra(EXTRA_UUID, uuid);
				startActivity(intent);

			}
		});

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



	
	public void salva(View v) {
		EditText sub = (EditText) findViewById(R.id.oggetto);
		EditText location = (EditText) findViewById(R.id.luogo);
		if (sub.length() > 0 && location.length()>0) {
			db.save(sub.getEditableText().toString(), location.getEditableText().toString());
			adapter.changeCursor(db.query());
			sub.setText("");
			location.setText("");
		}
	}

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
				Toast.makeText(this, "Adesso puoi scansionare il QR Code", Toast.LENGTH_SHORT).show();
			}
			else{
				Toast.makeText(this, "Permesso Negato", Toast.LENGTH_SHORT).show();
			}
		}
	}
}
