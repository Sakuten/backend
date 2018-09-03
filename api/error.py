from api.schemas import error_schema
from api.models import Error
from flask import jsonify

def error_response(code):
    """
        Construct json response from error code
        Args:
            code(int): Error Code specified in error table json file
        Returns:
            resp(Response): flask response with error message
    """
    error = Error.query().filter_by(code=code).first()
    result = error_schema.dump(error)[0]
    return jsonify(result), error.http_code
