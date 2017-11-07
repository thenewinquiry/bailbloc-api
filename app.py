import stats
import config
from raven import Client
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler
from raven.contrib.flask import Sentry

CACHE_SIZE = 500
CACHE_STEP = 12
POLL_INTERVAL_MINS = 5
# so we get every CACHE_STEP * POLL_INTERVAL_MINS timestep
# e.g. if CACHE_STEP=12, POLL_INTERVAL_MINS=5, then timestep is every 60min

app = Flask(__name__)
sentry = Sentry(app, dsn=config.SENTRY_DSN)
client = Client(config.SENTRY_DSN)

def update_stats():
    """snapshot stats and append to cache"""
    print('Updating stats')
    try:
        stats.snapshot_stats()
    except:
        client.captureException()


@app.route('/')
def history():
    """return the last CACHE_SIZE stats,
    most recent first"""
    cache_size = request.args.get('n', CACHE_SIZE)
    cache_step = request.args.get('step', CACHE_STEP)
    last = reversed(stats.last_n(int(cache_size), step_size=int(cache_step)))
    return jsonify(list(last))

CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job('update_stats', update_stats, **{'trigger': 'interval', 'minutes': POLL_INTERVAL_MINS})
scheduler.start()


if __name__ == '__main__':
    app.run()