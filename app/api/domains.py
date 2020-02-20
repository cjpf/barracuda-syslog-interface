from app.api import bp


@bp.route('/domains/<int:id>', methods=['GET'])
def get_domain(id):
    pass


@bp.route('/domains', methods=['GET'])
def get_domains(id):
    pass


@bp.route('/domains', methods=['POST'])
def create_domain():
    pass


@bp.route('/domains/<int:id>', methods=['PUT'])
def update_domain(id):
    pass


@bp.route('/domains/<int:id>', methods=['DELETE'])
def delete_domain(id):
    pass
