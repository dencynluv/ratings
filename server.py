"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

import seed

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


# Add sign up route 
@app.route("/sign-up")
def user_sign_up():
    """Allow user to sign up."""

    return render_template("sign_up.html")


@app.route("/new-user", methods=["POST"])
def add_new_user():
    """Add new user to database."""

    # Process sign-up form and set to respective variables
    email = request.form.get("email")
    password = request.form.get("password")

    # check if user name exists
    user = db.session.query(User).filter(User.email == email).first()

    # if user does not exist add user to database

    if user:
        if user.email == email:
            flash("you already logged in before silly willy")
            pass
    else: 
        # calling function set_val_user_id() from seed.py file
        # to prevent conflicting id's
        user_id = seed.set_val_user_id()

        user = User(user_id=user_id, email=email, password=password)

        # We need to add to the session or it won't be stored
        db.session.add(user)

        # Once we're done, we should commit our work
        db.session.commit()
        
        session['current_user'] = user.user_id
        flash('You were successfully signed up')

    return redirect('/')

# Add sign in route 
@app.route("/sign-in")
def user_sign_in():
    """Allow user to sign in."""

    return render_template("sign_in.html")


@app.route("/process-sign-in", methods=["POST"])
def process_sign_in():
    """Process username and password."""

    # Process sign-in form and set to respective variables
    email = request.form.get("email")
    password = request.form.get("password")

    # Query for user whose email matches email above
    # Return a user object
    user = db.session.query(User).filter(User.email == email).one()

    if user:
        if user.password == password:
            #Log them in
            session['current_user'] = user.user_id
            flash("Signed in as {}".format(user.email))
            return redirect('/')
    else:
        flash("You don't exist!")
        redirect('/sign-up')
        
    flash("Login and/or password is incorrect! Try again.")
    return redirect('/sign-in')


@app.route("/sign-out")
def user_sign_out():
    """Allow user to sign out."""

    del session['current_user'] 
    flash("You have successfully logged out.")

    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
