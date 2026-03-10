from tortoise.models import Model
from tortoise import fields


class Week(Model):
    """HEMIS week"""

    id = fields.IntField(pk=True)

    week_number = fields.IntField()
    start_date = fields.DateField(null=True)
    end_date = fields.DateField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weeks"

    def __str__(self):
        return f"Week {self.week_number}"