from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('adminpassword', method='pbkdf2:sha256'),
        is_admin=True,
        can_publish=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Utilisateur admin créé avec succès.")