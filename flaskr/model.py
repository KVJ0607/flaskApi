from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('model', __name__)


@bp.route('/')
def index():
    db = get_db()
    models = db.execute(
        'SELECT m.id, model_name, description, created, author_id, username'
        ' FROM model m JOIN user u ON m.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('model/index.html', models=models)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        model_name = request.form['model_name']
        description = request.form['description']
        git_url = request.form['git_url']
        error = None

        if not model_name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO model (model_name, description, author_id ,git_url)'
                ' VALUES (?, ?, ?)',
                (model_name, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('model.index'))

    return render_template('model/create.html')


def get_model(id, check_author=True):
    model = get_db().execute(
        'SELECT p.id, model_name, description, created, author_id, username'
        ' FROM model m JOIN user u ON m.author_id = u.id'
        ' WHERE m.id = ?',
        (id,)
    ).fetchone()

    if model is None:
        abort(404, f"Model id {id} doesn't exist.")

    if check_author and model['author_id'] != g.user['id']:
        abort(403)

    return model 



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    model = get_model(id)

    if request.method == 'POST':
        model_name = request.form['model_name']
        description = request.form['description']
        git_url = request.form['git_url']
        error = None

        if not model_name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE model SET model_name = ?, description = ?, git_url = ?'
                ' WHERE id = ?',
                (model_name, description, git_url)
            )
            db.commit()
            return redirect(url_for('model.index'))

    return render_template('model/update.html', model=model)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_model(id)
    db = get_db()
    db.execute('DELETE FROM model WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('model.index'))