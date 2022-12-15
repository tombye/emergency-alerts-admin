from flask import Blueprint

main = Blueprint("main", __name__)
no_cookie = Blueprint("no_cookie", __name__)

from app.main.views import (  # noqa isort:skip
    add_service,
    agreement,
    api_keys,
    broadcast,
    choose_account,
    code_not_received,
    conversation,
    dashboard,
    email_branding,
    feedback,
    find_services,
    find_users,
    forgot_password,
    history,
    inbound_number,
    index,
    invites,
    jobs,
    letter_branding,
    manage_users,
    new_password,
    notifications,
    organisations,
    performance,
    platform_admin,
    pricing,
    providers,
    register,
    returned_letters,
    security_policy,
    send,
    sign_in,
    sign_out,
    templates,
    tour,
    two_factor,
    uploads,
    user_profile,
    verify,
    webauthn_credentials,
)
from app.main.views.service_settings import (  # noqa isort:skip
    index,
)
