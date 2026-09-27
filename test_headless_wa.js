import pkg from 'whatsapp-web.js';
const { Client, LocalAuth } = pkg;
import qrcode from 'qrcode-terminal';

console.log("Initializing headless WhatsApp browser...");

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true, // This makes it run invisibly on a cloud server!
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Generates a QR code in your terminal
client.on('qr', (qr) => {
    console.log('Open WhatsApp on your phone -> Linked Devices -> Scan this QR code:');
    qrcode.generate(qr, { small: true });
});

// Fires when the connection is successful
client.on('ready', () => {
    console.log('Headless Client is ready! Sending test message...');
    
    // REPLACE THIS with your exact phone number (Country code + Number, NO PLUS SIGN)
    const phoneNumber = "916304563008"; 
    const chatId = `${phoneNumber}@c.us`;
    
    client.sendMessage(chatId, 'This is a headless production test from the agency!')
        .then(() => {
            console.log(`[SUCCESS] Message routed exactly to: ${chatId}`);
            console.log('Waiting 5 seconds for the network to sync...');
            
            // 5-second delay to guarantee the sync
            setTimeout(() => {
                process.exit(0);
            }, 5000);
        })
        .catch((err) => console.error('[ERROR] Failed to send:', err));
});

client.initialize();