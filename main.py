# Kivy imports
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.app import App

# time
from datetime import datetime

# SQLite
import sqlite3
from sqlite3 import Error

button_size = Window.size[1]/20
Window.softinput_mode = "below_target"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


connection = create_connection(r"database.db")

sql_create_devices_table = """ CREATE TABLE IF NOT EXISTS devices (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    power integer
                                ); """

sql_create_history_table = """CREATE TABLE IF NOT EXISTS history (
                                id integer PRIMARY KEY,
                                name datetime,
                                data text
                            );"""


sql_create_favourite_table = """CREATE TABLE IF NOT EXISTS favourite (
                                id integer PRIMARY KEY,
                                name text,
                                data text
                            );"""

if connection is not None:
    create_table(connection, sql_create_devices_table)
    create_table(connection, sql_create_history_table)
    create_table(connection, sql_create_favourite_table)
else:
    print("Error! cannot create the database connection.")


def select_all_device():
    cur = connection.cursor()
    cur.execute("SELECT * FROM devices")
    rows = cur.fetchall()

    return rows


def select_all_favourite():
    cur = connection.cursor()
    cur.execute("SELECT * FROM favourite")
    rows = cur.fetchall()

    return rows


def select_all_history():
    cur = connection.cursor()
    cur.execute("SELECT * FROM history")
    rows = cur.fetchall()

    return rows


def create_device(connection_to_db, device):
    sql = ''' INSERT INTO devices(name,power)
              VALUES(?,?) '''
    cur = connection_to_db.cursor()
    cur.execute(sql, device)
    connection_to_db.commit()

    return cur.lastrowid


def create_favourite(connection_to_db, favourite):
    sql = ''' INSERT INTO favourite(name,data)
              VALUES(?,?) '''
    cur = connection_to_db.cursor()
    cur.execute(sql, favourite)
    connection_to_db.commit()

    return cur.lastrowid


def create_history(connection_to_db, history):
    sql = ''' INSERT INTO history(name,data)
              VALUES(?,?) '''
    cur = connection_to_db.cursor()
    cur.execute(sql, history)
    connection_to_db.commit()

    return cur.lastrowid


class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)
        self.height = button_size


class SpinnerWidget(Spinner):
    def __init__(self, **kwargs):
        super(SpinnerWidget, self).__init__(**kwargs)
        self.option_cls = SpinnerOptions


class MyTextInput(TextInput):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.text != "":
            self.text = ""
        return super(MyTextInput, self).on_touch_down(touch)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()

        self.btn_new_calculation = Button(text="New Calculation",
                                          pos_hint={"x": 0.2, "y": 0.5},
                                          size_hint=(0.6, 0.1),
                                          on_press=self.go_to)
        self.float_layout.add_widget(self.btn_new_calculation)

        self.btn_history = Button(text="History",
                                  pos_hint={"x": 0.2, "y": 0.3},
                                  size_hint=(0.6, 0.1),
                                  on_press=self.go_to)
        self.float_layout.add_widget(self.btn_history)

        self.btn_favourite = Button(text="Favourite",
                                    pos_hint={"x": 0.2, "y": 0.1},
                                    size_hint=(0.6, 0.1),
                                    on_press=self.go_to)
        self.float_layout.add_widget(self.btn_favourite)

        self.add_widget(self.float_layout)

    def go_to(self, instance):
        if instance == self.btn_new_calculation:
            screen_manager.current = "calculation"
        elif instance == self.btn_history:
            s1 = screen_manager.get_screen("history")
            s1.load_history()
            screen_manager.current = "history"
        elif instance == self.btn_favourite:
            s1 = screen_manager.get_screen("favourite")
            s1.load_favourite()
            screen_manager.current = "favourite"


class CalculationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()
        self.body_row_data = []
        self.devices = [f"{device[1]} {device[2]} W" for device in select_all_device()]

        popup_content = BoxLayout(orientation="vertical")

        label_box_1 = Label(text='Device Name')
        self.text_box_1 = MyTextInput(text='')
        popup_content.add_widget(label_box_1)
        popup_content.add_widget(self.text_box_1)

        label_box_2 = Label(text='Device power [W]')
        self.text_box_2 = MyTextInput(text='')
        popup_content.add_widget(label_box_2)
        popup_content.add_widget(self.text_box_2)

        popup_content.add_widget(Button(text="Submit", on_press=self.add_new_device))

        self.popup_new_device = Popup(title='Add new device',
                                      content=popup_content,
                                      size_hint=(None, None),
                                      size=(Window.width/1.5, Window.height/3))

        btn = Button(text="Add new device",
                     pos_hint={"x": 0, "y": 1 - button_size/Window.size[1]},
                     size_hint=(0.6, button_size/Window.size[1]),
                     on_press=self.popup_new_device.open)
        self.float_layout.add_widget(btn)

        btn_new_line = Button(text="Add row",
                              pos_hint={"x": 0.6, "y": 1 - button_size/Window.size[1]},
                              size_hint=(0.2, button_size/Window.size[1]),
                              on_press=self.add_new_row)
        self.float_layout.add_widget(btn_new_line)

        self.btn_change_home = Button(text="Menu",
                                      pos_hint={"x": 0.8, "y": 1 - button_size/Window.size[1]},
                                      size_hint=(0.2, button_size/Window.size[1]),
                                      on_press=self.change_view)
        self.float_layout.add_widget(self.btn_change_home)

        self.layout = GridLayout(cols=5, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        # root = ScrollView(size_hint=(1, None),
        #                   size=(Window.width, 8.5*Window.height/10-20),
        #                   pos_hint={"x": 0, "y": 0.1 + 10/Window.height})

        root = ScrollView(size_hint=(1, None),
                          size=(Window.width, Window.height - 3 * button_size - 20),
                          pos_hint={"x": 0, "y": (2 * button_size + 10)/Window.size[1]})

        root.add_widget(self.layout)
        self.float_layout.add_widget(root)

        self.favourite_name = MyTextInput(text="<Favourite>",
                                          halign="center",
                                          pos_hint={"x": 0, "y": button_size/Window.size[1]},
                                          size_hint=(0.7, button_size/Window.size[1]))
        self.float_layout.add_widget(self.favourite_name)

        self.btn_save = Button(text="Save",
                               pos_hint={"x": 0.7, "y": button_size/Window.size[1]},
                               size_hint=(0.3, button_size/Window.size[1]),
                               on_press=self.save)
        self.float_layout.add_widget(self.btn_save)

        self.btn_print = Button(text="Result:",
                                pos_hint={"x": 0, "y": 0},
                                size_hint=(0.7, button_size/Window.size[1]),
                                on_press=self.save)
        self.float_layout.add_widget(self.btn_print)

        self.label_result = Label(text="- kWh",
                                  pos_hint={"x": 0.7, "y": 0},
                                  size_hint=(0.3, button_size/Window.size[1]))
        self.float_layout.add_widget(self.label_result)
        self.add_widget(self.float_layout)

        self.add_new_row()

    def add_new_row(self, instance=None):
        spin_number = MyTextInput(text="num",
                                  halign="center",
                                  size_hint_x=None,
                                  width=Window.size[0]/8)
        self.layout.add_widget(spin_number)

        spin_time = MyTextInput(text="time",
                                halign="center",
                                size_hint_x=None,
                                width=Window.size[0]/8)
        self.layout.add_widget(spin_time)

        spin = SpinnerWidget(text="device",
                             values=self.devices,
                             size_hint_y=None,
                             height=Window.height/20,
                             size_hint_x=None,
                             width=Window.size[0]/3)
        self.layout.add_widget(spin)

        btn_x = Button(text="x",
                       size_hint_y=None,
                       height=Window.height/20,
                       size_hint_x=None,
                       width=Window.size[0]/6,
                       on_press=self.remove_row)
        self.layout.add_widget(btn_x)

        label_result = Label(text="- kWh",
                             size_hint_x=None,
                             width=Window.size[0]/6)
        self.layout.add_widget(label_result)

        self.body_row_data.append([spin_number, spin_time, spin, label_result, btn_x])

    def remove_row(self, instance):
        for row in self.body_row_data:
            if instance in row:
                for widget in row:
                    self.layout.remove_widget(widget)
                self.body_row_data.remove(row)

    def update_from_history(self, data):
        for row in self.body_row_data.copy():
            for widget in row:
                self.layout.remove_widget(widget)
            self.body_row_data.remove(row)
        data = data[2].split("|")
        data.remove('')
        index = int(data[0])
        data.pop(0)
        for i in range(index):
            spin_number = MyTextInput(text=str(data[0 + 3 * i]),
                                      halign="center",
                                      size_hint_x=None,
                                      width=Window.size[0] / 8)
            self.layout.add_widget(spin_number)

            spin_time = MyTextInput(text=str(data[1 + 3 * i]),
                                    halign="center",
                                    size_hint_x=None,
                                    width=Window.size[0] / 8)
            self.layout.add_widget(spin_time)

            spin = SpinnerWidget(text=str(data[2 + 3 * i]),
                                 values=self.devices,
                                 size_hint_y=None,
                                 height=Window.height / 20,
                                 size_hint_x=None,
                                 width=Window.size[0] / 3)
            self.layout.add_widget(spin)

            btn_x = Button(text="x",
                           size_hint_y=None,
                           height=Window.height / 20,
                           size_hint_x=None,
                           width=Window.size[0] / 6,
                           on_press=self.remove_row)
            self.layout.add_widget(btn_x)

            label_result = Label(text="- kWh",
                                 size_hint_x=None,
                                 width=Window.size[0] / 6)
            self.layout.add_widget(label_result)

            self.body_row_data.append([spin_number, spin_time, spin, label_result, btn_x])

    def add_new_device(self, instance):
        device_name = self.text_box_1.text
        device_power = self.text_box_2.text
        if device_name and device_power:
            self.devices.append(f"{str(device_name)} {str(device_power)} W")
            for element in self.body_row_data:
                element[2].values = self.devices
            self.popup_new_device.dismiss()
            create_device(connection, (device_name, int(device_power)))
        self.text_box_1.text = ""
        self.text_box_2.text = ""

    def save(self, instance):
        value = 0
        try:
            record = f"{len(self.body_row_data)}|"
            for row in self.body_row_data:
                temp_value = int(row[0].text) * int(row[1].text) * int(row[2].text.split(" ")[1]) / 1000
                row[3].text = str(temp_value) + " kWh"
                value += temp_value
                record += f"{row[0].text}|{row[1].text}|{row[2].text}|"

            cur = connection.cursor()
            cur.execute("SELECT * FROM favourite WHERE name=?", (self.favourite_name.text,))
            data1 = cur.fetchall()

            cur.execute("SELECT * FROM history WHERE data=?", (record,))
            data2 = cur.fetchall()

            if instance == self.btn_save:
                if not data1:
                    create_favourite(connection, (self.favourite_name.text, record))
                else:
                    btn_close = BoxLayout(orientation="horizontal")
                    popup_warning = Popup(title='Favourite already exist!',
                                          content=btn_close,
                                          size_hint=(None, None),
                                          size=(Window.width / 2, Window.height / 8))
                    btn_close.add_widget(Button(text="close", on_press=popup_warning.dismiss))
                    popup_warning.open()

                if not data2:
                    create_history(connection, (datetime.today(), record))
            elif instance == self.btn_print:
                if not data2:
                    create_history(connection, (datetime.today(), record))
        except (ValueError, IndexError):
            btn_close = BoxLayout(orientation="horizontal")
            popup_warning = Popup(title='Incorrect input',
                                  content=btn_close,
                                  size_hint=(None, None),
                                  size=(Window.width / 2, Window.height / 8))
            btn_close.add_widget(Button(text="close", on_press=popup_warning.dismiss))
            popup_warning.open()

        self.label_result.text = str(round(value, 2)) + " kWh"

    def change_view(self, instance):
        if instance == self.btn_change_home:
            screen_manager.current = "home"


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.float_layout = FloatLayout()
        self.button_list = []

        self.btn_change_view_home = Button(text="Menu",
                                           pos_hint={"x": 0, "y": 0.95},
                                           size_hint=(1, 0.05),
                                           on_press=self.change_view)
        self.float_layout.add_widget(self.btn_change_view_home)

        self.layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        root = ScrollView(size_hint=(1, None),
                          size=(Window.width, 0.95 * Window.height-10),
                          pos_hint={"x": 0, "y": 0})
        root.add_widget(self.layout)
        self.float_layout.add_widget(root)
        self.add_widget(self.float_layout)

    def load_history(self, instance=None):
        for row in self.button_list.copy():
            for widget in row:
                self.layout.remove_widget(widget)
            self.button_list.remove(row)

        data_buttons = select_all_history()

        for record in data_buttons[::-1]:

            btn_change_view = Button(text=str(record[1]),
                                     size_hint_y=None,
                                     height=Window.height / 20,
                                     size_hint_x=None,
                                     width=Window.width - 50,
                                     on_press=self.update)
            self.layout.add_widget(btn_change_view)

            btn_change_x = Button(text="X",
                                  size_hint_y=None,
                                  height=Window.height / 20,
                                  size_hint_x=None,
                                  width=40,
                                  on_press=self.remove_history)

            self.layout.add_widget(btn_change_x)

            self.button_list.append([btn_change_view, btn_change_x])

    def remove_history(self, instance):
        for record in self.button_list:
            if instance == record[1]:

                cur = connection.cursor()
                cur.execute("SELECT * FROM history WHERE name=?", (record[0].text,))
                rows = cur.fetchall()
                if rows:
                    history_record = rows[0][0]
                    cur.execute('DELETE FROM history WHERE id=?', (history_record,))
                    connection.commit()
                self.layout.remove_widget(record[0])
                self.layout.remove_widget(record[1])
                self.button_list.remove(record)

    def update(self, instance):
        cur = connection.cursor()
        cur.execute("SELECT * FROM history WHERE name=?", (instance.text,))
        data = cur.fetchall()[0]
        s1 = screen_manager.get_screen('calculation')
        s1.update_from_history(data)
        s1.save(s1.btn_print)
        screen_manager.current = "calculation"

    def change_view(self, instance=None):
        if instance == self.btn_change_view_home:
            screen_manager.current = "home"


class FavouriteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_list = []
        self.float_layout = FloatLayout()

        self.btn_change_view_home = Button(text="Menu",
                                           pos_hint={"x": 0, "y": 0.95},
                                           size_hint=(1, 0.05),
                                           on_press=self.change_view)
        self.float_layout.add_widget(self.btn_change_view_home)

        self.layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        root = ScrollView(size_hint=(1, None),
                          size=(Window.width, 0.95 * Window.height-10),
                          pos_hint={"x": 0, "y": 0})
        root.add_widget(self.layout)
        self.float_layout.add_widget(root)
        self.add_widget(self.float_layout)

    def load_favourite(self, instance=None):
        for row in self.button_list.copy():
            for widget in row:
                self.layout.remove_widget(widget)
            self.button_list.remove(row)

        data_buttons = select_all_favourite()

        for record in data_buttons[::-1]:
            btn_change_view = Button(text=str(record[1]),
                                     size_hint_y=None,
                                     height=Window.height / 20,
                                     size_hint_x=None,
                                     width=Window.width - 50,
                                     on_press=self.update)
            self.layout.add_widget(btn_change_view)

            btn_change_x = Button(text="X",
                                  size_hint_y=None,
                                  height=Window.height / 20,
                                  size_hint_x=None,
                                  width=40,
                                  on_press=self.remove_favourite)

            self.layout.add_widget(btn_change_x)

            self.button_list.append([btn_change_view, btn_change_x])

    def update(self, instance):

        cur = connection.cursor()
        cur.execute("SELECT * FROM favourite WHERE name=?", (instance.text,))
        data = cur.fetchall()[0]

        s1 = screen_manager.get_screen("calculation")
        s1.update_from_history(data)
        s1.save(s1.btn_print)
        s1.favourite_name.text = instance.text
        screen_manager.current = "calculation"

    def remove_favourite(self, instance):
        for record in self.button_list:
            if instance == record[1]:
                cur = connection.cursor()
                cur.execute("SELECT * FROM favourite WHERE name=?", (record[0].text,))
                rows = cur.fetchall()
                if rows:
                    favourite_record = rows[0][0]
                    cur.execute('DELETE FROM favourite WHERE id=?', (favourite_record,))
                    connection.commit()

                self.layout.remove_widget(record[0])
                self.layout.remove_widget(record[1])
                self.button_list.remove(record)

    def change_view(self, instance=None):
        if instance == self.btn_change_view_home:
            screen_manager.current = "home"


screen_manager = ScreenManager(transition=NoTransition())

screen_manager.add_widget(HomeScreen(name='home'))
screen_manager.add_widget(CalculationScreen(name='calculation'))
screen_manager.add_widget(HistoryScreen(name='history'))
screen_manager.add_widget(FavouriteScreen(name='favourite'))


class MyApp(App):
    def build(self):
        return screen_manager


if __name__ == '__main__':
    MyApp().run()
