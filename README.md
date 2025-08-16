# LinkedIn LLM Post Generator

🚀 An AI-powered LinkedIn Post Caption Generator that leverages Large Language Models (LLMs) to create professional, creative, and engaging post captions. This project combines LinkedIn post data scraping with LLM-based text generation.

---

## 📌 Problem Statement
Creating impactful LinkedIn posts consistently is time-consuming and requires creativity. Many professionals struggle to write captions that are engaging, audience-focused, and tailored to LinkedIn’s professional environment.  

This project solves that problem by **scraping real LinkedIn post data** and using **LLM models (Gemini API & GPT-2)** to automatically generate effective LinkedIn post captions.

---

## 🛠️ Project Workflow
1. **Scraping Data**  
   - `Linkedin-post-Scrapper.py` scrapes LinkedIn posts and stores them in a structured dataset (`linkedin_data.csv`).

2. **Dataset**  
   - `linkedin_data.csv` contains scraped LinkedIn post text used for training and fine-tuning.

3. **LLM Models for Caption Generation**  
   - `llm_gemini_api.py` → Uses Google Gemini API to generate captions.  
   - `llm_gpt2.py` → Uses Hugging Face’s GPT-2 model to generate captions.  

4. **Results & Example**  
   - `Sample-input-output.png` shows sample input prompts and generated LinkedIn captions.

---

## 📂 Project Files
- **`Linkedin-post-Scrapper.py`** → Scrapes LinkedIn posts into a CSV dataset.  
- **`linkedin_data.csv`** → Scraped LinkedIn data used as training/analysis input.  
- **`llm_gemini_api.py`** → Caption generation using Google Gemini API.  
- **`llm_gpt2.py`** → Caption generation using GPT-2 model.  
- **`Sample-input-output.png`** → Example of generated LinkedIn captions.  
- **`README.md`** → Project documentation.

---

## ⚙️ How to Run
1. Clone this repository  
   ```bash
   git clone https://github.com/Chandrashekar0123/linkedin-llm-postgen.git
   cd linkedin-llm-postgen

## 🚀 Future Improvements

Fine-tune LLM models on larger LinkedIn datasets.

Add sentiment/emotion-based caption generation.

Deploy via Streamlit/Flask for interactive UI.
