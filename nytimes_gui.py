import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import requests

from nytimes_search import get_api_key, search_articles


class NytimesSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("NYTimes Article Search")
        self.geometry("1050x650")
        self.minsize(850, 520)

        self.api_key = get_api_key()
        self.articles = []
        self.selected_url = ""

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.title_var = tk.StringVar(value="Select an article")
        self.date_var = tk.StringVar(value="")
        self.url_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        search_frame = ttk.Frame(self, padding=12)
        search_frame.grid(row=0, column=0, sticky="ew")
        search_frame.columnconfigure(0, weight=1)

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        search_entry.bind("<Return>", lambda _event: self.search())

        search_button = ttk.Button(search_frame, text="Search", command=self.search)
        search_button.grid(row=0, column=1)

        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))

        results_frame = ttk.Frame(main_pane)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        columns = ("date", "headline")
        self.results_table = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.results_table.heading("date", text="Date")
        self.results_table.heading("headline", text="Headline")
        self.results_table.column("date", width=95, minwidth=85, stretch=False)
        self.results_table.column("headline", width=390, minwidth=220, stretch=True)
        self.results_table.grid(row=0, column=0, sticky="nsew")
        self.results_table.bind("<<TreeviewSelect>>", self.show_selected_article)
        self.results_table.bind("<Double-1>", lambda _event: self.open_selected_article())

        scrollbar = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.results_table.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_table.configure(yscrollcommand=scrollbar.set)

        details_frame = ttk.Frame(main_pane, padding=(14, 4, 0, 0))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(3, weight=1)

        title_label = ttk.Label(
            details_frame,
            textvariable=self.title_var,
            font=("Segoe UI", 16, "bold"),
            wraplength=460,
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        date_label = ttk.Label(details_frame, textvariable=self.date_var)
        date_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.snippet_text = tk.Text(
            details_frame,
            height=8,
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        self.snippet_text.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.snippet_text.configure(state="disabled")

        url_frame = ttk.Frame(details_frame)
        url_frame.grid(row=3, column=0, sticky="nsew")
        url_frame.columnconfigure(0, weight=1)

        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, state="readonly")
        url_entry.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        buttons_frame = ttk.Frame(url_frame)
        buttons_frame.grid(row=1, column=0, sticky="w")

        open_button = ttk.Button(
            buttons_frame,
            text="Open in browser",
            command=self.open_selected_article,
        )
        open_button.grid(row=0, column=0, padx=(0, 8))

        copy_button = ttk.Button(
            buttons_frame,
            text="Copy link",
            command=self.copy_selected_url,
        )
        copy_button.grid(row=0, column=1)

        main_pane.add(results_frame, weight=3)
        main_pane.add(details_frame, weight=2)

        status_bar = ttk.Label(self, textvariable=self.status_var, padding=(12, 0, 12, 8))
        status_bar.grid(row=2, column=0, sticky="ew")

        search_entry.focus()

    def search(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showinfo("Search term required", "Type a search term first.")
            return

        self.status_var.set("Searching...")
        self._clear_results()

        thread = threading.Thread(
            target=self._search_in_background,
            args=(search_term,),
            daemon=True,
        )
        thread.start()

    def _search_in_background(self, search_term):
        try:
            search_results = search_articles(search_term, self.api_key)
            articles = search_results.get("response", {}).get("docs", [])
        except requests.RequestException as error:
            self.after(0, lambda: self._show_error(error))
            return

        self.after(0, lambda: self._show_results(articles))

    def _show_results(self, articles):
        self.articles = articles

        for index, article in enumerate(articles):
            headline = article.get("headline", {}).get("main", "Untitled")
            pub_date = article.get("pub_date", "")[:10]
            self.results_table.insert("", "end", iid=str(index), values=(pub_date, headline))

        if articles:
            self.results_table.selection_set("0")
            self.results_table.focus("0")
            self.show_selected_article()
            self.status_var.set(f"Found {len(articles)} articles.")
        else:
            self.status_var.set("No articles found.")

    def show_selected_article(self, _event=None):
        selection = self.results_table.selection()
        if not selection:
            return

        article = self.articles[int(selection[0])]
        headline = article.get("headline", {}).get("main", "Untitled")
        pub_date = article.get("pub_date", "")[:10]
        source = article.get("source", "")
        section = article.get("section_name", "")
        snippet = article.get("abstract") or article.get("snippet") or "No summary available."
        web_url = article.get("web_url", "")

        meta_parts = [part for part in (pub_date, source, section) if part]
        self.selected_url = web_url
        self.title_var.set(headline)
        self.date_var.set(" | ".join(meta_parts))
        self.url_var.set(web_url)
        self._set_snippet(snippet)

    def open_selected_article(self):
        if not self.selected_url:
            messagebox.showinfo("No article selected", "Select an article first.")
            return

        webbrowser.open_new_tab(self.selected_url)
        self.status_var.set("Opened article in browser.")

    def copy_selected_url(self):
        if not self.selected_url:
            messagebox.showinfo("No article selected", "Select an article first.")
            return

        self.clipboard_clear()
        self.clipboard_append(self.selected_url)
        self.status_var.set("Link copied.")

    def _clear_results(self):
        self.articles = []
        self.selected_url = ""
        self.title_var.set("Select an article")
        self.date_var.set("")
        self.url_var.set("")
        self._set_snippet("")

        for item_id in self.results_table.get_children():
            self.results_table.delete(item_id)

    def _set_snippet(self, text):
        self.snippet_text.configure(state="normal")
        self.snippet_text.delete("1.0", tk.END)
        self.snippet_text.insert("1.0", text)
        self.snippet_text.configure(state="disabled")

    def _show_error(self, error):
        self.status_var.set("Search failed.")
        messagebox.showerror("Search failed", str(error))


if __name__ == "__main__":
    app = NytimesSearchApp()
    app.mainloop()
