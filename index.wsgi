import sae
from httpsocket import app

application = sae.create_wsgi_app(app)
