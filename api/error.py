from api.schemas import error_schema
from api.models import Error
from flask import jsonify


def error_response(code):
    """
        Construct json response from error code
        Args:
            code(int): Error Code specified in error table json file
        Returns:
            Tuple of those items
                 resp(Response): Flask.Response object
                http_code (int): error code
    """
    error = Error.query.filter_by(code=code).first()
    result = error_schema.dump(error)[0]
    return jsonify(result), error.http_code
