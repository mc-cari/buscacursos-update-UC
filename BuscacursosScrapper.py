import requests
import time
from bs4 import BeautifulSoup

class Course:

    def __init__(self, code):
        self.code = code
        self.sections_info = []
        self.page_url = ""

    def copy(self):
        
        copied_course = Course(self.code)
        copied_course.page_url = self.page_url
        copied_course.sections_info = self.sections_info.copy()

        return copied_course

class BuscacursosScrapper:

    def __init__(self):
        self.courses = []
        self.semester = -1
        self.year = -1

        self.ask_semester_to_scrap()

        self.ask_course_codes()

        self.get_table_info_columns_names(self.get_url_from_course(self.courses[0]))

        self.get_courses_info()

    def ask_semester_to_scrap(self):

        while(self.year == -1):
            try:
                self.year = int(input("Input year : "))
                
            except:
                print("Invalid Format")
                self.year = -1

        while(self.semester == -1):
            try:
                self.semester = int(input("Input semester number (TAV = 3): "))
                if(self.semester not in [1,2,3]):
                    raise Exception
            except:
                print("Invalid Format")
                self.semester = -1


    def ask_course_codes(self):

        course_code = "None"
        print("Input -1 or nothing to finish")
        while(course_code):
            course_code = input("Ingresar nueva sigla (e.g. IIC1001) de ramo: ")
            if(len(course_code) == 0 or course_code == '-1'):
                  break
            self.courses.append(Course(course_code))

    def get_table_info_columns_names(self, url):

        self.column_names = []

        try:
            resource = requests.get(url).text
            souped_resource = BeautifulSoup(resource,'html.parser')
            all_rows = souped_resource.find_all('tr')

            for row in all_rows:
                all_column = row.find_all('td')

                for i in range(len(all_column)):
 
                    val = all_column[i].string
                    
                    if(i == 0 and val != 'NRC'):
                        break   
                    if(val == 'Vacantes'):
                        self.column_names.append('Total')
                        self.column_names.append('Disponibles')
                        return

                    self.column_names.append(val)

            raise Exception("Information table not found, check if course code and semester is correct")

        except Exception as e:
            print(e)

    def get_courses_info(self):
        for course in self.courses: 
            course.page_url = self.get_url_from_course(course)
            course.sections_info = self.get_updated_sections_info(course)
            
    def get_url_from_course(self, course):
        return f'https://buscacursos.uc.cl/?cxml_semestre={self.year}-{self.semester}&cxml_sigla={course.code}#resultados'


    def print_courses_info(self):
        
        for course in self.courses:
            if(course.sections_info):
                print(course.sections_info[0]['Nombre'])
                for section in course.sections_info:
                    print(' Section', section['Sec.'], 'Vacancies available:', section['Disponibles'])

    def run_scrapper(self):

        self.print_courses_info()

        while True:

            updated_courses = self.copy_courses()

            for i in range(len(self.courses)):
                
                updated_courses[i].sections_info = self.get_updated_sections_info(updated_courses[i])
                for j in range(len(self.courses[i].sections_info)):

                    if(updated_courses[i].sections_info[j]['Disponibles'] != self.courses[i].sections_info[j]['Disponibles']):
                        self.print_updated_section_info(updated_courses[i].sections_info[j], self.courses[i].sections_info[j]['Disponibles'])
                        self.courses[i].sections_info[j]['Disponibles'] = updated_courses[i].sections_info[j]['Disponibles']

                time.sleep(1)

    def copy_courses(self):
        
        copied_courses = []
        for course in self.courses:
            copied_courses.append(course.copy())

        return copied_courses
    
    def print_updated_section_info(self, section_info, prev_vacancies_available):
        print(section_info['Nombre'], ' Update vacancies in Section', section_info['Sec.'],':', prev_vacancies_available, '->', section_info['Disponibles'], '\n')

    def get_updated_sections_info(self, course):
        
        sections_info = []

        try:
            resource = requests.get(course.page_url).text
        except:
            print("Internet Connection Failed")
            return

        souped_resource = BeautifulSoup(resource,'html.parser')

        odd_rows = souped_resource.find_all('tr', attrs={'class': 'resultadosRowImpar'})
        even_rows = souped_resource.find_all('tr', attrs={'class': 'resultadosRowPar'})

        # Traverse all columns in order
        for r in range(len(even_rows) + len(odd_rows)):

            if(r % 2 == 0):
                all_column = even_rows[r // 2].find_all('td')
            else:
                all_column = odd_rows[r // 2].find_all('td')

            section_info = dict()

            for i in range(len(all_column)):

                val = all_column[i].string
                if(i < len(self.column_names)):
                    section_info[self.column_names[i]] = val
            sections_info.append(section_info)

        return sections_info