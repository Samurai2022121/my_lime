from django.core import management

from lime import app


@app.task
def auto_order():
    management.call_command("auto_order")


@app.task
def update_search_index():
    management.call_command("update_index")
