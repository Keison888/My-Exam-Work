import flask_login
from flask import Flask, render_template, request, redirect, flash
from flask_login import UserMixin, login_user, login_required, logout_user
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, MetaData, Table, insert, select, update, delete
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass

@dataclass
class currentUser(UserMixin):
    def currentUser(self, currentUserId, name, email, password):
        self.currentUserId = currentUserId
        self.name = name
        self.email = email
        self.password = password

        return currentUserId

    @staticmethod
    def from_user(self, id):
        conn = engine.connect()
        row = conn.execute(select([User]).where(User.c.id == id)).fetchall()
        self.id = id


app = Flask(__name__)
app.secret_key = "secretKey"

# Login manager
lm = flask_login.LoginManager()
lm.init_app(app)
lm.login_view = ""
lm.login_message = ""

# Starts the db file
engine = create_engine('sqlite:///users.db')
conn = engine.connect()

Base = declarative_base()
metadata = MetaData()

# Creating all sql databases
Admin = Table('Admin', metadata,
             Column('Id', Integer, primary_key=True),
             Column('Name', String),
             Column('Email', String),
             Column('Password', String),
)

User = Table('User', metadata,
             Column('Id', Integer, primary_key=True),
             Column('Name', String),
             Column('Email', String),
             Column('Password', String),
             Column('PhoneNumber', String, default='N/A'),
             Column('ProducerVer', Boolean, default=False)
             )

Basket = Table('Basket', metadata,
             Column('Id', Integer, primary_key=True),
             Column('UserId', Integer),
             Column('ProductList', String)
             )

Order = Table('Order', metadata,
              Column('Id', Integer, primary_key=True),
              Column('UserId', Integer, default='N/A'),
              Column('Name', String, default='N/A'),
              Column('Email', String, default='N/A'),
              Column('PhoneNumber', String, default='N/A'),
              Column('Delivery', Boolean, default='N/A'),
              Column('Address', String, default='N/A'),
              Column('Payment', String, default='N/A')
              )

Product = Table('Product', metadata,
                Column('Id', Integer, primary_key=True),
                Column('UserId', Integer),
                Column('Image', String),
                Column('Item', String),
                Column('Mini', String),
                Column('Description', String),
                Column('Price', Float),
                Column('Quantity', Integer)
                )

Producer = Table('Producer', metadata,
                Column('Id', Integer, primary_key=True),
                Column('UserId', Integer),
                Column('Name', String),
                Column('Image', String),
                Column('Description', String, default="Hi I'm using Greenfield Local Hub")
                )


metadata.create_all(engine)


@lm.user_loader
def userLoader(email):
    conn = engine.connect()
    result = conn.execute(select([User]).where(User.c.Email == email)).fetchone()
    id = int(result[0])
    return id

@lm.user_loader
def adminLoader(email):
    conn = engine.connect()
    result = conn.execute(select([Admin]).where(Admin.c.Email == email)).fetchone()
    id = int(result[0])
    return id

@app.route("/")
def base():
    result = callAll(Product)
    return render_template("home.html", products=result)


@login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    conn = engine.connect()
    currentUserId = 1

    currentUserDetails = conn.execute(select([User]).where(User.c.Id == currentUserId)).fetchone()
    # Form to update the logged-in user's account details
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phoneNumber = request.form['phoneNumber']
        if name == "":
            name = currentUserDetails[2]
        if email == "":
            name = currentUserDetails[3]
        if phoneNumber == "":
            name = currentUserDetails[5]

        query = update(User).where(User.c.Id == currentUserId).values(Name=name, Email=email, PhoneNumber=phoneNumber)
        conn.execute(query)
        return redirect("account")
    return render_template("account.html", currentUserDetails=currentUserDetails)

@login_required
@app.route("/account_myProfile", methods=["GET", "POST"])
def myProfile():
    currentUserId = 1
    conn = engine.connect()
    currentProducerDetails = conn.execute(select([Producer]).where(Producer.c.UserId == currentUserId)).fetchone()
    # Form to update the Producer's profile
    if request.method == "POST":
        name = request.form['name']
        image = request.form['image']
        description = request.form['description']

        if name == "":
            name = currentProducerDetails[2]
        if image == "":
            image = currentProducerDetails[3]
        if description == "":
            description = currentProducerDetails[4]

        query = update(Producer).where(Producer.c.UserId == currentUserId).values(Name=name, Image=image, Description=description)
        conn = engine.connect()
        conn.execute(query)

    return render_template("account_myProfile.html", currentProducerDetails=currentProducerDetails)


