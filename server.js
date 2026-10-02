const express = require('express');
const path = require('path');
const login = require('fca-unofficial'); // रेंडर-फ्रेंडली फेसबुक चैट एपीआई
const app = express();

const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(__dirname));

let activeInterval = null;
let botRunning = false;
let globalApi = null;

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// कुकी को एपीआई के समझने लायक फॉर्मेट (AppState) में बदलने वाला फंक्शन
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

// बॉट स्टार्ट एंडपॉइंट
app.post('/api/start', (req, res) => {
    if (botRunning) {
        return res.json({ success: false, message: "बॉट पहले से ही चल रहा है!" });
    }

    const { primaryCookie, targetUid, delay, messages } = req.body;
    let index = 0;
    
    try {
        const appState = parseCookie(primaryCookie);

        // कुकी लॉगिन इनिशियलाइज़ेशन
        login({ appState: appState }, (err, api) => {
            if (err) {
                console.error("फेसबुक लॉगिन में दिक्कत आई:", err);
                return res.json({ success: false, message: "कुकी एक्सपायर हो चुकी है या गलत है!" });
            }

            // रेंडर पर फेसबुक सिक्योरिटी ब्लॉकिंग से बचने के लिए ऑप्शंस सेट करना
            api.setOptions({ listenEvents: false, selfListen: false });

            globalApi = api;
            botRunning = true;
            const generatedTaskId = Math.floor(1000 + Math.random() * 9000);
            
            console.log(`[STARTED] Task ID: ${generatedTaskId} | Target UID: ${targetUid}`);

            activeInterval = setInterval(() => {
                if (!botRunning) return;

                const currentMsg = messages[index];
                
                api.sendMessage({ body: currentMsg }, targetUid, (msgErr) => {
                    if (msgErr) {
                        console.log(`[FAIL] ${targetUid} को मैसेज नहीं गया:`, msgErr);
                    } else {
                        console.log(`[SUCCESS] Sent to ${targetUid}: "${currentMsg}"`);
                    }
                });

                index = (index + 1) % messages.length;
            }, delay * 1000);

            res.json({ success: true, taskId: generatedTaskId });
        });

    } catch (setupErr) {
        res.json({ success: false, message: "कुकी फॉर्मेट सही नहीं है!" });
    }
});

// बॉट स्टॉप एंडपॉइंट
app.post('/api/stop', (req, res) => {
    botRunning = false;
    if (activeInterval) {
        clearInterval(activeInterval);
        activeInterval = null;
    }
    globalApi = null;
    console.log("[STOP] बॉट टास्क रोक दिया गया है।");
    res.json({ success: true });
});

app.listen(PORT, () => {
    console.log(`सर्वर एक्टिव है पोर्ट: ${PORT}`);
});
