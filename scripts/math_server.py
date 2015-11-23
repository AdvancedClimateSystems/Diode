#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '../'))

import math
import asyncio

from diode import Dispatcher

app = Dispatcher()

@asyncio.coroutine
def handler(reader, writer):
    """ A handler for asynchronous request handling. """
    msg = yield from reader.read(1024)
    msg = msg.decode('utf-8')
    resp = yield from app.dispatch(msg)

    writer.write(resp.encode('utf-8'))
    yield from writer.drain()
    writer.close()


@app.route()
def add(x, y):
    """ Return sum of x and y. """
    print('Add {} and {}.'.format(x, y))
    return x + y


@app.route()
def factorial(n):
    """ Calculate factorial of n. This is very hard and might take a while. """
    print('Calculating factorial of {}. This might take a while...'.format(n))

    yield from asyncio.sleep(5)
    res = math.factorial(n)
    print('Factorial of {} is {}.'.format(n, res))

    return res

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handler, '127.0.0.1', 8888, loop=loop)
    server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

# Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
