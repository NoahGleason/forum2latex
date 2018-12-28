import requests
import os.path

from lxml import etree

import data

assignable_colors = [data.Color("blue"), data.Color("brown"), data.Color("cyan"), data.Color("green"),
                     data.Color("lime"), data.Color("magenta"), data.Color("olive"), data.Color("orange"),
                     data.Color("pink"), data.Color("purple"), data.Color("teal"), data.Color("violet"),
                     data.Color("yellow")]

pixels_to_pt = {8: 6, 9: 7, 10: 7.5, 11: 8, 12: 9, 13: 10, 14: 10.5, 15: 11, 16: 12, 17: 13, 18: 13.5, 19: 14, 20: 14.5,
                21: 15, 22: 16, 23: 17, 24: 18, 25: 19, 48: 36, 50: 37.5}

no_newline_after_tags = ["blockquote"]

header = """\\documentclass[ebook,12pt,oneside,openany]{memoir}
\\usepackage[T2A,T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage[russian,english]{babel}
\\usepackage{graphicx}
\\usepackage{textgreek}
\\usepackage{textcomp}
\\usepackage{url}
\\usepackage{hyperref}
\\usepackage[most]{tcolorbox}
\\usepackage{fancyhdr}
\\usepackage[paperwidth=441pt,paperheight=666pt,left=72pt,right=72pt,top=77pt,bottom=76pt]{geometry}
\\usepackage{pifont}
\\usepackage{amsmath,amssymb,latexsym}
\\usepackage[normalem]{ulem}

\\newcommand{\\carat}{$\\char`\\^$}
\\newcommand{\\mytexttilde}{\\raisebox{0.5ex}{\\texttildelow}}

\\tcbset{
    breakable,
    enhanced jigsaw
}

\\pagestyle{fancy}
\\lhead{}
\\chead{}
\\rhead{}
\\renewcommand{\\headrulewidth}{0pt}
\\cfoot{\\thepage}

\\begin{document}

\\title{Hypnotize Yourself To Be A Pony}
\\author{Internet}

\\maketitle
\\newpage"""


def set_colors(authors):
    # Deal with special cases
    op = None
    for author in authors:
        if author.get_name() == "Lord Bababa":
            op = author
    op.set_color(data.Color("red"))

    sorted_authors = sorted(authors, key=lambda x: x.get_num_comments(), reverse=True)
    sorted_authors.remove(op)

    for i in range(len(assignable_colors)):
        sorted_authors[i].set_color(assignable_colors[i])


def format_html(div, author: data.Author):
    to_ret = "\\begin{tcolorbox}[title=" + format_text(author.get_name())
    if author.has_color():
        to_ret += ","
        to_ret += author.get_color().get_latex()
    to_ret += "]\n"
    to_ret += format_text(div.text)
    end = "\\end{tcolorbox}\n"
    newline_allowed = False
    for i in range(len(div)):
        element = div[i]
        if element.tag == "blockquote":
            to_ret += format_blockquote(element)
            newline_allowed = False
        elif element.tag == "p":
            if newline_allowed:
                to_ret += format_p(element, True)
            else:
                new_text = format_p(div[i], False)
                newline_allowed = new_text.strip() != ""
                to_ret += new_text
    return to_ret + end


def format_text_tag(element, newline_allowed: bool):
    if element.tag == "p":
        return format_p(element, newline_allowed)
    elif element.tag == "blockquote":
        return format_blockquote(element)
    elif element.tag == "span":
        return format_span(element)
    elif element.tag == "strong" or element.tag == "b":
        return format_strong(element)
    elif element.tag == "a":
        return format_a(element)
    elif element.tag == "img":
        return format_img(element)
    elif element.tag == "div":
        return format_div(element)
    elif element.tag == "br":
        return format_br(element)
    elif element.tag == "em" or element.tag == "i":
        return format_em(element)
    elif element.tag == "strike" or element.tag == "del":
        return format_strike(element)
    elif element.tag == "sup":
        return format_sup(element)
    elif element.tag == "iframe":
        return format_iframe(element)
    elif element.tag == "u":
        return format_u(element)
    elif element.tag == "ul":
        return format_ul(element)
    elif element.tag == "ol":
        return format_ol(element)
    elif element.tag == "li":
        return format_li(element)
    else:
        print("ERROR: Unknown tag " + element.tag)


