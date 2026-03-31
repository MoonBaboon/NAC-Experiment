# NAC-Lab
This is a custom Nework Access Control implementation utilizing Docker, FreeRadius, Postgresql, Redis and FastAPI.

## Overview:
The design structure of the services looks as follows:

[![NAC Architecture](resources/nac-image.png)]

```text
.
├── api
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml
├── freeradius
│   └── config
│       ├── mods-enabled
│       │   └── rest
│       └── sites-enabled
│           └── default
├── postgres
│   ├── data
│   └── init.sql
├── README.md
└── redis

## Configuration and Setup:
- The `.env.example` file in root folder must be renamed as `.env`
- Values in the `.env` files can be configured

- Run `docker-compose up -d`, you should see all 4 services running and being healthy after 20-30 seconds by running `docker ps`