"""
MIT License

Copyright (c) 2021-present BobDotCom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
try:
    from kivy.lang import Builder
except ImportError:
    pass  # Kivy is not installed. Doesn't matter though since we don't use it.

def prep():
    from kivy.app import App
    from kivy.uix.widget import Widget
    from kivy.properties import ObjectProperty

    class Grid(Widget):
        name = ObjectProperty(None)
        email = ObjectProperty(None)

        def btn(self):
            print("Name:", self.name.text, "email:", self.email.text)
            self.name.text = ""
            self.email.text = ""

    class McLauncher(App):
        def build(self):
            Builder.load_string("""
<Grid>:

    name: name
    email: email

    GridLayout:
        cols:1
        size: root.width - 200, root.height -200
        pos: 100, 100

        GridLayout:
            cols:2

            Label:
                text: "Name: "

            TextInput:
                id: name
                multiline:False

            Label:
                text: "Email: "

            TextInput:
                id: email
                multiline:False

        Button:
            text:"Submit"
            on_press: root.btn()""")
            return Grid()

    return McLauncher
