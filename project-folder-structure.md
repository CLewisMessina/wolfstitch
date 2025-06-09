# 🐺 Wolfscribe Premium - Project Structure

**Enhanced AI Training Cost Optimizer with Professional Architecture**  
*Complete project organization for v2.2+ with modular design*

---

## 📁 Project Overview

```
wolfscribe/
├── 🚀 APPLICATION CORE
├── 💰 ENHANCED COST ANALYSIS ENGINE  
├── 🎨 MODERN UI SYSTEM
├── 📊 EXPORT & SESSION MANAGEMENT
├── 💎 PREMIUM LICENSING SYSTEM
└── 📦 ASSETS & CONFIGURATION
```

---

## 🗂️ Complete File Structure

```
wolfscribe/
│
├── 📋 PROJECT DOCUMENTATION
│   ├── README.md                              # Main user-facing documentation
│   ├── CHANGELOG.md                           # Complete version history
│   ├── requirements.txt                       # Python dependencies
│   └── refactor-appframe-plan-claude-V2*.md   # Development documentation
│
├── 🚀 APPLICATION ENTRY POINTS
│   ├── main.py                                # Application launcher with modern theme
│   └── controller.py                          # Enhanced processing controller
│
├── 💰 ENHANCED COST ANALYSIS SYSTEM
│   └── core/
│       ├── __init__.py                        # Core module initialization
│       ├── cost_calculator.py                # Main cost calculation engine (15+ approaches)
│       ├── cost_calculator_integration.py    # Unified cost analysis interface
│       ├── pricing_engine.py                 # Real-time cloud provider pricing
│       ├── roi_calculator.py                 # ROI analysis and optimization engine
│       ├── model_database.py                 # Comprehensive AI model database
│       ├── tokenizer_manager.py              # Professional tokenizer system
│       └── license_manager.py                # Premium licensing and trial management
│
├── 🎨 MODERN UI SYSTEM
│   └── ui/
│       ├── app_frame.py                       # Main application frame (~600 lines)
│       ├── cost_dialogs.py                   # Cost analysis dialogs and exports
│       ├── preview_dialogs.py                # Preview, analytics, and upgrade dialogs
│       ├── section_builders.py               # UI section creation and layout
│       └── styles.py                         # Modern slate theme and styling
│
├── 🔄 TEXT PROCESSING PIPELINE
│   └── processing/
│       ├── extract.py                        # Multi-format file extraction (PDF, EPUB, TXT)
│       ├── clean.py                          # Advanced text cleaning and preprocessing
│       └── splitter.py                       # Text chunking strategies
│
├── 📊 EXPORT & SESSION MANAGEMENT
│   ├── export/
│   │   └── dataset_exporter.py               # TXT and CSV export functionality
│   └── session.py                            # Session save/load with preferences
│
├── 📦 ASSETS & RESOURCES
│   ├── assets/
│   │   ├── main.qss                          # Legacy Qt stylesheet (unused)
│   │   ├── wolfscribe-icon.png               # Application icon
│   │   └── icons/                            # Material Design icon system
│   │       ├── 24px/                         # Button-sized icons
│   │       │   ├── upload_file.png
│   │       │   ├── tune.png
│   │       │   ├── visibility.png
│   │       │   ├── description.png
│   │       │   ├── table_view.png
│   │       │   ├── save.png
│   │       │   ├── folder_open.png
│   │       │   ├── analytics.png
│   │       │   ├── settings.png
│   │       │   └── diamond.png
│   │       └── 36px/                         # Header-sized icons
│   │           ├── folder_open.png
│   │           ├── tune.png
│   │           ├── visibility.png
│   │           ├── upload_file.png
│   │           ├── save.png
│   │           └── diamond.png
│
├── 🔒 GENERATED FILES & CACHE
│   ├── .wolfscribe_license                   # Premium license storage
│   ├── .wolfscribe_trial                     # Trial activation tracking
│   └── *.wsession                            # User session files
│
└── 🧪 DEVELOPMENT ENVIRONMENT
    ├── venv/                                  # Python virtual environment
    ├── .git/                                  # Git version control
    ├── .gitignore                             # Git ignore patterns
    └── __pycache__/                           # Python bytecode cache
```

---

## 🏗️ Architecture Overview

### **🚀 Application Core (2 files)**
| File | Purpose | Key Features |
|------|---------|--------------|
| `main.py` | Application launcher | Modern theme setup, window configuration |
| `controller.py` | Enhanced processing controller | Premium integration, cost analysis coordination |

### **💰 Enhanced Cost Analysis System (7 files)**
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `cost_calculator.py` | Main calculation engine | 15+ training approaches, GPU configurations |
| `pricing_engine.py` | Real-time pricing | Lambda Labs, Vast.ai, RunPod integration |
| `roi_calculator.py` | ROI analysis | Break-even, projections, optimization |
| `model_database.py` | AI model specifications | 25+ models with Chinchilla scaling |
| `tokenizer_manager.py` | Professional tokenizers | 5 tokenizers with compatibility matrix |
| `license_manager.py` | Premium licensing | Trial management, feature gating |
| `cost_calculator_integration.py` | Unified interface | Complete cost analysis coordination |

