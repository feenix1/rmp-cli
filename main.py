import os
import sys
import requests
import re
from bs4 import BeautifulSoup

class School:
    name = ""
    url = ""
    quality = 0.0
    rating_count = 0

    def get_id(self):
        return self.url.strip("https://www.ratemyprofessors.com/school/")

class Professor:
    name = ""
    url = ""
    quality = 0.0
    rating_cout = 0


def get_schools_matching(name):
    schools = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    resp = requests.get("https://www.ratemyprofessors.com/search/schools", params={ "q" : name.replace(" ", "%20") }, headers=headers)

    if (resp.status_code != 200):
        print(f"Error: {resp.status_code}")
        exit

    parsed = BeautifulSoup(resp.text, 'html.parser')
    elements = parsed.find_all("a", class_=re.compile("SchoolCard"))
    for element in elements:
        newSchool = School()
        newSchool.name = element.find("div", class_=re.compile("SchoolCardHeader")).getText()
        newSchool.url = "https://www.ratemyprofessors.com" + element["href"]
        newSchool.quality = element.find("div", class_=re.compile("CardNumRating__CardNumRatingNumber")).getText()
        newSchool.rating_count = element.find("div", class_=re.compile("CardNumRating__CardNumRatingCount")).getText().strip(" ratings")
        schools.append(newSchool)
    return schools

# def get_profs_for(school):
school_str = input("What school do you go to: ")
schools = get_schools_matching(school_str)
