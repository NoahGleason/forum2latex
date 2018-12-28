import requests
from lxml import etree
from io import StringIO
import json

parser = etree.HTMLParser()
base_url = "https://mlpforums.com/topic/47085-hypnotize-yourself-to-be-a-pony-links-included/?page="
start_page = 301
max_page = 341

# json_output = open("output.json", "a")
# html_output = open("output.html", "ab")
# json_output.write("[")
json_output.write(",\n")

for i in range(start_page, max_page+1):
    page = requests.get(base_url+str(i))
    print("Downloaded page "+str(i))
    tree = etree.parse(StringIO(page.text), parser)
    root = tree.getroot()
    # print(result)
    for element in root.iter("div", "script"):
        if element.get("data-role") == "commentContent":
            html_output.write(etree.tostring(element, method="html"))
        elif element.get("type") == "application/ld+json":
            parsed_json = json.loads(element.text)
            if parsed_json["@type"] == "DiscussionForumPosting":
                for j in range(len(parsed_json["comment"])):
                    json_output.write(json.dumps(parsed_json["comment"][j]))
                    if i != max_page or j != len(parsed_json["comment"]) - 1:
                        json_output.write(",\n")
    print("Finished page "+str(i))

# json_output.write("]")
json_output.close()
html_output.close()
