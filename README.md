## Fuzz Lightyear

This repo contains a password fuzzer and a simple target web app used for testing it.

---

### Repo Contents

1. **FuzzLightyear.py** - The main command-line password fuzzer.
2. **AlsToyBarn/** - A Node.js test server that mimics a login system. It includes:
    - `server.js`: The Express backend
    - `users.json`: A fake user database with hardcoded sample credentials
    - `public/index.html`: A login page for manual testing

---

### Running the Server
To start the **Al's Toy Barn** sever:

```bash
cd AlsToyBarn
node server.js
```

Then visit http://localhost:3000 to see the login page

---

### API Endpoint

To test login attempts using the fuzzer, send a POST request to http://localhost:3000/login with the following JSON format:

```json
{
    "username": "[USERNAME]",
    "password": "[PASSWORD]"
}
```

---

### Login Behavior:
On a correct login, the server responds with:
- HTTP status code: 200 OK
- JSON message: { "message": "Login successful!" }

On an incorrect login, the server responds with:
- HTTP status code: 401 Unauthorized
- JSON message { "message": "Invalid credentials." }

---