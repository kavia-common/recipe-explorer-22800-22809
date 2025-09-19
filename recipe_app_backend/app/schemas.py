from marshmallow import Schema, fields, validate


class PaginationSchema(Schema):
    page = fields.Int(load_default=1, metadata={"description": "Page number"})
    per_page = fields.Int(load_default=10, metadata={"description": "Items per page"})


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    name = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class UserRegisterSchema(Schema):
    email = fields.Email(required=True, metadata={"description": "User email"})
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    name = fields.Str(allow_none=True)


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class RecipeSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    ingredients = fields.Str(allow_none=True, metadata={"description": "Comma or newline separated ingredients"})
    instructions = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    author_id = fields.Int(dump_only=True)
    categories = fields.List(fields.Nested(CategorySchema), dump_only=True)


class RecipeCreateUpdateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    ingredients = fields.Str(allow_none=True)
    instructions = fields.Str(allow_none=True)
    category_names = fields.List(fields.Str(), load_default=[], metadata={"description": "List of category names to assign"})


class FavoriteActionSchema(Schema):
    recipe_id = fields.Int(required=True)
