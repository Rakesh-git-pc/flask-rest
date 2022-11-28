from flask import Flask, jsonify , redirect
import os
from src.constants.http_status_codes import HTTP_404_NOT_FOUND , HTTP_500_INTERNAL_SERVER_ERROR
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db , Bookmark
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import swag_from , Swagger
from src.config.swagger import template, swagger_config

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    if(test_config is None):
        app.config.from_mapping(
            SECRET_KEY  = os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS = False,
            JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),
            JWT_ACCESS_TOKEN_EXPIRES = False,

            SWAGGER = {
                'title':'Bookmarks api',
                'uiversion':3,

            }
        )    
    else :
        app.config.from_mapping(
            test_config
        )


    JWTManager(app)

    db.app = app
    db.init_app(app)



    with app.app_context():
        db.create_all()

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app,config=swagger_config,template=template)

    @app.get("/<short_url>")
    @swag_from("./docs/short_url.yaml")
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url  = short_url).first_or_404()

        if (bookmark):
            bookmark.visits = bookmark.visits+1
            db.session.commit()

            return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error':'not found'}),HTTP_404_NOT_FOUND
    def handle_500(e):
        return jsonify({'error':'something went wrong'}),HTTP_500_INTERNAL_SERVER_ERROR
    return app
