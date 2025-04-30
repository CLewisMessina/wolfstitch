wolfscribe/
├── assets/                 # App icons, example screenshots
├── ui/                     # GUI components
│   └── app_frame.py        # Main window layout + event binding
├── processing/             # Text extraction, cleaning, chunking
│   ├── extract.py          # PDF/EPUB/TXT loader
│   ├── clean.py            # Header/footer removal, formatting
│   └── splitter.py         # Sentence/paragraph/page splitting
├── export/                 # Final dataset writers
│   └── dataset_exporter.py # Save to .txt or .csv
├── main.py                 # App launcher
├── controller.py           # Bridge between UI and processing
├── requirements.txt        # Dependencies
├── README.md               # Overview and setup
└── CHANGELOG.md            # Version history
