from extensions import db

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)


def change_password(
    user,
    current_password,
    new_password,
    confirm_password
):

    if not check_password_hash(
        user.password_hash,
        current_password
    ):

        return False, "Current password is incorrect."

    if new_password != confirm_password:

        return False, "New passwords do not match."

    user.password_hash = generate_password_hash(
        new_password
    )

    db.session.commit()

    return True, "Password updated successfully."