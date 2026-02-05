"""
PDF Splitter - Android/Kivy Mobile Application
Split PDFs by chapters or custom page ranges
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.switch import Switch
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle
import fitz  # PyMuPDF

Window.size = (1080, 1920)

class PDFSplitterApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.97, 1)
        return MainScreen()

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(15)
        self.pdf_path = None
        self.chapters = []
        
        # Title
        title = Label(
            text='[b]PDF Splitter[/b]\nSplit by Chapters or Custom Ranges',
            markup=True,
            size_hint_y=None,
            height=dp(80),
            font_size=sp(24),
            color=(0.1, 0.3, 0.8, 1)
        )
        self.add_widget(title)
        
        # File Selection
        file_btn = Button(
            text='Select PDF File',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        file_btn.bind(on_press=self.show_file_chooser)
        self.add_widget(file_btn)
        
        # PDF Info
        self.pdf_info = Label(
            text='No PDF selected',
            size_hint_y=None,
            height=dp(50),
            color=(0.3, 0.3, 0.3, 1),
            font_size=sp(14)
        )
        self.add_widget(self.pdf_info)
        
        # Tabs/Actions
        actions_layout = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(50))
        
        auto_detect_btn = Button(
            text='Auto Detect',
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        auto_detect_btn.bind(on_press=self.auto_detect_chapters)
        actions_layout.add_widget(auto_detect_btn)
        
        equal_split_btn = Button(
            text='Equal Split',
            background_color=(0.8, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        equal_split_btn.bind(on_press=self.show_equal_split)
        actions_layout.add_widget(equal_split_btn)
        
        manual_btn = Button(
            text='Manual Ranges',
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        manual_btn.bind(on_press=self.show_manual_ranges)
        actions_layout.add_widget(manual_btn)
        
        self.add_widget(actions_layout)
        
        # Chapters List
        scroll = ScrollView(size_hint=(1, 1))
        self.chapters_grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            height=0
        )
        self.chapters_grid.bind(minimum_height=self.chapters_grid.setter('height'))
        scroll.add_widget(self.chapters_grid)
        self.add_widget(scroll)
        
        # Split Button
        split_btn = Button(
            text='Split PDF',
            size_hint_y=None,
            height=dp(60),
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        split_btn.bind(on_press=self.split_pdf)
        self.add_widget(split_btn)
    
    def show_file_chooser(self, instance):
        """Show file chooser to select PDF"""
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['*.pdf'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Select PDF', content=content, size_hint=(0.9, 0.9))
        
        def select_pdf(instance):
            if filechooser.selection:
                self.pdf_path = filechooser.selection[0]
                self.load_pdf()
                popup.dismiss()
        
        select_btn.bind(on_press=select_pdf)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def load_pdf(self):
        """Load PDF and extract metadata"""
        if not self.pdf_path:
            return
        
        try:
            doc = fitz.open(self.pdf_path)
            num_pages = doc.page_count
            filename = self.pdf_path.split('/')[-1]
            
            self.pdf_info.text = f'[b]{filename}[/b]\nPages: {num_pages}'
            self.chapters = []
            self.refresh_chapters()
            
            doc.close()
        except Exception as e:
            self.pdf_info.text = f'Error: {str(e)}'
    
    def auto_detect_chapters(self, instance):
        """Auto-detect chapters from PDF bookmarks"""
        if not self.pdf_path:
            return
        
        try:
            doc = fitz.open(self.pdf_path)
            toc = doc.get_toc()
            
            self.chapters = []
            for i, item in enumerate(toc):
                level, title, page = item
                self.chapters.append({
                    'title': title,
                    'start': page - 1,
                    'end': page - 1
                })
            
            # Adjust end pages
            for i in range(len(self.chapters) - 1):
                self.chapters[i]['end'] = self.chapters[i + 1]['start'] - 1
            
            if self.chapters:
                self.chapters[-1]['end'] = doc.page_count - 1
            
            self.refresh_chapters()
            doc.close()
        except Exception as e:
            self.pdf_info.text = f'[color=ff0000]Error: {str(e)}[/color]'
    
    def show_equal_split(self, instance):
        """Show equal split dialog"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        label = Label(text='Number of parts:', size_hint_y=0.2)
        content.add_widget(label)
        
        spinner = Spinner(
            text='2',
            values=tuple(str(i) for i in range(2, 21)),
            size_hint_y=0.3
        )
        content.add_widget(spinner)
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=dp(10))
        apply_btn = Button(text='Apply')
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(apply_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Equal Split', content=content, size_hint=(0.9, 0.5))
        
        def apply_split(instance):
            try:
                num_parts = int(spinner.text)
                doc = fitz.open(self.pdf_path)
                pages_per_part = doc.page_count // num_parts
                
                self.chapters = []
                for i in range(num_parts):
                    start = i * pages_per_part
                    end = (i + 1) * pages_per_part - 1 if i < num_parts - 1 else doc.page_count - 1
                    self.chapters.append({
                        'title': f'Part {i + 1}',
                        'start': start,
                        'end': end
                    })
                
                self.refresh_chapters()
                doc.close()
                popup.dismiss()
            except Exception as e:
                pass
        
        apply_btn.bind(on_press=apply_split)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_manual_ranges(self, instance):
        """Show manual page ranges dialog"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        label = Label(text='Chapter Name', size_hint_y=0.15)
        content.add_widget(label)
        
        name_input = TextInput(
            multiline=False,
            hint_text='Chapter Title',
            size_hint_y=0.15
        )
        content.add_widget(name_input)
        
        range_label = Label(text='Start - End Pages', size_hint_y=0.15)
        content.add_widget(range_label)
        
        range_input = TextInput(
            multiline=False,
            hint_text='e.g., 1-10',
            size_hint_y=0.15
        )
        content.add_widget(range_input)
        
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=dp(10))
        add_btn = Button(text='Add')
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Manual Range', content=content, size_hint=(0.9, 0.6))
        
        def add_chapter(instance):
            try:
                title = name_input.text or 'Untitled'
                parts = range_input.text.split('-')
                start = int(parts[0].strip()) - 1
                end = int(parts[1].strip()) - 1
                
                self.chapters.append({
                    'title': title,
                    'start': start,
                    'end': end
                })
                
                self.refresh_chapters()
                popup.dismiss()
            except Exception as e:
                pass
        
        add_btn.bind(on_press=add_chapter)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def refresh_chapters(self):
        """Refresh the chapters display"""
        self.chapters_grid.clear_widgets()
        
        for i, chapter in enumerate(self.chapters):
            chapter_widget = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10)
            )
            
            with chapter_widget.canvas.before:
                Color(0.95, 0.95, 0.97, 1)
                Rectangle(size=chapter_widget.size, pos=chapter_widget.pos)
            
            info = Label(
                text=f"[b]{chapter['title']}[/b]\nPages {chapter['start']+1}-{chapter['end']+1}",
                markup=True,
                size_hint_x=0.7
            )
            chapter_widget.add_widget(info)
            
            delete_btn = Button(text='Delete', size_hint_x=0.3)
            delete_btn.bind(on_press=lambda x, idx=i: self.delete_chapter(idx))
            chapter_widget.add_widget(delete_btn)
            
            self.chapters_grid.add_widget(chapter_widget)
    
    def delete_chapter(self, index):
        """Delete a chapter"""
        if 0 <= index < len(self.chapters):
            self.chapters.pop(index)
            self.refresh_chapters()
    
    def split_pdf(self, instance):
        """Split the PDF according to chapters"""
        if not self.pdf_path or not self.chapters:
            self.pdf_info.text = '[color=ff0000]Select PDF and configure chapters first[/color]'
            return
        
        try:
            doc = fitz.open(self.pdf_path)
            output_dir = '/sdcard/DCIM/PDFSplitter'
            
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            for i, chapter in enumerate(self.chapters):
                pdf_writer = fitz.open()
                
                for page_num in range(chapter['start'], min(chapter['end'] + 1, doc.page_count)):
                    pdf_writer.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # Sanitize filename
                filename = chapter['title'].replace('/', '_').replace('\\', '_')
                output_path = f'{output_dir}/{i+1:02d}_{filename}.pdf'
                pdf_writer.save(output_path)
                pdf_writer.close()
            
            self.pdf_info.text = f'[color=00ff00]Success! {len(self.chapters)} files created[/color]'
            doc.close()
        except Exception as e:
            self.pdf_info.text = f'[color=ff0000]Error: {str(e)}[/color]'

if __name__ == '__main__':
    PDFSplitterApp().run()
