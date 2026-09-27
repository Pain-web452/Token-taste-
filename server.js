const express = require('express');
const multer = require('multer');
const fs = require('fs');
const axios = require('axios');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.static(__dirname));
app.use(express.json());

let spamTimer = null; // लूप को चालू/बंद करने के लिए होल्डर

app.post('/api/start-bot', upload.fields([{ name: 'cookie' }, { name: 'abuse' }]), (req, res) => {
    const targetId = req.body.targetId;
    const delay = parseInt(req.body.delay || 2) * 1000; // सेकंड को मिलीसेकंड में बदलने के लिए

    if (!req.files || !req.files['cookie'] || !req.files['abuse']) {
        return res.json({ success: false, log: 'Missing required configuration files.' });
    }

    // फ़ाइलों से डेटा रीड करना
    const cookiesRaw = fs.readFileSync(req.files['cookie'][0].path, 'utf8');
    const abuseRaw = fs.readFileSync(req.files['abuse'][0].path, 'utf8');

    // कुकीज़ और गालियों/मैसेज को एरे (List) में बांटना
    const cookieList = cookiesRaw.split('\n').map(c => c.trim()).filter(c => c.length > 0);
    const messageLines = abuseRaw.split('\n').map(m => m.trim()).filter(m => m.length > 0);

    if (cookieList.length === 0 || messageLines.length === 0) {
        return res.json({ success: false, log: 'Files are empty or invalid.' });
    }

    let messageIndex = 0;
    let cookieIndex = 0;

    // अगर पहले से कोई बोट चल रहा है तो उसे रोकना
    if (spamTimer) clearInterval(spamTimer);

    console.log(`Automation started for Target: ${targetId}`);

    // ऑटोमेशन लूप (Interval Loop)
    spamTimer = setInterval(async () => {
        if (messageIndex >= messageLines.length) {
            messageIndex = 0; // फाइल खत्म होने पर दोबारा शुरू से शुरू करें
        }

        const currentMessage = messageLines[messageIndex];
        const currentCookie = cookieList[cookieIndex];

        // फेसबुक या किसी भी सोशल मीडिया मैसेंजर API एंडपॉइंट पर भेजने का स्ट्रक्चर
        // (नोट: यह फेसबुक ग्राफ/एमबेसिक स्ट्रक्चर का उदाहरण है)
        try {
            await axios.post(`https://facebook.com{targetId}/messages`, {
                messaging_product: "whatsapp", // या फेसबुक चैट एंडपॉइंट का डेटा
                recipient: { id: targetId },
                message: { text: currentMessage }
            }, {
                headers: {
                    'Authorization': `Bearer ${currentCookie}`, // अगर टोकन है
                    'Cookie': currentCookie // अगर वेब ब्राउज़र कुकी है
                }
            });
            console.log(`[Sent]: ${currentMessage} via Account ${cookieIndex + 1}`);
        } catch (error) {
            console.log(`[Failed/Block]: Token/Cookie ${cookieIndex + 1} expired or rate-limited.`);
        }

        // अगले मैसेज और अगली कुकी पर स्विच करें (Multi-ID रोटेशन)
        messageIndex++;
        cookieIndex = (cookieIndex + 1) % cookieList.length;

    }, delay);

    res.json({ success: true });
});

// बोट रोकने का एंडपॉइंट
app.post('/api/stop-bot', (req, res) => {
    if (spamTimer) {
        clearInterval(spamTimer);
        spamTimer = null;
        console.log("Automation sequence stopped by user.");
    }
    res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Locker Server live on port ${PORT}`));
