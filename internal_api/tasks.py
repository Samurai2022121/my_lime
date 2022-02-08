from django.core import management

from lime import app


@app.task
def auto_order():
    management.call_command('auto_order')
