import os
import mmap
import json
import filelock
import requests
from datetime import datetime
from collections import defaultdict

DUMP_FILE = 'stats.db'
WALLET_ADDR = '442uGwAdS8c3mS46h6b7KMPQiJcdqmLjjbuetpCfSKzcgv4S56ASPdvXdySiMizGTJ56ScZUyugpSeV6hx19QohZTmjuWiM'
TICKER_URL = 'https://api.cryptonator.com/api/ticker/xmr-usd'
STATS_URL = 'https://api.xmrpool.net/miner/{}/stats'.format(WALLET_ADDR)
MINER_URL = 'https://api.xmrpool.net/miner/{}/identifiers'.format(WALLET_ADDR)
LOCK = filelock.FileLock('/tmp/stats.lock')

# cache results in memory, refresh at an interval
# lower than the stats update interval
CACHED = {}
LAST_CHECKED = defaultdict(lambda: datetime.now())
REFRESH_INTERVAL = 60 * 5 # seconds


def get_stats():
    data = {}
    data['ticker'] = requests.get(TICKER_URL).json()['ticker']
    data['stats'] = requests.get(STATS_URL).json()
    data['miners'] = requests.get(MINER_URL).json()
    data['n_miners'] = len(data['miners'])
    data['timestamp'] = datetime.utcnow().timestamp()
    return data


def snapshot_stats():
    with LOCK.acquire(timeout=10):
        stats = get_stats()
        with open(DUMP_FILE, 'a') as f:
            f.write(json.dumps(stats))
            f.write('\n')
        return stats


def last_n_with_cache(n, step_size=1):
    key = '{}:{}'.format(n, step_size)
    time_since = (datetime.now() - LAST_CHECKED[key]).seconds
    if key not in CACHED or time_since >= REFRESH_INTERVAL:
        print('{}: refreshing cache:'.format(os.getpid()), key)
        LAST_CHECKED[key] = datetime.now()
        # try to refresh, but if not possible,
        # just use existing
        try:
            CACHED[key] = last_n(n, step_size)
        except filelock.Timeout:
            pass
    else:
        print('{}: loading from cache:'.format(os.getpid()), key)
    return CACHED[key]


def last_n(n, step_size=1):
    """returns last n items"""
    lines = list(l.decode('utf8') for l in tail(n*step_size))
    lines = list(reversed(lines))
    lines = lines[0::step_size]
    return list((map(json.loads, lines)))


# <https://stackoverflow.com/a/6813975>
def tail(n):
    """returns last n lines from the dump"""
    # check if the last line is an empty line
    # so we can adjust n accordingly
    if n > 0 and last_n(n=0):
        n -= 1
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

