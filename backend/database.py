from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy() # SINGLE DB INSTANCE (ONLY HERE)


def init_db(app):
    db.init_app(app)

    with app.app_context():
        from models import User  # avoid circular import

        db.create_all()

        
        admin = User.query.filter_by(role="admin").first() # Create admin automatically
        if not admin:
            admin = User(
                username="admin",
                email="admin@placement.com",
                password="admin123",
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

