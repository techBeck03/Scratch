#!/usr/bin/env python
import pymysql
import argparse
import time

PERSEUS_RDP_SERVERS = 'Perseus-Users-RDP'

parser = argparse.ArgumentParser()
parser.add_argument('--cec', help='CEC (or sAMAccountname) of user to add', required=True)
parser.add_argument('--db_host', help='DB hostname or IP', required=True)
parser.add_argument('--db_port', type=int, help='Mariadb port', required=True)
parser.add_argument('--db_user', help='DB username', required=True)
parser.add_argument('--db_password', help='DB user password', required=True)
parser.add_argument('--db_name', help='Database name', required=True)
args = parser.parse_args()

# Connect to Guacamole DB HAProxy
conn = pymysql.connect(host=args.db_host, port=args.db_port, user=args.db_user, passwd=args.db_password, db=args.db_name, cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# Check if user already exists
results = cur.execute("SELECT username FROM guacamole_user WHERE username=%s",(args.cec))

# Skip if user already exists
if results > 0:
    print("User {user} already exists...skipping".format(user=args.cec))
    cur.close()
    conn.close()
    exit(0)

# Get the target RDP Group
cur.execute("SELECT connection_id,connection_name FROM guacamole_connection WHERE connection_name=%s",(PERSEUS_RDP_SERVERS))
rdp_connection = cur.fetchone()

# Insert new user
cur.execute("INSERT INTO guacamole_user (username,disabled,expired,password_date) VALUES (%s,0,0,%s)",(args.cec,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
conn.commit()
user_id = cur.lastrowid

# Add connection permission
cur.execute("INSERT INTO guacamole_connection_permission (user_id,connection_id,permission) VALUES (%s,%s,'READ')",(user_id,rdp_connection["connection_id"]))
conn.commit()

# Close connections
cur.close()
conn.close()