from app import app, db
from app.models import Student, Book, User, Checkout

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Student': Student, 'Book': Book, 'User': User, 'Checkout': Checkout}