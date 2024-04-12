from git import Repo


class RepoDownloader:
    __url: str
    __path: str

    def __init__(self, url: str, path: str):
        self.__url = url
        self.__path = path

    def download(self):
        Repo.clone_from(self.__url, self.__path)
