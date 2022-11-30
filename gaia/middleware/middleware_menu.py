class menu_middleware_items(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        try:
            print(request.path)

            if '/bases/listado/' in request.path:
                request.session['item'] = 'inicio'
                request.session['sub_item'] = 'listado_de_bases'

            if 'bases/add/base/datos/' in request.path:
                request.session['item'] = 'inicio'
                request.session['sub_item'] = 'listado_de_bases'

            if 'bases/armar/intruccion/' in request.path:
                request.session['item'] = 'git'
                request.session['sub_item'] = 'armar_instruccion'

            if 'bases/web/scraping/' in request.path:
                request.session['item'] = 'web'
                request.session['sub_item'] = 'webscraping'

        except:
            pass
