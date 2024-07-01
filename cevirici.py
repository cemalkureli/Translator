import datetime
import pygame
from datetime import datetime, timedelta
import pyttsx3
import tkinter as tk
import customtkinter as ctk
from customtkinter import *
from tkinter import messagebox
import speech_recognition as sr
from googletrans import Translator
import threading
import time

translator = Translator()
recognizer = sr.Recognizer()
tts = pyttsx3.init()

recording = False
audio_data = None
listening_thread = None
stop_event = threading.Event()


def resource_path(relative_path):
   # PyInstaller ile paketlenmiş olduğunda, dosyaları doğru şekilde bulmak için 
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def start_listening():
    global recording, audio_data, stop_event  
    recording = True  # recording değişkenini True yaparak kaydın başladığını belirtir
    listen_button.configure(text="Stop   | | " , font=("Times New Roman", 20, "italic", "bold")) 

    app.update()  # GUI'yi günceller

    stop_event.clear()  # stop_event olayını temizler, yani sıfırlar

    try:
        with sr.Microphone() as source:  # Mikrofonu kaynak olarak kullanmak için açar
            recognizer.adjust_for_ambient_noise(source)  # Çevresel gürültüye göre mikrofonu ayarlar
            while not stop_event.is_set():  # stop_event tetiklenmedikçe devam eder
                audio_data = recognizer.listen(source, phrase_time_limit=20)  # Mikrofonu dinler ve 20 saniyelik ses kaydeder
                break  # Kaydı tamamladıktan sonra döngüden çıkar
    except sr.WaitTimeoutError:  # Zaman aşımı hatası olursa
        text_box.insert(tk.END, "Listening timed out, please try again...\n")  
    except Exception as e:  # Diğer herhangi bir hata olursa
        text_box.insert(tk.END, f"Error during listening: {e}\n")  

    recording = False  # Kaydın bittiğini belirtmek için recording değişkenini False yapar
    listen_button.configure(text="Speak ▶️" , font=("Times New Roman", 20, "italic", "bold"))  
    app.update()  # GUI'yi günceller

    translate_audio()  # Kaydedilen sesi çevirmek için translate_audio fonksiyonunu çağırır

# Dil seçenekleri
language_options = {
    1: "English",
    2: "Turkish",
    3: "Korean",
    4: "Chinese",
    5: "Japanese",
    6: "Russian",
    7: "German",
    8: "French",
    9: "Italian",
    10: "Spanish",
    11: "Portuguese",
    12: "Arabic"
}

# Ses tanıma ve çeviri fonksiyonu
def translate_audio():
    global audio_data
    try:
        # Kullanıcının seçtiği dili al
        selected_lang = selected_language.get()

        # Hedef dil kodunu al
        dest_lang = language_map.get(selected_lang)

        # Dil seçilmemişse uyarı ver
        if not dest_lang:
            text_box.insert(tk.END, "\nNo language selected. Please select a language to translate.\n")
            return

        if audio_data:
            # Ses tanıma (Türkçe)
            turkish_text = recognizer.recognize_google(audio_data, language="tr-TR")
            text_box.insert(tk.END, f"\nTurkish Text: {turkish_text}\n", "white_text")

            # Seçilen dile çevir
            translated_text = translator.translate(turkish_text, src='tr', dest=dest_lang).text
            text_box.insert(tk.END, f"Translated Text: {translated_text}\n", "default_text")


        else:
            text_box.insert(tk.END, "\nNo audio data to translate.\n")
    except sr.UnknownValueError:
        text_box.insert(tk.END, "\nCould not understand the audio, please try again...\n")
    except sr.RequestError as e:
        text_box.insert(tk.END, f"\nAPI error: {e}\n")
    except Exception as e:
        text_box.insert(tk.END, f"\nError: {e}\n")

def listen_and_translate():
    global listening_thread, recording, stop_event
    if not recording:
        stop_event.clear()
        listening_thread = threading.Thread(target=start_listening)
        listening_thread.start()
    else:
        stop_event.set()
        
# Dil haritası
language_map = {
    "Selected Language to Translate Into: English": "en",
    "Selected Language to Translate Into: Turkish": "tr",
    "Selected Language to Translate Into: Korean": "ko",
    "Selected Language to Translate Into: Chinese": "zh-CN",
    "Selected Language to Translate Into: Japanese": "ja",
    "Selected Language to Translate Into: Russian": "ru",
    "Selected Language to Translate Into: German": "de",
    "Selected Language to Translate Into: French": "fr",
    "Selected Language to Translate Into: Italian": "it",
    "Selected Language to Translate Into: Spanish": "es",
    "Selected Language to Translate Into: Portuguese": "pt",
    "Selected Language to Translate Into: Arabic": "ar"
}

