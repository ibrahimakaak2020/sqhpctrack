import pytz
from datetime import datetime
from tzlocal import get_localzone

# Get local timezone automatically
local_timezone = get_localzone()

# Get current time in local timezone
local_time = datetime.now(local_timezone)

