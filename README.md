# Recipe Web App with AI Chat Bot

## Overview

Get ready to explore this vibrant Recipe Web Application, built with Flask! It’s your go-to platform to:

- **Browse and search** for delicious recipes with ease
- Dive into **detailed recipe guides**, complete with step-by-step instructions
- Chat with a **clever AI Chat Bot**, powered by a multi-agent architecture and Retrieval-Augmented Generation (RAG), ready to answer all your recipe queries!

The app leverages recipe data embedded in the **Milvus vector database** for lightning-fast semantic search, initially hosted locally via Docker Compose and later upgraded to **Zilliz Cloud** for production. Deployed on **Vercel**, it’s accessible, fast, and reliable!

## Features

🔍 **Recipe Search**: Hunt for recipes by ingredients or keywords in a snap  
📖 **Recipe Browsing**: Explore a delightful collection of culinary creations  
🥘 **Recipe Details**: Get full instructions and ingredient lists for every dish  
🤖 **AI Chat Bot**: Ask away and get smart, instant recipe advice  
📦 **Milvus/Zilliz Cloud**: Semantic search powered by advanced embeddings  
🚀 **Vercel Deployment**: Smooth, scalable hosting for a seamless experience  

## Tech Stack

- **Backend**: Flask (Python) – lightweight and powerful  
- **Database**: Milvus (local via Docker Compose) → Zilliz Cloud for production  
- **AI/ML**: Sentence Transformers, RAG, Multi-Agent Architecture for intelligent interactions  
- **Deployment**: Vercel for fast, dependable hosting  

## Setup & Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/HienMinh58/recipe-web.git
   cd recipe-web
   ```

2. **Set Up Virtual Environment**  
   ```bash
   py -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask App Locally**  
   ```bash
   flask run
   ```

   Visit `http://localhost:5000` to see the app in action!

## License

This project is licensed under the MIT License – feel free to use, modify, and share!