def format_children(parent, initial_newline_allowed=True):
    to_ret = ""
    newline_allowed = initial_newline_allowed
    for i in range(len(parent)):
        if newline_allowed:
            to_ret += format_text_tag(parent[i], True)
            newline_allowed = parent[i].tag not in no_newline_after_tags
        else:
            new_text = format_text_tag(parent[i], False)
            newline_allowed = new_text.strip() != "" and parent[i].tag not in no_newline_after_tags
            to_ret += new_text
    return to_ret


def format_p(p, newline_allowed: bool):
    if format_text(p.text).strip() == "" and len(p) == 0:
        if newline_allowed:
            return "\\newline" + format_text(p.tail) + "\n"
        elif format_text(p.tail).strip() == "":
            return ""
        else:
            return format_text(p.tail) + "\n"
    to_ret = "\\par{"
    end = "}" + format_text(p.tail) + "\n"
    for key in p.keys():
        if key == "style":
            style_output = format_style(p.get("style"))
            to_ret += style_output[0]
            end += style_output[1]
        else:
            print("ERROR: Unknown <p> attribute " + key)
    to_ret += format_text(p.text)
    to_ret += format_children(p)
    return to_ret + end


def format_style(style: str):
    front = ""
    end = ""
    attributes = style.split(";")
    for attribute in attributes:
        if attribute[:6] == "color:":
            if attribute[6:9] == "rgb":
                rgb = attribute[10:-1]
                front += "\\textcolor[RGB]{" + rgb + "}{"
                end = "}" + end
            else:
                front += "\\textcolor[HTML]{" + attribute[7:13] + "}{"
                end = "}" + end
        elif attribute == "font-weight:bold" or attribute == "font-weight:600":
            front += "\\textbf{"
            end = "}" + end
        elif attribute[:10] == "font-size:":
            if attribute == "font-size:small":
                front += "\\begin{small}"
                end = "\\end{small}" + end
            elif attribute == "font-size:large":
                front += "\\begin{large}"
                end = "\\end{large}" + end
            else:
                pt_size = 0
                if attribute[-2:] == "pt":
                    pt_size = float(attribute[10:-2])
                elif attribute[-2:] == "px":
                    pt_size = pixels_to_pt[int(float(attribute[10:-2]))]
                else:
                    print("Unrecognized font units: " + attribute)
                if pt_size <= 7:
                    front += "\\begin{tiny}"
                    end = "\\end{tiny}" + end
                elif pt_size <= 9:
                    front += "\\begin{scriptsize}"
                    end = "\\end{scriptsize}" + end
                elif pt_size <= 10.475:
                    front += "\\begin{footnotesize}"
                    end = "\\end{footnotesize}" + end
                elif pt_size <= 11.475:
                    front += "\\begin{small}"
                    end = "\\end{small}" + end
                elif pt_size <= 13.2:
                    front += "\\begin{normalsize}"
                    end = "\\end{normalsize}" + end
                elif pt_size <= 15.84:
                    front += "\\begin{large}"
                    end = "\\end{large}" + end
                elif pt_size <= 19:
                    front += "\\begin{Large}"
                    end = "\\end{Large}" + end
                elif pt_size <= 22.81:
                    front += "\\begin{LARGE}"
                    end = "\\end{LARGE}" + end
                else:
                    front += "\\begin{huge}"
                    end = "\\end{huge}" + end
        elif attribute[
             :12] == "font-family:" or attribute == "text-align:justify" or attribute == "background-color:transparent":
            front += ""  # Do nothing
        elif attribute[:17] == "background-color:":
            if attribute[17:20] == "rgb":
                rgb = attribute[21:-1]
                front += "\\colorbox[RGB]{" + rgb + "}{"
                end = "}" + end
            else:
                print("Unknown background color encoding!")
        elif attribute.strip() == "":
            front += ""
        else:
            print("ERROR: Unknown style attribute " + attribute)
    return front, end


def format_blockquote(blockquote):
    to_ret = "\\begin{tcolorbox}[title=" + format_text(blockquote.get("data-ipsquote-username")) + "]\n"
    to_ret += format_text(blockquote.text)
    to_ret += format_children(blockquote, initial_newline_allowed=False)
    end = "\\end{tcolorbox}\n" + format_text(blockquote.tail)
    return to_ret + end


