from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^reply/', reply),
    url(r'^show_fsm/', show_fsm),
    url(r'^user_list/', user_list),
    url(r'^(?P<uid>\S+)/user_detail/', user_detail),
    url(r'^msg_log_list/', msg_log_list),
    url(r'^(?P<uid>\S+)/msg_log_detail/', msg_log_detail),
    url(r'^unrecog_msgs/', unrecognized_msg_list),
    url(r'^(?P<mid>\S+)/handle_unrecognized_msg/', handle_unrecognized_msg),
]
