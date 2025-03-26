const express = require('express');
const { ReveAI } = require('reve-sdk');
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

const app = express();
app.use(express.json());

// Log environment variables for debugging (redacting sensitive info)
console.log('Environment check:', {
    projectId: process.env.REVE_PROJECT_ID,
    hasAuth: !!process.env.REVE_AUTH_TOKEN,
    hasCookie: !!process.env.REVE_COOKIE
});

// Initialize REVE with authentication options and project ID
const reve = new ReveAI({
    auth: {
        authorization: process.env.REVE_AUTH_TOKEN,
        cookie: process.env.REVE_COOKIE
    },
    projectId: 'dab7963f-d96e-4d1b-b99b-714f73564afd',  // Hardcode for now
    baseUrl: 'https://preview.reve.art',
    verbose: true
});

app.post('/generate-image', async (req, res) => {
    try {
        const { prompt } = req.body;
        if (!prompt) {
            return res.status(400).json({ error: 'Prompt is required' });
        }

        console.log('Generating image for prompt:', prompt);

        // Generate image using REVE
        const result = await reve.generateImage({
            prompt: prompt,
            negative_prompt: "blurry, low quality, distorted, watermark",
            width: 1024,
            height: 1024,
            guidance_scale: 7.5,
            num_inference_steps: 50
        });

        console.log('Generation result:', result);

        // Check if we have image URLs
        if (!result.imageUrls || result.imageUrls.length === 0) {
            throw new Error('No image URLs returned from generation');
        }

        // Download the first image
        const imageUrl = result.imageUrls[0];
        let imageData;

        if (imageUrl.startsWith('data:')) {
            // Handle base64 data URL
            const base64Data = imageUrl.split(',')[1];
            imageData = Buffer.from(base64Data, 'base64');
        } else {
            // Handle regular URL
            const imageResponse = await axios.get(imageUrl, {
                responseType: 'arraybuffer'
            });
            imageData = Buffer.from(imageResponse.data);
        }

        // Create images directory if it doesn't exist
        const imagesDir = path.join(__dirname, '..', 'images');
        await fs.mkdir(imagesDir, { recursive: true });

        // Save image with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '');
        const filename = `reve-${timestamp}.png`;
        const filepath = path.join(imagesDir, filename);

        // Save the image
        await fs.writeFile(filepath, imageData);

        res.json({ 
            success: true, 
            filename: filename,
            filepath: filepath,
            seed: result.seed,
            prompt: result.prompt
        });

    } catch (error) {
        console.error('Detailed error:', error);
        res.status(500).json({ 
            error: 'Failed to generate image',
            details: error.message,
            type: error.type,
            stack: error.stack
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`REVE image service running on port ${PORT}`);
}); 