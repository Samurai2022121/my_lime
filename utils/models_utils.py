class ListDisplayAllModelFieldsAdminMixin(object):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(ListDisplayAllModelFieldsAdminMixin, self).__init__(model, admin_site)
