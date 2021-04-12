package com.example.finestre;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteException;

public class DbManager 
{
	private DBhelper dbhelper;
	

	public DbManager(Context ctx) 
	{
		dbhelper=new DBhelper(ctx);
	}
	
	public void save(String uuid, String luogo)
	{
		SQLiteDatabase db=dbhelper.getWritableDatabase();
		
		ContentValues cv=new ContentValues();
		cv.put(DatabaseStrings.FIELD_LOCATION, luogo);
		cv.put(DatabaseStrings.FIELD_SUBJECT, uuid);

		try
		{
			db.insert(DatabaseStrings.TBL_NAME, null,cv);
		}
		catch (SQLiteException sqle)
		{
			// Gestione delle eccezioni
		}
	}
	
	public boolean delete(long id)
	{
		SQLiteDatabase db=dbhelper.getWritableDatabase();
		try
		{
			if (db.delete(DatabaseStrings.TBL_NAME, DatabaseStrings.FIELD_ID+"=?", new String[]{Long.toString(id)})>0)
				return true;
			return false;
		}
		catch (SQLiteException sqle)
		{
			return false;
		}
		
	}
	
	public Cursor query()
	{
		Cursor crs=null;
		try
		{
			SQLiteDatabase db=dbhelper.getReadableDatabase();
			crs=db.query(DatabaseStrings.TBL_NAME, null, null, null, null, null, null, null);
		}
		catch(SQLiteException sqle)
		{
			return null;
		}
		return crs;
	}

}
