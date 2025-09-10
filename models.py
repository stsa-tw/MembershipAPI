class MembershipToken:
    name = None
    email = None
    username = None

    def __init__(self, name, email, username):
        self.name = name
        self.email = email
        self.username = username

    def serialize(self):
        return f"{self.name}|##|{self.email}|##|{self.username}"

    @classmethod
    def deserialize(cls, data):
        try:
            name, email, username = data.split("|##|")
            return cls(name, email, username)
        except ValueError:
            return None
