# 🔍 Information Retrieval Project – Wikipedia Search Engine

**By:** Naama Maimon & Stav Barak  

## 📌 Project Overview
This project implements a **search engine for Wikipedia** using Python, deployed on **Google Cloud Platform (GCP)**, indexing over **6 million articles**.  
The system uses **inverted indexes**, multiple ranking functions, and weighting strategies to optimize both **search precision** and **runtime performance**.

---

## 🎯 Objectives
- Build efficient **body** and **title** inverted indexes for Wikipedia articles.
- Implement multiple **ranking methods** and evaluate their accuracy and runtime.
- Combine ranking scores from **title**, **body**, and **PageRank** to improve results.
- Deploy the search engine on **GCP** for large-scale performance testing.

---

## 📂 Project Structure
1. **Inverted Index (GCP)** – Preprocessed `body_index` and `title_index` stored as pickle files.  
2. **Search Frontend** – Reads indexes, document metadata, and integrates ranking results.  
3. **Backend** – Contains all ranking methods and scoring logic.  
4. **Project Report** – Detailed methodology, tests, and performance results.

---

## 🛠 Methodology

### Indexing
- Created **two inverted indexes**:
  - `body_index` – indexing article content.
  - `title_index` – indexing article titles.
- Generated supporting dictionaries:
  - `doc_id → title`
  - `doc_id → PageRank score`
- All stored as **pickle** files for fast retrieval.

### Ranking Methods Tested
1. **Cosine Similarity**  
   - Tested separately on body and title indexes.  
   - Low precision (0.07467) and slow runtime (~9.58s).  

2. **BM25**  
   - Better balance between term frequency and document length.  
   - Precision improved to 0.221 with weights: `title=0.6`, `body=0.4`.

3. **Dynamic Query Length Weighting**  
   - Adjusted weights depending on query length:  
     - 1 term → full weight to title index.  
     - 2–3 terms → `title=0.6`, `body=0.4`.  
     - ≥4 terms → full weight to body index.  

4. **PageRank Integration**  
   - Normalized scores (log-scaled).  
   - Final score = `0.6 * BM25 score + 0.4 * PageRank score`.

5. **Heap-based Sorting**  
   - Replaced standard sort with heap sort for top-100 results.  
   - Reduced runtime significantly while keeping precision stable.

---

## 📌 Observations
- **Short queries** (1–2 tokens) perform best when using **title index** only.  
- **Longer queries** (≥4 tokens) require **body index** for better recall.  
- PageRank helps in boosting authoritative pages.  
- Heap-based sorting significantly reduced search time.  

---

## 📈 Example Queries & Performance
**High accuracy:**
- `genetics`  
- `snowboard`  
- `When was the United Nations founded?`  
- `Describe the process of water erosion`

**Low accuracy (rare phrases):**
- `Who is considered the "Father of the United States"?`  
  - Precision: 0  
  - Cause: very low frequency of the full phrase in indexed documents.

---

## 🚀 Possible Improvements
- Query expansion using synonyms and related terms.
- Better handling of rare multi-word phrases.
- Experiment with learning-to-rank models.

---

## 📜 License
This project was developed as part of the **Information Retrieval course** at Ben-Gurion University.  
Data was sourced from the **English Wikipedia dump**.
