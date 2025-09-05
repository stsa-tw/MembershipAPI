import time


class MembershipToken:
    name = None
    email = None
    expiry = None

    def __init__(self, name, email, expiry):
        self.name = name
        self.email = email
        self.expiry = expiry

    def is_expired(self):
        return time.time() >= self.expiry