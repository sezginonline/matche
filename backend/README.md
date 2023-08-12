### Installation

```bash
# Install
pip install .

# Dev
sanic run.app --dev

# Debug
sanic run.app --debug

# Production goin' fast w/ 16 workers
python run.py

# Production single worker
sanic run.app

# Host and port
sanic run:app --host=match-e.com --port=443

# Testing
cd tests
pytest
pytest test_example.py
```

* Set FORWARDED_SECRET both .env and nginx.conf
