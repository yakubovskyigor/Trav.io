from flask import Flask, request, jsonify
import pymongo
from flask_mail import Mail
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "testing"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "igorby8881@gmail.com"
app.config['MAIL_PASSWORD'] = "i5526678"
client = pymongo.MongoClient(host="localhost", port=27017)
dbtravio = client.dbtravio
users = dbtravio.users
active_orders = dbtravio.active_orders
completed_orders = dbtravio.completed_orders
mail = Mail(app)
CORS(app)


@app.route("/", methods=['post', 'get'])
def index_page():
    return "Main page"


@app.route("/news", methods=['post', 'get'])
def news():
    return ("News")


@app.route('/add', methods=['GET', 'POST'])
def add():
    first_name = request.json["first_name"]
    password = request.json["password"]
    email = request.json["email"]
    user_info = dict(first_name=first_name, password=password, email=email)
    users.insert_one(user_info)
    return jsonify(message="Пользователь успешно добавлен")


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == "GET":
        return jsonify({"response": "Get Request Called"})
    elif request.method == "POST":
        req_Json = request.json
        name = req_Json['name']
        return jsonify({"response": "Hi " + name})


"""Первый шаг регистрации"""


@app.route('/logged_in_one', methods=["POST"])
def logged_in_one():
    email = request.json["email"]
    #password = request.json["password"]

    # password_two = request.json["password_two"]
    check = users.find_one({"email": email})
    if check:
        return jsonify(message="Пользователь с данным e-mail уже зарегистрирован")
    return email
    #elif password != password_two:
    #     return jsonify(message="Пароли не совпадают")
    # else:
    #     return jsonify(message="Давайте познакомимся")


"""Второй шаг регистрации"""


@app.route('/logged_in_two', methods=["POST"])
def logged_in_two():
    email = request.json["email"]
    organizational_legal_form = request.json["organizational_legal_form"]
    organization_name = request.json["organization_name"]
    field_of_activity = request.json["field_of_activity"]
    unp = request.json["unp"]
    address = request.json["address"]
    last_name = request.json["last_name"]
    first_name = request.json["first_name"]
    patronymic = request.json["patronymic"]
    position = request.json["position"]
    phone_number = request.json["phone_number"]

    check = users.find_one({"email": email})
    if check:
        return jsonify(message="Пользователь с данным e-mail уже зарегистрирован")
    else:
        user_info = dict(email=email, organizational_legal_form=organizational_legal_form,
                         organization_name=organization_name, field_of_activity=field_of_activity, unp=unp,
                         address=address, last_name=last_name, first_name=first_name, patronymic=patronymic,
                         position=position, phone_number=phone_number)
        users.insert_one(user_info)
        return jsonify(message="Пользователь успешно добавлен"), 200


"""Авторизация"""


@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.json["email"]
        password = request.json["password"]

    check = users.find_one({"email": email, "password": password})
    if check:
        return jsonify(message="Пользователь с таким именем зарегистрирован"), 200


@app.route("/send", methods=['post', 'get'])
def send_mail():
    msg = mail.send_message(
        'Send Mail tutorial!',
        sender='igorby8881@gmail.com',
        recipients=['igorby@mail.ru'],
        body="Congratulations you've succeeded!"
    )
    return 'Mail sent'


"""Заявка производителя (6.1)"""


@app.route("/producer_order", methods=['post', 'get'])
def producer_order():
    user_id = request.json["_id"]
    order_data = {
        #"_id": user_id,
        "order_number": request.json["order_number"],
        "order_status": None,
        "waste_category": request.json["waste_category"],
        "waste_volume_weight": request.json["waste_volume_weight"],
        "waste_photo": request.json["waste_photo"],
        "address": request.json["address"],
        "transport": request.json["transport"],
        "as_soon_as_possible": request.json["as_soon_as_possible"],
        "period_of_execution": request.json["period_of_execution"],
        "relevance_of_the_order": request.json["relevance_of_the_order"],
        "contact_person": request.json["contact_person"]
    }
    dbtravio.active_orders.insert_one(order_data)
    # dbtravio.users.update_one(
    #     {"_id": ObjectId(user_id)},
    #     {"$set": {"order_data": order_data}}
    # )
    return jsonify("Yes"), 200


"""Публикация заявки производителя (6.2)"""


@app.route("/publication_producer_order", methods=['post', 'get'])
def publication_producer_order():
    user_id = request.json["_id"]
    order_number = request.json["order_number"]
    order_status = "Опубликована"
    order_data = {
        "order_number": order_number,
        "order_status": order_status,
        "waste_category": request.json["waste_category"],
        "waste_volume_weight": request.json["waste_volume_weight"],
        "waste_photo": request.json["waste_photo"],
        "address": request.json["address"],
        "transport": request.json["transport"],
        "as_soon_as_possible": request.json["as_soon_as_possible"],
        "period_of_execution": request.json["period_of_execution"],
        "relevance_of_the_order": request.json["relevance_of_the_order"],
        "contact_person": request.json["contact_person"]
    }
    dbtravio.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"order_data": order_data}}
    )
    return jsonify("Заявка опубликована"), 200


"""Удаление заявки производителем (6.3)"""


@app.route("/delete_order", methods=['post', 'get'])
def delete_order():
    order_id = request.json["_id"]
    for i in order_id:
        dbtravio.active_orders.delete_one({"_id": ObjectId(i)})
    return jsonify("Удалена")


"""Смена роли производитель/переработчик"""


@app.route("/change_activity", methods=['post', 'get'])
def change_activity():
    user_id = request.json["_id"]
    new_activity = request.json["field_of_activity"]

    dbtravio.users.update_one(
             {"_id": ObjectId(user_id)},
             {"$set": {"field_of_activity": new_activity}}
             )
    return jsonify("Yes"), 200


# @app.route("/find_document", methods=['post', 'get'])
# def find_document():
#     results = users.find({'order_data.order_status': 'Опубликована'})
#     return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)