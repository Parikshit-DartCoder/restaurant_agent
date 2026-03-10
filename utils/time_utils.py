from datetime import datetime

def now():

    return datetime.now().strftime("%H:%M:%S")