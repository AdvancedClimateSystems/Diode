import json


class JSON_RPCError(Exception):
    """ Base class for JSON-RPC errors. """
    def to_json(self):
        return json.dumps({
            'code': self.code,
            'message': self.__doc__,
        })


class ParseError(JSON_RPCError):
    """ Invalid JSON was received by the server. An error occurred on the
    server while parsing the JSON text.
    """
    code = -32700


class InvalidRequestError(JSON_RPCError):
    """ The JSON sent is not a valid Request object. """
    code = -32600


class MethodNotFoundError(JSON_RPCError):
    """ The method does not exist / is not available. """
    code = -32601


class InvalidParamsError(JSON_RPCError):
    """ Invalid methods parameter(s). """
    code = -32602


class InternalError(JSON_RPCError):
    """ Internal JSON-RPC error. """
    code = -32603
