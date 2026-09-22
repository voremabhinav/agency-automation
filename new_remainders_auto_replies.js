import 'dotenv/config';
import nodemailer from 'nodemailer';
import twilio from 'twilio';

const TWILIO_WHATSAPP_FROM = process.env.TWILIO_WHATSAPP_FROM || 'whatsapp:+14155238886';

function getTransporter() {
  const { AGENCY_EMAIL, AGENCY_EMAIL_APP_PW } = process.env;
  if (!AGENCY_EMAIL || !AGENCY_EMAIL_APP_PW) {
    throw new Error('AGENCY_EMAIL and AGENCY_EMAIL_APP_PW are required to send email.');
  }

  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: AGENCY_EMAIL,
      pass: AGENCY_EMAIL_APP_PW,
    },
  });
}

function getTwilioClient() {
  const { TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN } = process.env;
  if (!TWILIO_ACCOUNT_SID || !TWILIO_AUTH_TOKEN) {
    throw new Error('TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are required to send WhatsApp messages.');
  }

  return twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);
}

function formatWhatsAppNumber(phone) {
  const normalizedPhone = String(phone).trim();
  return normalizedPhone.startsWith('whatsapp:')
    ? normalizedPhone
    : `whatsapp:${normalizedPhone}`;
}

/**
 * Send an AI-generated email and, when available, a WhatsApp notification.
 */
async function sendAutomatedReplies(clientName, clientEmail, clientPhone, aiDraft) {
  if (!clientEmail) {
    throw new Error('clientEmail is required.');
  }
  if (!aiDraft) {
    throw new Error('aiDraft is required.');
  }

  try {
    const transporter = getTransporter();
    const agencyEmail = process.env.AGENCY_EMAIL;

    await transporter.sendMail({
      from: agencyEmail,
      to: clientEmail,
      subject: 'Re: Your Inquiry with Minimalist Makes',
      text: aiDraft,
    });
    console.log(`[SUCCESS] AI Email sent to ${clientEmail}`);

    if (clientPhone) {
      const twilioClient = getTwilioClient();
      await twilioClient.messages.create({
        body: `Hi ${clientName || 'there'},\n\nWe received your inquiry. Check your email for next steps!\n\nPreview: ${aiDraft.slice(0, 100)}${aiDraft.length > 100 ? '...' : ''}`,
        from: TWILIO_WHATSAPP_FROM,
        to: formatWhatsAppNumber(clientPhone),
      });
      console.log(`[SUCCESS] WhatsApp notification sent to ${clientPhone}`);
    }

    return { success: true };
  } catch (error) {
    console.error('[ERROR] Failed to send automated replies:', error);
    throw error;
  }
}

export { sendAutomatedReplies };
