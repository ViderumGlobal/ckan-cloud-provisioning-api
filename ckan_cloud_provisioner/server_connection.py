from io import StringIO
import os
import sys

import fabric
from paramiko import RSAKey
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from .config import instance_manager, default_timeout

private_ssh_key = os.environ['PRIVATE_SSH_KEY']
private_ssh_key = StringIO(private_ssh_key)
private_ssh_key = RSAKey.from_private_key(private_ssh_key)

def get_connection():
    return fabric.Connection(instance_manager, connect_kwargs=dict(pkey=private_ssh_key))


server_executor = ThreadPoolExecutor(max_workers=1)


def execute_remote(func):
    try:
        res = server_executor.submit(func)
        return res.result(timeout=default_timeout)
    except TimeoutError:
        return {}
    except Exception as e:
        return dict(
            success=False,
            errors=str(e)
        )


def ping():
    def func():
        import logging
        try:
            ping = get_connection().run('echo ping', hide='both')
            logging.error('PING RESULT %r', ping.stdout)
            logging.error('PING ERRORS %r', ping.stderr)
        except Exception as e:
            logging.error('PING ERROR %r', e)

    execute_remote(func)

ping()