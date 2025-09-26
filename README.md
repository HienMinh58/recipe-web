Recipe Web App with AI Chat Bot
Overview

This project is a Recipe Web Application built with Flask.
It allows users to:

Browse and search for recipes

View detailed recipe information

Interact with an integrated AI Chat Bot powered by multi-agent architecture and Retrieval-Augmented Generation (RAG) for recipe-related queries

Recipe data is embedded into Milvus vector database for semantic search, first hosted locally with Docker Compose and later migrated to Zilliz Cloud.
The application is deployed on Vercel for easy access.

Features

🔍 Search Recipes by ingredients or keywords

📖 Browse Recipes from the collection

🥘 Recipe Details with full instructions and ingredients

🤖 AI Chat Bot for intelligent Q&A support

📦 Milvus/Zilliz Cloud Integration with embeddings for semantic search

🚀 Vercel Deployment for fast and reliable hosting

Tech Stack

Backend: Flask (Python)

Database: Milvus (local via Docker Compose) → Zilliz Cloud

AI/ML: Sentence Transformers, RAG, Multi-Agent Architecture

Deployment: Vercel

Setup & Installation
1. Clone the repository
git clone https://github.com/HienMinh58/web.git
cd web

2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Linux/Mac

3. Install dependencies
pip install -r requirements.txt

4. Run the Flask app locally
flask run


The app will be available at: http://localhost:5000

Deployment

Local development uses Docker Compose to run Milvus.

Embeddings are migrated to Zilliz Cloud for production.

Future Improvements

User authentication (login & register)

Recipe rating and comments

Personalized recommendations

License

This project is licensed under the MIT License.
