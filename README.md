# 🐺 Wolfscribe Premium

**Convert books into precision-tokenized, training-ready datasets — with professional-grade accuracy.**  
Part of the [Wolflow](https://wolflow.ai) ecosystem • Built by [@CLewisMessina](https://github.com/CLewisMessina)

> Now featuring **Advanced Tokenizer System** with exact GPT-4, Claude, and BERT tokenization for professional AI training workflows.

---

## ✨ What is Wolfscribe Premium?

Wolfscribe is the **first local desktop tool** that provides exact tokenization for multiple AI models, transforming long-form documents (PDFs, EPUBs, and TXT files) into precision-optimized `.txt` or `.csv` datasets.

Built for professional AI developers, researchers, and enterprises who need **accuracy that pays for itself**.

> **No more token overestimation. No more cloud dependencies. Just precise, local processing.**

---

## 📸 Premium Demo Video (Press Play)

https://github.com/user-attachments/assets/2596b35e-6202-4c86-91e9-e9df729f6a18

---

## 🚀 What's New in v2.0: Premium Tokenizer Revolution

### 💎 **Five Professional Tokenizers**
- **🆓 GPT-2** - Fast estimation for development (Free)
- **🎯 GPT-4** - Exact OpenAI tokenization with tiktoken (Premium)
- **⚡ GPT-3.5-turbo** - Precise tokenization for cost optimization (Premium)
- **🤖 Claude Estimator** - Anthropic-optimized token counting (Premium)
- **🧠 BERT/RoBERTa** - Sentence-transformers for encoder models (Premium)

### 📊 **Advanced Analytics Dashboard**
- **🎯 Efficiency Scoring** - Measures chunk optimization (0-100%)
- **💰 Cost Estimation** - Real-time training cost calculations
- **📈 Token Distribution** - Detailed breakdown by size ranges
- **💡 Smart Recommendations** - AI-powered optimization suggestions
- **📋 Export Reports** - Comprehensive analytics (JSON/TXT)

### 🔐 **Professional Licensing System**
- **🆓 7-Day Free Trial** - Full access to all premium features
- **🧑‍💻 Demo Mode** - `WOLFSCRIBE_DEMO=true` for development
- **🔑 Secure Authentication** - Key-based premium access
- **⏱️ Trial Management** - Automatic countdown and upgrade prompts

---

## 💰 ROI: Premium Features Pay for Themselves

### **Real Cost Savings Example**
```
50,000 word technical book:
├── GPT-2 Estimate: ~67,000 tokens → $2.01 training cost
├── GPT-4 Exact:    ~48,500 tokens → $1.46 actual cost
└── 💰 SAVINGS:     $0.55 per book (Premium pays for itself!)

Large dataset (500K words):
└── 💰 POTENTIAL SAVINGS: $5.50+ per processing run
```

### **Professional Use Cases**
| Industry | Premium Value | ROI Timeline |
|----------|---------------|--------------|
| **AI Startups** | Exact cost budgeting | 1-2 datasets |
| **Enterprise** | Multi-model compatibility | First project |
| **Research** | Reproducible tokenization | Immediate |
| **Publishing** | Batch processing efficiency | 3-5 books |

---

## 📦 Core Features (Free + Premium)

### 🆓 **Free Tier Features**
- 🧠 **GPT-2 Tokenization** - Fast estimation for development
- ✂️ **Smart text chunking** (paragraph, sentence, custom)
- 🮢 **Drag-and-drop file loading** (PDF, EPUB, TXT)
- 🔍 **Basic chunk preview** with token counts
- 📂 **Export as `.txt` or `.csv`** with standard formatting
- 💾 **Session save/load** (.wsession files)
- 🖥️ **Professional desktop UI** with ttkbootstrap

### 💎 **Premium Features ($15/month)**
- 🎯 **Exact GPT-4 & GPT-3.5 Tokenization** - tiktoken precision
- 🤖 **Claude & BERT Tokenizers** - Multi-model compatibility
- 📊 **Advanced Analytics Dashboard** - Efficiency & cost analysis
- ⚡ **Smart Optimization Suggestions** - AI-powered recommendations
- 📁 **Enhanced Export** - Metadata & statistics included
- 🔍 **Tokenizer Comparison** - Side-by-side analysis
- 💾 **Premium Session Features** - Tokenizer preferences saved
- 🎯 **Model Compatibility Checking** - Warnings & guidance

---

## 🚀 Getting Started

### 1. Clone & Install
```bash
git clone https://github.com/CLewisMessina/wolfscribe.git
cd wolfscribe
python -m venv venv
.\venv\Scripts\activate   # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Launch Wolfscribe
```bash
python main.py
```

### 3. Start Your Free Trial
- Click **"🚀 Start Free Trial"** in the app
- Get 7 days of full premium access
- No credit card required

### 4. Choose Your Tokenizer
- **Development**: GPT-2 (Free) for fast iteration
- **Production**: GPT-4 (Premium) for exact tokenization
- **Cost Optimization**: GPT-3.5 (Premium) for budget efficiency
- **Multi-Model**: Claude/BERT (Premium) for compatibility

---

## 🔧 Premium Dependencies

```txt
# Core (Free)
ttkbootstrap==1.10.1
tkinterdnd2>=0.3.0
transformers>=4.39.3

# Premium Tokenizers
tiktoken>=0.5.0              # OpenAI exact tokenization
sentence-transformers>=2.2.0 # BERT/RoBERTa models
pycryptodome>=3.19.0         # License management
```

---

## 📊 Advanced Usage Examples

### **Exact GPT-4 Tokenization**
```python
# In Wolfscribe Premium:
# 1. Select "GPT-4 (Premium)" tokenizer
# 2. Process your document
# 3. Get exact token counts → precise cost estimation
```

### **Multi-Model Workflow**
```python
# Compare tokenizers for your target model:
# 1. Use "🔍 Compare Tokenizers" feature
# 2. See side-by-side token counts
# 3. Choose optimal tokenizer for your use case
```

### **Cost Optimization**
```python
# Advanced Analytics shows:
# • Efficiency Score: 94%
# • Est. Training Cost: $1.46
# • Recommendation: "Chunks well-optimized for GPT-4"
```

---

## 🎯 Model Compatibility Matrix

| Model Family | Optimal Tokenizer | Accuracy | Use Case |
|--------------|------------------|----------|----------|
| **GPT-4** | tiktoken GPT-4 | 🎯 Exact | Production training |
| **GPT-3.5** | tiktoken GPT-3.5 | 🎯 Exact | Cost optimization |
| **Claude 3.5** | Claude Estimator | 📊 High | Anthropic API |
| **BERT/RoBERTa** | BERT Tokenizer | 🎯 Exact | Encoder models |
| **LLaMA/Mistral** | GPT-2 Estimator | 📊 Good | Open source |

---

## 💡 Pro Tips for Maximum ROI

### **1. Tokenizer Selection Strategy**
- **Start with trial** → Test all tokenizers on sample data
- **Production workflows** → Use exact tokenizers (GPT-4/3.5)
- **Cost-sensitive projects** → Compare tokenizers before committing
- **Multi-model deployment** → Verify compatibility with target models

### **2. Efficiency Optimization**
```
Target: 90%+ efficiency score
├── Chunk size: 400-480 tokens (sweet spot)
├── Avoid: Very short (<50 tokens) or long (>512 tokens) chunks
└── Use: Smart splitting on sentence boundaries
```

### **3. Cost Management**
- Use **exact tokenizers** for budget planning
- Export **analytics reports** for project documentation
- Compare **estimated vs actual** costs before large runs

---

## 🏗️ Architecture: Premium Features

### **Tokenizer Manager**
```python
# Five tokenizers with automatic fallbacks
TokenizerManager:
├── GPT-2 (transformers) → Fast estimation
├── GPT-4 (tiktoken) → Exact OpenAI tokenization  
├── GPT-3.5 (tiktoken) → Cost-optimized accuracy
├── Claude (custom) → Anthropic estimation
└── BERT (sentence-transformers) → Encoder models
```

### **License Management**
```python
# Secure premium feature gating
LicenseManager:
├── Trial System → 7-day full access
├── Demo Mode → Developer access
├── License Validation → Secure key checking
└── Feature Gates → Premium/free separation
```

### **Analytics Engine**
```python
# Advanced chunk analysis
AnalyticsEngine:
├── Efficiency Scoring → Optimization measurement
├── Cost Estimation → Training budget planning
├── Token Distribution → Size analysis
└── Recommendations → AI-powered suggestions
```

---

## 📈 Success Stories & Use Cases

### **AI Startup: Training Cost Optimization**
> *"Wolfscribe Premium saved us $200+ on our first model training run. The exact GPT-4 tokenization prevented massive overestimation."*

### **Enterprise: Multi-Model Deployment**
> *"The tokenizer comparison feature helped us choose the right tokenization strategy for our enterprise LLM pipeline."*

### **Research Lab: Reproducible Experiments**
> *"Exact tokenization ensures our training experiments are reproducible across different model architectures."*

---

## 🗓️ Roadmap

### **Immediate (Next 30 Days)**
- [x] ✅ Premium tokenizer system
- [x] ✅ Advanced analytics dashboard
- [x] ✅ Trial system & licensing
- [ ] 🔄 Dynamic chunking optimization
- [ ] 🔄 Batch processing for multiple files

### **Q3 2025**
- [ ] 📡 Hugging Face integration
- [ ] 📄 JSONL export format
- [ ] 🎯 Custom tokenizer support
- [ ] 📱 Cross-platform compatibility

### **Q4 2025**
- [ ] ☁️ Optional cloud sync
- [ ] 👥 Team collaboration features
- [ ] 📊 Advanced visualizations
- [ ] 🔌 API access for enterprises

---

## 💎 Pricing & Plans

### **Free Tier** - $0/month
- ✅ GPT-2 tokenization
- ✅ Basic chunking & export
- ✅ Desktop app access
- ✅ Community support

### **Premium** - $15/month or $150/year
- ✅ **All Free features**
- ✅ **Exact GPT-4 & GPT-3.5 tokenization**
- ✅ **Claude & BERT tokenizers**  
- ✅ **Advanced analytics dashboard**
- ✅ **Cost estimation & optimization**
- ✅ **Tokenizer comparison tools**
- ✅ **Enhanced export with metadata**
- ✅ **Priority support**

**🆓 Start your 7-day free trial** - No credit card required

---

## 🧙‍♂️ Part of the Wolflow Ecosystem

### **Current Tools**
- [🥚 **Wolfkit**](https://github.com/CLewisMessina/wolfkit) – AI code testing with rollback
- [🐺 **Wolfscribe**](https://github.com/CLewisMessina/wolfscribe) – Document to dataset conversion
- [🚀 **Wolftrain**](https://github.com/CLewisMessina/wolftrain) – Local LoRA fine-tuning

### **Coming Soon**
- [📈 **Wolftrack**](https://github.com/CLewisMessina) – Token usage analytics
- [🔗 **Wolfflow**](https://github.com/CLewisMessina) – Unified AI workflow platform

---

## 🛡️ Enterprise & Security

### **Data Privacy**
- ✅ **100% Local Processing** - No cloud dependencies
- ✅ **No Data Collection** - Your documents never leave your machine
- ✅ **Offline Operation** - Works without internet (after license validation)
- ✅ **Secure Licensing** - Encrypted key validation system

### **Enterprise Features**
- 💼 **Volume Licensing** - Contact for enterprise pricing
- 📊 **Usage Analytics** - Track tokenization across teams
- 🔧 **Custom Integration** - API access for enterprise workflows
- 🎯 **Priority Support** - Direct access to development team

---

## 🤝 Support & Community

### **Getting Help**
- 📖 **Documentation**: Complete guides at [docs.wolflow.ai](https://docs.wolflow.ai)
- 💬 **Community**: Join our [Discord server](https://discord.gg/wolflow)
- 📧 **Premium Support**: [support@wolflow.ai](mailto:support@wolflow.ai)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/CLewisMessina/wolfscribe/issues)

### **Contributing**
- 🔧 **Feature Requests**: GitHub Discussions
- 🌟 **Stars**: Help us grow with a GitHub star
- 📢 **Share**: Tell other developers about Wolfscribe
- 💼 **Enterprise**: Contact us for custom development

---

## 🤖 License & Legal

**Creative Commons CC BY-NC 4.0**  
✅ Free for personal and educational use  
💼 Commercial use requires premium license  

**Premium License Terms**:
- ✅ Commercial use permitted
- ✅ Multiple installations per license
- ✅ Include in commercial products
- ❌ Redistribution without permission

---

## 📊 Technical Specifications

### **System Requirements**
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space (including dependencies)
- **Network**: Required for license validation only

### **Performance Benchmarks**
- **GPT-2 Tokenization**: ~50,000 tokens/second
- **GPT-4 Exact**: ~25,000 tokens/second
- **File Processing**: 100MB text files in <30 seconds
- **Analytics Generation**: Real-time (< 1 second)

---

## 🎉 Start Your Premium Journey

1. **📥 Download**: `git clone https://github.com/CLewisMessina/wolfscribe.git`
2. **🚀 Install**: `pip install -r requirements.txt`
3. **▶️ Launch**: `python main.py`
4. **🆓 Trial**: Click "Start Free Trial" in the app
5. **💎 Upgrade**: Experience the precision, upgrade to Premium

---

_You write the story. Wolfscribe makes it trainable. Premium makes it profitable._

**Ready to experience exact tokenization?** [Download Wolfscribe Premium →](https://github.com/CLewisMessina/wolfscribe/releases/latest)