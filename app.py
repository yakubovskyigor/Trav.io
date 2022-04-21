from flask import Flask, request, jsonify, json
from pip._vendor import requests
from pymongo import MongoClient
import pymongo
from flask_mail import Mail, Message
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token
from threading import Thread
import datetime

app = Flask(__name__)
app.secret_key = "testing"
app.config["JWT_SECRET_KEY"] = "this-is-secret-key"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = "igorby8881@gmail.com"
app.config['MAIL_PASSWORD'] = "i5526678"
cluster = MongoClient("mongodb+srv://igorby8881:i5526678@cluster0.cymiq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
dbtravio = cluster.dbtravio
users = dbtravio.users
active_orders = dbtravio.active_orders
completed_orders = dbtravio.completed_orders
mail = Mail(app)
CORS(app)
jwt = JWTManager(app)


@app.route("/", methods=['post', 'get'])
def index_page():
    return "Main page"


@app.route("/news", methods=['post', 'get'])
def news():
    unp = request.json['unp']
    response_API = requests.get(f'http://egr.gov.by/api/v2/egr/getBaseInfoByRegNum/{unp}')
    # print(response_API)
    data = response_API.text
    parse_json = json.loads(data)
    # info = parse_json[1]['vn']
    for i in parse_json:
        return jsonify(i['nsi00219']['vnsostk'])


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
    # email = request.json["email"]
    # # password = request.json["password"]
    #
    # # password_two = request.json["password_two"]
    # check = users.find_one({"email": email})
    # if check:
    #     return jsonify(message="Пользователь с данным e-mail уже зарегистрирован")
    # return jsonify(message=f"{email}")
    # #elif password != password_two:
    # #     return jsonify(message="Пароли не совпадают")
    # # else:
    # #     return jsonify(message="Давайте познакомимся")
    email = request.json["email"]
    check = users.find_one({"email": email})
    if check:
        return jsonify(message="User Exist")
    else:
        email = request.json["email"]
        password = request.json["password"]

        user_info = dict(email=email, password=password)
        users.insert_one(user_info)
        # access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        return jsonify(message="User added successfully", refresh_token=refresh_token, user=email), 200


"""Второй шаг регистрации"""


@app.route('/logged_in_two', methods=["POST"])
def logged_in_two():
    email = request.json["email"]
    password = request.json["password"]
    unp = request.json["unp"]
    organization_name = request.json["organization_name"]
    status_organization_name = request.json["status_organization_name"]
    field_of_activity = request.json["field_of_activity"]
    activity_code = request.json["activity_code"]
    address = request.json["address"]
    post_address = request.json["post_address"]
    phone_number = request.json["phone_number"]
    electronic_address = request.json["electronic_address"]
    #personal data
    last_name = request.json["last_name"]
    first_name = request.json["first_name"]
    patronymic = request.json["patronymic"]
    position = request.json["position"]
    electronic_address_two = request.json["electronic_address_two"]
    note = request.json["note"]

    check = users.find_one({"email": email})
    if check:
        return jsonify(message="Пользователь с данным e-mail уже зарегистрирован")
    else:
        user_info = dict(email=email, password=password, unp=unp,
                         organization_name=organization_name,
                         status_organization_name=status_organization_name, field_of_activity=field_of_activity,
                         activity_code=activity_code, address=address, post_address=post_address,
                         phone_number=phone_number, electronic_address=electronic_address,
                         last_name=last_name, first_name=first_name, patronymic=patronymic,
                         position=position, electronic_address_two=electronic_address_two,
                         note=note)
        users.insert_one(user_info)
        return jsonify("Пользователь успешно добавлен")
        # send_mail(
        #                organization_name, field_of_activity, unp, address, last_name,
        #                first_name, patronymic, position, phone_number, email, password), 200


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
        access_token = create_access_token(identity=email)
        return jsonify(message="Пользователь с таким именем зарегистрирован", access_token=access_token, user=email), 200
    else:
        return jsonify(message="Неверный логин или пароль"), 401


@app.route("/send", methods=['post', 'get'])
def send_mail(organization_name, field_of_activity, unp, address, last_name,
              first_name, patronymic, position, phone_number, email, password):
    msg = Message(subject="Регистрация в TRAV.IO успешно осуществлена. Ознакомьтесь с регистрационной информацией.",
                  sender='igorby8881@gmail.com', recipients=["igorby@mail.ru"])
    msg.body = "Уважаемый пользователь! \n" \
               "Благодарим Вас, за выбор системы http://TRAV.IO \n"\
               "\n" \
               "Вы прошли регистрацию со следующими данными:\n" \
               f"Наименование организации: {organization_name}\n "\
               f"Сфера деятельности: {field_of_activity}\n" \
               f"УНП: {unp}\n" \
               f"Юридический адрес: {address}\n" \
               "\n" \
               "Данные контактного лица\n" \
               "\n" \
               f"Ф.И.О. : {last_name} {first_name} {patronymic}\n" \
               f"Должность в организации: {position}\n" \
               f"Контактный номер: {phone_number}\n" \
               "\n" \
               "Данные для входа в систему TRAV.IO:\n" \
               f"E-mail: {email}\n" \
               f"Пароль: {password}\n" \
               "\n" \
               "\n" \
               "ЛОГО\n" \
               "www.trav.io"
    mail.send(msg)
    return jsonify(message="Пользователь успешно добавлен")


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
    return jsonify("Yes", user_id), 200


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
    check = active_orders.find_one({"_id": ObjectId(order_id)})
    if check:
        dbtravio.completed_orders.insert_one(check)
    else:
        return jsonify("No")
    order_id = [order_id]
    for i in order_id:
        dbtravio.active_orders.delete_one({"_id": ObjectId(i)})
    return jsonify("Удалена")


"""Смена роли производитель/переработчик U.S. 2.2"""


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