def format_span(span):
    to_ret = ""
    end = format_text(span.tail)
    for key in span.keys():
        if key == "style":
            style_output = format_style(span.get("style"))
            to_ret += style_output[0]
            end += style_output[1]
        else:
            print("ERROR: Unknown <span> attribute " + key)
    to_ret += format_text(span.text)
    to_ret += format_children(span)
    return to_ret + end


def format_strong(strong):
    to_ret = "\\textbf{"
    to_ret += format_text(strong.text)
    to_ret += format_children(strong)
    to_ret += "}"
    to_ret += format_text(strong.tail)
    return to_ret


def format_em(em):
    to_ret = "\\textit{"
    to_ret += format_text(em.text)
    to_ret += format_children(em)
    to_ret += "}"
    to_ret += format_text(em.tail)
    return to_ret


def format_a(a):
    # print(etree.tostring(a, method="html", encoding="unicode", pretty_print=True))
    to_ret = ""
    if a.get("href") is not None:
        to_ret += "\\href{" + a.get("href") + "}{"
    to_ret += format_text(a.text)
    to_ret += format_children(a)
    if a.get("href") is not None:
        to_ret += "}"
    to_ret += format_text(a.tail)
    return to_ret


def format_img(img):
    to_ret = ""
    image_url = img.get("src")
    filename = image_url.split("/")[-1]
    if not os.path.isfile(filename):
        img_data = requests.get(image_url)
        if img_data.status_code == 404:
            if "alt" in img.keys():
                to_ret += format_text(img.get("alt"))
        else:
            with open(filename, 'wb') as handler:
                handler.write(img_data.content)
            print("Downloading image from " + image_url)
            to_ret += "\\includegraphics{" + filename + "}"
    else:
        to_ret += "\\includegraphics{" + filename + "}"
    to_ret += format_text(img.tail)
    return to_ret


def format_div(div):
    to_ret = format_text(div.text)
    to_ret += format_children(div)
    to_ret += format_text(div.tail)
    return to_ret


def format_br(br):
    return "\\newline\n" + format_text(br.tail)


def format_strike(strike):
    to_ret = "\\sout{"
    to_ret += format_text(strike.text)
    to_ret += format_children(strike)
    to_ret += "}"
    to_ret += format_text(strike.tail)
    return to_ret


def format_sup(sup):
    to_ret = "\\textsuperscript{"
    to_ret += format_text(sup.text)
    to_ret += format_children(sup)
    to_ret += "}"
    to_ret += format_text(sup.tail)
    return to_ret


def format_iframe(iframe):
    to_ret = "\\href{" + iframe.get("src") + "}{[Embedded Video]}"
    return to_ret + format_text(iframe.tail) + "\n"


def format_u(u):
    to_ret = "\\underline{"
    to_ret += format_text(u.text)
    to_ret += format_children(u)
    to_ret += "}"
    to_ret += format_text(u.tail)
    return to_ret


def format_ol(ol):
    to_ret = "\\begin{enumerate}\n"
    to_ret += format_text(ol.text)
    to_ret += format_children(ol)
    to_ret += "\\end{enumerate}\n"
    to_ret += format_text(ol.tail)
    return to_ret


def format_ul(ul):
    to_ret = "\\begin{itemize}\n"
    to_ret += format_text(ul.text)
    to_ret += format_children(ul)
    to_ret += "\\end{itemize}\n"
    to_ret += format_text(ul.tail)
    return to_ret


def format_li(li):
    to_ret = "\\item{\n"
    to_ret += format_text(li.text)
    to_ret += format_children(li)
    to_ret += "}\n"
    to_ret += format_text(li.tail)
    return to_ret


def format_text(text: str):
    if text is None or text.strip() == " ":
        return ""
    to_ret = text
    if "\n" in to_ret or "\t" in to_ret:
        to_ret = to_ret.strip()
    to_ret = to_ret.replace("~", "\\mytexttilde{}")
    to_ret = to_ret.replace("$", "\\$")
    to_ret = to_ret.replace("#", "\\#")
    to_ret = to_ret.replace("%", "\\%")
    to_ret = to_ret.replace("_", "\\_")
    to_ret = to_ret.replace("&", "\\&")
    to_ret = to_ret.replace("^", "\\carat{}")
    to_ret = to_ret.replace(" ", " ")  # This isn't a space, it's a non-breaking space
    to_ret = to_ret.replace("♥", "\\ding{170}")
    return to_ret
