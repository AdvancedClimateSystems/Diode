import json
import asyncio

from diode.exceptions import (JSON_RPCError, ParseError, MethodNotFoundError,
                              InvalidRequestError, InvalidParamsError,
                              InternalError)


def validate_json_rpc_request(data):
    """ Validate JSON-RPC request object.

    :param data: A dictionary representing a JSON-RPC request.
    :raises: :class:`InvalidRequestError`.
    """
    try:
        assert data['jsonrpc'] == "2.0"
        assert isinstance(data['method'], str)

        # If 'params' attribute is available it must be of type list or dict.
        assert isinstance(data.get('params', list), list) or \
            isinstance(data.get('params', dict), dict)
    except (KeyError, AssertionError):
        raise InvalidRequestError


def build_json_rpc_response(result, id):
    """ Return a JSON-RPC formatted response object. """
    return json.dumps({
        "jsonrpc": "2.0",
        "result": result,
        "id": id,
    })


def build_json_rpc_error(error, id_=None):
    return json.dumps({
        "jsonrpc": "2.0",
        "error": error.to_json(),
        "id": None if id_ is None else id_,

    })


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

        """
        try:
            try:
                data = json.loads(msg)
            except TypeError:
                raise ParseError

            validate_json_rpc_request(data)

            try:
                result = yield from self.execute(**data)
            except TypeError:
                raise InvalidParamsError

            try:
                return build_json_rpc_response(result=result, id=data['id'])
            # Server must not reply when request doesn't contain 'id' attribute.
            except KeyError:
                pass

        except JSON_RPCError as e:
            return build_json_rpc_error(e)
        except:
            return build_json_rpc_error(InternalError())

    @asyncio.coroutine
    def execute(self, jsonrpc, method, params=None, id=None):
        """ Execute method mentioned in JSON-RPC request. """
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
