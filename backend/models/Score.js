const mongoose = require('mongoose');
const { Schema } = mongoose;

const ScoreSchema = new Schema({
    query_id: {
        type: String,
        required: true,
        unique: true
    },
    model: {
        type: String,
        required: true
    },
    vote: {
        type: String,
        required: true
    },
    timestamp: {
        type: Date,
        default: Date.now
    }
});

const Score = mongoose.model('score', ScoreSchema);
module.exports = Score;
