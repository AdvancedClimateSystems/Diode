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


def build_json_rpc_response(result, id_):
    """ Return a JSON-RPC formatted response object.

    :param result: Result of a method call.
    :param id_: Response id.
    :return: JSON-RPC formatted string.
    """
    return json.dumps({
        "jsonrpc": "2.0",
        "result": result,
        "id": id,
    })


def build_json_rpc_error(error, id_=False):
    """ Create JSON-RPC error response. When `id_` is False, response id
    is `None`.

    :param error: Instance of JSON_RPCError.
    :param id_: Response id, default is False.
    :return: JSON-RPC formatted string.
    """
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
        :return: JSON-RPC formatted string.
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
                return build_json_rpc_response(result=result, id_=data['id'])
            # Server must not reply when request doesn't contain 'id' attribute.
            except KeyError:
                pass
        except JSON_RPCError as e:
            return build_json_rpc_error(e, data.get('id', False))
        except:
            return build_json_rpc_error(InternalError(), data.get('id', False))

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
