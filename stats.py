import os
import mmap
import json
import filelock
import requests
from datetime import datetime

DUMP_FILE = 'stats.db'
WALLET_ADDR = '442uGwAdS8c3mS46h6b7KMPQiJcdqmLjjbuetpCfSKzcgv4S56ASPdvXdySiMizGTJ56ScZUyugpSeV6hx19QohZTmjuWiM'
TICKER_URL = 'https://api.cryptonator.com/api/ticker/xmr-usd'
STATS_URL = 'https://api.xmrpool.net/miner/{}/stats'.format(WALLET_ADDR)
MINER_URL = 'https://api.xmrpool.net/miner/{}/identifiers'.format(WALLET_ADDR)
LOCK = filelock.FileLock('/tmp/stats.lock')


def get_stats():
    data = {}
    data['ticker'] = requests.get(TICKER_URL).json()['ticker']
    data['stats'] = requests.get(STATS_URL).json()
    data['miners'] = requests.get(MINER_URL).json()
    data['timestamp'] = datetime.utcnow().timestamp()
    return data


def snapshot_stats():
    with LOCK.acquire(timeout=10):
        stats = get_stats()
        with open(DUMP_FILE, 'a') as f:
            f.write(json.dumps(stats))
            f.write('\n')
        return stats


def last_n(n, step_size=1):
    """returns last n items"""
    lines = [l.decode('utf8') for l in tail(n*step_size)]
    lines = lines[0::step_size]
    return list(map(json.loads, lines))


# <https://stackoverflow.com/a/6813975>
def tail(n):
    """returns last n lines from the dump"""
    with LOCK.acquire(timeout=5):
        try:
            size = os.path.getsize(DUMP_FILE)
        except FileNotFoundError:
            return []
        if size == 0:
            return []
        with open(DUMP_FILE, 'rb') as f:
            fm = mmap.mmap(f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
            try:
                for i in range(size - 1, -1, -1):
                    if fm[i] == ord('\n'):
                        n -= 1
                        if n == -1:
                            break
                return fm[i + 1 if i else 0:].splitlines()
            finally:
                fm.close()

