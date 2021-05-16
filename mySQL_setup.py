import mysql.connector
from mysql.connector import errorcode

#Define tables
TABLES = {}
TABLES['experiments'] = (
    "CREATE TABLE `experiments` (" 
    "`simNum` INT AUTO_INCREMENT,"
    "`simDateTime` datetime DEFAULT NOW(),"
    "`simLen` INT NOT NULL,"
    "`stepSize` FLOAT NOT NULL,"
    "PRIMARY KEY (`simNUM`)"
    ") ENGINE=InnoDB")

TABLES['trajectories'] = (
    "CREATE TABLE `trajectories` ("
    "`obsNum` INT AUTO_INCREMENT,"
    "`simNum` INT NOT NULL,"
    "`stepNum` INT NOT NULL,"
    "`xpos` FLOAT NOT NULL,"
    "`ypos` FLOAT NOT NULL,"
    "PRIMARY KEY (`obsNum`),"
    "FOREIGN KEY (`simNum`)"
    "   REFERENCES `experiments`(`simNum`)"
    "   ON UPDATE CASCADE ON DELETE CASCADE"
    ") ENGINE=InnoDB")

TABLES['sq_displacements'] = (
    "CREATE TABLE `sq_displacements` ("
    "`obsNum` INT AUTO_INCREMENT,"
    "`simNum` INT NOT NULL,"
    "`stepSize` INT NOT NULL,"
    "`sd` FLOAT NOT NULL,"
    "PRIMARY KEY (`obsNum`),"
    "FOREIGN KEY (`simNum`)"
    "   REFERENCES `experiments`(`simNum`)"
    "   ON UPDATE CASCADE ON DELETE CASCADE"
    ") ENGINE=InnoDB")

TABLES['msdSetMeta'] = (
    "CREATE TABLE `msdSetMeta` ("
    "`setNum` INT AUTO_INCREMENT,"
    "`setDateTime` datetime DEFAULT NOW(),"
    "`simCount` INT NOT NULL,"
    "PRIMARY KEY(`setNum`)"
    ") ENGINE=InnoDB")

TABLES['msdSets'] = (
    "CREATE TABLE `msdSets` ("
    "`setNum` INT NOT NULL,"
    "`simNum` INT NOT NULL,"
    "PRIMARY KEY (`setNum`, `simNum`),"
    "FOREIGN KEY (`setNum`)"
    "   REFERENCES `msdSetMeta`(`setNum`)"
    "   ON UPDATE CASCADE ON DELETE RESTRICT,"
    "FOREIGN KEY (`simNum`)"
    "   REFERENCES `experiments`(`simNum`)"
    "   ON UPDATE CASCADE ON DELETE RESTRICT"
    ") ENGINE=InnoDB")

TABLES['MSDs'] = (
    "CREATE TABLE `MSDs` ("
    "`obsNum` INT AUTO_INCREMENT,"
    "`setNum` INT,"
    "`stepNum` INT NOT NULL,"
    "`msd` FLOAT NOT NULL,"
    "`stdev` FLOAT NOT NULL,"
    "`sdCount` INT NOT NULL,"
    "PRIMARY KEY (`obsNum`),"
    "FOREIGN KEY(`setNum`)"
    "   REFERENCES `msdSets`(`setNum`)"
    "   ON UPDATE CASCADE ON DELETE RESTRICT"
    ") ENGINE=InnoDB")
#Connect to server 
cnx = mysql.connector.connect(
        host='localhost',
	user='root',
	password='password'
	)
cursor = cnx.cursor()

#Ensure DB exists or create
DB_name = '2D_walk'
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(DB_name))
except mysql.connector.Error as err:
    print("Database {} does not exist.".format(DB_name))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_name))
        cnx.database = DB_name
    else:
        print(err)
        exit(1)        

#Attempt to create tables
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

#Wrap up
cnx.commit()
cursor.close()
cnx.close()
