from app import db
from sqlalchemy import asc, desc


class Recipe(db.Model):
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
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    cover_image = db.Column(db.String(100), default=None)

    @classmethod
    def get_all_published(cls, page, per_page):
        return (
            cls.query.filter_by(is_publish=True)
            .order_by(desc(cls.created_at))
            .paginate(page=page, per_page=per_page)
        )

    @classmethod
    def get_by_id(cls, recipe_id):
        return cls.query.get_or_404(recipe_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
