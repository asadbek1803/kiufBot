from tortoise.models import Model
from tortoise import fields


class Schedule(Model):
    """Lesson schedule"""

    id = fields.IntField(pk=True)

    group: fields.ForeignKeyRelation["Group"] = fields.ForeignKeyField(
        "models.Group",
        related_name="schedules"
    )

    week: fields.ForeignKeyRelation["Week"] = fields.ForeignKeyField(
        "models.Week",
        related_name="schedules"
    )

    day = fields.CharField(max_length=20)

    pair_number = fields.IntField()

    subject = fields.CharField(max_length=255)

    teacher = fields.CharField(max_length=255, null=True)

    room = fields.CharField(max_length=100, null=True)

    lesson_type = fields.CharField(max_length=50, null=True)

    lesson_time = fields.CharField(max_length=20, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "schedules"
        unique_together = ("group", "week", "day", "pair_number")

    def __str__(self):
        return f"{self.subject} ({self.day})"