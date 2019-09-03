from urls import api
from marshmallow import Schema, fields


@api.schema('Question')
class QuestionSchema(Schema):
    id = fields.Integer()
    question_text = fields.Str()
    pub_date = fields.DateTime()


@api.schema('Choice')
class ChoiceSchema(Schema):
    id = fields.Integer()
    question = fields.Integer()
    choice_text = fields.Str()
    votes = fields.Integer()


@api.schema('User')
class UserSchema(Schema):
    id = fields.Integer()
    username = fields.Str()
    password = fields.Str()