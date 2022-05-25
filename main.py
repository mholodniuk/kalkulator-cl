import os
import requests
from bs4 import BeautifulSoup
from Parser import Parser
from dotenv import load_dotenv

class EdukacjaCl:
    session: requests.session
    username: str
    password: str
    current_semester: int
    web_token: str
    web_session_token: str
    index: str

    def __init__(self, session: requests.session, username=None, password=None) -> None:
        self.session = session
        if username is None or password is None:
            #print('using data from .env file to log in')
            if load_dotenv('.env'):
                self.username = os.getenv('USERNAME')
                self.password = os.getenv('PASSWORD')
            else:
                print('Didn`t find .env file')
        else:
            self.username = username
            self.password = password

        self.web_token = self.get_web_token()        
        self.web_session_token = self.get_web_session_token()
        self.index = self.get_index()
        self.current_semester = self.get_current_semester()

    def get_web_token(self) -> str:
        try:
            get_login = self.session.get("https://edukacja.pwr.wroc.pl/EdukacjaWeb/studia.do")
            home = BeautifulSoup(get_login.content, 'html.parser')
            return home.find('input', {'name': 'cl.edu.web.TOKEN'}).get('value')
        except requests.ConnectionError:
            print('Unable to connect to edukacja.cl')

    def get_web_session_token(self) -> str:
        data = {
            'cl.edu.web.TOKEN': self.web_token,
            'login': self.username,
            'password': self.password 
        }
        post_login = self.session.post("https://edukacja.pwr.wroc.pl/EdukacjaWeb/logInUser.do", data=data)

        if requests.get(post_login.url, auth=('user', 'pass')).status_code == 200:
            login = BeautifulSoup(post_login.content, 'html.parser')
            # get the token from form tag and compose login-post data
            return login.find('input', {'name': 'clEduWebSESSIONTOKEN'}).get('value')
        else:
            print('Unable to log in using your data')
            exit()

    def get_index(self) -> str:
        # get the index subpage
        index_url = "https://edukacja.pwr.wroc.pl/EdukacjaWeb/indeks.do?clEduWebSESSIONTOKEN=" + self.web_session_token + \
            "&event=WyborSluchacza"
        try:
            return self.session.get(index_url).content
        except:
            print('Unable to get index')
            exit()

    def get_current_semester(self) -> int:
        courses = BeautifulSoup(self.index, 'html.parser')
        personal_data = Parser.find_course_data(str(Parser.find_courses_table(-3, courses)))
        return int(personal_data[38])

    def get_semester_gpa(self, number_of_semester) -> float:
        if number_of_semester >= self.current_semester:
            print('incorrect semester chosen')
        else:
            courses = BeautifulSoup(self.index, 'html.parser')
            course_list = Parser.find_course_data(
                str(Parser.find_courses_table((self.current_semester - number_of_semester), courses))
            )
            course_list = Parser.divide_into_sublists(Parser.filter_data(course_list))

            print(Parser.calculate_average(course_list[0]))


if __name__ == "__main__":
    with requests.Session() as session:
        edukacja = EdukacjaCl(session)
        edukacja.get_semester_gpa(3)
