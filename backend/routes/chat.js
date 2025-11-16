const express = require('express');
const router = express.Router();
const fetchuser = require('../middleware/fetchuser');
const Chat = require('../models/Chat');
const Score = require('../models/Score');

// Route 1: Save a chat conversation - POST "/api/chat/save" (Login Required)
router.post('/save', fetchuser, async (req, res) => {
    try {
        const { messages } = req.body;
        const userId = req.user.id;

        const chat = new Chat({
            user: userId,
            messages: messages,
        });

        const savedChat = await chat.save();
        res.json({ success: true, chat: savedChat });
    } catch (error) {
        console.error("Save Chat Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

// Route 2: Fetch all chat conversations for a user - GET "/api/chat/history" (Login Required)
router.get('/history', fetchuser, async (req, res) => {
    try {
        const userId = req.user.id;
        const chats = await Chat.find({ user: userId }).sort({ date: -1 });
        res.json({ success: true, chats });
    } catch (error) {
        console.error("Fetch Chat History Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

// Route 3: Fetch a specific chat conversation by ID - GET "/api/chat/:id" (Login Required)
router.get('/:id', fetchuser, async (req, res) => {
    try {
        const chatId = req.params.id;
        const userId = req.user.id;

        const chat = await Chat.findOne({ _id: chatId, user: userId });

        if (!chat) {
            return res.status(404).json({ success: false, error: "Chat not found or unauthorized" });
        }

        res.json({ success: true, chat });
    } catch (error) {
        console.error("Fetch Specific Chat Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

// Route 4: Delete a specific chat conversation by ID - DELETE "/api/chat/:id" (Login Required)
router.delete('/:id', fetchuser, async (req, res) => {
    try {
        const chatId = req.params.id;
        const userId = req.user.id;

        const chat = await Chat.findOneAndDelete({ _id: chatId, user: userId });

        if (!chat) {
            return res.status(404).json({ success: false, error: "Chat not found or unauthorized" });
        }

        res.json({ success: true, message: "Chat deleted successfully" });
    } catch (error) {
        console.error("Delete Chat Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

// Route 5: Rate a response - POST "/api/chat/rate" (Login Required)
router.post('/rate', fetchuser, async (req, res) => {
    try {
        const { query_id, model, vote } = req.body;

        const score = new Score({
            query_id,
            model,
            vote,
        });

        await score.save();
        res.json({ success: true, message: "Vote saved successfully" });
    } catch (error) {
        console.error("Rate Response Error:", error.message);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

module.exports = router;