def add_prefix_to_values(values, prefix):
    # Her bir değerin başına belirtilen önek eklenir
    return [f"{prefix}: {value}" for value in values]

def clear_text():
    text_box.delete(1.0, tk.END)

def increase_font_size():
    # Mevcut font boyutunu al
    current_font_size = font_size_slider.get()
    # Maksimum boyutu aşmadığı sürece
    if current_font_size < 60:  
        # Mevcut boyuta 2 ekleyerek yeni font boyutunu ayarla
        font_size_slider.set(current_font_size + 2)
        # Yeni font boyutunu set_font_size fonksiyonuna geçirerek metin kutusunu güncelle
        set_font_size(current_font_size + 2)

def decrease_font_size():
    # Mevcut font boyutunu al
    current_font_size = font_size_slider.get()
    # Minimum boyutu aşmadığı sürece
    if current_font_size > 20:  
        # Mevcut boyuttan 2 çıkararak yeni font boyutunu ayarla
        font_size_slider.set(current_font_size - 2)
        # Yeni font boyutunu set_font_size fonksiyonuna geçirerek metin kutusunu güncelle
        set_font_size(current_font_size - 2)

def set_font_size(value):
    text_box.configure(font=("Times New Roman", value, "italic"))  

# Global değişkenler
info_window_open = False  # Info penceresinin açık olup olmadığını kontrol eden değişken
info_window = None  # Info penceresi penceresini tutan değişken

# Global variables
info_window_open = False  # Kontrol penceresinin açık olup olmadığını tutan değişken
info_window = None  # Info penceresi penceresini tutan değişken

def show_custom_info_message():
    global info_window_open, info_window
    
    # Eğer info penceresi zaten açıksa işlem yapma
    if info_window_open:
        info_window.lift()  # Pencereyi en öne getir
        info_window.attributes("-topmost", True)  # Pencerenin her zaman en önde olmasını sağla
        return
    
    title = "Information"
    message = "Copyright ©2024 Turkey, C.K. Ltd. All rights reserved."
    
    # Yeni bir Toplevel penceresi oluştur
    custom_box = tk.Toplevel()
    custom_box.config(bg="black")
    custom_box.title(title)
    custom_box.resizable(False, False)  # Pencerenin boyutunu değiştirilemez yap
    
    # Pencereyi ekranın ortasına yerleştir
    custom_box.geometry("+{}+{}".format(640, 480))
    
    # Başlık çubuğunu gizle
    custom_box.overrideredirect(True)
    
    # Pencerenin köşelerini beyaz renkli çerçeve ile belirt
    custom_box.config(highlightbackground="white", highlightthickness=2)
    
    # Bilgi mesajını gösterecek etiket oluştur
    label = tk.Label(custom_box, text=message, bg="black", fg="white", font=("Times New Roman", 15, "bold", "italic"))
    label.pack(padx=20, pady=10)
    
    # Onay butonu oluştur
    ok_button = tk.Button(custom_box, text="✓", command=lambda: close_info_window(custom_box), bg="gray", fg="white", font=("Calibri", 18))
    ok_button.pack(pady=10)
    
    # Pencereyi en öne getir ve her zaman en önde tut
    custom_box.lift()
    custom_box.attributes("-topmost", True)
    
    # Pencereyi açık olarak işaretle
    info_window_open = True
    info_window = custom_box

def close_info_window(window):
    global info_window_open, info_window
    
    window.destroy()  # Pencereyi kapat
    info_window_open = False  # Info penceresinin açık olup olmadığını güncelle
    info_window = None  # Info penceresi penceresini temizle

def on_close():
    result = messagebox.askquestion("Shutdown", "Are you sure you want to quit?")
    if result == "yes":
        app.destroy()

# Saati güncelleyen fonksiyon
def update_clock():
    current_time = time.strftime("%H:%M:%S")
    clock_label.configure(text=current_time)
    app.after(1000, update_clock)  # Her 1000 milisaniyede bir saat güncellensin

def update_date():
    current_date = datetime.now().strftime("%d %B %Y")
    date_label.configure(text=current_date)
    # Gece yarısı yeniden güncelle
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    milliseconds_until_midnight = int((next_midnight - now).total_seconds() * 1000)
    app.after(milliseconds_until_midnight, update_date)

# Hover fonksiyonları
def on_enter_label_title(_):
    label_title.configure(text_color="red")

def on_leave_label_title(_):
    label_title.configure(text_color="white")

def on_enter_clock_label(_):
    clock_label.configure(text_color="red")
    date_label.configure(text_color="red")

