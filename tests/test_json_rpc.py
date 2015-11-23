import json
import pytest

from diode.json_rpc import validate_request, build_response, build_error
from diode.exceptions import InvalidRequestError


def test_validate_request_without_error():
    """ 'validate_request' should validate request without exception. """
    assert validate_request({'jsonrpc': '2.0', 'method': 'add'}) is None


def test_validate_request_with_invalid_jsonrpc_attribute():
    """ 'validate_request' should raise InvalidRequestError when
    JSON-RPC version is not '2.0'.
    """
    with pytest.raises(InvalidRequestError):
        validate_request({'jsonrpc': '1.0'})


def test_validate_request_with_invalid_method_attribute():
    """ 'validate_request` should raise InvalidRequestError when method
    attribute in request is not a string.
    """
    with pytest.raises(InvalidRequestError):
        validate_request({'jsonrpc': '2.0', 'method': 3})


def test_validate_request_with_invalid_param_attribute():
    """ 'validate_request' should raise InvalidRequestError when param attribute
    in request is available but not of type list or dict.
    """
    with pytest.raises(InvalidRequestError):
        validate_request({'jsonrpc': '2.0', 'method': 'add', 'params': 3})


def test_build_response():
    assert build_response('result', 1) == json.dumps({'jsonrpc': '2.0',
                                                      'result': 'result',
                                                      'id': 1})


def test_build_error_with_id():
    expected = json.dumps({'jsonrpc': '2.0',
                           'error': InvalidRequestError().to_json(),
                           'id': 3})
    assert build_error(InvalidRequestError(), 3) == expected
