from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models import User, Product
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('api', __name__)

# Base route (for sanity check)
@bp.route('/', methods=['GET'])
def api_home():
    return jsonify({'message': 'API is running!'}), 200


# Register new user (POST only)
@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'message': 'Missing JSON body'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], email=data['email'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# Login user (POST only)
@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Missing JSON body'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid email or password'}), 401


# Create a product (POST only, needs JWT)
@bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    data = request.json
    if not data:
        return jsonify({'message': 'Missing JSON body'}), 400

    product = Product(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        price=data['price'],
        image_url=data.get('image_url', None),
        user_id=user_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201


# Get all products (GET only)
@bp.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    query = Product.query
    if category:
        query = query.filter_by(category=category)

    products = query.all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'category': p.category,
            'price': p.price,
            'image_url': p.image_url,
            'owner': p.owner.username
        })
    return jsonify(result), 200


# Edit product (PUT only, needs JWT)
@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def edit_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    if product.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.json
    product.title = data.get('title', product.title)
    product.description = data.get('description', product.description)
    product.category = data.get('category', product.category)
    product.price = data.get('price', product.price)
    product.image_url = data.get('image_url', product.image_url)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200


# Delete product (DELETE only, needs JWT)
@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get_or_404(product_id)
    if product.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
