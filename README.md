# MembershipAPI

### Usage

1. Install Docker and Docker Compose on your server.
2. Download `client_secrets.template.json` and edit according to your IdP settings.
3. Rename it to `client_secrets.json`.
4. Run the following commands to download `docker-compose.yml`:

```bash
wget https://raw.githubusercontent.com/stsatw/MembershipAPI/main/docker-compose.yml
```

5. Configure your environment variables in a `.env` file as needed.

```
OAUTH_CONFIG=</path/to/client_secrets.json>
PORT=8080
```

6. Start the service using Docker Compose:

```bash
docker-compose up -d
# OR
docker compose up -d
```

7. Access the API at `http://<your-server-ip>:<PORT>/api`.

### Authentication

- `Authorization Bearer <token>` header is required for all endpoints except `/` and `/verify_code/<code>`.
- Generated codes are valid for 5 minutes and can be used infinitely many times.

### API Endpoints

- `GET /`: Health check endpoint.
- `GET /me`: Retrieve information about the current bearer token.
- `GET /get_code`: Get a code for authentication.
- `GET /verify_code/<code>`: Verify the provided code, returns the user's email & name if valid.