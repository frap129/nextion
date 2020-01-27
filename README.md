# Nextion serial client [![Build Status](https://travis-ci.org/yozik04/nextion.svg?branch=master)](https://travis-ci.org/yozik04/nextion)
Lightweight Python 3.5+ async library to control Nextion displays.

## Installation
### Pypi
`pip install nextion`

## Simple usage:
```python
import asyncio
import logging
import random

from nextion import Nextion, EventType

def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')

    logging.info('Event %s data: %s' % (type, str(data)))

async def run():
    client = Nextion('/dev/ttyS1', 9600, event_handler)
    await client.connect()

    # await client.sleep()
    # await client.wakeup()

    # await client.command('sendxy=0')

    print(await client.get('sleep'))
    print(await client.get('field1.txt'))

    await client.set('field1.txt', "%.1f" % (random.randint(0, 1000) / 10))
    await client.set('field2.txt', "%.1f" % (random.randint(0, 1000) / 10))
    
    await client.set('field3.txt', random.randint(0, 100))

    print('finished')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run())
    loop.run_forever()
```

## Event handling

```event_handler``` method in the example above will be called on every event comming from the display.

| EventType        | Data                       | Data attributes                    |
|------------------|----------------------------|------------------------------------|
| TOUCH            | TouchDataPayload           | page_id, component_id, touch_event |
| TOUCH_COORDINATE | TouchCoordinateDataPayload | x, y, touch_event                  |
| TOUCH_IN_SLEEP   | TouchCoordinateDataPayload | x, y, touch_event                  |
| AUTO_SLEEP       | None                       | -                                  |
| AUTO_WAKE        | None                       | -                                  |
| STARTUP          | None                       | -                                  |
| SD_CARD_UPGRADE  | None                       | -                                  |

For some components in the Nextion Editor you need to check `Send Component ID` for required event.

# Additional resources:
- https://www.itead.cc/wiki/Nextion_Instruction_Set
- [PyPI](https://pypi.org/project/nextion/)
