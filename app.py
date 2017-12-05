import stats
import config
from flask_cors import CORS
from flask import Flask, jsonify, request
from raven.contrib.flask import Sentry

CACHE_SIZE = 500
CACHE_STEP = 4
# so we get every CACHE_STEP * POLL_INTERVAL_MINS timestep
# e.g. if CACHE_STEP=4, POLL_INTERVAL_MINS=15, then timestep is every 60min

app = Flask(__name__)
sentry = Sentry(app, dsn=config.SENTRY_DSN)

@app.route('/')
def history():
    """return the last CACHE_SIZE stats,
    most recent first"""
    cache_size = request.args.get('n', CACHE_SIZE)
    cache_step = request.args.get('step', CACHE_STEP)
    last = stats.last_n_with_cache(int(cache_size), step_size=int(cache_step))
    return jsonify(last)

CORS(app)

if __name__ == '__main__':
    app.run()