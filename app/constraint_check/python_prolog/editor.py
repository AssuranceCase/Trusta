from tkinter import Tk, Text, Menu, filedialog, Label, Button, END, W, E, FALSE
from tkinter.scrolledtext import ScrolledText
from prologpy.solver import Solver


def is_file_path_selected(file_path):
    return file_path is not None and file_path != ""


def get_file_contents(file_path):
    with open(file_path, encoding="utf-8") as f:
        file_contents = f.read()

    return file_contents


class Editor(object):
    def __init__(self, root_):

        self.root = root_
        self.file_path = None
        self.root.title("Prolog Interpreter")

        self.rule_editor_label = Label(
            self.root, text="Prolog Rules: ", padx=10, pady=1
        )

        self.rule_editor_label.grid(
            sticky="W", row=0, column=0, columnspan=2, pady=3
        )

        self.rule_editor = ScrolledText(
            self.root, width=100, height=30, padx=10, pady=10
        )

        self.rule_editor.grid(
            sticky=W + E, row=1, column=0, columnspan=2, padx=10
        )

        self.rule_editor.config(wrap="word", undo=True)

        self.rule_editor.focus()

        self.query_label = Label(self.root, text="Prolog Query:", padx=10, pady=1)

        self.query_label.grid(sticky=W, row=2, column=0, columnspan=2, pady=3)

        self.query_editor = Text(self.root, width=77, height=2, padx=10, pady=10)

        self.query_editor.grid(sticky=W, row=3, column=0, pady=3, padx=10)

        self.query_editor.config(wrap="word", undo=True)

        self.run_button = Button(
            self.root,
            text="Find Query Solutions",
            height=2,
            width=20,
            command=self.run_query,
        )

        self.run_button.grid(sticky=E, row=3, column=1, pady=3, padx=10)

        self.solutions_label = Label(
            self.root, text="Query Solutions:", padx=10, pady=1
        )

        self.solutions_label.grid(
            sticky="W", row=4, column=0, columnspan=2, padx=10, pady=3
        )

        self.solutions_display = ScrolledText(
            self.root, width=100, height=5, padx=10, pady=10
        )

        self.solutions_display.grid(
            row=5, column=0, columnspan=2, padx=10, pady=7
        )

        self.menu_bar = self.create_file_menu()

    def create_file_menu(self):

        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)

        file_menu.add_command(
            label="Open...", underline=1, command=self.open_file
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save", underline=1, command=self.save_file
        )
        file_menu.add_command(
            label="Save As...", underline=5, command=self.save_file_as
        )
        file_menu.add_separator()
        file_menu.add_command(label="Run", underline=1, command=self.run_query)
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit", underline=2, command=self.root.destroy
        )

        menu_bar.add_cascade(label="File", underline=0, menu=file_menu)

        self.root.config(menu=menu_bar)
        return menu_bar

    def set_busy(self):
        self.root.config(cursor="watch")
        self.root.update()

    def set_not_busy(self):
        self.root.config(cursor="")

    def run_query(self):
        self.solutions_display.delete("1.0", END)

        self.set_busy()

        rules_text = self.rule_editor.get(1.0, "end-1c")
        query_text = self.query_editor.get(1.0, "end-1c")

        try:
            solver = Solver(rules_text)
        except Exception as e:
            self.handle_exception("Error processing prolog rules.", str(e))
            return

        try:
            solutions = solver.find_solutions(query_text)
        except Exception as e:
            self.handle_exception("Error processing prolog query.", str(e))
            return

        if isinstance(solutions, bool):
            self.solutions_display.insert(END, "Yes." if solutions else "No.")

        elif isinstance(solutions, dict):
            self.solutions_display.insert(
                END,
                "\n".join(
                    "{} = {}"
                    .format(variable, value[0] if len(value) == 1 else value)
                    for variable, value in solutions.items()
                ),
            )
        else:

            self.solutions_display.insert(END, "No solutions found.")

        self.set_not_busy()

    def handle_exception(self, error_message, exception=""):
        self.solutions_display.insert(END, error_message + "\n")
        self.solutions_display.insert(END, str(exception) + "\n")
        self.set_not_busy()

    def set_rule_editor_text(self, text):
        self.rule_editor.delete(1.0, "end")
        self.rule_editor.insert(1.0, text)
        self.rule_editor.edit_modified(False)

    def set_query_editor_text(self, text):
        self.query_editor.delete(1.0, "end")
        self.query_editor.insert(1.0, text)
        self.query_editor.edit_modified(False)

    def set_solutions_display_text(self, text):
        self.solutions_display.delete(1.0, "end")
        self.solutions_display.insert(1.0, text)
        self.solutions_display.edit_modified(False)

    def open_file(self, file_path=None):

        if file_path is None:
            file_path = filedialog.askopenfilename()

        if is_file_path_selected(file_path):
            file_contents = get_file_contents(file_path)

            self.set_rule_editor_text(file_contents)
            self.file_path = file_path

    def save_file(self):
        if self.file_path is None:
            result = self.save_file_as()
        else:
            result = self.save_file_as(file_path=self.file_path)

        return result

    def write_editor_text_to_file(self, file):
        editor_text = self.rule_editor.get(1.0, "end-1c")
        file.write(bytes(editor_text, "UTF-8"))
        self.rule_editor.edit_modified(False)

    def save_file_as(self, file_path=None):
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                filetypes=(
                    ("Text files", "*.txt"),
                    ("Prolog files", "*.pl *.pro"),
                    ("All files", "*.*"),
                )
            )

        try:

            with open(file_path, "wb") as file:
                self.write_editor_text_to_file(file)
                self.file_path = file_path
                return "saved"

        except FileNotFoundError:
            return "cancelled"

    def undo(self):
        self.rule_editor.edit_undo()

    def redo(self):
        self.rule_editor.edit_redo()

def main(prolog_data, top_claim, state_info):
    root = Tk()
    editor = Editor(root)
    editor.set_rule_editor_text(prolog_data)
    editor.set_query_editor_text(top_claim)
    editor.set_solutions_display_text(str(state_info))

    root.resizable(width=FALSE, height=FALSE)
    root.mainloop()

if __name__ == "__main__":

    root = Tk()
    editor = Editor(root)

    root.resizable(width=FALSE, height=FALSE)

    root.mainloop()
