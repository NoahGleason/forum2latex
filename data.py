import urllib.request
import datetime


class Comment:

    def __init__(self, author, text, date: datetime):
        self.author = author
        self.text = text
        self.date = date

    def get_author(self):
        return self.author

    def get_date(self) -> datetime:
        return self.date

    def get_text(self):
        return self.text

    def __str__(self):
        return "author: " + self.author.get_name() + "\n" + \
               "date: " + str(self.date) + "\n" + \
               "text: " + self.text


class Color:

    def __init__(self, bg_color, title_text_color="white"):
        self.bg_color = bg_color
        self.title_text_color = title_text_color

    def get_latex(self) -> str:
        to_ret = ""
        if not self.bg_color == "white":
            to_ret += "colback=" + self.bg_color + "!5!white,"
        else:
            to_ret += "colback=" + self.bg_color + ","

        if not self.bg_color == "black":
            to_ret += "colframe=" + self.bg_color + "!75!black,"
        else:
            to_ret += "colframe=" + self.bg_color + ","

        to_ret += "coltitle=" + self.title_text_color
        return to_ret

    def __str__(self):
        return "{Background: "+self.bg_color+",Title Text:"+self.title_text_color+"}"


class Author:

    def __init__(self, name, image_url):
        self.comments = []
        self.name = name
        self.image_url = image_url
        self.image = None
        self.color = None

    def download_image(self, directory):
        urllib.request.urlretrieve(self.image_url, directory + self.name + ".png")
        self.image = directory + self.name + ".png"

    def get_name(self):
        return self.name

    def get_image(self):
        return self.image

    def add_comment(self, comment):
        self.comments.append(comment)

    def get_num_comments(self):
        return len(self.comments)

    def get_color(self) -> Color:
        return self.color

    def has_color(self):
        return self.color is not None

    def set_color(self, color):
        if self.color is not None:
            print("WARNING: Overwriting color for " + self.name)
            print("Previous color: "+str(self.color))
        self.color = color

    def __str__(self):
        return "name: " + self.name + "\n" + \
               "posts: " + str(self.get_num_comments())
