from flask_sqlalchemy import SQLAlchemy 
from src.database import User 

users = User.query.all()
print(users)