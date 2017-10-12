import stats
from flask_cors import CORS
from flask import Flask, jsonify
from flask_apscheduler import APScheduler

CACHE_SIZE = 500
POLL_INTERVAL_MINS = 5
app = Flask(__name__)


def update_stats():
    """snapshot stats and append to cache"""
    print('Updating stats')
    stats.snapshot_stats()


@app.route('/')
def history():
    """return the last CACHE_SIZE stats,
    most recent first"""
    last = reversed(stats.last_n(CACHE_SIZE))
    return jsonify(list(last))

CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job('update_stats', update_stats, **{'trigger': 'interval', 'minutes': POLL_INTERVAL_MINS})
scheduler.start()


if __name__ == '__main__':
    app.run()