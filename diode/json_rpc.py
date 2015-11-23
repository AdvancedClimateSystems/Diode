import json

from diode.exceptions import InvalidRequestError


def validate_request(data):
    """ Validate JSON-RPC request object.

    :param data: A dictionary representing a JSON-RPC request.
    :raises: :class:`InvalidRequestError`.
    """
    try:
        assert data['jsonrpc'] == '2.0'
        assert isinstance(data['method'], str)

        # If 'params' attribute is available it must be of type list or dict.
        assert isinstance(data.get('params', list()), list) or \
            isinstance(data.get('params', dict()), dict)
    except (KeyError, AssertionError):
        raise InvalidRequestError


def build_response(result, id_):
    """ Return a JSON-RPC formatted response object.

    :param result: Result of a method call.
    :param id_: Response id.
    :return: JSON-RPC formatted string.
    """
    return json.dumps({
        'jsonrpc': '2.0',
        'result': result,
        'id': id_,
    })


def build_error(error, id_=False):
    """ Create JSON-RPC error response. When `id_` is False, response id
    is `None`.

    :param error: Instance of JSON_RPCError.
    :param id_: Response id, default is False.
    :return: JSON-RPC formatted string.
    """
    return json.dumps({
        'jsonrpc': '2.0',
        'error': error.to_json(),
        'id': None if id_ is None else id_,

    })
