from flask import Blueprint,request
from flask.json import jsonify
from flask_jwt_extended import jwt_required , get_jwt_identity
import validators
from src.constants.http_status_codes import HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST ,HTTP_200_OK, HTTP_201_CREATED
from src.database import Bookmark , db

bookmarks = Blueprint("bookmarks",__name__, url_prefix = "/api/v1/bookmarks")


@bookmarks.post('/add')
@jwt_required()

def add():
    user = get_jwt_identity()

    message = request.json['message']
    url = request.json['url']

    if not validators.url(url):
        return jsonify({
            "msg" : "Invalid url"
        }),HTTP_400_BAD_REQUEST
    
    
    if Bookmark.query.filter_by(url = url).first():
        return jsonify({
            "msg": "URl already exists"
        }),HTTP_409_CONFLICT
    
    bookmark = Bookmark(url = url , body = message , user_id = user  )
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'short_url':bookmark.short_url,
        'visit': bookmark.visits,
        'message':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at
    }),HTTP_201_CREATED

@bookmarks.get("/all")
@jwt_required()
def get_all():
    page = request.args.get('page',1,type=int)
    per_page = 10
    current_user = get_jwt_identity()
    bookmarks = Bookmark.query.filter_by(user_id = current_user ).paginate(page= page,per_page=per_page)
    data = []
    for bookmark in bookmarks:
        data.append({
            'id':bookmark.id,
            'url':bookmark.url,
            'short_url':bookmark.short_url,
            'visit': bookmark.visits,
            'message':bookmark.body,
            'created_at':bookmark.created_at,
            'updated_at':bookmark.updated_at
        })
    meta = {
        "page":bookmarks.page,
        "pages":bookmarks.pages,
        "total_count": bookmarks.total,
        "prev_page":bookmarks.prev_num,
        "next_page":bookmarks.next_num,
        "has_next":bookmarks.has_next,
        "has_prev":bookmarks.has_prev,
    }
    return jsonify({"data":data, 'meta':meta}),HTTP_200_OK

@bookmarks.get("/<int:id>") 
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id = current_user , id = id).first()

    if not bookmark :
        return jsonify({"msg":"no bookmark found"}),HTTP_404_NOT_FOUND
    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'short_url':bookmark.short_url,
        'visit': bookmark.visits,
        'message':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at
    }),HTTP_200_OK


@bookmarks.put("/<int:id>") 
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id = current_user , id = id).first()

    if not bookmark :
        return jsonify({"msg":"no bookmark found"}),HTTP_404_NOT_FOUND

    message = request.get_json().get('message','')
    url = request.get_json().get('body','')

    
    if url:
        if not validators.url(url):
            return jsonify({
                "msg" : "Invalid url"
            }),HTTP_400_BAD_REQUEST
        bookmark.url = url
    if message:    
        bookmark.body = message

    db.session.commit()

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'short_url':bookmark.short_url,
        'visit': bookmark.visits,
        'message':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at
    }),HTTP_200_OK

@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_record(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user , id = id).first()

    if not bookmark :
        return jsonify({"msg":"no bookmark found"}),HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({"msg":"deleted "})