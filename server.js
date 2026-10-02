const express = require('express');
const path = require('path');
const login = require('fca-project-origo'); // फेसबुक चैट API
const app = express();

const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(__dirname));

let activeInterval = null;
let botRunning = false;
let globalApi = null; // फेसबुक API सेशन स्टोर करने के लिए

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// कुकी स्ट्रिंग को FCA फ़ॉर्मेट (AppState) में बदलने वाला फंक्शन
function parseCookie(cookieStr) {
    const appState = [];
    const pairs = cookieStr.split(';');
    pairs.forEach(pair => {
        const [key, value] = pair.split('=');
        if (key && value) {
            appState.push({
                key: key.trim(),
                value: value.trim(),
                domain: "facebook.com",
                path: "/",
                hostOnly: false,
                creation: new Date().toISOString(),
                lastAccessed: new Date().toISOString()
            });
        }
    });
    return appState;
}

// बॉट स्टार्ट API
app.post('/api/start', (req, res) => {
    if (botRunning) {
        return res.json({ success: false, message: "बॉट पहले से ही चल रहा है!" });
    }

    const { primaryCookie, targetUid, delay, messages } = req.body;
    let index = 0;
    
    try {
        const appState = parseCookie(primaryCookie);

        // फेसबुक में कुकीज़ के ज़रिए लॉगिन करें
        login({ appState: appState }, (err, api) => {
            if (err) {
                console.error("फेसबुक लॉगिन फ़ेल हुआ:", err);
                return res.json({ success: false, message: "कुकीज़ अमान्य (Invalid) हैं या एक्सपायर हो चुकी हैं!" });
            }

            globalApi = api;
            botRunning = true;
            const generatedTaskId = Math.floor(1000 + Math.random() * 9000);
            
            // मैसेज भेजने का लूप चालू करें
            activeInterval = setInterval(() => {
                if (!botRunning) return;

                const currentMsg = messages[index];
                
                // असली फेसबुक मैसेंजर सेंड फ़ंक्शन
                api.sendMessage({ body: currentMsg }, targetUid, (msgErr) => {
                    if (msgErr) {
                        console.log(`[Error] ${targetUid} को मैसेज नहीं भेजा जा सका:`, msgErr);
                    } else {
                        console.log(`[Success] Sent to ${targetUid}: "${currentMsg}"`);
                    }
                });

                index = (index + 1) % messages.length;
            }, delay * 1000);

            // फ्रंटएंड को कामयाबी का रिस्पॉन्स भेजें
            res.json({ success: true, taskId: generatedTaskId });
        });

    } catch (setupErr) {
        res.json({ success: false, message: "कुकी फॉर्मेट सही नहीं है!" });
    }
});

// बॉट स्टॉप API
app.post('/api/stop', (req, res) => {
    botRunning = false;
    if (activeInterval) {
        clearInterval(activeInterval);
        activeInterval = null;
    }
    if (globalApi) {
        globalApi.logout();
        globalApi = null;
    }
    console.log("[STOP] बॉट रोक दिया गया है।");
    res.json({ success: true });
});

app.listen(PORT, () => {
    console.log(`सर्वर एक्टिव है पोर्ट: ${PORT}`);
});
