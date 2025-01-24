from Src import app, db, bcrypt  # Change Src to src
from Src.models import User  # Change Src to src and specify the correct module

import pycountry 

if __name__ == '__main__':
    admin = User(
        username="admin",
        email="admin@admin.com",
        password=bcrypt.generate_password_hash("admin"),
        phone='99999999',
        address="admin",
        secretQn="",
        isAdmin=True,
        cart=""
    )
    try:
        user = User.query.filter_by(email=admin.email).first()
        if user is None:  # Changed this line to check if user exists
            db.session.add(admin)
            db.session.commit()
    except Exception as e:  # Capture the exception for debugging
        print("Account exists:", e)

app.run(debug=True, port=000)