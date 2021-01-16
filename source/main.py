#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Description of script
"""

# TODO rewrite with pyqt5 and embed browser: https://codeloop.org/python-how-to-make-browser-in-pyqt5-with-pyqtwebengine/

import argparse
import pyperclip
import tkinter as tk
import os
from pathlib import Path
import easyocr
import subprocess
import webbrowser

GIT_REPO_DIR = Path(__file__).absolute().parent.parent

# fmt: off
def comandline_argument_parser(parser=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument("-s","--screenshot", action='store_true', help="Take a screenshot, copy resulting OCR to clipboard and translate")
    return parser
# fmt: on


def clearScreen(frame):
    for widget in frame.winfo_children():
        widget.destroy()


class OCRReader:
    sim_reader = easyocr.Reader(["ch_sim", "en"])
    tra_reader = easyocr.Reader(["ch_tra", "en"])

    reader_modes = {"simplified": sim_reader, "traditional": tra_reader}

    def __init__(self):
        pass

    def read_image(self, file_path, reader="simplified"):
        return "".join(OCRReader.reader_modes[reader].readtext(file_path, detail=0))


class Application(tk.Frame):

    translation_provider_url = {
        "Google": "https://translate.google.com/?hl=de&sl=auto&tl=en&text=TRANSLATETHIS&op=translate",
        "MDBG": "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqtm=0&wdqcham=1&wdqt=TRANSLATETHIS",
        "DeepL": "https://www.deepl.com/translator#zh/de/TRANSLATETHIS%0A",
    }

    def __init__(self, master=None):
        super().__init__(master)
        self.OCR_obj = OCRReader()
        self.master = master
        self.grid()
        self.data_directory = self.create_data_directory("tmp_data")
        self.create_widgets()
        self.current_OCR_text = None

        self.master.bind("q", lambda event: self.master.destroy())
        self.master.bind("s", lambda event: self.take_screenshot())
        self.master.bind("t", lambda event: self.translate())
        self.master.bind("g", lambda event: self.quick_translate())
        self.master.bind("c", lambda event: self.switch_reader())
        self.master.bind("p", lambda event: self.switch_website())

    def create_data_directory(self, directory_name):
        full_dir_name = os.path.join(GIT_REPO_DIR, directory_name)
        os.makedirs(full_dir_name, exist_ok=True)
        return full_dir_name

    def switch_website(self):
        if self.website == "google":
            self.website = "mdbg"
            self.switch_website_button[
                "text"
            ] = "Switch from mdbg to google translation (p)"
        elif self.website == "mdbg":
            self.website = "google"
            self.switch_website_button[
                "text"
            ] = "Switch from google to mdbg translation (p)"
        else:
            print("WARNING: this makes no sense!")

    def switch_reader(self):
        if self.OCR_obj.reader is OCRReader.sim_reader:
            self.OCR_obj.reader = OCRReader.tra_reader
            self.switch_reader_button["text"] = "Switch to simplified Chinese OCR (c)"
        elif self.OCR_obj.reader is OCRReader.tra_reader:
            self.OCR_obj.reader = OCRReader.sim_reader
            self.switch_reader_button["text"] = "Switch to traditional Chinese OCR (c)"
        else:
            print("WARNING: this makes no sense!")

    def update_text(self, text):
        self.Text.delete("1.0", "end")
        self.Text.insert(tk.END, "\n" + text)
        self.Text.tag_add("center", 1.0, "end")
        self.Text.update()

    def take_screenshot(self):
        screenshot_file_path = os.path.join(self.data_directory, "screenshot.png")
        subprocess.call(["import", screenshot_file_path])
        self.current_OCR_text = self.OCR_obj.read_image(
            screenshot_file_path, self.reader_mode.get()
        )
        if self.current_OCR_text:
            pyperclip.copy(self.current_OCR_text)
            self.update_text(self.current_OCR_text)

    def translate(self):
        webbrowser.open(
            Application.translation_provider_url[
                self.translation_provider.get()
            ].replace("TRANSLATETHIS", self.current_OCR_text)
        )

    def quick_translate(self):
        self.take_screenshot()
        self.translate()

    def create_widgets(self):

        self.translation_provider = tk.StringVar(self)
        self.translation_provider.set(
            list(Application.translation_provider_url.keys())[0]
        )
        self.translation_provider_menu = tk.OptionMenu(
            self,
            self.translation_provider,
            *Application.translation_provider_url.keys()
        )
        self.translation_provider_menu.config(font=("Helvetica", 12))
        self.translation_provider_menu.grid()

        self.reader_mode = tk.StringVar(self)
        self.reader_mode.set(list(OCRReader.reader_modes.keys())[0])
        self.reader_mode_menu = tk.OptionMenu(
            self, self.reader_mode, *OCRReader.reader_modes.keys()
        )
        self.reader_mode_menu.config(font=("Helvetica", 12))
        self.reader_mode_menu.grid()

        self.take_screenshot_button = tk.Button(self)
        self.take_screenshot_button["text"] = "Take a Screenshot (s)"
        self.take_screenshot_button["command"] = self.take_screenshot
        self.take_screenshot_button.grid()

        self.translate_button = tk.Button(self)
        self.translate_button["text"] = "Translate (t)"
        self.translate_button["command"] = self.translate
        self.translate_button.grid()

        self.quick_translate_button = tk.Button(self)
        self.quick_translate_button["text"] = "Screenshot & Translate (g)"
        self.quick_translate_button["command"] = self.quick_translate
        self.quick_translate_button.grid()

        # TODO chinese characters are cut of at the top atm
        self.Text = tk.Text(self, font=("Courier", 24), height=10, width=50)
        self.Text.grid()
        self.Text.tag_configure("center", justify="center")
        self.Text.insert(tk.END, "\nNo characters caputred so far!")
        self.Text.tag_add("center", 1.0, "end")

        self.quit = tk.Button(
            self, text="QUIT (q)", fg="red", command=self.master.destroy
        )
        self.quit.grid()


def main(args):
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    parser = comandline_argument_parser()
    command_line_arguments = parser.parse_args()
    main(command_line_arguments)