### **🎨 Modern UI System (5 files)**
| Component | Purpose | Lines | Responsibilities |
|-----------|---------|-------|------------------|
| `app_frame.py` | Main application frame | ~600 | Core logic, state management, delegation |
| `cost_dialogs.py` | Cost analysis UI | ~800 | Cost dialogs, export functionality |
| `preview_dialogs.py` | Preview & analytics | ~400 | Chunk preview, upgrade dialogs |
| `section_builders.py` | UI construction | ~300 | Section creation, layout management |
| `styles.py` | Modern theme | ~400 | Slate theme, colors, component styles |

### **🔄 Text Processing Pipeline (3 files)**
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `extract.py` | File processing | PDF (pdfminer), EPUB (BeautifulSoup), TXT |
| `clean.py` | Text preprocessing | Header removal, whitespace normalization |
| `splitter.py` | Text chunking | Paragraph, sentence, custom delimiter |

### **📊 Export & Session (2 files)**
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `dataset_exporter.py` | Data export | TXT, CSV with proper encoding |
| `session.py` | State persistence | Save/load workflows with preferences |

---

## 🔧 Key Dependencies by System

### **Core Application**
```python
ttkbootstrap==1.10.1      # Modern UI framework
tkinterdnd2>=0.3.0        # Drag & drop support
transformers>=4.39.3      # Basic GPT-2 tokenization
```

### **Enhanced Cost Calculator**
```python
aiohttp>=3.8.0            # Cloud provider APIs
numpy>=1.21.0             # Advanced calculations
asyncio-throttle>=1.0.0   # API rate limiting
```

### **Premium Tokenizers**
```python
tiktoken>=0.5.0           # OpenAI exact tokenization
sentence-transformers>=2.2.0  # BERT/RoBERTa models
```

### **Document Processing**
```python
beautifulsoup4>=4.12.3    # EPUB processing
pdfminer.six>=20221105    # PDF extraction
```

### **Premium Features**
```python
pycryptodome>=3.19.0      # License encryption
openpyxl>=3.0.0           # Excel export (auto-installed)
```

---

## 🔄 Data Flow Architecture

```
📁 Input Files (PDF/EPUB/TXT)
    ↓
🔄 Processing Pipeline (extract → clean → split)
    ↓
🧠 Tokenizer Manager (5 professional tokenizers)
    ↓
💰 Enhanced Cost Calculator (15+ approaches)
    ↓
📊 Analytics & ROI Analysis
    ↓
🎨 Modern UI Display (cost dialogs, previews)
    ↓
📋 Professional Export (JSON/CSV/Excel/TXT)
```

---

## 🚀 Development Highlights

### **v2.2 Architecture Achievements**
- ✅ **73% Code Reduction**: app_frame.py from 2167 → 600 lines
- ✅ **Modular Design**: Clean separation of concerns across 20+ files
- ✅ **Enhanced Features**: Complete cost analysis system integration
- ✅ **Professional UI**: Modern dark theme with responsive design
- ✅ **Scalable Foundation**: Easy to add new features and maintain

### **Performance Optimizations**
- 🚀 **5-minute analysis cache** to prevent redundant calculations
- ⚡ **Threaded operations** with loading states for smooth UX
- 💾 **Smart session management** with preference restoration
- 🎯 **Efficient tokenization** with graceful fallbacks

### **Code Quality Improvements**
- 📏 **Maintainable Size**: All files under 1000 lines
- 🔧 **Clean Interfaces**: Simple delegation patterns throughout
- 🛡️ **Robust Error Handling**: Graceful fallbacks for all operations
- 📊 **Comprehensive Logging**: Professional development experience

---

## 🔮 Future Architecture Plans

### **Q3 2025 Enhancements**
- 📡 Advanced market intelligence integration
- 🤖 ML-powered cost optimization algorithms
- 📊 Enhanced visualization with charts and graphs
- 🏢 Enterprise team collaboration features

### **Scalability Considerations**
- 🔌 **Plugin Architecture**: Modular cost calculator extensions
- 🌐 **API Integration**: REST API for enterprise customers
- 📱 **Cross-Platform**: Foundation ready for mobile/web versions
- ☁️ **Cloud Sync**: Optional cloud storage for enterprise teams

---

## 💡 For Developers

### **Getting Started with the Codebase**
1. **Entry Point**: Start with `main.py` and `app_frame.py`
2. **Cost Features**: Explore `core/cost_calculator.py` and related files
3. **UI Components**: Review `ui/` directory for interface patterns
4. **Adding Features**: Follow the delegation pattern established in v2.2

### **Architecture Principles**
- 🎯 **Single Responsibility**: Each file has a clear, focused purpose
- 🔗 **Loose Coupling**: Components communicate through clean interfaces
- 🛡️ **Error Resilience**: Graceful degradation when features unavailable
- 📊 **Premium Integration**: Feature gating throughout the application

---

_This structure represents the culmination of multiple major releases, creating a professional-grade application architecture suitable for enterprise use and continued development._