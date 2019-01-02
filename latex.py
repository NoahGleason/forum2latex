import requests
import os.path
from PIL import Image

import data

assignable_colors = [data.Color("blue"), data.Color("brown"), data.Color("cyan"), data.Color("green"),
                     data.Color("lime"), data.Color("magenta"), data.Color("olive"), data.Color("orange"),
                     data.Color("pink"), data.Color("purple"), data.Color("teal"), data.Color("violet"),
                     data.Color("yellow")]

extensions = ["png", "jpg", "gif"]

pixels_to_pt = {8: 6, 9: 7, 10: 7.5, 11: 8, 12: 9, 13: 10, 14: 10.5, 15: 11, 16: 12, 17: 13, 18: 13.5, 19: 14, 20: 14.5,
                21: 15, 22: 16, 23: 17, 24: 18, 25: 19, 36: 27, 48: 36, 50: 37.5}

no_newline_after_tags = ["blockquote"]

DOC_WIDTH_PX = 264

approx_chars_per_line = 37


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


def format_html(comment: data.Comment):
    to_ret = "\\begin{tcolorbox}[title=" + format_text(comment.get_author().get_name())
    to_ret += ",after title={\\hfill " + comment.get_date().strftime("%H:%M, %B %d, %Y") + "}"
    if comment.get_author().has_color():
        to_ret += ","
        to_ret += comment.get_author().get_color().get_latex()
    to_ret += "]\n"
    to_ret += format_text(comment.get_text().text)
    end = "\\end{tcolorbox}\n"
    to_ret += format_children(comment.get_text(), False)
    return to_ret + end


def format_text_tag(element, newline_allowed: bool):
    if element.tag == "p":
        return format_p(element, newline_allowed)
    elif element.tag == "blockquote":
        return format_blockquote(element)
    elif element.tag == "span":
        return format_span(element, newline_allowed)
    elif element.tag == "strong" or element.tag == "b":
        return format_strong(element)
    elif element.tag == "a":
        return format_a(element)
    elif element.tag == "img":
        return format_img(element)
    elif element.tag == "div":
        return format_div(element, newline_allowed)
    elif element.tag == "br":
        return format_br(element, newline_allowed)
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


def format_children(children, initial_newline_allowed=True):
    to_ret = ""
    newline_allowed = initial_newline_allowed
    for i in range(len(children)):
        if newline_allowed:
            to_ret += format_text_tag(children[i], True)
            newline_allowed = children[i].tag not in no_newline_after_tags
        else:
            new_text = format_text_tag(children[i], False)
            newline_allowed = new_text.strip() != "" and children[i].tag not in no_newline_after_tags
            to_ret += new_text
    return to_ret


def format_p(p, newline_allowed: bool):
    if format_text(p.text).strip() == "" and len(p) == 0:
        if newline_allowed:
            return "\\newline{}" + format_text(p.tail) + "\n"
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
            end = style_output[1] + end
        else:
            print("ERROR: Unknown <p> attribute " + key)
    to_ret += format_text(p.text)
    to_ret += format_children(p, initial_newline_allowed=False)
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
        elif attribute[:12] == "font-family:" or attribute[:12] == "margin-left:" or attribute == "text-align:justify" or attribute == "background-color:transparent":
            front += ""  # Do nothing
        elif attribute[:11] == "text-align:":
            if attribute[11:].lower() == "center":
                front += "\\begin{center}"
                end = "\\end{center}" + end
            else:
                print("WARNING: unknown text alignment "+attribute)
        elif attribute[:17] == "background-color:":
            if attribute[17:20] == "rgb":
                rgb = attribute[21:-1]
                front += "\\colorbox[RGB]{" + rgb + "}{"
                end = "}" + end
            else:
                print("Unknown background color encoding: "+attribute)
        elif attribute.strip() == "":
            front += ""
        else:
            print("WARNING: Unknown style attribute " + attribute)
    return front, end


def format_blockquote(blockquote):
    to_ret = "\\begin{tcolorbox}[title=" + format_text(blockquote.get("data-ipsquote-username")) + "]\n"
    to_ret += format_text(blockquote.text)
    to_ret += format_children(blockquote, initial_newline_allowed=False)
    end = "\\end{tcolorbox}\n" + format_text(blockquote.tail)
    return to_ret + end


def format_span(span, newline_allowed: bool):
    if "data-excludequote" in span.keys():
        return ""
    to_ret = ""
    end = format_text(span.tail)
    for key in span.keys():
        if key == "style":
            style_output = format_style(span.get("style"))
            to_ret += style_output[0]
            end = style_output[1] + end
        else:
            print("ERROR: Unknown <span> attribute " + key)
    to_ret += format_text(span.text)
    if to_ret.strip() != "" or end.strip() != "":  # If there's actual content
        end += "\n"
    to_ret += format_children(span, initial_newline_allowed=(newline_allowed or format_text(span.text).strip() != ""))
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
    to_ret = ""
    if a.get("href") is not None:
        to_ret += "\\href{" + format_arguments(a.get("href")) + "}{"

    if " " not in format_text(a.text) and len(format_text(a.text)) > approx_chars_per_line:
        to_ret += "[link]"
    else:
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

    if filename[:14] == "imageproxy.php":
        if "alt" in img.keys():
            to_ret += format_text(img.get("alt"))
        else:
            to_ret += "[missing image]"
    else:
        filename = filename.replace("jpeg", "jpg")
        dot_split = filename.split(".")
        extension_index = 1
        while dot_split[extension_index][:3].lower() not in extensions:
            extension_index += 1
            if extension_index == len(dot_split):
                print("Error formatting file "+img.get("src"))
        filename = dot_split[0] + "." + dot_split[extension_index][:3]
        filename = "images/" + filename
        embed_output = embed_image(image_url, filename)
        if embed_output == "":
            if "alt" in img.keys():
                to_ret += format_text(img.get("alt"))
            else:
                to_ret += "[missing image]"
        else:
            to_ret += embed_output

    to_ret += format_text(img.tail)
    return to_ret


