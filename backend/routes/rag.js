const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');

router.post('/query', (req, res) => {
    const { query } = req.body;
    console.log('Received query:', query);

    if (!query) {
        return res.status(400).json({ error: 'Query is required' });
    }

    const pythonProcess = spawn('python', [path.join(__dirname, '..', 'node', 'rag_query.py')]);

    let stdoutBuffer = '';
    let stderr = '';
    let finalAnswer = null;
    let rewardScore = null;

    pythonProcess.stdin.write(query);
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        stdoutBuffer += data.toString();
        let newlineIndex;
        while ((newlineIndex = stdoutBuffer.indexOf('\n')) !== -1) {
            const line = stdoutBuffer.substring(0, newlineIndex).trim();
            stdoutBuffer = stdoutBuffer.substring(newlineIndex + 1);

            if (line) {
                // Only attempt to parse as JSON if it looks like JSON
                if (line.startsWith('{') && line.endsWith('}')) {
                    try {
                        const jsonMessage = JSON.parse(line);
                        if (jsonMessage.type === "final_answer") {
                            finalAnswer = jsonMessage.answer;
                        } else if (jsonMessage.type === "reward_score") {
                            rewardScore = jsonMessage.score;
                        }
                    } catch (e) {
                        // If JSON parsing fails, log it but don't treat as process update
                        console.log('Python stdout (malformed JSON or non-JSON):', line);
                    }
                } else {
                    // Log non-JSON lines but don't treat as process update
                    console.log('Python stdout (non-JSON):', line);
                }
            }
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error('Python stderr:', data.toString());
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);
        if (code !== 0) {
            console.error('Error executing Python script:', stderr);
            return res.status(500).json({ error: 'Failed to process query', details: stderr });
        }

        if (finalAnswer !== null && rewardScore !== null) {
            console.log('Successfully processed query:', { finalAnswer, rewardScore });
            res.json({ answer: finalAnswer, reward_score: rewardScore });
        } else {
            console.error('Failed to get final answer or reward score from Python script. Full stdout buffer:', stdoutBuffer);
            res.status(500).json({ error: 'Failed to parse Python script output', details: stdoutBuffer });
        }
    });
});


router.post('/compare', (req, res) => {
    const { query } = req.body;
    console.log('Received query for comparison:', query);

    if (!query) {
        return res.status(400).json({ error: 'Query is required' });
    }

    const pythonProcess = spawn('python', [path.join(__dirname, '..', 'node', 'rag_query_compare.py')]);

    let stdoutBuffer = '';
    let stderr = '';

    pythonProcess.stdin.write(query);
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        stdoutBuffer += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error('Python stderr:', data.toString());
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script for comparison exited with code ${code}`);
        if (code !== 0) {
            console.error('Error executing Python script for comparison:', stderr);
            return res.status(500).json({ error: 'Failed to process query for comparison', details: stderr });
        }

        try {
            const result = JSON.parse(stdoutBuffer);
            console.log('Successfully processed query for comparison:', result);
            res.json(result);
        } catch (e) {
            console.error('Failed to parse Python script output for comparison. Full stdout buffer:', stdoutBuffer);
            res.status(500).json({ error: 'Failed to parse Python script output for comparison', details: stdoutBuffer });
        }
    });
});

module.exports = router;

