# BlurFit Studio

**BlurFit Studio** to nowoczesna, lekka i w pełni przenośna aplikacja desktopowa napisana w **Pythonie** przy użyciu **PyQt6**, służąca do inteligentnego dopasowywania proporcji wideo (np. konwersji poziomych nagrań z YouTube 16:9 do pionowego formatu 9:16 dla TikTok, Shorts czy Reels). 

Aplikacja rozwiązuje problem czarnych pasów na bokach ekranu poprzez wygenerowanie rozmytego tła na bazie oryginalnego wideo (klasyczny efekt "blurfit") lub bezpośrednie wykadrowanie z regulacją przesunięcia kadru w czasie rzeczywistym.

---

## Główne funkcje

- **Inteligentne tryby skalowania obrazu**:
  - **Dopasuj z rozmytym tłem (BlurFit)**: Tworzy estetyczną, rozmytą i powiększoną wersję wideo w tle, na którą nakłada oryginalny kadr. Suwak pozwala płynnie kontrolować intensywność rozmycia (0–100%).
  - **Przytnij i wypełnij (Crop & Fill)**: Wypełnia cały kadr docelowy oryginalnym wideo poprzez dopasowanie jednego z wymiarów i kadrowanie drugiego. Suwak pozwala przesuwać punkt kadrowania (offset) w poziomie lub pionie w czasie rzeczywistym.
- **Obsługa popularnych formatów docelowych**:
  - `9:16` – Pionowy (TikTok, YouTube Shorts, Instagram Reels)
  - `16:9` – Poziomy (YouTube, klasyczne ekrany)
  - `1:1` – Kwadratowy (Kwadrat / Instagram Feed)
  - `4:3` – Standardowy / Klasyczny TV
- **Interaktywny podgląd na żywo**:
  - Automatyczne ładowanie i renderowanie pierwszej klatki wideo od razu po załadowaniu pliku (brak czarnego ekranu).
  - Dwudzielny podgląd: oryginalne wideo z lewej strony oraz symulacja efektu końcowego w czasie rzeczywistym z prawej.
- **Dopracowany interfejs (Premium UI & UX)**:
  - **Dwa motywy do wyboru**: Ciemny (Dark Mode) oraz Jasny (Light Mode).
  - **Automatyczna detekcja systemu**: Przy pierwszym uruchomieniu aplikacja dopasowuje motyw do ustawień systemowych użytkownika.
  - **Trwałość ustawień**: Wybrany motyw jest zapamiętywany pomiędzy uruchomieniami aplikacji za pomocą `QSettings`.
  - **Wektorowe kontrolki (QPainter)**: Przyciski Play/Pause, wyciszenia oraz wyboru motywu (Słońce / Złoty Księżyc w pełni z kraterami) są w 100% rysowane wektorowo i płynnie reagują na najechanie myszą (*hover*).
  - **Suwaki natychmiastowego przewijania (JumpSlider)**: Możliwość kliknięcia w dowolne miejsce paska osi czasu, głośności lub ustawień obrazu, aby suwak od razu przeskoczył w dane miejsce (*click-to-seek*).
- **Przenośność (Portable FFmpeg Support)**:
  - Brak konieczności instalowania FFmpeg globalnie w systemie! Aplikacja automatycznie wyszukuje i priorytetyzuje pliki wykonywalne `ffmpeg` i `ffprobe` umieszczone w lokalnym folderze projektu.

---

## Architektura projektu

```text
Blurfit-studio/
├── blurfit_studio/
│   ├── bin/               # [NEW/OPCJONALNIE] Folder na lokalne pliki ffmpeg.exe i ffprobe.exe
│   ├── core/
│   │   └── video_worker.py # Logika wątku procesowego oraz wywoływanie filtrów FFmpeg
│   ├── ui/
│   │   ├── __init__.py     # Programowe generowanie ikon wektorowych platform
│   │   ├── main_window.py  # Główny interfejs aplikacji i zachowanie kontrolek
│   │   ├── preview.py      # Widgety podglądu wideo i dynamicznego rozmycia tła
│   │   └── style_sheets.py # Premium style CSS dla motywu jasnego oraz ciemnego
│   └── app.py             # Punkt wejścia inicjujący QApplication
├── tests/
│   └── test_ffmpeg.py     # Testy sprawdzające poprawność przetwarzania filtrów
├── requirements.txt       # Wymagane pakiety Pythona (jedynie PyQt6)
├── run.py                 # Główny skrypt uruchomieniowy
└── README.md              # Niniejszy plik dokumentacji
```

---

## Instalacja i Uruchomienie

### Wymagania wstępne
- **Python 3.8 lub nowszy**
- Środowisko wirtualne (zalecane)

### Krok 1: Klonowanie repozytorium i instalacja zależności
Otwórz terminal w folderze projektu i wykonaj:

```bash
# Utworzenie i aktywacja środowiska wirtualnego
python -m venv .venv
# Na Windows:
.venv\Scripts\activate
# Na macOS/Linux:
source .venv/bin/activate

# Instalacja PyQt6
pip install -r requirements.txt
```

### Krok 2: Dostarczenie binarek FFmpeg (Wersja przenośna)
Aby aplikacja mogła odczytywać i renderować pliki wideo, potrzebuje narzędzi **FFmpeg** oraz **FFprobe**.

Możesz ułatwić życie sobie i innym użytkownikom przenosząc pliki wykonywalne bezpośrednio do projektu:
1. Pobierz stabilną kompilację FFmpeg dla swojego systemu operacyjnego (dla Windows zalecany build z [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)).
2. Rozpakuj archiwum i przejdź do folderu `bin`.
3. Skopiuj pliki:
   - `ffmpeg.exe` i `ffprobe.exe` (na Windows)
   - `ffmpeg` i `ffprobe` (na macOS / Linux)
4. Wklej je bezpośrednio do folderu wewnątrz projektu:
   - `blurfit_studio/bin/`

*Alternatywnie:* Jeżeli posiadasz już FFmpeg zainstalowany globalnie w systemie i dodany do zmiennej środowiskowej `PATH`, aplikacja automatycznie wykryje go i użyje jako fallback.

### Krok 3: Uruchomienie programu
Uruchom główny plik startowy za pomocą interpretera Pythona ze środowiska wirtualnego:

```bash
python run.py
```

---

## Uruchamianie Testów
W projekcie znajduje się zestaw testów sprawdzających poprawność składania poleceń FFmpeg oraz kadrowania obrazu. Możesz je uruchomić za pomocą:

```bash
python -m unittest tests/test_ffmpeg.py
```

---

## Technologie
- **GUI & Preview**: PyQt6 (QtMultimedia, QtMultimediaWidgets, QGraphicsBlurEffect)
- **Engine przetwarzania wideo**: FFmpeg / FFprobe (wywoływane asynchronicznie w tle poprzez `QThread` i `subprocess`)
- **Design System**: Dedykowane arkusze stylów Qt (QSS) wspierające dynamiczne kompozycje, wektorowe ikony rysowane na obiektach `QPixmap` oraz autorskie widgety klasy `QAbstractButton` reagujące na interakcje użytkownika.

---
Stworzone z dbałością o detale wizualne i płynność działania. 
