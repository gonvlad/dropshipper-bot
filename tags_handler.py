from text_templates import ADD_ACTION_SIGN
from text_templates import TAG_ADDED
from text_templates import TAG_ALREADY_EXISTS
from text_templates import REMOVE_ACTION_SIGN
from text_templates import TAG_REMOVED
from text_templates import TAG_DO_NOT_EXISTS


def handle_tag_action(action, tag, tags):
    if action == ADD_ACTION_SIGN:
        if (tag not in tags):
            return TAG_ADDED
        else:
            return TAG_ALREADY_EXISTS
    elif action == REMOVE_ACTION_SIGN:
        if (tag in tags):
            return TAG_REMOVED
        else:
            return TAG_DO_NOT_EXISTS