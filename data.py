import cx_Oracle
from configparser import ConfigParser

class VesselInfo :

	def __init__(self,mmsi = None) :
		self.mmsi = mmsi

	def init_db(self) :
		config = ConfigParser()
		config.read_file(open('config.ini'))
		username = config['ORACLE_DATABASE']['username']; 			
		password = config['ORACLE_DATABASE']['password']; 		
		db = "(DESCRIPTION =(ADDRESS_LIST =(ADDRESS =(PROTOCOL = TCP)(HOST = 192.168.20.51)(PORT = 1521)))(CONNECT_DATA =(SID = ais)(SERVER = DEDICATED)))";
		connection = cx_Oracle.connect(username, password, db)
		return connection

	def get_vessel_info(self) :
		connection = self.init_db()
		cursor = connection.cursor()
		cursor.execute("""
		    SELECT mmsi, name, lat, lon, destination, eta, sog, cog, size_a, size_b,
				to_char(last_posdate,'FMMonth ddth, YYYY HH24:MI:SS') last_posdate_,
				to_char(last_posdate,'Day') day  
					, (SELECT name from COUNTRYMID WHERE COUNTRYMID.ID = SUBSTR(vessel_info.mmsi,1,3)) country
			FROM vessel_info WHERE mmsi= :mmsi """,
		    mmsi = self.mmsi
		   )
		return cursor

	def get_vessel_info_by_keyword(self, arg_keyword) :
		connection = self.init_db()
		cursor = connection.cursor()
		cursor.arraysize = 4
		cursor.execute("""
		    select mmsi, name, lon, lat, to_char((last_posdate + INTERVAL '7' HOUR),'DD-MM-YYYY HH24:MI:SS') last_posdate_ 
				FROM vessel_info 
				WHERE (upper(name) like upper('%' || :arg_keyword || '%') OR (MMSI LIKE '%' || :arg_keyword || '%'))
				and rownum < 5 """,
		    arg_keyword = arg_keyword
		   )
		return cursor
		
class LastPosdate :

	def get_global_last_posdate(self) :
		connection = VesselInfo.init_db(self)
		cursor = connection.cursor()
		cursor.execute("select * from view_get_last_posdate")
		return cursor