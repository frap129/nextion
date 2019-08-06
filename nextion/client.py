import asyncio
import serial_asyncio

from .exceptions import CommandFailed, command_failed_codes

import logging

logger = logging.getLogger('nextion').getChild(__name__)

class NextionProtocol(asyncio.Protocol):
    EOL = b'\xff\xff\xff'
    def __init__(self):
        self.transport = None
        self.buffer = b''
        self.queue = asyncio.Queue()
        self.connect_future = asyncio.get_event_loop().create_future()

    def connection_made(self, transport):
        self.transport = transport
        self.transport._serial.write_timeout = None
        logger.info("Connected")
        self.connect_future.set_result(True)

    def data_received(self, data):
        self.buffer += data
        if self.EOL in self.buffer:
            messages = self.buffer.split(self.EOL)
            for message in messages:
                logger.info("received: %s", message.decode())
                self.queue.put_nowait(message)
            self.buffer = messages[-1]

    def write(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.transport.write(data + self.EOL)

    def connection_lost(self, exc):
        logger.error('Connection lost')
        self.connect_future = asyncio.get_event_loop().create_future()

class Nextion:
    connection: NextionProtocol

    def __init__(self, url, baudrate):
        self.url = url
        self.baudrate = baudrate
        self.connection = None

    def make_protocol(self) -> NextionProtocol:
        return NextionProtocol()

    async def connect(self):
        loop = asyncio.get_event_loop()
        _, self.connection = await serial_asyncio.create_serial_connection(loop, self.make_protocol, url=self.url, baudrate=self.baudrate)
        await self.connection.connect_future

        await self.write('connect')
        result = await self.read()

        assert result[:6] == b'comok '

    async def write(self, data):
        self.connection.write(data)

    async def read(self):
        return await self.connection.queue.get()

    async def command(self, command):
        await self.write(command)
        res = await self.read()

        if res == b'':
            return True
        else:
            print(res[0])
            error = command_failed_codes.get(res[0])
            if error:
                raise CommandFailed(error)

    async def sleep(self, on: bool):
        await self.command('sleep=' + ('1' if on else '0'))

    async def dim(self, val: int):
        assert 0 <= val <= 100

        await self.command('dim=' + str(val))