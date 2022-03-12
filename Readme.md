

## Run for development

Start the frontend with:

```
cd frontend
npm use 16.14.0
npm run start
```

Start the backend with:

```
uvicorn oplc.api:app --reload
```

This will launch the frontend server at `http://localhost:3000/` and the backend
server at `http://localhost:8000/`, but the two services are set up to work
behind a reverse proxy that serve them at the same origin, the front at
`http://localhost/` and the backend at `http://localhost/api/`.

To run the application during development, run a nginx server locally that does
the relevant redirections, like:

```
server {

    server_name localhost;
    listen_port 2000;

    location / {
        proxy_pass http://localhost:3000/;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
    }
}
```

