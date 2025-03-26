const axios = require('axios');

async function testImageGeneration() {
    try {
        console.log('Sending request to generate image...');
        
        const response = await axios.post('http://localhost:3000/generate-image', {
            prompt: "A close-up photograph of green and black olives being harvested from an olive tree, with hands gently picking them"
        }, {
            timeout: 60000  // 60 second timeout
        });
        
        console.log('Image generation successful!');
        console.log('Response:', JSON.stringify(response.data, null, 2));
    } catch (error) {
        console.error('Error generating image:');
        if (error.response) {
            console.error('Response data:', error.response.data);
            console.error('Response status:', error.response.status);
            if (error.response.data.details) {
                console.error('Error details:', error.response.data.details);
            }
        } else {
            console.error('Error:', error.message);
        }
    }
}

console.log('Starting test...');
testImageGeneration(); 