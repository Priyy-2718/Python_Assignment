from flask import Flask, request, jsonify
from config import Config
from models import db, Users_data
from flask_migrate import Migrate
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)



@app.route('/')
def index():
    return 'Hello, Flask with PostgreSQL!'

@app.route('/add_users', methods=['POST'])
def add_users():
    data = request.get_json()

    response = []
    for user_data in data:
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        company_name = user_data.get('company_name')
        age = user_data.get('age')
        city = user_data.get('city')
        state = user_data.get('state')
        zip = user_data.get('zip')
        email = user_data.get('email')
        web = user_data.get('web')

        if not all([first_name, last_name, company_name, age, city, state, zip, email, web]):
            response.append({"status": "error", "message": "All fields are required", "email": email})
            continue

        if Users_data.query.filter_by(email=email).first() is not None:
            response.append({"status": "error", "message": "Email already exists", "email": email})
            continue

        new_user = Users_data(
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            age=age,
            city=city,
            state=state,
            zip=zip,
            email=email,
            web=web
        )
        db.session.add(new_user)
        response.append({"status": "success", "user": new_user.to_dict()})

    db.session.commit()

    return jsonify(response), 201

def paginate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        search = request.args.get('search', '')
        sort_field = request.args.get('sort_field', '')

        return func(*args, page=page, limit=limit, search=search, sort_field=sort_field, **kwargs)
    return wrapper

@app.route('/users')
@paginate
def get_users(page, limit, search, sort_field):
    query = Users_data.query  # Initialize the query
    
    if search:
        query = query.filter(db.or_(Users_data.first_name.ilike(f'%{search}%'), Users_data.last_name.ilike(f'%{search}%')))
    
    if sort_field:
        if sort_field.startswith('-'):
            sort_field = sort_field[1:]
            query = query.order_by(getattr(Users_data, sort_field).desc())
        else:
            query = query.order_by(getattr(Users_data, sort_field))
            
    users_data = query.paginate(page=page, per_page=limit, error_out=False)
    results = []
    for user in users_data.items:
        results.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'company_name': user.company_name,
            'age': user.age,
            'city': user.city,
            'state': user.state,
            'zip': user.zip,
            'email': user.email,
            'web': user.web
        })

    return jsonify({
        'page': users_data.page,
        'total_pages': users_data.pages,
        'total_users': users_data.total,
        'users': results
    })

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = Users_data.query.get_or_404(id)
    return jsonify(user.to_dict())


@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = Users_data.query.get_or_404(id)
    
    data = request.json
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'age' in data:
        user.age = data['age']

    db.session.commit()

    return jsonify(user.to_dict()), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = Users_data.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({}), 204


if __name__ == '__main__':
    app.run(debug=True)
