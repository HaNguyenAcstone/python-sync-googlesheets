from apscheduler.schedulers.background import BackgroundScheduler
from syncgooglesheets import views

def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(views.sync_data_google_sheets, 'interval', minutes=1, id="call_list_post", replace_existing=True)
    # scheduler.start()