def format_div(div, newline_allowed: bool):
    if div.get("class") == "ipsQuote_citation":
        return ""
    to_ret = ""
    end = format_text(div.tail)
    for key in div.keys():
        if key == "style":
            style_output = format_style(div.get("style"))
            to_ret += style_output[0]
            end = style_output[1] + end
    to_ret += format_text(div.text)
    if to_ret.strip() != "" or end.strip() != "":  # If there's actual content
        end += "\n"
    to_ret += format_children(div, initial_newline_allowed=(newline_allowed or format_text(div.text).strip() != ""))
    return to_ret + end


def format_br(br, newline_allowed: bool):
    if newline_allowed:
        return "\\newline{}\n" + format_text(br.tail)
    else:
        return format_text(br.tail)


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
    to_ret = ""
    video_code = iframe.get("src").split("/")[-1]
    video_code = video_code.split("?")[0]
    embed_output = embed_image("https://img.youtube.com/vi/" + video_code + "/maxresdefault.jpg",
                               "thumbnails/" + video_code + ".jpg")
    if embed_output == "":
        # Retry with HQ instead of maxres
        embed_output = embed_image("https://img.youtube.com/vi/" + video_code + "/hqdefault.jpg",
                                   "thumbnails/" + video_code + ".jpg")
        if embed_output == "":
            to_ret += "\\href{https://www.youtube.com/watch?v=" + format_arguments(video_code) + "}{[Embedded Video]}"
        else:
            to_ret += "\\href{https://www.youtube.com/watch?v=" + format_arguments(
                video_code) + "}{" + embed_output + "}"
    else:
        to_ret += "\\href{https://www.youtube.com/watch?v=" + format_arguments(video_code) + "}{" + embed_output + "}"

    to_ret += format_text(iframe.tail)
    to_ret += "\n"
    return to_ret


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


def embed_image(image_url, filename):
    filename = filename.replace("%", "p")
    og_filename = filename
    if filename[-3:].lower() == "gif":
        filename = filename[:-3] + "png"

    if not os.path.isfile(filename):
        img_data = requests.get(image_url)
        if img_data.status_code == 404:
            return ""
        else:
            with open(og_filename, 'wb') as handler:
                handler.write(img_data.content)
            print("Downloading image from " + image_url)
            if filename != og_filename:
                img_obj = Image.open(og_filename)
                img_obj.save(filename)
                os.remove(og_filename)

    if Image.open(filename).size[0] > DOC_WIDTH_PX:
        return "\\includegraphics[width=\\textwidth]{" + filename + "}"
    else:
        return "\\includegraphics{" + filename + "}"


def format_arguments(text: str):
    if text is None or text.strip() == " ":
        return ""
    to_ret = text
    to_ret = to_ret.replace("$", "\\$")
    to_ret = to_ret.replace("#", "\\#")
    to_ret = to_ret.replace("%", "\\%")
    to_ret = to_ret.replace("_", "\\_")
    to_ret = to_ret.replace("&", "\\&")
    return to_ret


def format_text(text: str):
    if text is None:
        return ""
    to_ret = text
    to_ret = to_ret.replace(" ", " ")  # This isn't a space, it's a non-breaking space
    if "\n" in to_ret or "\t" in to_ret:
        to_ret = to_ret.strip()
    to_ret = to_ret.replace("\\", "\\textbackslash{}")
    to_ret = to_ret.replace("$", "\\$")
    to_ret = to_ret.replace("#", "\\#")
    to_ret = to_ret.replace("%", "\\%")
    to_ret = to_ret.replace("_", "\\_")
    to_ret = to_ret.replace("&", "\\&")
    to_ret = to_ret.replace("( ͡° ͜ʖ ͡°)", "\\Lenny{}")

    new_text = ""
    in_japanese = False
    for char in to_ret:
        if int("0x3040", 16) <= ord(char) <= int("0x30FF", 16) or int("0x31F0", 16) <= ord(char) <= int("0x31FF",
                                                                                                        16) or int(
                "0xFF00", 16) <= ord(char) <= int("0xFFEF", 16):
            if not in_japanese:
                in_japanese = True
                new_text += "\\begin{CJK}{UTF8}{goth}"
        elif in_japanese:
            in_japanese = False
            new_text += "\\end{CJK}"
        new_text += char
    to_ret = new_text

    to_ret = to_ret.replace("♥", "\\ding{170}")
    to_ret = to_ret.replace("☣", "$\\biohazard$")
    to_ret = to_ret.replace("∞", "$\\infty$")
    to_ret = to_ret.replace("▽", "$\\triangledown$")
    to_ret = to_ret.replace("^", "\\carat{}")
    to_ret = to_ret.replace("~", "\\mytexttilde{}")
    return to_ret
