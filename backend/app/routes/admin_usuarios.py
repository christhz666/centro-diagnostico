from flask import Blueprint
bp = Blueprint('admin_usuarios', __name__)

@bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    return {'usuarios': []}

@bp.route('/roles', methods=['GET'])
def listar_roles():
    return {'roles': []}
