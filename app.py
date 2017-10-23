import stats
from flask_cors import CORS
from flask import Flask, jsonify
from flask_apscheduler import APScheduler

CACHE_SIZE = 500
CACHE_STEP = 12
POLL_INTERVAL_MINS = 5
# so we get every CACHE_STEP * POLL_INTERVAL_MINS timestep
# e.g. if CACHE_STEP=12, POLL_INTERVAL_MINS=5, then timestep is every 60min

app = Flask(__name__)


def update_stats():
    """snapshot stats and append to cache"""
    print('Updating stats')
    stats.snapshot_stats()


@app.route('/')
def history():
    """return the last CACHE_SIZE stats,
    most recent first"""
    last = reversed(stats.last_n(CACHE_SIZE, step_size=CACHE_STEP))
    return jsonify(list(last))

CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job('update_stats', update_stats, **{'trigger': 'interval', 'minutes': POLL_INTERVAL_MINS})
scheduler.start()


if __name__ == '__main__':
    app.run()