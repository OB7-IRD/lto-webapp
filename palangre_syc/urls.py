from django.urls import path

from palangre_syc.views import checking_logbook, listing_files, send_logbook2Observe, userguideline

urlpatterns = [
    path("", listing_files, name="listing files"),
    path("checking_logbook", checking_logbook, name="checking logbook"),
    path("send_logbook2Observe", send_logbook2Observe, name="send logbook2Observe"),
    path("userguideline", userguideline, name="user guideline")
    # path("../logbook", return_to_logbook),
]
