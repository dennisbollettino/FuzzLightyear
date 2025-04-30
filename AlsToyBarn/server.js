const express = require('express');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static('public'));  // Serve index.html

// Load users from JSON
function loadUsers() {
    const data = fs.readFileSync('users.json', 'utf8');
    return JSON.parse(data);
}

// Login route
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const users = loadUsers();

    if (users[username] === password) {
        res.status(200).json({ message: "Login successful!" });
    } else {
        res.status(401).json({ message: "Invalid credentials." });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Al's Toy Barn running at http://localhost:${PORT}`);
});
