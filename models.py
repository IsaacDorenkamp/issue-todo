class Namespace:
    def __init__(self, url, user, repository, filekey):
        self.__url = url
        self.__user = user
        self.__repo = repository
        self.__key = filekey

    @property
    def url(self):
        return self.__url

    @property
    def user(self):
        return self.__user

    @property
    def repo(self):
        return self.__repo

    @property
    def key(self):
        return self.__key

    @staticmethod
    def fromstr(ns_str):
        parts = ns_str.split(' ')
        if len(parts) != 4:
            return None
        else:
            return Namespace(parts[0], parts[1], parts[2], parts[3])

    def __str__(self):
        return "%s %s %s %s" % (self.__url, self.__user, self.__repo, self.__key)

    def getAsURL(self, protocol=None):
        if protocol is not None:
            return "%s://%s/%s/%s" % (protocol, self.__url, self.__user, self.__repo)
        else:
            return "%s/%s/%s" % (self.__url, self.__user, self.__repo)

class Issue:
    def __init__(self, number, desc=""):
        self.__id = number
        self.__desc = desc

    @property
    def id(self):
        return self.__id

    @property
    def description(self):
        return self.__desc
