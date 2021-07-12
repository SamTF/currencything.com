# This class stores user information in an easily accessible object, and generates their URL link
class User:
    def __init__(self, id, name, currency_thing = False):
        self.id         = int(id)
        self.name       = str(name)
        self.url        = f'<a href="/@{name}">{name}</a>'
        self.mention    = f'<@{id}>'
        self.avatar     = "www.avatar.com"

        # Currency Thing redirects back to the main page
        if currency_thing: self.url = f'<a href="/">{name}</a>'
    
    def __repr__(self):                                                                     # this is what gets output in the console when you print the object. cool! -> https://www.pythontutorial.net/python-oop/python-__repr__/
        return f'User: {self.id} | {self.name} | {self.url}'


USERS = [User(216972321099874305, 'Sam'), User(270377335675551745, 'Joe'), User(337352276219920384, 'Max'), User(840976021687762955, 'Currency Thing', True), User(565279368327200823, 'Emote Dealer'), User(829084517146296341, 'Stockman')]


# creates a dictionary to lookup a user value and replace it with another
def replace_thing(key, value):
    replace = {}
    for user in USERS:
        dict = {
        "id"        : user.id,
        "mention"   : user.mention,
        "name"      : user.name,
        "url"       : user.url
        }
        replace[dict[key]] = dict[value]
    
    return replace

# Gets a User object by name
def get_user(name: str):
        for user in USERS:
            if(user.name == name):
                return user

# the thing
if (__name__ == "__main__"):
    print ("Executed when invoked directly")
    print(replace_thing("mention", "url"))
else:
    print ("USERS IMPORTED")