def on_leave_clock_label(_):
    clock_label.configure(text_color="white")
    date_label.configure(text_color="white")

def on_enter_text_box(_):
    text_box.configure(text_color="red")

def on_leave_text_box(_):    
    text_box.configure(text_color="white")


def assign_shortcut(button_name, assigned_key):
    shortcut_mapping[button_name] = assigned_key
    assigned_labels[button_name].configure(text=f"Assigned Key: {assigned_key}")

def update_assigned_labels():
    for btn_name, assigned_key in shortcut_mapping.items():
        assigned_text = f"Assigned Key: {assigned_key}" if assigned_key else "Assigned Key: None"
        assigned_labels[btn_name].configure(text=assigned_text)

# Pygame ile ses dosyasını başlat
def start_background_music():
    pygame.mixer.init()  # Pygame mikserini başlat
    pygame.mixer.music.load("fairy_tale.mp3")  # Ses dosyasını yükle
    pygame.mixer.music.play(-1)  # Sonsuz döngüde çal

# Ses aç/kapat butonu için işlev
def toggle_sound():
    global sound_on

    if sound_on:
        pygame.mixer.music.pause()  # Sesi durdur
        sound_button.configure(text="🔈", fg_color="red")  
    else:
        pygame.mixer.music.unpause()  # Sesi tekrar başlat
        sound_button.configure(text="🔊", fg_color="black")  

    sound_on = not sound_on  # Ses durumunu değiştir


app = ctk.CTk()
app.title("Voice Translator")
app.geometry("900x1000")
app.resizable(False, False)

# Pencere kapatma olayını izleme
app.protocol("WM_DELETE_WINDOW", on_close)

# Pencereyi sol üst köşede açma
app.geometry("+{}+{}".format(0, 0)) # Pencerenin konumunu belirler. Bu durumda, pencere sol üst köşede açılacaktır. 
# {} içine girilen değerler, pencerenin x ve y koordinatlarını belirler. Burada, pencereyi ekranın sol üst köşesine yerleştirmek için x ve y koordinatları 0 olarak belirlenir.


frame = ctk.CTkFrame(app, fg_color="black", bg_color="black")
frame.pack(fill=ctk.BOTH, expand=True)

# Sekmeler (Tabs) oluşturma
notebook = ctk.CTkTabview(frame, fg_color="black", bg_color="black", corner_radius=16, 
                          segmented_button_fg_color= "white",
                          segmented_button_selected_hover_color="red",
                          segmented_button_unselected_color= "black",
                          segmented_button_selected_color= "red",
                          segmented_button_unselected_hover_color= "red"
                        )
notebook.pack(expand=True, fill=ctk.BOTH)

# Ana sekme
main_frame = notebook.add("Translator")


# Options sekmesi için frame oluşturma
options_frame = notebook.add("Shortcuts")

# Shortcut Settings çerçevesi 
shortcut_settings_frame = ctk.CTkFrame(options_frame, fg_color="black", bg_color="black")
shortcut_settings_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=20)


# Kısayol tuşları için bir sözlük (varsayılan olarak atanacaklar)
shortcut_mapping = {
    "Listen Button": "k",
    "Stop Button": "p",
    "Clear Button": "r",
    "Increase Font Level Button": "a",
    "Decrease Font Level Button": "z",
    "Info Button": "i"
}


def on_enter(event, label_key, assigned_label):
    label_key.configure(text_color="red")  # Metin rengini kırmızı yapar
    assigned_label.configure(text_color="red")  # Metin rengini kırmızı yapar

def on_leave(event, label_key, assigned_label):
    label_key.configure(text_color="white")  # Metin rengini beyaz yapar
    assigned_label.configure(text_color="white")  # Metin rengini beyaz yapar

# Atanmış tuşları göstermek için bir sözlük
assigned_labels = {}

