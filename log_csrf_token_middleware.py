import logging


class LogCsrfTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        logging.error(f'MIDDLEWARE CALLED')
        logging.error(f'Request headers: {request.headers}')
        logging.error(f'Response headers: {response.headers}')
        if response.has_header('X-CSRFToken'):
            csrf_token = response.get('X-CSRFToken')
            logging.error(f'CSRF TOKEN: {csrf_token}')

        return response
