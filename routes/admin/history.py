from flask import Blueprint, render_template, request
from db.prompt_history import Datastore as PromptHistoryDatastore
from db.init_db import create_connection
from ..shared.auth import platform_admin_required

history = Blueprint('history', __name__)

@history.route('/history')
@platform_admin_required
def prompt_history():
    conn = create_connection()
    datastore = PromptHistoryDatastore(conn)

    offset = request.args.get('offset', type=int, default=0)
    limit = 1

    history = datastore.get_prompt_history(offset, limit)
    return render_template('superuser_ui/prompt_history.html', 
                            entry=history['entry'],
                            has_prev=history['has_prev'],
                            has_next=history['has_next'],
                            prev_offset=history['prev_offset'],
                            next_offset=history['next_offset'])
