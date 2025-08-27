# Pharmaceutical SOP Author - AI Model Training

Google Colab-based training pipeline for fine-tuning Ollama models on pharmaceutical datasets to generate regulatory-compliant SOPs.

## 🎯 Overview

This directory contains the complete AI training pipeline for the Pharmaceutical SOP Author system, utilizing Google Colab for GPU-accelerated model fine-tuning with real FDA datasets.

## 📁 Project Structure

```
colab-training/
├── notebooks/                    # Jupyter notebooks for training pipeline
│   ├── 01_setup_ollama_environment.ipynb
│   ├── 02_data_collection.ipynb
│   ├── 03_model_fine_tuning.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_model_deployment.ipynb
├── src/                         # Supporting Python modules
│   ├── data_collectors/         # FDA data collection scripts
│   └── training/                # Training utilities
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Google Colab account
- ngrok account (for tunneling)
- Access to FDA datasets
- GPU-enabled Colab runtime

### Training Pipeline Setup

1. **Open Google Colab**
   - Go to [colab.research.google.com](https://colab.research.google.com)

2. **Upload Training Notebooks**
   - Upload all notebooks from `colab-training/notebooks/` to Colab

3. **Start Environment Setup**
   - Open `01_setup_ollama_environment.ipynb`
   - Run all cells to:
     - Install Ollama and dependencies
     - Set up GPU acceleration
     - Configure ngrok tunneling
     - Initialize the training environment

4. **Data Collection**
   - Open `02_data_collection.ipynb`
   - Execute cells to collect:
     - FDA Pharmaceuticals FAQ dataset
     - FDA Drug Labels database
     - FDA Adverse Event Reports
     - FDA Orange Book (drug approvals)
     - EPA Chemical Registry data

5. **Model Fine-tuning**
   - Open `03_model_fine_tuning.ipynb`
   - Run fine-tuning process:
     - Load base Ollama model (Mistral/Llama)
     - Apply LoRA/QLoRA for efficient training
     - Fine-tune on pharmaceutical datasets
     - Optimize for SOP structure and terminology

6. **Model Evaluation**
   - Open `04_model_evaluation.ipynb`
   - Test model performance:
     - Regulatory compliance accuracy
     - Pharmaceutical terminology validation
     - SOP structure adherence

7. **Model Deployment**
   - Open `05_model_deployment.ipynb`
   - Export fine-tuned model
   - Generate deployment scripts
   - Create model archive for local deployment

## 🛠 Technical Details

### Supported Models
- **Mistral 7B Instruct** - Primary model for SOP generation
- **Llama 2 7B Chat** - Alternative model for comparison
- **CodeLlama 7B** - For structured document generation

### Datasets Used
- **FDA Pharmaceuticals FAQ** (Hugging Face)
- **FDA Drug Labels Database**
- **FDA Adverse Event Reports**
- **FDA Orange Book**
- **EPA CompTox Chemical Registry**

### Training Configuration
- **LoRA Parameters**: Rank 8, Alpha 16
- **Learning Rate**: 2e-4
- **Batch Size**: 4 (Colab GPU limit)
- **Training Steps**: 1000-2000
- **Gradient Accumulation**: 4 steps

## 🔧 Configuration

### ngrok Setup
```bash
# Install ngrok in Colab
!pip install pyngrok

# Authenticate ngrok
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")

# Create tunnel
public_url = ngrok.connect(11434)
print(f"Ollama accessible at: {public_url}")
```

### Environment Variables
```python
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "mistral:7b-instruct"
DATASETS = [
    "fda_pharmaceuticals_faq",
    "fda_drug_labels",
    "fda_adverse_events",
    "fda_orange_book",
    "epa_chemical_registry"
]
```

## 📊 Performance Metrics

### Target Performance
- **Regulatory Compliance**: > 95% accuracy
- **Pharmaceutical Terminology**: > 90% correct usage
- **SOP Structure**: > 85% adherence to templates
- **Generation Time**: < 30 seconds per SOP

### Evaluation Criteria
- FDA 21 CFR Part 211 compliance
- ICH Q7 guidelines adherence
- GMP requirements validation
- ALCOA+ data integrity principles

## 🚨 Troubleshooting

### Common Issues

**Colab GPU Not Available:**
- Runtime → Change runtime type → GPU
- Check GPU status: `!nvidia-smi`

**ngrok Connection Issues:**
```bash
# Kill existing tunnels
!pkill ngrok

# Restart ngrok with new auth
ngrok.set_auth_token("NEW_TOKEN")
```

**Ollama Installation Issues:**
```bash
# Manual Ollama installation
!curl -fsSL https://ollama.com/install.sh | sh
!ollama serve &
```

**Memory Issues:**
- Reduce batch size to 2
- Use gradient checkpointing
- Clear GPU cache: `torch.cuda.empty_cache()`

### Colab-Specific Tips
- Use Colab Pro for longer runtimes
- Save checkpoints frequently
- Use persistent storage for large datasets
- Monitor GPU usage to avoid disconnections

## 📈 Model Optimization

### Fine-tuning Strategies
- **LoRA**: Low-Rank Adaptation for efficient training
- **QLoRA**: Quantized LoRA for memory efficiency
- **Gradient Checkpointing**: Trade compute for memory
- **Mixed Precision**: FP16 training for speed

### Dataset Preparation
- **Data Cleaning**: Remove duplicates and irrelevant content
- **Tokenization**: Use appropriate tokenizer for base model
- **Formatting**: Structure data for instruction tuning
- **Validation**: Ensure regulatory compliance of training data

## 🔒 Security & Compliance

### Data Privacy
- All training data is publicly available FDA datasets
- No patient PII or proprietary pharmaceutical data used
- Models trained for general SOP generation patterns

### Regulatory Compliance
- Training data validated against FDA guidelines
- Models tested for regulatory terminology accuracy
- Audit trail maintained for model development process

## 📚 References

### FDA Resources
- [FDA Open Data Portal](https://open.fda.gov)
- [FDA Drug Labels](https://dailymed.nlm.nih.gov)
- [FDA Orange Book](https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files)

### Pharmaceutical Standards
- FDA 21 CFR Part 211
- ICH Q7 Good Manufacturing Practice
- WHO GMP Guidelines
- EMA GMP Guidelines

## 🤝 Contributing

1. Test notebooks in Colab environment
2. Validate with FDA datasets
3. Ensure regulatory compliance
4. Update documentation
5. Submit pull request

### Development Guidelines
- Use clear variable names
- Add comments for complex operations
- Include error handling
- Test with multiple model sizes
- Validate output quality

## 📞 Support

For technical issues with the training pipeline:
- Check Colab runtime logs
- Verify ngrok tunnel status
- Test Ollama model loading
- Validate dataset accessibility

---

**⚠️ Regulatory Notice:** These models are trained for general SOP generation assistance. All generated content should be reviewed by qualified pharmaceutical professionals before use in regulated environments.