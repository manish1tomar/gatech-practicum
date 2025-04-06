============================================================================
                                Prerequisites:
============================================================================
Project Setup
1. Unzip the file provided.
2. Verify the directory structure
    gatech-practicum
       -> chromadb
          ->  docs
          ->  general_chroma_db
       -> readme.md

SQL Server Setup
1. Execute the sql script chromadb/sql/scripts/create_fcsdb_objects_ddl.sql
    This step creates 5 tables and 1 view.
2. Import data in the tables using import wizard in SQL utility. (Or) Load CSV files independently into the tables created from Step1 using the command below,
		BULK INSERT YourTableName
		FROM 'C:\Path\To\YourFile.csv'
		WITH (
			FIELDTERMINATOR = ',',
			ROWTERMINATOR = '\n',
			FIRSTROW = 2 -- Skip the header row
		);
	Modify the Table name and Pathname and repeat this for all the 5 tables.
	Data for Course Requirements table is available in chromadb/sql/data/ directory.
	For Grades data representing Grades 9,10,11,12, utilize data from FCS provided CSV Files.
3. Execute the sql script chromadb/sql/scripts/chatbot.sql
   This step will create all the necessary data for chatbot functionality.

Python Libraries setup
1. Run the below commands in Python environment terminal
    pip install chromadb sentence_transformers pillow streamlit spacy pandas ollama openpyxl pyodbc
    python -m spacy download en_core_web_sm

Ollama Setup
1. Install Ollama
2. Open the terminal and run the command
    ollama pull llama2
    This will download llama2 model, may take some time.
3. Verify the model
    ollama list
    This should list llama2 model

============================================================================
                                Chatbot Startup
============================================================================
1. Update the below database parameters in chromadb/set_env.py file
    SERVER = ''
    DATABASE = ''
    USERNAME = ''
    PASSWORD = ''
2. cd .\chromadb\
3. streamlit run .\chatbot_v1.py
    This will open a chatbot window in web explorer - chrome, edge, etc.

============================================================================
                                App re-deploy
============================================================================
How to reset the chromadb vector database ?
This reset will be needed if we add/delete/update any questions or answers in files present in chromadb/docs/
1. Delete all the files present in chromadb/general_chroma_db folder.
2. Run create_db_general.py in chromadb/ folder
3. Run create_db_dual.py in chromadb/ folder
4. Run create_db_scholarship.py in chromadb/ folder
5. Run create_db_counselling.py in chromadb/ folder
6. Run create_db_grad_reqs.py in chromadb/ folder
7. cd .\chromadb\
8. streamlit run .\chatbot_v1.py
    This will open a chatbot window in web explorer - chrome, edge, etc.

How to change the embedding model ?
Replace "all-MiniLM-L6-v2" to another model in files:
    chatbot_v1.py
    create_db_general.py
    create_db_dual.py
    create_db_scholarship.py
    create_db_counselling.py
    create_db_grad_reqs.py
in chromadb/ folder.
