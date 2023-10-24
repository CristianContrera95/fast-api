from schemas import AccountSchema


def get_account_by_username(db, account_username):
    return db.query(AccountSchema).filter_by(username=account_username).first()


def get_account_by_email(db, account_email):
    return db.query(AccountSchema).filter_by(email=account_email).first()
