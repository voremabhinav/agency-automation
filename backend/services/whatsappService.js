const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

// Initialize the headless browser
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Generate QR Code for the server terminal
client.on('qr', (qr) => {
    console.log('\n=== ACTION REQUIRED: Scan this QR code to authenticate the Node.js Server ===\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ Express Headless WhatsApp Client is connected and ready!');
});

// Boot the client
client.initialize();

// Helper function to dispatch messages
const sendWhatsAppMessage = async (phoneNumber, message) => {
    try {
        const chatId = `${phoneNumber}@c.us`;
        await client.sendMessage(chatId, message);
        return true;
    } catch (error) {
        console.error('[ERROR] WhatsApp Service Failed:', error);
        throw error;
    }
};

module.exports = { sendWhatsAppMessage };