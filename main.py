import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import requests
import json

kivy.require('2.0.0')

VPS_IP = "presentr.ai"  # Replace this with your actual VPS IP or domain


class ConfigViewer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.categories = ['surgical', 'shadesail']
        self.config_data = {cat: [] for cat in self.categories}
        self.columns = {}

        # Refresh button at top
        top_bar = BoxLayout(size_hint_y=None, height=50)
        refresh_btn = Button(text="Refresh Configs")
        refresh_btn.bind(on_release=lambda btn: self.refresh_configs())
        top_bar.add_widget(refresh_btn)
        self.add_widget(top_bar)

        # Container for both category columns
        self.column_container = BoxLayout(orientation='horizontal')
        self.add_widget(self.column_container)

        # Trigger initial load
        Clock.schedule_once(lambda dt: self.refresh_configs(), 0.1)

    def refresh_configs(self):
        for category in self.categories:
            try:
                url = f"http://{VPS_IP}/copelands/list_configs/{category}"
                response = requests.get(url)
                response.raise_for_status()
                self.config_data[category] = response.json()
            except Exception as e:
                self.config_data[category] = [f"Error loading: {e}"]

        self.build_columns()

    def build_columns(self):
        self.column_container.clear_widgets()

        for category in self.categories:
            column = BoxLayout(orientation='vertical', size_hint_x=0.5)
            column.add_widget(Label(text=category.capitalize(), size_hint_y=None, height=40))

            scroll = self.create_scroll_view(category)
            column.add_widget(scroll)

            self.columns[category] = column
            self.column_container.add_widget(column)

    def create_scroll_view(self, category):
        layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for item in self.config_data[category]:
            btn = Button(text=item, size_hint_y=None, height=40)
            btn.bind(on_release=lambda b, name=item, cat=category: self.open_draw_popup(cat, name))
            layout.add_widget(btn)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(layout)
        return scroll

    def open_draw_popup(self, category, config_name):
        try:
            url = f"http://{VPS_IP}/copelands/get_config/{category}/{config_name}"
            response = requests.get(url)
            response.raise_for_status()
            config_data = response.json()
            config_text = json.dumps(config_data, indent=2)
        except Exception as e:
            config_text = f"Error loading config: {e}"

        content = BoxLayout(orientation='vertical')
        text_area = TextInput(text=config_text, readonly=True, size_hint_y=0.8)
        draw_button = Button(text="Draw", size_hint_y=0.2)
        draw_button.bind(on_release=lambda btn: self.draw(config_name))

        content.add_widget(text_area)
        content.add_widget(draw_button)

        popup = Popup(
            title=f"{config_name}",
            content=content,
            size_hint=(0.7, 0.7)
        )
        popup.open()

    def draw(self, config_name):
        print(f"Drawing: {config_name}")  # placeholder


class ConfigApp(App):
    def build(self):
        return ConfigViewer()


if __name__ == '__main__':
    ConfigApp().run()
