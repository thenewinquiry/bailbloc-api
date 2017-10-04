import stats
from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from collections import deque

CACHE_SIZE = 200
POLL_INTERVAL_MINS = 1
cache = deque(list(reversed(stats.last_n(CACHE_SIZE))), maxlen=CACHE_SIZE)
app = Flask(__name__)


def update_stats():
    """snapshot stats and append to cache"""
    print('Updating stats')
    data = stats.snapshot_stats()
    cache.appendleft(data)


@app.route('/')
def history():
    """return the last CACHE_SIZE stats,
    most recent first"""
    return jsonify(list(cache))


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job('update_stats', update_stats, **{'trigger': 'interval', 'minutes': POLL_INTERVAL_MINS})
scheduler.start()


if __name__ == '__main__':
    app.run()