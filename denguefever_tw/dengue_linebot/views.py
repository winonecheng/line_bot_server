from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import logging
from pprint import pformat

import ujson
from linebot.client import LineBotClient


from .models import LINEUser
from .LINEBotHandler import LINE_operation_factory
from .LINEBotHandler import LINE_message_factory
from .DengueBotFSM import DengueBotMachine

client = LineBotClient(**settings.LINE_BOT_SETTINGS)
logger = logging.getLogger('django')
# Maximum mid to sent in single request
MAXIMUM_COUNT = 150


@csrf_exempt
def reply(request):
    # Check signature
    try:
        if not client.validate_signature(request.META['HTTP_X_LINE_CHANNELSIGNATURE'],
                                         request.body.decode('utf-8')):
            logger.warning(('Invalid request to callback function.\n'
                            'Not valid signature'
                            'request: \n {req}').format(req=request))
            return HttpResponseBadRequest()
    except KeyError as ke:
        logger.exception(('Invalid request to callback function.\n'
                          'Does not contain X-Line-Channelsignature\n'
                          'request: {req}\n'
                          'exception: {e}').format(req=request,
                                                   e=ke))
        return HttpResponseBadRequest()

    # Load request content
    req_json = ujson.loads(request.body.decode('utf-8'))
    logger.info('Request Received: {req}'.format(req=pformat(req_json, indent=4)))
    req_content = req_json['result'][0]['content']

    if 'opType' in req_content.keys():
        handler = LINE_operation_factory(client, req_content)
    elif 'contentType' in req_content.keys():
        handler = LINE_message_factory(client, req_content)
    logger.debug('{handler} is created.'.format(handler=handler.__class__.__name__))
    resp = handler.handle()
    try:
        if resp.status_code == 200:
            logger.debug(('Successfully handled\n'
                          'Response after handled:\n{resp}').format(resp=pformat(resp.text)))
        else:
            logger.debug(('Failed to handle\n'
                          'Response after handled:\n{resp}').format(resp=pformat(resp.text)))
    except AttributeError:
        logger.debug('No response needed after handling.')
    return HttpResponse()


@login_required
@csrf_exempt
def broadcast(request):
    if request.method == 'POST':
        content = request.POST['content']
        try:
            mids = request.POST.getlist('mids')
        except (KeyError, ValueError) as e:
            logger.exception(("Exception happends. Broadcast to all users\n"
                              "{exp}\n").format(exp=e))
            mids = [user.user_mid for user in LINEUser.objects.all()]
        spilt_mids = [mids[i:i+MAXIMUM_COUNT]
                      for i in range(0, len(mids), MAXIMUM_COUNT)]
        for m in spilt_mids:
            resp = client.send_text(
                to_mid=mids,
                text=content
            )
            logger.info(('Broadcast Receivers: {mids}\n'
                         'Broadcase Content {content}\n'
                         'Response after broadcast: {resp}').format(
                             mids=mids,
                             content=content,
                             resp=resp))
        return HttpResponse()
    elif request.method == 'GET':
        line_users = LINEUser.objects.all()
        context = {'line_user': line_users}
        return render(request, 'dengue_linebot/broadcast.html', context)


@login_required
def show_fsm(request):
    resp = HttpResponse(content_type="image/png")
    resp.name = 'state.png'
    machine = DengueBotMachine()
    machine.draw_graph(resp, prog='dot')
    return resp
