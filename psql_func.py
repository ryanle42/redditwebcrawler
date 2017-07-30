import psycopg2

def db_init(cur):
	cur.execute("""CREATE TABLE IF NOT EXISTS users (name char(20), age int, pts int, activity int, PRIMARY KEY(name));""")

def db_adduser(cur, user):
	cur.execute("""INSERT INTO users (name, age, pts, activity) 
		SELECT %(name)s, %(age)s, %(pts)s, %(activity)s WHERE NOT EXISTS 
		(SELECT name FROM users WHERE name = %(name)s);""", user)