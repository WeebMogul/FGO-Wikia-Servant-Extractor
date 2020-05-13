import stats_database as ssdb
import database_formatter
import servant_database as stdb

state,serv_df = stdb.ServantDB().create_ServantDB_file()
stat_df = ssdb.StatsDB().create_StatsDB_file(state,serv_df)
database_formatter.format_dataframe(stat_df,serv_df)