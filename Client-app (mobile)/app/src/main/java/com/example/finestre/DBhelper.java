package com.example.finestre;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DBhelper extends SQLiteOpenHelper
{
	public static final String DBNAME="BILLBOOK";
	
	
	
	public DBhelper(Context context) {
		super(context, DBNAME, null, 1);
	}

	@Override
	public void onCreate(SQLiteDatabase db)  
	{
		String q="CREATE TABLE "+DatabaseStrings.TBL_NAME+" ( _id INTEGER PRIMARY KEY AUTOINCREMENT," +
				DatabaseStrings.FIELD_LOCATION+" TEXT," +
				DatabaseStrings.FIELD_SUBJECT+" TEXT)";

		db.execSQL(q);
	}

	@Override
	public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) 
	{
		
	}

}
