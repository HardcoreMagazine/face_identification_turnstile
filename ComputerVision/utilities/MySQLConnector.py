import mysql.connector as mql


class MySQLConnector:
    def __init__(self, host='localhost', user='developer',
                 passwd='developer', database='cv2', table='visitors'):
        """
        Called on object initialization.
        It sets database variables, required for connection
        :param self: represent the instance of the class
        :param host: IPv4 of remote database server
        :param user: username for database write access
        :param passwd: user password
        :param database: working database name
        :param table: working table name within selected database
        """
        self.__host = host
        self.__user = user
        self.__passwd = passwd
        self.__database = database
        self.__table = table

    def ConnectAndQuery(self, name, date):
        """
        Connects to the MySQL database and inserts a record into the table.
        :param name: detected user's name
        :param date: current date
        """
        if not name or not date:
            print('MySQL> No data provided')
        else:
            db_conn = mql.connect(host=self.__host, user=self.__user,
                                  password=self.__passwd, db=self.__database)
            db_cursor = db_conn.cursor()
            db_cursor.execute(f"INSERT INTO `{self.__database}`.`{self.__table}` "
                              f"(`full_name`, `time`) VALUES ('{name}', '{date}');")
            db_conn.commit()
            print(f'MySQL> {db_cursor.rowcount} record inserted.')
            db_cursor.close()
            db_conn.close()
