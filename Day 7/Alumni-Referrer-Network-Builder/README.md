use version python 3.11.9

py -3.11 -m venv venv_py311

# Activate the environment
venv_py311\Scripts\activate

# Install compatible numpy first
pip install "numpy>=1.23.2,<2.0.0"

# Install core packages
pip install streamlit pymongo python-dotenv requests plotly networkx

# Install AI packages
pip install google-generativeai
pip install "langchain>=0.3.0,<0.4.0"
pip install "langchain-community>=0.3.0,<0.4.0" 
pip install "langchain-google-genai>=2.0.0,<3.0.0"

# Install ML packages
pip install pandas scikit-learn sentence-transformers faiss-cpu

# Install remaining packages
pip install beautifulsoup4 Pillow altair motor dnspython



# Install with the fixed requirements
pip install -r requirements.txt



streamlit run app.py


-go to admin panel add the csv file i add in this repo
-create student
-check tabwise based on skill