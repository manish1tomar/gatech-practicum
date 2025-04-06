#                                Prerequisites:
Project Setup
1. Unzip the file provided.
2. Verify the directory structure
    gatech-practicum -> chromadb
    gatech-practicum -> chromadb -> docs
    gatech-practicum -> chromadb -> general_chroma_db
    gatech-practicum -> readme.md

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

#                                Chatbot Startup
1. Update the below database parameters in chromadb/set_env.py file
    SERVER = ''
    DATABASE = ''
    USERNAME = ''
    PASSWORD = ''
2. cd .\chromadb\
3. streamlit run .\chatbot_v1.py
    This will open a chatbot window in web explorer - chrome, edge, etc.

#                                App re-deploy
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

#                                Versions
altair==5.5.0
annotated-types==0.7.0
anyio==4.8.0
asgiref==3.8.1
attrs==25.1.0
backoff==2.2.1
bcrypt==4.3.0
blinker==1.9.0
blis==1.2.0
build==1.2.2.post1
cachetools==5.5.2
catalogue==2.0.10
certifi==2025.1.31
charset-normalizer==3.4.1
chroma-hnswlib==0.7.6
chromadb==0.6.3
click==8.1.8
cloudpathlib==0.21.0
colorama==0.4.6
coloredlogs==15.0.1
confection==0.1.5
cymem==2.0.11
Deprecated==1.2.18
distro==1.9.0
durationpy==0.9
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85
et_xmlfile==2.0.0
fastapi==0.115.11
filelock==3.17.0
flatbuffers==25.2.10
fsspec==2025.2.0
gitdb==4.0.12
GitPython==3.1.44
google-auth==2.38.0
googleapis-common-protos==1.69.1
grpcio==1.70.0
h11==0.14.0
httpcore==1.0.7
httptools==0.6.4
httpx==0.28.1
huggingface-hub==0.29.2
humanfriendly==10.0
idna==3.10
importlib_metadata==8.5.0
importlib_resources==6.5.2
Jinja2==3.1.6
joblib==1.4.2
jsonschema==4.23.0
jsonschema-specifications==2024.10.1
kubernetes==32.0.1
langcodes==3.5.0
language_data==1.3.0
marisa-trie==1.2.1
markdown-it-py==3.0.0
MarkupSafe==3.0.2
mdurl==0.1.2
mmh3==5.1.0
monotonic==1.6
mpmath==1.3.0
murmurhash==1.0.12
narwhals==1.29.1
networkx==3.4.2
numpy==2.2.3
oauthlib==3.2.2
ollama==0.4.7
onnxruntime==1.20.1
openpyxl==3.1.5
opentelemetry-api==1.30.0
opentelemetry-exporter-otlp-proto-common==1.30.0
opentelemetry-exporter-otlp-proto-grpc==1.30.0
opentelemetry-instrumentation==0.51b0
opentelemetry-instrumentation-asgi==0.51b0
opentelemetry-instrumentation-fastapi==0.51b0
opentelemetry-proto==1.30.0
opentelemetry-sdk==1.30.0
opentelemetry-semantic-conventions==0.51b0
opentelemetry-util-http==0.51b0
orjson==3.10.15
overrides==7.7.0
packaging==24.2
pandas==2.2.3
pillow==11.1.0
posthog==3.19.0
preshed==3.0.9
protobuf==5.29.3
pyarrow==19.0.1
pyasn1==0.6.1
pyasn1_modules==0.4.1
pydantic==2.10.6
pydantic_core==2.27.2
pydeck==0.9.1
Pygments==2.19.1
pyodbc==5.2.0
PyPika==0.48.9
pyproject_hooks==1.2.0
pyreadline3==3.5.4
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
pytz==2025.1
PyYAML==6.0.2
referencing==0.36.2
regex==2024.11.6
requests==2.32.3
requests-oauthlib==2.0.0
rich==13.9.4
rpds-py==0.23.1
rsa==4.9
safetensors==0.5.3
scikit-learn==1.6.1
scipy==1.15.2
sentence-transformers==3.4.1
shellingham==1.5.4
six==1.17.0
smart-open==7.1.0
smmap==5.0.2
sniffio==1.3.1
spacy==3.8.4
spacy-legacy==3.0.12
spacy-loggers==1.0.5
srsly==2.5.1
starlette==0.46.0
streamlit==1.43.0
sympy==1.13.1
tenacity==9.0.0
thinc==8.3.4
threadpoolctl==3.5.0
tokenizers==0.21.0
toml==0.10.2
torch==2.6.0
tornado==6.4.2
tqdm==4.67.1
transformers==4.49.0
typer==0.15.2
typing_extensions==4.12.2
tzdata==2025.1
urllib3==2.3.0
uvicorn==0.34.0
wasabi==1.1.3
watchdog==6.0.0
watchfiles==1.0.4
weasel==0.4.1
websocket-client==1.8.0
websockets==15.0.1
wrapt==1.17.2
zipp==3.21.0
