#! /usr/bin/env python3
# coding: utf-8

import xml.etree.ElementTree as ET

file_name = "Space_Invaders.kml"

def get_calc_list(docu):
    return docu.findall("{http://www.opengis.net/kml/2.2}Folder")

def get_style_list(docu):
    return docu.findall("{http://www.opengis.net/kml/2.2}StyleMap")

def get_all_placemarks(calc_list):
    placemark_list = []
    for calc in calc_list:
        placemark_list.extend(calc.findall("{http://www.opengis.net/kml/2.2}Placemark"))

    return placemark_list

def is_placemark_good_styleUrl(placemark, styleUrlString):
    style_url = placemark.findall("{http://www.opengis.net/kml/2.2}styleUrl")
    if styleUrlString in style_url[0].text :
        return True
    else:
        return False


def get_placemarks_by_styleUrl(placemark_list, styleUrl):
    pl_list_style = []
    for placemark in placemark_list:
        if is_placemark_good_styleUrl(placemark, styleUrl):
            pl_list_style.append(placemark)

    return pl_list_style


def sort_placemark_by_styles(placemark_list, style_list):
    placemarks_by_color = {}
    sum = 0
    for style in style_list:
        #only keep the styles with an id of size 15
        if len(style.attrib["id"]) == 15:
            placemarks = get_placemarks_by_styleUrl(placemark_list, "#" + style.attrib["id"])

            placemarks_by_color[style.attrib["id"]] = placemarks
            sum = sum + int(len(placemarks))
    print("initial_size : " + str(len(placemark_list)))
    print("sum : " + str(sum))
    return placemarks_by_color



def recreate_folders(tree, docu, placemarks_by_styles):
    for key in placemarks_by_styles.keys():
        folder = ET.SubElement(docu,"Folder")
        name = ET.SubElement(folder,"name")
        name.text = key
        for placemark in placemarks_by_styles[key]:
            folder.append(placemark)

        #create the file and remove the xmlFolder for the next one
        tree.write(key + '.kml', encoding="utf-8")
        docu.remove(docu[-1])


def main():
    tree = ET.parse(file_name)
    root = tree.getroot()

    docu = root[0]
    calc_list = get_calc_list(docu)
    placemark_list = get_all_placemarks(calc_list)
    style_list = get_style_list(docu)

    placemarks_by_styles = sort_placemark_by_styles(placemark_list, style_list)

    #delete all folders
    for i in range(0,3):
        docu.remove(docu[-1])

    recreate_folders(tree, docu, placemarks_by_styles)


if __name__ == "__main__":
    main()
