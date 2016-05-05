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

    if session:
        current_session = session['current_user']
    else: 
        current_session = None

    return render_template("homepage.html", session=current_session)


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

    # Check if user exists in database and return user object
    user = db.session.query(User).filter(User.email == email).first()

    # Want to check if user is a user object
    # If user is None, go into else statement
    if user:
        if user.email == email:
            flash("you already logged in before silly willy")
            pass
    else: 
        # Calling function set_val_user_id() from seed.py fil
        # to prevent conflicting id's
        user_id = seed.set_val_user_id()

        # Instantiating user in the User class
        user = User(user_id=user_id, email=email, password=password)

        # We need to add to the transaction or it won't be stored
        db.session.add(user)

        # Once we're done, we should commit our work
        db.session.commit()
        
        # To keep user logged in, holding onto user_id in a flask session
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

    # Want to check if user is a user object
    # If user is None, go into else statement
    if user:
        if user.password == password:
            #Keep user logged in by setting session key to user_id
            session['current_user'] = user.user_id
            flash("Signed in as {}".format(user.email))
            return redirect('/')
    else:
        flash("You don't exist!")
        redirect('/sign-up')
    
    #If user's information is incorrect, flash message and redirect to sign-in
    flash("Login and/or password is incorrect! Try again.")
    return redirect('/sign-in')


@app.route("/sign-out")
def user_sign_out():
    """Allow user to sign out."""

    if session['current_user']:
        del session['current_user'] 
        flash("You have successfully logged out.")
    else:
        flash("You were not logged in")

    return redirect('/')

@app.route("/profile/<int:user_id>")
def show_profile(user_id):
    """Show user profile."""
    # Flask is grabbing user_id from the URL route
    # and passing it as an argument to our show_profile function 

    #List of rating objects 
    
    user_ratings = db.session.query(Rating).filter(Rating.user_id == user_id).all()


    movies = []
    ratings = []

    #TO DO: Zip movies and ratings list together to create movie/rating list

    for rating in user_ratings:

        age = rating.user.age
        zipcode = rating.user.zipcode
        movie_title = rating.movie.title
        score = rating.score

        movies.append(movie_title)
        ratings.append(score)

    print movies

    raise Exception("hi")
    return render_template("profile.html",
                            age=age,
                            zipcode=zipcode,
                            movies=movies,
                            ratings=ratings)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
