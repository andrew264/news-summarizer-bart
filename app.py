import tkinter
import typing
from multiprocessing import Process, Queue

import customtkinter
from PIL import ImageTk

from fetch import fetch_news
from select_window import SelectWindow

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
START = "1.0"
END = "end"
FONT = ("Comic Sans MS", 20)


class SearchWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("News Summary")
        self.iconphoto(True, ImageTk.PhotoImage(file="icon.png"))
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(background="black")
        self._create_ui()

    def _create_ui(self):

        self.search_label = customtkinter.CTkLabel(self, text="Search", width=320, height=40,
                                                   font=FONT)
        self.search_label.place(relx=0.55, rely=0.1, anchor=tkinter.NE)

        self.search_box = customtkinter.CTkTextbox(self, width=320, height=40,
                                                   activate_scrollbars=False, font=FONT)
        self.search_box.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
        self.search_box.focus_set()
        self.search_box.bind("<Return>", self.fetch_results)

        self.drop_down_label = customtkinter.CTkLabel(self, text="Category", width=320, height=40,
                                                      font=FONT)
        self.drop_down_label.place(relx=0.55, rely=0.3, anchor=tkinter.NE)
        self.drop_down = customtkinter.CTkComboBox(self, width=320, height=40, font=FONT,
                                                   values=["ALL", "Business", "Entertainment", "General",
                                                           "Health", "Science", "Sports", "Technology"])
        self.drop_down.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)

        self.search_button = customtkinter.CTkButton(self, text="Search", width=320, height=40,
                                                     font=FONT, command=self.fetch_results)
        self.search_button.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

        self.progress_bar = customtkinter.CTkProgressBar(self, width=720, height=8,
                                                         mode="indeterminate",
                                                         indeterminate_speed=1)

    @property
    def category(self) -> typing.Optional[str]:
        return None if self.drop_down.get() == "ALL" else self.drop_down.get().lower()

    @property
    def search_term(self) -> typing.Optional[str]:
        parsed_str = self.search_box.get(START, END).strip()
        self.search_box.delete(START, END)
        return parsed_str if parsed_str != "" else None

    def fetch_results(self):
        self.progress_bar.place(relx=0.5, rely=0.8, anchor=tkinter.S)
        self.progress_bar.start()
        queue = Queue()
        process = Process(target=fetch_news, args=(self.search_term, self.category, queue))
        process.start()
        while process.is_alive():
            self.update()
        results = queue.get()
        self.progress_bar.stop()
        self.progress_bar.place_forget()
        process.join()
        del queue, process
        next_window = SelectWindow(self)
        next_window.insert_articles(results)
        for result in results:
            print(result)
        self.withdraw()


if __name__ == "__main__":
    app = SearchWindow()
    app.mainloop()