# Kısayol tuşlarını ayarlamak için döngü
for button_name, assigned_key in shortcut_mapping.items():
    frame2 = ctk.CTkFrame(shortcut_settings_frame, fg_color="black", bg_color="black")
    frame2.pack(fill='x', padx=20, pady=(10, 0))

    label_key = ctk.CTkLabel(frame2, text=f"{button_name}", bg_color="black", fg_color="black", font=("Times New Roman", 25, "italic"), text_color="white")
    label_key.pack(side='left', padx=(0, 10), pady=20)

    assigned_label = ctk.CTkLabel(frame2, text=f"Shortcut Key: {assigned_key}", bg_color="black", fg_color="black", font=("Times New Roman", 25, "italic"), text_color="white")
    assigned_label.pack(side='right', padx=(0, 10))
    assigned_labels[button_name] = assigned_label

    # Her iki label için event binding
    assigned_label.bind("<Enter>", lambda event, lk=label_key, al=assigned_label: on_enter(event, lk, al))
    # assigned_label etiketine mouse girdiğinde (hover) on_enter fonksiyonunu çalıştırır.
    # lambda fonksiyonu, on_enter fonksiyonuna event, label_key ve assigned_label argümanlarını geçmek için kullanılır.
    # lk=label_key ve al=assigned_label kısımları, lambda fonksiyonunun on_enter fonksiyonuna hangi label'ları
    # geçeceğini belirtir.
    assigned_label.bind("<Leave>", lambda event, lk=label_key, al=assigned_label: on_leave(event, lk, al))
    label_key.bind("<Enter>", lambda event, lk=label_key, al=assigned_label: on_enter(event, lk, al))
    label_key.bind("<Leave>", lambda event, lk=label_key, al=assigned_label: on_leave(event, lk, al))
    
# Başlangıçta atanan tuşları göster
update_assigned_labels()


# Üst Frame
top_frame = ctk.CTkFrame(main_frame, fg_color="black")
top_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=5)

# Label'ı top_frame üstüne ekleme
label_title = ctk.CTkLabel(master=top_frame, text="   ☢️☢️☢️​ MCS99 TRANSLATOR   ☢️☢️☢️​", font=("Times New Roman", 34, "bold", "italic"))
label_title.pack(side=ctk.TOP, pady=(5, 20))  # Birazcık yükseklik bırakmak için padding ayarladık
label_title.configure(fg_color="black", width=50, height=20, text_color="white")

# Textbox'ı label'in altına yerleştirme
text_box = ctk.CTkTextbox(top_frame, wrap=ctk.WORD, width=50, height=20, font=("Times New Roman", 40, "italic"), fg_color="black", text_color="white")
text_box.pack(fill=ctk.BOTH, expand=True, pady=(5, 10))  # Label ve textbox arasında biraz boşluk bıraktık
text_box.configure(border_color="white", border_width=2, scrollbar_button_color="white", scrollbar_button_hover_color="red")
text_box.insert('1.0', """Welcome!

Voice Translation Program

Translate your texts instantly by speaking. Follow the steps below to get started:

1. Select the Translation Language:
   Choose the target language for translation from the menu at the lower-left upper corner.

2. Use the Microphone:
   Click the "Speak" button and speak into the microphone with the text you want to translate.

3. Wait for the Translation:
   The program will automatically detect your speech and translate it into the selected language.

Tips:
- Speak clearly and minimize background noise for better accuracy.
- Use short sentences and simple phrases to get more accurate translations.

Your feedback and suggestions are always valuable to us. Happy translating!
""")

# Alt Frame
bottom_frame = ctk.CTkFrame(frame, fg_color="black")
bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=5, pady=5)

left_bottom_frame = ctk.CTkFrame(bottom_frame, fg_color="black")
left_bottom_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
right_bottom_frame = ctk.CTkFrame(bottom_frame, fg_color="black")
right_bottom_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

bottom_frame.grid_columnconfigure(0, weight=95)
bottom_frame.grid_columnconfigure(1, weight=5)

# Dil seçeneği için bir StringVar oluştur
selected_language = tk.StringVar(app)
selected_language.set("-- Select the Language to be Translated --")

values = ["English", "Turkish", "Korean", "Chinese", "Japanese", "Russian", "German", "French", "Italian", "Spanish", "Portuguese", "Arabic"]

# Prefix eklemek için fonksiyon
def add_prefix_to_values(values, prefix):
    return [f"{prefix}: {value}" for value in values]

# Prefix ile değerleri güncelle
prefixed_values = add_prefix_to_values(values, "Selected Language to Translate Into")

language_menu = ctk.CTkOptionMenu(
    left_bottom_frame,
    variable=selected_language,
    values=prefixed_values,
    fg_color="black",
    button_color="gray",
    button_hover_color="red",
    text_color="white",
    dropdown_hover_color="gray",
    font=("Times New Roman", 25, "italic")
)

language_menu.configure(width = 20)
language_menu.pack(fill=ctk.BOTH, padx=15, pady=10)


listen_button = ctk.CTkButton(left_bottom_frame, text="Speak ▶️",
                               command=listen_and_translate, fg_color="black", hover_color="red", 
                               corner_radius=32, border_color="white", border_width=2, text_color="white", 
                               font=("Times New Roman", 20, "italic", "bold"))
listen_button.pack(side=ctk.TOP, fill=ctk.X, padx=15, pady=5)

