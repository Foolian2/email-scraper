import flet as ft
import re
import requests
import threading
from queue import Queue
from googlesearch import search
import time

RESULT_COUNT = 100
TIMEOUT = 5

class emailscraper:
    def __init__(self):
        self.emails_seen = set()
        self.url_queue = Queue()
        self.file_lock = threading.Lock()
        self.is_running = False
        self.total_emails = 0

    def main(self, page: ft.Page):
        page.title = "Email Scraper"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 30
        page.bgcolor = "#1a1a1a"

        self.status_text = ft.Text(
            "Ready to start",
            color="#4CAF50",
            size=16,
            weight=ft.FontWeight.BOLD
        )
        
        self.progress_bar = ft.ProgressBar(
            width=400,
            color="green",
            bgcolor="#333333",
            visible=False
        )

        self.domain_input = ft.TextField(
            label="Domain Extension",
            hint_text="e.g., .ch, .fr, .com",
            width=400,
            border_color="#333333",
            focused_border_color="#4CAF50",
            prefix_icon=ft.icons.DOMAIN
        )

        self.results_text = ft.Text(
            "",
            color="#ffffff",
            size=14,
            selectable=True
        )

        self.start_button = ft.ElevatedButton(
            "Start Scraping",
            icon=ft.icons.SEARCH,
            on_click=self.start_scraping,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#4CAF50",
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )

        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Email Scraper",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color="#4CAF50"
                        ),
                        self.domain_input,
                        self.start_button,
                        self.status_text,
                        self.progress_bar,
                        self.results_text
                    ],
                    spacing=20
                ),
                padding=20,
                border_radius=10,
                bgcolor="#2d2d2d"
            )
        )

    def process_url(self):
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        
        while not self.url_queue.empty() and self.is_running:
            url = self.url_queue.get()
            try:
                self.update_status(f"Fetching: {url}")
                response = requests.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                
                emails = set(re.findall(email_pattern, response.text)) - self.emails_seen
                
                if emails:
                    with self.file_lock:
                        with open(self.output_file, "a") as f:
                            for email in emails:
                                f.write(email + "\n")
                                self.emails_seen.add(email)
                        
                        self.total_emails += len(emails)
                        self.update_results(f"Total emails found: {self.total_emails}")
                
            except requests.exceptions.RequestException:
                self.update_status(f"Skipping {url} (timeout or error)")
            finally:
                self.url_queue.task_done()

    def remove_duplicates(self):
        self.update_status("🔄 Removing duplicates from output file...")
        
        try:
            with open(self.output_file, 'r') as f:
                emails = f.readlines()
            
            unique_emails = []
            seen = set()
            for email in emails:
                email = email.strip()
                if email not in seen:
                    seen.add(email)
                    unique_emails.append(email)
            
            with open(self.output_file, 'w') as f:
                for email in unique_emails:
                    f.write(email + '\n')
            
            duplicates_removed = len(emails) - len(unique_emails)
            self.update_status(f"✅ Removed {duplicates_removed} duplicate emails. Final count: {len(unique_emails)}")
            self.update_results(f"Final unique emails: {len(unique_emails)}")
            
        except Exception as e:
            self.update_status(f"Error removing duplicates: {str(e)}")

    def update_status(self, message):
        self.status_text.value = message
        self.status_text.update()

    def update_results(self, message):
        self.results_text.value = message
        self.results_text.update()

    def start_scraping(self, e):
        if not self.domain_input.value:
            self.update_status("Please enter a domain extension")
            return

        if self.is_running:
            return

        self.is_running = True
        self.total_emails = 0
        self.emails_seen.clear()
        
        domain_extension = self.domain_input.value.strip()
        self.output_file = f"email{domain_extension}.txt"
        
        self.start_button.disabled = True
        self.progress_bar.visible = True
        self.start_button.update()
        self.progress_bar.update()
        
        def scrape_thread():
            query = f'intext:@*yahoo|gmail|hotmail".com filetype:txt site:{domain_extension}'
            
            try:
                self.update_status("🔍 Searching Google...")
                for url in search(query, num_results=RESULT_COUNT):
                    if not self.is_running:
                        break
                    self.url_queue.put(url)

                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=self.process_url)
                    thread.start()
                    threads.append(thread)

                for thread in threads:
                    thread.join()

                self.remove_duplicates()
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
            
            finally:
                self.is_running = False
                self.start_button.disabled = False
                self.progress_bar.visible = False
                self.start_button.update()
                self.progress_bar.update()

        threading.Thread(target=scrape_thread).start()

if __name__ == "__main__":
    app = emailscraper()
    ft.app(target=app.main)