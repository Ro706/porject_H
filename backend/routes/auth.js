const express = require('express');
require('dotenv').config();
const router = express.Router();
const User = require('../models/User');
const fetchuser = require('../middleware/fetchuser');
const bcrypt = require('bcryptjs');
const { body, validationResult } = require('express-validator');
const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET ;

// Route 1: Create a User - POST "/api/auth/signup" (No Auth Required)
router.post(
    '/signup',
    [
        body('email', 'Enter a valid email').isEmail(),
        body('name', 'Name must be at least 3 characters').isLength({ min: 3 }),
        body('password', 'Password must be at least 5 characters').isLength({ min: 5 }),
    ],
    async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ success: false, errors: errors.array() });
        }

        try {
            // Check if user already exists
            const existingUser = await User.findOne({ email: req.body.email });
            if (existingUser) {
                return res.status(400).json({ success: false, error: "User with this email already exists" });
            }

            // Hash the password
            const salt = await bcrypt.genSalt(10);
            const secPass = await bcrypt.hash(req.body.password, salt);

            // Create user
            const user = new User({
                name: req.body.name,
                email: req.body.email,
                password: secPass,
            });

            await user.save();

            // Generate JWT Token
            const data = { user: { id: user.id } };
            const authtoken = jwt.sign(data, JWT_SECRET);

            res.json({ success: true, authtoken, name: user.name });
        } catch (error) {
            console.error("Signup Error:", error.message);
            res.status(500).json({ success: false, error: "Internal Server Error" });
        }
    }
);

// Route 2: Authenticate User - POST "/api/auth/login" (No Auth Required)
router.post('/login', [
    body('email', 'Enter a valid email').isEmail(),
    body('password', 'Password cannot be blank').exists(),
], async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ success: false, errors: errors.array() });
    }

    try {
        const user = await User.findOne({ email: req.body.email });
        if (!user) {
            return res.status(400).json({ success: false, error: "Invalid Credentials" });
        }

        const passwordCompare = await bcrypt.compare(req.body.password, user.password);
        if (!passwordCompare) {
            return res.status(400).json({ success: false, error: "Invalid Credentials" });
        }

        // Generate JWT Token
        const data = { user: { id: user.id } };
        const authtoken = jwt.sign(data, JWT_SECRET);

        res.json({ success: true, authtoken, name: user.name, email: user.email });
    } catch (error) {
        console.error("Login Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

// Route 3: Get Logged-in User - POST "/api/auth/getuser" (Login Required)
router.post('/getuser', fetchuser, async (req, res) => {
    try {
        const userId = req.user.id;
        const user = await User.findById(userId).select("-password");

        if (!user) {
            return res.status(404).json({ success: false, error: "User not found" });
        }

        res.json({ success: true, user });
    } catch (error) {
        console.error("GetUser Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

module.exports = router;