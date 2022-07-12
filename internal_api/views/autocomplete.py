from dal import autocomplete
from django.apps import apps


class Autocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        current_model = apps.get_model(
            app_label=self.request.GET.get("app_label"),
            model_name=self.request.GET.get("model_name"),
        )

        if self.q:
            return current_model.objects.filter(
                **{self.request.GET.get("filter_string"): self.q}
            )
        else:
            return current_model.objects.none()
