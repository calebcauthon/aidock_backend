from flask import Blueprint, render_template

librarian_routes = Blueprint('librarian', __name__)

@librarian_routes.route('/librarian')
def librarian_home():
    return render_template('librarian/librarian_home.html')
