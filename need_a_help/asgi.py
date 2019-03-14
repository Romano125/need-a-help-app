import os
import django
from channels.routing import get_default_application

<<<<<<< HEAD
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cfehome.settings")
=======
os.environ.setdefault("DJANGO_SETTINGS_MODULE","need_a_help.settings")
>>>>>>> e3720368a7c4a31f6e1d2116715c89750821c8ef
django.setup()
application = get_default_application()
