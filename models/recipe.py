from app import db


class Recipe(db.Model):
    recipe_list = []
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    cook_time = db.Column(db.Integer)
    description = db.Column(db.String(200))
    num_of_servings = db.Column(db.Integer)
    directions = db.Column(db.String(1000))
    is_publish = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))

    @classmethod
    def get_last_id(cls):
        if cls.recipe_list:
            last_recipe = cls.recipe_list[-1]
        else:
            return 1
        return last_recipe.id + 1
