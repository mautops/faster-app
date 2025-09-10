from tortoise import fields
from faster_app.models import UUIDModel, DateTimeModel, StatusModel


class DemoModel(UUIDModel, DateTimeModel, StatusModel):
    name = fields.CharField(max_length=255)

    class Meta:
        table = "demo"
        table_description = "Demo Model"

    def __str__(self):
        return self.name
