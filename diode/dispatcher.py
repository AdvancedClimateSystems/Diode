import json
from asyncio import coroutine


class Dispatcher(object):
    def route(self):
        """ Decorator for binding functions as JSON-RPC methods on
        :class:`Dispatcher` instance. The functions are converted to coroutines
        implicitly.

        .. code:: python

            app = Dispatcher()

            @app.route()
            def add(x, y):
                return x + y

            def sleep(n):
                asyncio.sleep(n)

        """
        def inner(f):
            self.__setattr__(f.__name__, coroutine(f))

        return inner

    def dispatch(self, msg):
        """ Dispatch JSON-RPC request.

        :param msg: JSON-RPC formatted string.
        """
        data = json.loads(msg)
        fn = getattr(self, data['method'])

        try:
            params = data['params']
        except KeyError:
            return fn()

        if isinstance(params, list):
            return fn(*params)

        return fn(**params)
