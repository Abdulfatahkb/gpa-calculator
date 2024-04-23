from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen, ScreenManager
import json

backup_file = '.backup.json'                                        # To save the current state of the running app


def read_json_file(file_path):                                      # For reading the json file
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{file_path}'.")
        return None

def write_json_file( data, file_path):                              # Fot writing 
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except json.JSONDecodeError:
        print(f"Error decoding JSON data.")
    except Exception as e:
        print(f"An error occurred: {e}")


class GPACalculator(App):
    header = ['Unit', 'grade']
    courses = []
    restored = False
    def __init__(self):
        super(GPACalculator, self).__init__()


    def previous(self):                                             # For restoring previous state of the application
        courses_backup = read_json_file(backup_file)
        if courses_backup and not (self.restored):                  # Check if backup file exist
            self.courses = courses_backup
            self.root.ids.grade_input.text = 'A'                    # Initial Placeholders
            self.root.ids.credit_input.text = '3'
            self.restored = True
        else: 
            self.calculate_gpa_button_pressed()
        self.update_course_list()
        self.root.ids.previous_id.text = 'Calculate'


    def add_course(self, credit, grade):
        grade_values = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
        grade_value = grade_values.get(grade.upper(), 0)
        self.courses.append({'credit': float(credit), 'grade': grade_value})
        self.update_course_list()
    
    # Clear Every Insterted Courses
    def clear_courses(self):
        self.courses.clear()
        self.update_course_list()
        self.root.ids.previous_id.text = 'Calculate'
        self.restored = True
        self.calculate_gpa_button_pressed()

    # Delete a single course
    def delete_course(self, instance):                              
        course_index = int(instance.id)
        del self.courses[course_index]
        self.calculate_gpa_button_pressed()
        self.update_course_list()

    # For calculating the gpa
    def calculate_gpa(self):
        total_grade_points = 0
        total_credit = 0
        for course in self.courses:
            total_grade_points += course['credit'] * course['grade']
            total_credit += course['credit']
        if total_credit == 0:
            return 0
        gpa = total_grade_points / total_credit
        return gpa

    # This will be called when adding, deleting the course
    def update_course_list(self):
        course_list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        course_list_layout.bind(minimum_height=course_list_layout.setter('height'))
        grade_values_inv = {5: 'A', 4: 'B', 3: 'C', 2: 'D', 1: 'E', 0: 'F'}

        for index, course in enumerate(self.courses):                       # Insert Credit value
            self.unit_label = Label(
                text=f"{course['credit']}", 
                size_hint= [.8, .8], color = (0, 0, 0, 1),
                font_size = 40,
                )
            self.grade_label = Label(                                       # Insert Grade value
                text=f"{grade_values_inv[course['grade']].upper()}", 
                size_hint= [.8, 1], color = (0, 0, 0, 1),
                font_size = 40
                )
             
            
            delete_button = Button(text='X', size_hint= [.2, 1], color = (1, 0, 0, .75), font_size = 40)
            delete_button.bind(on_press=self.delete_course)
            delete_button.background_normal = ''
            delete_button.background_color = (.5, .5, .5, .5)
            delete_button.id = str(index)
            
            course_unit_layout = BoxLayout(size_hint_y=None, height=50)
            course_unit_layout.add_widget(self.unit_label)
            course_unit_layout.add_widget(self.grade_label)
            course_unit_layout.add_widget(delete_button)
            course_list_layout.padding = 10


            # For drawing a single [white] line by the side
            course_list_layout.add_widget(course_unit_layout)
            line_height = (course_list_layout.size[1]/2) * len(course_list_layout.children)
            position = course_list_layout.size[0] / 2
            with course_list_layout.canvas:
                Color(1, 1, 1, .5)
                Rectangle(pos=(position, 30), size=(3, line_height ))

        # clear the previous courses and then update the courses
        self.root.ids.course_list.clear_widgets()
        self.root.ids.course_list.add_widget(course_list_layout)
        data_to_write =  self.courses
        write_json_file(data_to_write, backup_file)



    def add_course_button_pressed(self):                        # Adding a course when [Grade] is added
        self.restored = True
        credit = self.root.ids.credit_input.text
        grade = self.root.ids.grade_input.text
        try:
            credit = float(credit)
            if credit <= 0:
                raise ValueError
            self.add_course(credit, grade)
            self.root.ids.credit_input.text = ''
            self.root.ids.grade_input.text = ''
        except ValueError:
            self.root.ids.credit_input.text = str(credit)
            self.root.ids.grade_input.text = ''
        
        
        self.root.ids.credit_input.text = str(credit)
        self.root.ids.grade_input.text = ''
    def calculate_gpa_button_pressed(self):
        gpa = self.calculate_gpa()
        self.root.ids.result_label.text = f'{gpa:.2f}'
        self.root.ids.progress_id.value = gpa

    def build(self):
        return GPACalculatorUI()

class GPACalculatorUI(BoxLayout):
    pass

    
if __name__ == '__main__':
    GPACalculator().run()
