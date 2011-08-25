from django.utils import simplejson
from exceptions import Exception
from django.http import HttpResponse

# 400: Arguments weren't right
class BadRequest(Exception):
    pass

# 401: Invalid FB or site access code auth, or failed login
class Unauthorized(Exception):
    pass

# 403: Trying to do an action your user is not allowed to do, like post as another user
class Forbidden(Exception):
    pass

# 404: URL doesn't exist
class NotFound(Exception):
    pass

# 500: The code fucked up
class ServerError(Exception):
    pass


# JSON Request modeled after foursquare's API
def brocab_json_request(f):
    '''
    Decorator for get/post requests allowing the request function
    to return an object, which will be translated into a json request
    '''
    def addError(obj, code, errorDetail = ''):
        obj['meta']['code'] = code
        obj['meta']['errorDetail'] = errorDetail

    def wrap(req,*args,**kwargs):
        obj = {
            'meta':{
                'code':200
            }
        }

        try:
            # Get response
            response_obj = f(req,*args,**kwargs)
            if isinstance(response_obj,dict):
                obj['response'] = response_obj or {}
            elif isinstance(response_obj, list):
                obj['response'] = response_obj or []
            else:
                raise ServerError("Handler didn't return an object")

        except BadRequest, e:
            addError(obj,400,e.message)
        except Unauthorized,e:
            addError(obj,401,e.message)
        except Forbidden, e:
            addError(obj,403,e.message)
        except NotFound, e:
            addError(obj,404,e.message)
        except ServerError, e:
            addError(obj,500,e.message)
        except Exception, e:
            if req.REQUEST.get('htmlonerror', None):
                raise Exception(e)
            addError(obj,500,e.message)

        # Response
        json = simplejson.dumps(obj)

        return HttpResponse(content = json,
                            status = obj['meta']['code'],
                            content_type = 'application/json')
    return wrap

def json_in_body(f):
    def wrap(request, *args, **kwargs):
        try:
            reqObj = simplejson.loads(request.raw_post_data)
        except ValueError, e:
            raise BadRequest("Couldn't parse JSON")

        return f(request, reqObj, *args, **kwargs)
    return wrap
