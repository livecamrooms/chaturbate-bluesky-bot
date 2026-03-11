name: Chaturbate Bluesky Bot

on:
  schedule:
    - cron: '0 * * * *'      # Every hour
  workflow_dispatch:         # Manual trigger button

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6      # ← UPDATED (Node 24)
      
      - name: Set up Python
        uses: actions/setup-python@v6   # ← UPDATED (Node 24)
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install atproto requests
      
      - name: Run bot
        env:
          BLUESKY_HANDLE: ${{ secrets.BLUESKY_HANDLE }}
          BLUESKY_PASSWORD: ${{ secrets.BLUESKY_PASSWORD }}
        run: python bot.py
