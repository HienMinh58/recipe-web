Recipe Web App with AI Chat Bot
Overview
Dive into this exciting Recipe Web Application crafted with Flask! It empowers users to:

Effortlessly browse and search for mouthwatering recipes
Dive deep into detailed recipe info, from prep to perfection
Engage with a smart AI Chat Bot, fueled by cutting-edge multi-agent architecture and Retrieval-Augmented Generation (RAG), ready to tackle all your recipe questions!

Recipe data is cleverly embedded into the Milvus vector database for lightning-fast semantic search—starting locally with Docker Compose and seamlessly upgraded to Zilliz Cloud. Plus, it's all deployed on Vercel for super-smooth, hassle-free access.
Features
🔍 Search Recipes by ingredients or keywords—find your next culinary adventure in seconds!
📖 Browse Recipes from our vibrant collection of tasty ideas
🥘 Recipe Details packed with step-by-step instructions and essential ingredients
🤖 AI Chat Bot delivering intelligent, on-the-spot Q&A support
📦 Milvus/Zilliz Cloud Integration with powerful embeddings for spot-on semantic search
🚀 Vercel Deployment ensuring fast, reliable, and always-up hosting
Tech Stack

Backend: Flask (Python) for robust, efficient performance
Database: Milvus (kickstarted locally via Docker Compose) → Zilliz Cloud for scalable power
AI/ML: Sentence Transformers, RAG, and Multi-Agent Architecture for next-level intelligence
Deployment: Vercel for seamless, high-speed delivery

Setup & Installation


Clone the repository
git clone https://github.com/HienMinh58/web.git
cd web


Create and activate virtual environment
py -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Linux/Mac


Install dependencies
pip install -r requirements.txt


Run the Flask app locally
flask run
Fire it up and head to: http://localhost:5000 for instant action!


Deployment
For local dev, spin up Milvus effortlessly with Docker Compose. When it's go-time, embeddings shift to Zilliz Cloud for production-grade awesomeness.
Future Improvements

User authentication (login & register) to make it personal
Recipe rating and comments for community vibes
Personalized recommendations tailored just for you

License
This project is licensed under the MIT License—feel free to innovate and share!
