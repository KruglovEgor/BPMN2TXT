from marshmallow import Schema, fields


class ConversionSchema(Schema):
    """Схема данных конвертации: image_id и model_id."""

    image_id = fields.String()
    model_id = fields.String()
