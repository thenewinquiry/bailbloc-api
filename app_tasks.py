import stats
import config
from raven import Client
from flask import Flask
from flask_apscheduler import APScheduler
from raven.contrib.flask import Sentry

POLL_INTERVAL_MINS = 15
# so we get every CACHE_STEP * POLL_INTERVAL_MINS timestep
# e.g. if CACHE_STEP=4, POLL_INTERVAL_MINS=15, then timestep is every 60min

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

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job('update_stats', update_stats, **{'trigger': 'interval', 'minutes': POLL_INTERVAL_MINS})
scheduler.start()

if __name__ == '__main__':
    app.run(port=5001)
