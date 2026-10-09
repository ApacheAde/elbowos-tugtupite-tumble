# Tugtupite Tumble

Full-colour Python 3 crimson boulder-run arcade for ElbowOS.

Steer a spinning tugtupite boulder down a navy ice stair. Scoop pearl shards. Black spikes break the streak.

Not a commercial emulator and not a ROM.

Featured account: https://x.com/ElbowOS

Drive reel: https://drive.google.com/file/d/1_v9VkEToDVIjdbTzyrs7qbpjpQZ6ER6q/view

## Play

```
pip install -r requirements.txt
python3 tugtupite_tumble.py --play
```

A / Left and D / Right steer. R restarts.

## Record a 9:16 reel

```
python3 tugtupite_tumble.py --record
```

Headless autoplay writes a 1080x1920, 15-second, 30fps H.264 MP4. Dummy SDL video is used if there is no display.
