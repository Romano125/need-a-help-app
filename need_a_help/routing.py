from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from chat.consumers import ChatConsumer

application = ProtocolTypeRouter({
<<<<<<< HEAD
    # Empty for now (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(  # wrapa sockete i provjerava da sve sto radi reqest mora biti u allowed hosts u setting.py
        AuthMiddlewareStack(  # zelimo li da useri unutar chata budu unutar socketa
            URLRouter(
                [
                    url(r"^chat/messages/(?P<username>[\w.@+-]+)/$", ChatConsumer),
                ]
            )
        )
    )
=======
	# Empty for now (http->django views is added by default)
	'websocket': AllowedHostsOriginValidator(               ##wrapa sockete i provjerava da sve sto radi reqest mora biti u allowed hosts u setting.py
		AuthMiddlewareStack(							##zelimo li da useri unutar chata budu unutar socketa
			URLRouter(
				[
					url(r"^chat/messages/<str:username>",ChatConsumer),
				]
			)
		)
	)
>>>>>>> e3720368a7c4a31f6e1d2116715c89750821c8ef
})
