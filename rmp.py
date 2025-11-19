import os
import sys
from sys import exit
import webbrowser
import json
import requests
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

DATA_DIR = os.path.expanduser(os.path.join("~", ".rmpcli"))
DATA_PATH = os.path.join(DATA_DIR, "config.json")

class School:
    name = ""
    url = ""
    quality = 0.0
    rating_count = 0

    @classmethod
    def from_dict(cls, data):
        school = cls()

        if (data is None):
            return None

        school.name = data["name"]
        school.url = data["url"]
        school.quality = data["quality"]
        school.rating_count = data["rating_count"]
        return school

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "quality": self.quality,
            "rating_count": self.rating_count
        }

    def get_id(self):
        return self.url.strip("https://www.ratemyprofessors.com/school/")\
        
    def __str__(self):
        return f"School(name: {self.name}, url: {self.url}, quality: {self.quality}, rating_count: {self.rating_count})"
    
    def __repr__(self):
        return f"School({self.name}, {self.url}, {self.quality}, {self.rating_count})"

class Professor():
    name = ""
    url = ""
    department = ""
    school = School()
    quality = 0.0
    rating_cout = 0
    take_again_percentage = 0
    difficulty = 0.0

    def __str__(self):
        return f"Professor(name: {self.name}, url: {self.url}, department: {self.department}, school: {self.school.name}, quality: {self.quality}, rating_count: {self.rating_count}, take_again_percentage: {self.take_again_percentage}, difficulty: {self.difficulty})"

    def __repr__(self):
        return f"Professor({self.name}, {self.url}, {self.department}, {self.school}, {self.quality}, {self.rating_count}, {self.take_again_percentage}, {self.difficulty})"


def save_data(key, data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    data_dict = {}

    with open(DATA_PATH, "r") as f:    
        try:
            data_dict = json.load(f)
        except json.JSONDecodeError:
            print("No existing data found, creating new data file.")
            pass
    
    with open(DATA_PATH, "w+") as f:
        data_dict[key] = data
        f.write(json.dumps(data_dict))
        

def load_data(key):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    with open(DATA_PATH, "r") as f:
        try:
            data_dict = json.load(f)
        except json.JSONDecodeError:
            return None
        
    return data_dict[key] if key in data_dict else None
    
def delete_data(key):
    data_dict = {}

    if not os.path.exists(DATA_DIR):
        return

    with open(DATA_PATH, "r") as f:
        try:
            data_dict = json.load(f)
        except json.JSONDecodeError:
            return
        
    if key in data_dict:
        del data_dict[key]

    with open(DATA_PATH, "w") as f:
        f.write(json.dumps(data_dict))


def get_schools_matching(name: str) -> list[School]:
    schools = []

    resp = requests.get("https://www.ratemyprofessors.com/search/schools", params={ "q" : name.replace(" ", "%20") }, headers=headers)

    if (resp.status_code != 200):
        print(f"Error: {resp.status_code}")
        exit()

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

def get_profs_at(school: School, name: str, ):
    """
    Returns a list of professor objects mataching name and working at school. 
    """

    profs = []
    resp = requests.get(f"https://www.ratemyprofessors.com/search/professors/{school.get_id()}", params={ "q" : name.replace(" ", "%20") }, headers=headers)

    if (resp.status_code != 200):
        print(f"Error: {resp.status_code}")
        exit()

    parsed = BeautifulSoup(resp.text, 'html.parser')
    elements = parsed.find_all("a", class_=re.compile("TeacherCard"))
    for element in elements:
        newProf = Professor()
        newProf.name = element.find("div", class_=re.compile("CardName")).getText()
        newProf.url = "https://www.ratemyprofessors.com" + element["href"]
        newProf.quality = element.find("div", class_=re.compile("CardNumRating__CardNumRatingNumber")).getText()
        newProf.rating_count = element.find("div", class_=re.compile("CardNumRating__CardNumRatingCount")).getText().strip(" ratings")
        newProf.department = element.find("div", class_=re.compile("CardSchool__Department")).getText()
        newProf.school = school
        profs.append(newProf)

    return profs

def print_help():
    print("rmp - Rate My Professors CLI by Matthew Dinh")
    print("Usage: rmp <command> [options]")
    print("Commands:")
    print("  config <school name>   Configure the school to search professors at")
    print("  find <professor name>  Find a professor at the configured school")

if __name__ == "__main__":
    pass

args = sys.argv

if len(args) <= 1:
    print_help()

if len(args) >= 2 and args[1] == "help" or args[1] == "-?" or args[1] == "--help":
    print_help()

if len(args) >= 2 and args[1] == "config":
    if len(args) <= 2:
        print("Usage: rmp config <school name>")
        exit()

    school_name = " ".join(args[2:])
    matching_schools = get_schools_matching(school_name)

    if len(matching_schools) == 0:
        print(f"No schools found matching '{school_name}'")
        exit()

    print("Matching schools:")
    for i, prof in enumerate(matching_schools):
        print(f"{i + 1}. {prof.name} (Quality: {prof.quality}, Ratings: {prof.rating_count})")

    selection = input("Select a school by number: ")
    try:
        selection_index = int(selection) - 1
        if selection_index < 0 or selection_index >= len(matching_schools):
            print("Invalid selection.")
            exit()
    except ValueError:
        print("Invalid selection.")
        exit()

    selected_school = matching_schools[selection_index]
    save_data("school", selected_school.to_dict())

    print(f"Configured school: {selected_school.name}")

if len(args) >= 2 and args[1] == "find":
    if len(args) <= 2:
        print("Usage: rmp find <professor name>")
        exit()

    config_school = School.from_dict(load_data("school"))

    if (config_school is None):
        print("No school configured. Please set a school using 'rmp config <school name>'")
        exit()

    prof_name = " ".join(args[2:])
    matching_profs = get_profs_at(config_school, prof_name)

    if len(matching_profs) == 0:
        print(f"No professors found matching '{prof_name}' at '{config_school.name}'")
        exit()

    print("Matching professors:")
    for i, prof in enumerate(matching_profs):
        print(f"{i + 1}. {prof.name} (Quality: {prof.quality}, Ratings: {prof.rating_count})")

    selection = input("Select to open in web browser: ")
    try:
        selection_index = int(selection) - 1
        if selection_index < 0 or selection_index >= len(matching_profs):
            print("Invalid selection.")
            exit()
    except ValueError:
        print("Invalid selection.")
        exit()

    webbrowser.open(matching_profs[selection_index].url, new=2)

if len(args) >= 2 and args[1] == "exit":
    exit()


