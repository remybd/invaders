#! /usr/bin/env python3
# coding: utf-8

import xml.etree.ElementTree as ET
import json
import re

style_actif = "#icon-503-009D57"
style_dead = "#icon-960-DB4436-nodesc"
actif_and_dead_placemarks = { style_actif : [], style_dead : []}

file_name = "Space_Invaders_By_Categories.kml"
json_file_name = "invaders.json"

def get_calc_list(docu):
    return docu.findall("{http://www.opengis.net/kml/2.2}Folder")

def get_style_list(docu):
    return docu.findall("{http://www.opengis.net/kml/2.2}StyleMap")

def get_all_placemarks(calc_list):
    placemark_list = []
    for calc in calc_list:
        placemark_list.extend(calc.findall("{http://www.opengis.net/kml/2.2}Placemark"))

    return placemark_list

def get_json_data():
    data = json.load(open(json_file_name))
    return data

def set_style_function_state(placemark, state):
    styleUrl = placemark.findall("{http://www.opengis.net/kml/2.2}styleUrl")[0]

    if state:
        styleUrl.text = style_actif
        actif_and_dead_placemarks[style_actif].append(placemark)
    else:
        styleUrl.text = style_dead
        actif_and_dead_placemarks[style_dead].append(placemark)



def add_image(placemark, url):
    extendedData = placemark.find("{http://www.opengis.net/kml/2.2}ExtendedData")

    if url:
        if extendedData and extendedData[0]:
            extendedData[0][0].text = extendedData[0][0].text + " " + url
        else:
            #create extende data
            extendedData = ET.SubElement(placemark, "ExtendedData")
            data = ET.SubElement(extendedData, "Data", {"name":"gx_media_links"})
            value = ET.SubElement(data, "value")
            value.text = url



def update_invader_state(placemark, json_data):
    name = placemark.findall("{http://www.opengis.net/kml/2.2}name")
    m = re.search('PA(-|_)(?P<num_invader>[0-9]{1,4})', name[0].text)
    if m:
        num_invader_string = m.group("num_invader")
        num_invader = int(num_invader_string)
        invader_json = [item for item in json_data if item["Id"] == num_invader][0]

        set_style_function_state(placemark, invader_json["Islive"])
        add_image(placemark, invader_json["Url"])
    '''else:
        print(name[0].text)'''


def update_invaders(placemark_list, json_data):
    for placemark in placemark_list:
        update_invader_state(placemark, json_data)


def recreate_folders(tree, docu):
    for key in actif_and_dead_placemarks.keys():
        folder = ET.SubElement(docu,"Folder")
        name = ET.SubElement(folder,"name")
        name.text = key
        for placemark in actif_and_dead_placemarks[key]:
            folder.append(placemark)

        #create the file and remove the xmlFolder for the next one
        tree.write(key[1:] + '.kml', encoding="utf-8")
        docu.remove(docu[-1])




def main():
    tree = ET.parse(file_name)
    root = tree.getroot()

    docu = root[0]
    calc_list = get_calc_list(docu)
    placemark_list = get_all_placemarks(calc_list)
    len_calc_list = len(calc_list)

    json_data = get_json_data()
    update_invaders(placemark_list, json_data)

    #delete all folders
    for i in range(0, len_calc_list):
        docu.remove(docu[-1])

    print(len(actif_and_dead_placemarks[style_actif]))
    recreate_folders(tree, docu)



if __name__ == "__main__":
    main()
