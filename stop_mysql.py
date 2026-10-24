import json
from pathlib import Path
import pymysql
config=json.loads((Path(__file__).parent/'.local'/'mysql-admin.json').read_text())
try:
    connection=pymysql.connect(host='127.0.0.1',port=config['port'],user=config['user'],password=config['password'])
except pymysql.OperationalError as error:
    if error.args[0]==2003:
        print('MySQL ya estaba detenido.')
        raise SystemExit(0)
    raise
try:
    with connection.cursor() as c: c.execute('SHUTDOWN')
finally: connection.close()
