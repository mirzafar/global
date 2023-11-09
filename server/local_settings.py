import os

settings = {
    'mongo': {
        'db_host': '127.0.0.1',
        'db_port': 27017,
        'db_database': 'diplomdb'
    },
    'db': {
        'host': '127.0.0.1',
        'database': 'postgres',
        'port': 5433,
        'user': 'postgres',
        'password': '1234',
    },

    'tg': {
        # 'token': '6355183591:AAFEZD9E2JnmV7p1PsyXYaC6r_d5oPNAZME'
        'token': '1047171618:AAESsy8R1FmqI8aqd9UniehB3KDSsG_rlRY'
    },
    'redis': 'redis://127.0.0.1:6379',
    'mq': 'amqp://guest:guest@127.0.0.1/',
    'root_dir': os.path.dirname(os.path.abspath(__file__)),
    'file_path': '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])
}