# This page allows the Producer to be able to list their products onto the market
@login_required
@app.route("/account_addProducts", methods=["GET", "POST"])
def addProducts():
    if request.method == "POST":
        userId = 1
        image = request.form['image']
        item = request.form['item']
        miniDescription = request.form['mini']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']



        # Insert values into the database
        conn = engine.connect()
        conn.execute(insert(Product).values(UserId=userId, Image=image, Item=item, Mini=miniDescription, Description=description, Price=price, Quantity=quantity))

    return render_template("account_addProducts.html")

# Allows Producers to update details of their stock, using product ID as a selector.
@login_required
@app.route("/account_editProducts", methods=["GET", "POST"])
def editProducts():
    conn = engine.connect()
    currentUserId = 1
    result = conn.execute(select([Product]).where(Product.c.UserId == currentUserId)).fetchall()

    if request.method == "POST":
        # Missing id check
        if request.form['id'] == "":
            return redirect("/account_editProducts")

        productInfo = conn.execute(select([Product]).where(Product.c.Id == request.form['id'])).fetchall()
        image = request.form['image']
        if image == "":
            image = productInfo[0][2]
        item = request.form['item']
        if item == "":
            item = productInfo[0][3]
        miniDescription = request.form['mini']
        if miniDescription == "":
            miniDescription = productInfo[0][4]
        description = request.form['description']
        if description == "":
            description = productInfo[0][5]
        price = request.form['price']
        if price == "":
            price = productInfo[0][6]
        quantity = request.form['quantity']
        if quantity == "":
            quantity = productInfo[0][7]

        conn = engine.connect()

        if quantity == "0":
            conn.execute(delete(Product).where(Product.c.Id == request.form['id']))
        else:
            conn.execute(update(Product).where(Product.c.Id == request.form['id']).values(Image=image, Item=item, Mini=miniDescription, Description=description, Price=price, Quantity=quantity))

        return redirect("/account_editProducts")

    return render_template("account_editProducts.html", products=result)


@app.route("/adminLogin", methods=["GET", "POST"])
def adminLogin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        conn = engine.connect()
        result = conn.execute(select([Admin]).where(Admin.c.Email == email)).fetchall()
        if result and password == result[0][3]:
            flash('Logged in successfully.')
            return redirect("/adminPanel")
        else:
            return redirect("/adminLogin")
    return render_template("adminLogin.html")

@login_required
@app.route("/adminPanel", methods=["GET", "POST"])
def adminPanel():
    conn = engine.connect()
    currentUserId = 1
    currentUserDetails = conn.execute(select([Admin]).where(Admin.c.Id == currentUserId)).fetchone()

    print(flask_login.current_user)
    # Form to update the logged-in user's account details
    if request.method == "POST":
        currentUserId = 1
        name = request.form['name']
        email = request.form['email']
        phoneNumber = request.form['phoneNumber']

        if name == "":
            name = currentUserDetails[2]
        if email == "":
            name = currentUserDetails[3]
        if phoneNumber == "":
            name = currentUserDetails[5]

        query = update(Admin).where(Admin.c.Id == currentUserId).values(Name=name, Email=email, PhoneNumber=phoneNumber)
        conn.execute(query)

    return render_template("adminPanel.html", currentUserDetails=currentUserDetails)

@login_required
@app.route("/adminPanel_marketControl", methods=["GET", "POST"])
def adminPanel_marketControl():
    result = callAll(Product)

    if request.method == "POST":
        query = delete(Product).where(Product.c.Id == request.form['remove'])
        conn = engine.connect()
        conn.execute(query)

        return redirect("/adminPanel_marketControl")

    return render_template("adminPanel_marketControl.html", result=result)

'''
The producer whitelist allows admins to change the status of any regular user to a producer.
Automatically creating a separate database to store additional producer information.
When de-listing a user this will also automatically remove their status and it's database.
'''
@login_required
@app.route("/adminPanel_producerWhitelist", methods=["GET", "POST"])
def adminPanel_producerWhitelist():
    result = callAll(User)
    callAll(Producer)
    if request.method == "POST":
        grant()
        remove()

        return redirect("/adminPanel_producerWhitelist")

    return render_template("adminPanel_producerWhitelist.html", result=result,)

'''
Does two things:
1. Changes a user's "Producer Verification" to "True"
2. Create a new row in the "Producer" database, using their User ID and Name 
'''
def grant():
    conn = engine.connect()
    conn.execute(update(User).where(User.c.Id == request.form['grant']).values(ProducerVer=True))
    userInfo = conn.execute(select([User]).where(User.c.Id == request.form['grant'])).fetchall()

    try:
        userId = userInfo[0][0]
        name = userInfo[0][1]
        conn.execute(insert(Producer).values(UserId=userId, Name=name))

    except:
        pass

