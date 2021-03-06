import models

from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from flask_login import current_user, login_required

from flask_cors import CORS

palettes = Blueprint('palettes','palettes')

# probably will need to refactor similar to getOne to join colors & saves
@palettes.route('/all', methods=['GET'])
def get_all_palettes():
    try:
        palettes = [model_to_dict(palettes) for palettes in models.Palette.select()]
        return jsonify(data=palettes, status={"code": 200, "message": "Success"})
    except models.DoesNotExist:
        return jsonify(data={},status={"code": 404, "message": "Error - that model doesn\'t exist"})
# still need something to stop password from being passed through 
# del palettes['app_user']['password'] didn't work
# Look up 'lazy loading'


# show the user their palettes
@palettes.route('/', methods=['GET'])
@login_required
def get_user_palettes():
    try:
        palettes = [model_to_dict(palettes) for palettes in \
                    models.Palette.select() \
                   .join_from(models.Palette, models.AppUser) \
                   .where(models.AppUser.id == current_user.id) \
                   .group_by(models.Palette.id)]
        return jsonify(data=palettes, status={"code": 200, "message": "Success"})
    except models.DoesNotExist:
        return jsonify(data={}, \
                       status={"code": 401, "message": "Log in or sign up to view your palettes"})


@palettes.route('/new', methods=['POST'])
@login_required
def create_palette():
    payload = request.get_json()
    palette = models.Palette.create(name=payload['name'], app_user_id=current_user.id)
    palette_dict = model_to_dict(palette)
    del palette_dict['app_user']['password']
    return jsonify(data=palette_dict, status={"code": 201, "message": "Successfully created"})


@palettes.route('/<id>', methods=['GET'])
def get_palette(id):
    try:
        query = (models.ColorPalette.select()
                 .join(models.Palette)
                 .switch(models.ColorPalette)
                 .join(models.Color)
                 .where(models.ColorPalette.palette == id))
        palette = [model_to_dict(item) for item in query]

        return jsonify(data=palette, \
                       status={"code": 200, "message": "Success"})
    except models.DoesNotExist:
        return jsonify(data={}, \
                       status={"code": 404, "message": "resource not found"})


@palettes.route('/name/<id>', methods=['GET'])
def get_palette_name(id):
    try:
        palette = (models.Palette.select()
                  .where(models.Palette.id == id))
        palette_dict = [model_to_dict(palette) for palette in palette]
        return jsonify(data=palette_dict, status={"code": 201, "message": "Successfully found"})
    except models.DoesNotExist:
        return jsonify(data={}, \
                       status={"code": 404, "message": "resource not found"})

# update a palette. will mainly be to change the name
# will probably need some sort of auth to edit - login_required just means no anonymous users
@palettes.route('/<id>', methods=['PUT'])
@login_required
def update_palette(id):
    try:
        payload = request.get_json()
        payload['app_user_id'] = current_user.id
        query = models.Palette.update(**payload).where(models.Palette.id==id)
        query.execute()
        updated_palette = model_to_dict(models.Palette.get_by_id(id))
        return jsonify(data=updated_palette, \
                       status={"code": 200, "message": "Successfully updated"})
    except models.DoesNotExist:
        return jsonify(data={}, \
                       status={"code": 404, "message": "resource not found"})

# delete a palette - need better auth
@palettes.route('/<id>', methods=['Delete'])
@login_required
def delete_palette(id):
    palette_to_delete = models.Palette.get_by_id(id)
    palette_to_delete.delete_instance(recursive=True)
    return jsonify(data={},status={"code": 200, "message": "Successfully deleted"})