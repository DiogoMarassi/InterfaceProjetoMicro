myapp/
│
├── app/
│   ├── __init__.py 
│   ├── config.py               # Configurações (ex: ambiente, banco de dados)
│   │
│   ├── models/                 # Modelos 
│   │   ├── __init__.py
│   │   └── user.py             
│   │
│   ├── services/               
│   │   ├── __init__.py
│   │   └── user_service.py
│   │
│   ├── controllers/           # Rotas e lógica de requisições
│   │   ├── __init__.py
│   │   └── user_controller.py
│   │
│   ├── schemas/               # Serialização e validações com Marshmallow
│   │   ├── __init__.py
│   │   └── user_schema.py
│   │
│   ├── db/                    # Conexão e gerenciamento do banco
│   │
│   └── templates/             
│       └── home.html
│
├── static/                    
│
├── run.py                     # Ponto de entrada 
├── requirements.txt
└── .env                       
