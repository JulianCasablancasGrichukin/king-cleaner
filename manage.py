import argparse
import os
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from db import connect
from schema import install

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')


def backup():
    destination=ROOT/'.local'/'backups'
    destination.mkdir(parents=True,exist_ok=True)
    target=destination/(datetime.now().strftime('%Y%m%d-%H%M%S')+'.sql')
    connection=connect()
    try:
        with connection.cursor() as c, target.open('w',encoding='utf-8') as f:
            c.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT')
            c.execute('SHOW FULL TABLES'); objects=c.fetchall()
            f.write('SET FOREIGN_KEY_CHECKS=0;\n')
            for row in objects:
                name,kind=list(row.values())
                if kind!='BASE TABLE': continue
                safe=name.replace('`','``')
                c.execute(f'SHOW CREATE TABLE `{safe}`'); f.write(list(c.fetchone().values())[1]+';\n')
                c.execute(f'SELECT * FROM `{safe}`')
                for record in c.fetchall():
                    columns=','.join('`'+x.replace('`','``')+'`' for x in record)
                    statement=f'INSERT INTO `{safe}` ({columns}) VALUES ('+','.join(['%s']*len(record))+');\n'
                    f.write(c.mogrify(statement,tuple(record.values())))
            for row in objects:
                name,kind=list(row.values())
                if kind=='VIEW':
                    c.execute('SHOW CREATE VIEW `'+name.replace('`','``')+'`')
                    f.write(c.fetchone()['Create View']+';\n')
            f.write('SET FOREIGN_KEY_CHECKS=1;\n')
    finally: connection.close()
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='KING CLEANER · Administración local')
    parser.add_argument('action',choices=['init','migrate','backup'])
    args=parser.parse_args()
    if args.action=='init':
        name=os.getenv('DB_NAME','control_produccion_db')
        if not re.fullmatch('[A-Za-z0-9_]+',name): raise ValueError('Nombre de base inválido')
        connection=connect(database=False)
        try:
            with connection.cursor() as c:
                c.execute(f'CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            connection.commit()
        finally: connection.close()
        install(new=True)
        print('Base nueva inicializada sin registros de ejemplo.')
    elif args.action=='migrate':
        target=backup()
        print('Copia previa: '+str(target))
        install(new=False)
        print('Extensiones instaladas. Las tablas y vistas originales se conservaron.')
    else: print('Copia guardada: '+str(backup()))
