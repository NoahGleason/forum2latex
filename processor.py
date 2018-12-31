import json
import data
import datetime
from lxml import etree
import latex


def parse_date(datestring):
    # format: YYYY-MM-DDTHH:mm:SS+0000
    year = int(datestring[:4])
    month = int(datestring[5:7])
    day = int(datestring[8:10])
    hour = int(datestring[11:13])
    minute = int(datestring[14:16])
    second = int(datestring[17:19])
    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)


name = "output"

output = open(name + ".json", "r")
json_comments = json.loads(output.read())
parser = etree.HTMLParser()
html_comments = etree.parse(name + ".html", parser).getroot()[0]
comments = []
authors = {}

for i in range(len(json_comments)):
    comment = json_comments[i]
    author_name = comment["author"]["name"]
    if author_name not in authors:
        new_author = data.Author(author_name, comment["author"]["image"])
        authors[author_name] = new_author
    new_comment = data.Comment(authors[author_name], html_comments[i], parse_date(comment["dateCreated"]))

    comments.append(new_comment)
    authors[author_name].add_comment(new_comment)

latex.set_colors(authors.values())

with open("header.tex", 'r') as reader:
    header = reader.read()

writer = open(name + ".tex", mode="w")
writer.write(header)
count = 0
for comment in comments:
    count += 1
    writer.write(latex.format_html(comment.get_text(), comment.get_author()))
    # print("Finished comment "+str(count)+" of 8514 ("+str(count/8514 * 100.)+"%)")
    if count % 100 == 0:
        print("Finished comment {0} of 8514 ({1:.2f}%)".format(count, count/8514. * 100.))
writer.write("\n\\end{document}")
writer.close()
