import stats
from flask import Flask, jsonify
from collections import deque
from apscheduler.schedulers.background import BackgroundScheduler

CACHE_SIZE = 200
POLL_INTERVAL_MINS = 5
cache = deque(list(reversed(stats.last_n(CACHE_SIZE))), maxlen=CACHE_SIZE)
app = Flask(__name__)


def update_stats():
    """snapshot stats and append to cache"""
    data = stats.snapshot_stats()
    cache.appendleft(data)


@app.route('/')
def history():
    """return the last CACHE_SIZE stats,
    most recent first"""
    return jsonify(list(cache))


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_stats, **{'trigger': 'interval', 'minutes': POLL_INTERVAL_MINS})
    scheduler.start()

    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()