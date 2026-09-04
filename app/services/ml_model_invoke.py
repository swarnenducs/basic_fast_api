"""ML scoring hook. Returns the static response schema for now."""

from app.schemas.response import STATIC_ML_RESPONSE


class MLModelInvoke:
    def invoke_ml_model(self, _):
        """Implement your code"""
        return STATIC_ML_RESPONSE
