from bs4 import BeautifulSoup
from Course import Course


class Parser:

    @staticmethod
    def find_student_data(courses: BeautifulSoup, data_to_look_for='Numer semestru') -> str:
        '''
        params: 
            courses - html table from index subpage, 
            data_to_look_for - type of information you want to extract

        returns: value of wanted information element
        '''
        tables = courses.find(
            'table', {'class': 'KOLOROWA'})  # first table - personal data
        # filter
        tables = list(
            filter(None, Parser.search_for_rows_and_filter(str(tables))))
        # returns value of wanted parameter
        return tables[tables.index(data_to_look_for) + 1]

    @staticmethod
    def find_semesters_data(courses: BeautifulSoup, semester_to_look_for=1) -> list:
        '''
        params: semester to look for grades (all grades must be given)

        Finds all rows from the index table from given semester.

        returns: list with proper semester data (raw HTML)
        '''
        tables = courses.find('table', {'class': 'KOLOROWA', 'border': 0}).find_all(
            'table')[semester_to_look_for + 1]
        semester_list = []
        for table in tables:
            semester_list.append(table)
        return semester_list

    @staticmethod
    def search_for_rows_and_filter(semester_table_data: str) -> list:
        '''
        params: str -  HTML text to parse and find proper course data

        Removes all the unnecessary parts of HTML from course_table_data,
        and transforms it into a list.

        return: nice formatted data (unfiltered)
        '''
        soup = BeautifulSoup(semester_table_data, 'html.parser')
        list_of_courses = []
        for tr in soup.find_all('tr'):
            for td in tr:
                word = str(td.text)
                word = word.replace("\r\n", "")
                word = word.replace("\xa0", "")
                word = word.replace("\n", "")
                word = word.strip()
                list_of_courses.append(word)

        return list_of_courses

    @staticmethod
    def filter_and_format_data(unfiltered_list: list) -> list:
        '''
        param: unfiltered_list - list with empty spaces and undivided into Course format

        Divides the result of find_course_data method into Course type chunks
        (still including unnecessary title-data).

        returns: filtered list
        '''
        filtered_list = list(filter(None, unfiltered_list))
        chunked_list = list()
        for i in range(0, len(filtered_list), 5):
            chunked_list.append(filtered_list[i:i + 5])

        return chunked_list

    @staticmethod
    def split_into_course_format(chunked_list: list) -> list:
        '''
        param: chunked list - raw list of undivided courses

        Divides given list into list of lists (list of semesters, which are list of courses)
        and filters rows with title-data

        returns: list (semesters) of lists (courses in this semester) 
        '''
        courses_in_semester = []
        semester_list = []
        for chunk in chunked_list:
            if (chunk[0].strip() != "Kod kursu"):
                courses_in_semester.append(
                    Course(chunk[0].strip(), chunk[1].strip(), chunk[2].strip(), int(chunk[3]), float(chunk[4])))
            else:
                semester_list.append(courses_in_semester)
                courses_in_semester = []
        if courses_in_semester:
            semester_list.append(courses_in_semester)
        semester_list.pop(0)

        return semester_list
