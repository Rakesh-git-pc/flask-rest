from flask import Blueprint , request , jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_codes import HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_409_CONFLICT , HTTP_401_UNAUTHORIZED , HTTP_200_OK
import validators
from flask_jwt_extended import create_access_token , create_refresh_token , jwt_required , get_jwt_identity

from src.database import User , db

auth = Blueprint("auth",__name__,url_prefix="/api/v1/auth")
 
@auth.post("/register")

def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    
    if len(password) < 6 :
        return jsonify({"msg":"password too short"}),HTTP_400_BAD_REQUEST

    if len(username) < 3 :
        return jsonify({"msg":"username too short"}),HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({"msg":"Should be alphanumeric and no spaces"}),HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({"msg":"not a valid email"}),HTTP_400_BAD_REQUEST

    if User.query.filter_by(email= email).first() is not None:
        return jsonify({"msg":"email is taken"}),HTTP_409_CONFLICT

    if User.query.filter_by(user_name= username).first() is not None:
        return jsonify({"msg":"email is taken"}),HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user=User(user_name = username, password = pwd_hash, email= email )

    db.session.add(user)

    db.session.commit()

    return jsonify(
        {
            "msg":"usercreated" , 
            "user":{
                "username": username,
                "email":email
            }
        }),HTTP_201_CREATED      


@auth.post("/login")
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')

    user = User.query.filter_by(email = email).first()

    if user :
        is_pass_correct = check_password_hash(user.password , password)
        if is_pass_correct :
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify(
                {
                    'user':{
                        'refresh':refresh,
                        'access':access,
                        'username': user.user_name,
                        'email':email
                    }
                }
            ),HTTP_200_OK
        return jsonify({'msg':'invalid credentials'}),HTTP_401_UNAUTHORIZED
    return jsonify({'msg':'user not found'}),HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id = user_id).first()



    return jsonify({
        "user":user.user_name,
        "email":user.email
        }),HTTP_200_OK

@auth.get("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access':access
    }),HTTP_200_OK