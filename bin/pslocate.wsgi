import os
os.environ["PSLOCATE_SETTINGS"] = "/etc/perfsonar/pslocate.conf"
from pslocate.rest import app as application