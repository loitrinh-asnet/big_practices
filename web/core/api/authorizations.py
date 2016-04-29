from tastypie.exceptions import BadRequest
from tastypie.authorization import Authorization
import json


class CustomAuthorization(Authorization):
    """Custom authorization."""

    def is_authorized(self, request, object=None):
        """Only logged in user will can modify entry."""
        raise BadRequest(json.dumps({"error": "Authorization error"}))

    def apply_limits(self, request, object_list=None):
        """Only allow delete/modify Entry belong to this user."""
        if request.method in ("DELETE", "PUT"):
            filter_list = object_list.filter_list(created_by=request.user.get_profile())
            if not filter_list:
                raise BadRequest(json.dumps({"error": "Authorization error"}))
            return filter_list
        return object_list
