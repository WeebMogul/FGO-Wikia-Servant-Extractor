import stats_database as ssdb
import database_formatter
import servant_name_id_database as stdb

if __name__ == "__main__":
    
    state,serv_df = stdb.ServantDB().create_ServantDB_file()
    if state == True:
        print("File is already updated")
    else:
        stat_df = ssdb.StatsDB().create_StatsDB_file(state,serv_df)
        database_formatter.format_dataframe(stat_df,serv_df)