clear_button = ctk.CTkButton(left_bottom_frame, text="Clear 🗑️",
                              command=clear_text, fg_color="black", hover_color="red",
                              corner_radius=32, border_color="white", border_width=2, 
                              text_color="white", font=("Times New Roman", 20, "italic", "bold"))
clear_button.pack(side=ctk.TOP, fill=ctk.X, padx=15, pady=5)

increase_button = ctk.CTkButton(right_bottom_frame, text="+", command=increase_font_size, fg_color="black", 
                                hover_color="red", corner_radius=32, border_color="white", border_width=2, 
                                text_color="white", font=("Times New Roman", 20, "italic", "bold"))
increase_button.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5)

decrease_button = ctk.CTkButton(right_bottom_frame, text="–", command=decrease_font_size, fg_color="black",
                                 hover_color="red", corner_radius=32, border_color="white", border_width=2,
                                 text_color="white", font=("Times New Roman", 20, "italic", "bold"))
decrease_button.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=5)

#Info Butonu
info_button = ctk.CTkButton(left_bottom_frame, text="🛈", command=show_custom_info_message, font=("Times New Roman", 20), 
                        width=30 , height= 30, fg_color="black", hover_color="red", corner_radius=32, border_color="white", border_width=2)
info_button.pack(side="right", padx=15, pady=5)


# Saat etiketini oluştur
clock_label = ctk.CTkLabel(left_bottom_frame, text="", font=("Times New Roman", 25, "italic"))
clock_label.pack(padx= 15, side="left")

# Tarih etiketini oluştur
date_label = ctk.CTkLabel(left_bottom_frame, text="", font=("Times New Roman", 25, "italic"))
date_label.pack(pady=5, side="left")

# Hover eventleri ekle
label_title.bind("<Enter>", on_enter_label_title)
label_title.bind("<Leave>", on_leave_label_title)
clock_label.bind("<Enter>", on_enter_clock_label)
clock_label.bind("<Leave>", on_leave_clock_label)
date_label.bind("<Enter>", on_enter_clock_label)
date_label.bind("<Leave>", on_leave_clock_label)
text_box.bind("<Enter>", on_enter_text_box)
text_box.bind("<Leave>", on_leave_text_box)


# Slider oluşturma
font_size_slider = ctk.CTkSlider(
    master=right_bottom_frame,
    command=set_font_size,
    from_=20,
    to=60,
    number_of_steps=50,  # 20'den 60'a kadar 50 adımlı bir slider 
    width=200,
    height=20,
    border_width=2,
    fg_color="black",
    progress_color=("white", "red"),  # Renk geçişi
    border_color="black",
    button_color="white",
    button_hover_color = "white",
    orientation="horizontal",
)
font_size_slider.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=10)


# Ses aç/kapat butonunu oluştur
sound_on = True
sound_button = ctk.CTkButton(right_bottom_frame, text="🔊", font=("Arial", 16), command=toggle_sound, height= 50, width=20, 
                         fg_color="black", hover_color="red", corner_radius=32, border_color="white", border_width=2)
sound_button.pack(pady=20)

# Program başlatıldığında arka plan müziğini başlat
start_background_music()



# Saati güncelle
update_clock()
# Tarihi güncelle
update_date()

app.bind("<Key>", lambda event: handle_keypress(event))  # Tüm tuş basışlarını handle_keypress fonksiyonuna yönlendirir.

def handle_keypress(event):  # Tuş basışlarını işlemek için fonksiyon tanımı.
    key = event.keysym  # Basılan tuşun ismini alır.
    for button_name, assigned_key in shortcut_mapping.items():  # Tuş atama haritasındaki her bir tuşu kontrol eder.
        if key == assigned_key:  # Basılan tuş atanmış tuş ile eşleşirse.
            if button_name == "Listen Button":  
                listen_and_translate()  # listen_and_translate fonksiyonunu çağırır.
            elif button_name == "Stop Button":  
                stop_event.set()  # stop_event'i set ederek dinlemeyi durdurur.
            elif button_name == "Clear Button":  
                clear_text()  # clear_text fonksiyonunu çağırır.
            elif button_name == "Increase Font Level Button":  
                increase_font_size()  # increase_font_size fonksiyonunu çağırır.
            elif button_name == "Decrease Font Level Button": 
                decrease_font_size()  # decrease_font_size fonksiyonunu çağırır.
            elif button_name == "Info Button": 
                show_custom_info_message()  # show_custom_info_message fonksiyonunu çağırır.


# Pencereyi çalıştırma
app.mainloop()



# CTRL + K / CTRL + U (Seçilen metni comment satırına al / çıkar)