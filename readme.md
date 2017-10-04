setup:

    pip install -r requirements.txt

run:

    python app.py

use:

    GET localhost:5000/

to get last `CACHE_SIZE` stats updates.

---

notes:

- polls stats endpoints every `POLL_INTERVAL_MINS`
- `/` endpoint returns `CACHE_SIZE` most recent stats, most recent first