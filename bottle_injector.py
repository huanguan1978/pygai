import inspect
import inject
from bottle import PluginError, HTTPError

class InjectorPlugin(object):
    ''' This plugin passes an Injector handle to route callbacks
    that accept a `injector` keyword argument. If a callback does not expect
    such a parameter, no Injector any module. '''

    name = 'injector'
    api = 2

    def __init__(self, injector:inject.Injector, keyword:str='injector'):
         self.modules = injector
         self.keyword = keyword
         self.injector = injector


    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, InjectorPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another injector plugin with "\
                "conflicting settings (non-unique keyword).")

    def apply(self, callback, route):
        # Override global configuration with route-specific values.
        config = route.config
        _callback = route.callback

        # Override global configuration with route-specific values.
        if "injector" in config:
            # support for configuration before `ConfigDict` namespaces
            g = lambda key, default: config.get('injector', {}).get(key, default)
        else:
            g = lambda key, default: config.get('injector.' + key, default)

        injector = g('injector', self.modules)
        keyword = g('keyword', self.keyword)


        # Test if the original callback accepts a 'injector' keyword.
        # Ignore it if it does not need a Injector handle.
        """ 
        args = inspect.getargspec(_callback)
        if keyword not in args:
            return callback
        """

        # argspec = inspect.getargspec(_callback)
        # fix: AttributeError: module 'inspect' has no attribute 'getargspec'.
        cbargs = []
        if hasattr(inspect, 'getargspec'):
            argspec = inspect.getargspec(_callback)
            cbargs = argspec.args

        if hasattr(inspect, 'getfullargspec'):
            fullArgSpec = inspect.getfullargspec(_callback)
            cbargs = fullArgSpec.args

        if keyword not in cbargs:
            return callback

        def wrapper(*args, **kwargs):
            # pass-through injector instance
            # injector = Injector(modules)
            kwargs[keyword] = self.injector 

            try:
                rv = callback(*args, **kwargs)
            except inject.InjectorException as e:
                raise HTTPError(500, "inject.InjectorException", e)
            except inject.ConstructorTypeError as e:
                raise HTTPError(500, "inject.ConstructorTypeError", e)            
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper
