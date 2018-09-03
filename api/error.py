from schemas import error_schema
from models import Error


def error_response(code, http_code):
    """
        Construct json response from error code
        Args:
            code(int): Error Code specified in error table json file
            http_code(int): HTTP Error Code
        Returns:
            resp(Response): flask response with error message
    """
    error = Error.query().filter_by(code=code).first()
    result = error_schema.dump(error)[0]
    return jsonify(result), http_code
