from rest_framework import serializers


class RepresentationModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for on_read_field in [
            field for field in self.fields if field.find("on_read") >= 0
        ]:
            data[self.fields.get(on_read_field).source] = data.pop(on_read_field)
        return data