'''
Does two things:
1. Changes a user's "Producer Verification" to "False"
2. Deletes their corresponding producer data in the db
'''
def remove():
    conn = engine.connect()
    conn.execute(update(User).where(User.c.Id == request.form['remove']).values(ProducerVer=False))
    conn.execute(delete(Producer).where(Producer.c.UserId == request.form['remove']))

@app.route("/basket")
def basket():
    return render_template("basket.html")


@app.route("/checkout")
def checkout():
    if request.method == "POST":
        currentUserId = 1
        name = request.form['name']
        email = request.form['email']
        phoneNumber = request.form['phoneNumber']

        conn = engine.connect()
        conn.execute(insert(Order).values(UserId=currentUserId, Name=name, Email=email, PhoneNumber=phoneNumber))
        return render_template("checkout_collectionOrDelivery.html")

    return render_template("checkout.html")

@app.route("/checkout_collectionOrDelivery", methods=["GET", "POST"])
def checkout_collectionOrDelivery():
    if request.method == "POST":
        currentUserId = 1
        if request.form['delivery'] == "True":
            delivery = True
        else:
            delivery = False
        address = [request.form['houseNumber'], request.form['address1'], request.form['address2'], request.form['postCode']]

        conn = engine.connect()
        conn.execute(update(Order).where(Order.c.UserId == currentUserId).values(Delivery=delivery, Address=address))

    return render_template("checkout_collectionOrDelivery.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        conn = engine.connect()
        result = conn.execute(select([User]).where(User.c.Email == email)).fetchall()
        if result and password == result[0][3]:
            flash('Logged in successfully.')
            return redirect("/account")
        else:
            return redirect("/login")

    return render_template("login.html")


@login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

# The main page for regular customer shopping
@app.route("/shop", methods=["GET", "POST"])
def market():
    result = callAll(Product)
    if request.method == "POST":
        search = request.method['search']

    return render_template("market.html", products=result)

# Extracts the producer selected and their listed products
@app.route("/producer")
def producer():
    conn = engine.connect()
    currentProducerId = 2
    products = conn.execute(select([Product]).where(Product.c.UserId == currentProducerId)).fetchall()
    producer = conn.execute(select([Producer]).where(Producer.c.UserId == currentProducerId)).fetchall()

    return render_template("producer.html", products=products, producer=producer)


@app.route("/ourProducers", methods=["GET", "POST"])
def ourProducers():
    result = callAll(Producer)
    if request.method == "POST":
        search = request.method['search']

    return render_template("ourProducers.html", producers=result)


@app.route("/product")
def product():
    '''
    Pre-statement extracts all necessary details of a product,
    And prepares the basket for the data
    '''

    conn = engine.connect()
    productId = 1
    currentUserId = 1
    product = conn.execute(select([Product]).where(Product.c.Id == productId)).fetchall()
    '''
    conn = engine.connect()
    basket = conn.execute(select([Basket]).where(Basket.c.UserId == currentUserId)).fetchall()
    
    basketContent = basket[0][2]

    if request.method == "POST":
        quantity = request.method['quantity']
        newItem = {"itemId": productId,
                   "quantity": quantity
                   }

        conn = engine.connect()
        basket = conn.execute(select([Basket]).where(Basket.c.UserId == currentUserId)).fetchall()
        basketContent = basket[0][2]


        conn.execute(insert(Basket).values())
    '''

    return render_template("product.html", product=product)


'''
Signup page, does two things:
1. New users can create an account and have the benefits of stored data
2. Automatically creates a basket linked to their user Id.
'''
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Insert values into the database
        conn = engine.connect()
        conn.execute(insert(User).values(Name=name, Email=email, Password=password))

        userInfo = conn.execute(select([User]).where(User.c.Email == email)).fetchall()
        userId = userInfo[0]
        conn.execute(insert(Basket).values(UserId=userId))
    return render_template("signup.html")

# A temporary page that is used to fill in any links that could be built on in the future.
@app.route("/wip")
def wip():
    return render_template("wip.html")


'''
A useful function that extracts all values from any given table,
Can be found everywhere due to it's ability to reduce repetitive functions.
'''
def callAll(tableName):
    conn = engine.connect()
    result = conn.execute(select([tableName])).fetchall()
    return result

if __name__ == "__main__":
    app.run(debug=True)
