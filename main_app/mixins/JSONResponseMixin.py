import json
from django.http import HttpResponse


class JSONResponseMixin(object):
    # a mixin that can be used to render a JSON response
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(self.convert_context_to_json(context), **response_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)
