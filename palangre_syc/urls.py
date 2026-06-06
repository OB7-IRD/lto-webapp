from django.urls import path

# from . import views
from palangre_syc.views import checking_logbook, send_logbook2observe, presenting_previous_trip

urlpatterns = [
    path("presenting_previous_trip", presenting_previous_trip, name = "presenting_previous_trip"),
    path("checking_logbook", checking_logbook, name="checking_logbook"),
    path("send_logbook2bserve", send_logbook2observe, name="send_logbook2observe"),
]
