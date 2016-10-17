from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

import logging
from pprint import pformat

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError

from .DengueBotFSM import DengueBotMachine


logger = logging.getLogger('django')

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
line_parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

DengueBotMachine.load_config()
machine = DengueBotMachine(line_bot_api)


def _log_line_api_error(e):
    logger.warning(
        ('LineBotApiError\n'
            'Status Code: {status_code}\n'
            'Error Message: {err_msg}\n'
            'Error Details: {err_detail}').format(status_code=e.status_code,
                                                  err_msg=e.error.message,
                                                  err_detail=e.error.details)
    )


@csrf_exempt
@require_POST
def reply(request):
    # Check Signature
    try:
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        events = line_parser.parse(body, signature)
    except KeyError:
        logger.warning(
            'Not a Line request.\n{req}\n'.format(req=pformat(request.text))
        )
        return HttpResponseBadRequest()
    except InvalidSignatureError:
        logger.warning(
            'Invalid Signature.\n{req}'.format(req=pformat(request.text))
        )
        return HttpResponseBadRequest()
    except LineBotApiError as e:
        _log_line_api_error()
        return HttpResponseBadRequest()

    for event in events:
        try:
            user_id = event.source.user_id
            state = cache.get(user_id) or 'user'

            machine.set_state(state)
            machine.advance(event)
        except LineBotApiError as e:
            _log_line_api_error(e)

    return HttpResponse()


@login_required
def show_fsm(request):
    DengueBotMachine.load_config()
    resp = HttpResponse(content_type="image/png")
    resp.name = 'state.png'
    machine = DengueBotMachine()
    machine.draw_graph(resp, prog='dot')
    return resp
