import json
import asyncio

from diode.json_rpc import validate_request, build_response, build_error
from diode.exceptions import (JSON_RPCError, ParseError, MethodNotFoundError,
                              InvalidRequestError, InvalidParamsError,
                              InternalError)


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
            self.__setattr__(f.__name__, asyncio.coroutine(f))

        return inner

    @asyncio.coroutine
    def dispatch(self, msg):
        """ Dispatch JSON-RPC request.

        :param msg: JSON-RPC formatted string.
        :return: JSON-RPC formatted string.
        """
        try:
            try:
                data = json.loads(msg)
            except TypeError:
                raise ParseError

            validate_request(data)

            try:
                result = yield from self.execute(**data)
            except TypeError:
                raise InvalidParamsError

            try:
                return build_response(result=result, id_=data['id'])
            # Server must not reply when request doesn't contain 'id' attribute.
            except KeyError:
                pass
        except JSON_RPCError as e:
            return build_error(e, data.get('id', False))
        except:
            return build_error(InternalError(), data.get('id', False))

    @asyncio.coroutine
    def execute(self, jsonrpc, method, params=None, id=None):
        """ Execute method mentioned in JSON-RPC request.

        :param jsonrpc: Number specifying version of JSON-RPC protocol.
        :param method: String containing name of method to invoke.
        :param params: Method's arguments. Default None.
        :param id: Request identifier.
        :return: Result of method.
        :raises: :class:`MethodNotFoundError`, when calling unknown method.
        """
        try:
            fn = getattr(self, method)
        except AttributeError:
            raise MethodNotFoundError

        if params is None:
            result = yield from fn()
            return result

        if isinstance(params, list):
            result = yield from fn(*params)
            return result

        result = yield from fn(**params)
        return result
