current_view = None

def _set_current_view(view_name):
    global current_view
    assert view_name is not None
    current_view = view_name

def _get_current_view():
    global current_view
    return current_view
