import { GoogleGenerativeAI } from '@google/generative-ai';
import whatsapp from 'whatsapp-web.js';
import qrcode from 'qrcode-terminal';
import nodemailer from 'nodemailer';
import cron from 'node-cron';
import dotenv from 'dotenv';

dotenv.config();

// Validate environment variables
const requiredEnvVars = ['GEMINI_API_KEY', 'SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASS'];
for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    console.error(`? Missing required environment variable: ${envVar}`);
    process.exit(1);
  }
}

// Setup & Initialization
const ai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const emailTransporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT),
  secure: false,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

const { Client, LocalAuth } = whatsapp;
const waClient = new Client({
  authStrategy: new LocalAuth({
    dataPath: './.wwebjs_auth'
  }),
  puppeteer: {
    headless: false,
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu'
    ]
  }
});

waClient.on('qr', (qr) => {
  qrcode.generate(qr, { small: true });
});

waClient.on('ready', () => {
  console.log('? WhatsApp Client is ready and listening for incoming messages!');
  process.stdin.resume();
});

waClient.on('error', (err) => {
  console.error('? WhatsApp client error:', err);
});

// AI Reply Engine
async function generateAIReply(incomingMessage, channel) {
  const prompt = `
You are an automated customer support AI for our business.
Generate a polite, professional, and concise response to the following customer message.
Keep WhatsApp messages under 3 sentences. For email, include a clear greeting and sign-off.

Channel: ${channel}
Customer Message: "${incomingMessage}"
`;

  try {
    const model = ai.getGenerativeModel({ model: 'gemini-3.6-flash' });
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text().trim();
  } catch (error) {
    console.error('AI Generation Error:', error);
    return 'Thank you for reaching out! We have received your message and will get back to you shortly.';
  }
}

// WhatsApp Incoming Auto-Reply
waClient.on('message', async (msg) => {
  if (
    msg.from.endsWith('@g.us') || 
    msg.from.endsWith('@newsletter') || 
    msg.isStatus || 
    msg.from === 'status@broadcast'
  ) {
    return;
  }

  console.log(`[WhatsApp Incoming] ${msg.from}: ${msg.body}`);

  try {
    const replyText = await generateAIReply(msg.body, 'whatsapp');
    await waClient.sendMessage(msg.from, replyText);
    console.log(`[WhatsApp Sent] to ${msg.from}: ${replyText}`);
  } catch (err) {
    console.error('Failed to send reply:', err);
  }
});

// Helper Functions
async function sendWhatsAppMessage(phone, message) {
  try {
    const formattedPhone = phone.includes('@c.us') ? phone : `${phone}@c.us`;
    await waClient.sendMessage(formattedPhone, message);
    console.log(`[Reminder Sent - WA] to ${phone}`);
  } catch (err) {
    console.error('Error sending WA message:', err);
  }
}

async function sendEmail(to, subject, body) {
  try {
    await emailTransporter.sendMail({
      from: process.env.SMTP_USER,
      to,
      subject,
      text: body,
    });
    console.log(`[Reminder Sent - Email] to ${to}`);
  } catch (err) {
    console.error('Error sending Email:', err);
  }
}

// Scheduled Cron Alerts
cron.schedule('0 9 * * *', async () => {
  console.log('[Task Running] Daily Payment Reminders');
});

cron.schedule('0 8 * * 1', async () => {
  console.log('[Task Running] Weekly Stock Check Alert');
  const alertText = 'Weekly Automated Alert: Please conduct a stock check for fast-moving inventory items today.';
  await sendEmail(process.env.SMTP_USER, 'Internal Alert: Weekly Stock Check Required', alertText);
});

// Initialize Client
waClient.initialize();
