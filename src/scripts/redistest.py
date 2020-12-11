# Using python 3.8
import redis
import os
from time import sleep
#import requests
if os.environ.get('RUNFOREVER') and int(os.environ['RUNFOREVER']) == 1:
    RUNFOREVER = 1
else:
    RUNFOREVER = 0

rdb = redis.Redis(
host=str(os.environ['DB_HOSTNAME']),
port=int(os.environ['DB_PORT']),
password=str(os.environ['DB_PASSWORD']))

### Using SSL
# r = redis.Redis( url='rediss://:password@hostname:port/0',
# password='password',
# ssl_keyfile='path_to_keyfile',
# ssl_certfile='path_to_certfile',
# ssl_cert_reqs='required',
# ssl_ca_certs='path_to_ca_certfile')

# .set(name, value, ex=<ms expiry>, px=<sec expiry>)
rdb.set('foo', 'bar', px=200)
value = rdb.get('foo')
if value:
    print("OK")

sleep(15)

if RUNFOREVER == 1:
    counter = 0
    while True:
        if counter == 0:
            print(value)
        print("Still alive")
        counter = 1
        sleep(3600) # sleep 1hr

exit(0)
