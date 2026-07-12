from __future__ import annotations

import os
import sys


def main() -> int:
    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        print("REDIS_URL is required for the Render background worker.", file=sys.stderr)
        return 2
    from redis import Redis
    from rq import Queue, Worker

    connection = Redis.from_url(redis_url)
    queue_name = os.getenv("SC_LAB_QUEUE_NAME", "sc-lab-compute")
    worker = Worker([Queue(queue_name, connection=connection)], connection=connection)
    worker.work(with_scheduler=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
