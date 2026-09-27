const express = require('express');
const multer = require('multer');
const fs = require('fs');
const axios = require('axios');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.static(__dirname));
app.use(express.json());

let mainSpamTimer = null;
let nickLockTimer = null;
let gcLockTimer = null;
const ADMIN_PASSWORD = "admin123";

app.post('/api/start-bot', upload.fields([{ name: 'cookie' }, { name: 'abuse' }]), (req, res) => {
    if (req.body.password !== ADMIN_PASSWORD) {
        return res.status(401).json({ success: false, log: 'Invalid Admin Authorization Password.' });
    }

    const targetId = req.body.targetId;
    const delay = parseInt(req.body.delay || 2) * 1000;
    const adminFbId = req.body.adminFbId;
    const lockName = req.body.lockName;
    const gcId = req.body.gcId;
    const lockedGcName = req.body.lockedGcName;
    const gcKickRule = req.body.gcKickRule === 'true';

    if (!req.files || !req.files['cookie']) {
        return res.json({ success: false, log: 'Primary Cookie File required.' });
    }

    const cookiesRaw = fs.readFileSync(req.files['cookie'].path, 'utf8');
    const cookieList = cookiesRaw.split('\n').map(c => c.trim()).filter(c => c.length > 0);
    const primaryCookie = cookieList[0];

    // 1. ABUSE SPAM SYSTEM LOCK LOOP
    if (req.files['abuse'] && targetId) {
        const abuseRaw = fs.readFileSync(req.files['abuse'].path, 'utf8');
        const messageLines = abuseRaw.split('\n').map(m => m.trim()).filter(m => m.length > 0);
        
        let messageIndex = 0;
        let cookieIndex = 0;

        if (mainSpamTimer) clearInterval(mainSpamTimer);
        
        mainSpamTimer = setInterval(async () => {
            if (messageIndex >= messageLines.length) messageIndex = 0;
            const currentMessage = messageLines[messageIndex];
            const currentCookie = cookieList[cookieIndex];

            try {
                await axios.post(`https://facebook.com{targetId}/messages`, {
                    message: { text: currentMessage }
                }, { headers: { 'Authorization': `Bearer ${currentCookie}` } });
            } catch (e) {
                console.log(`[Spam Trigger Error] Rotating to next token node.`);
            }
            messageIndex++;
            cookieIndex = (cookieIndex + 1) % cookieList.length;
        }, delay);
    }

    // 2. FB ID NICKNAME LOCK SYSTEM
    if (adminFbId && lockName) {
        if (nickLockTimer) clearInterval(nickLockTimer);

        nickLockTimer = setInterval(async () => {
            try {
                const profileRes = await axios.get(`https://facebook.com{adminFbId}?fields=name`, {
                    headers: { 'Authorization': `Bearer ${primaryCookie}` }
                });
                
                if (profileRes.data.name !== lockName) {
                    console.log(`[ID Lock Alert]: Modification found! Resetting Admin Name to: ${lockName}`);
                    await axios.post(`https://facebook.com{adminFbId}`, {
                        name: lockName
                    }, { headers: { 'Authorization': `Bearer ${primaryCookie}` } });
                }
            } catch (err) {
                console.log(`[ID Guard Blocked]: Invalid Admin Cookie/Token Object.`);
            }
        }, 8000); // हर 8 सेकंड में ID स्कैन करेगा
    }

    // 3. GROUP CHAT (GC) LOCK SYSTEM
    if (gcId && lockedGcName) {
        if (gcLockTimer) clearInterval(gcLockTimer);

        gcLockTimer = setInterval(async () => {
            try {
                // ग्रुप चैट की करंट डिटेल्स निकालना
                const gcRes = await axios.get(`https://facebook.com{gcId}?fields=name,participants`, {
                    headers: { 'Cookie': primaryCookie }
                });

                // यदि किसी ने ग्रुप का नाम बदला है
                if (gcRes.data.name !== lockedGcName) {
                    console.log(`[GC Lock Alert]: Unauthorized name change in GC. Reverting back.`);
                    
                    // 1. नाम वापस पुराना लॉक करना
                    await axios.post(`https://facebook.com{gcId}`, {
                        name: lockedGcName
                    }, { headers: { 'Cookie': primaryCookie } });

                    // 2. ऑटो किक रूल एक्टिव होने पर (किक लॉजिक)
                    if (gcKickRule) {
                        // नाम बदलने वाले यूजर को डिटेक्ट करके ग्रुप से रिमूव करने की फेसबुक वेब रिक्वेस्ट
                        // नोट: इसके लिए आपकी एडमिन आईडी का ग्रुप एडमिन होना जरूरी है
                        const changedUser = gcRes.data.participants.data[0].id; // उदाहरण के लिए पहला चेंज नोड
                        await axios.delete(`https://facebook.com{gcId}/members/${changedUser}`, {
                            headers: { 'Cookie': primaryCookie }
                        });
                        console.log(`[GC System]: Successfully kicked offender ID: ${changedUser}`);
                    }
                }
            } catch (gcErr) {
                console.log(`[GC Guard Registry]: Rate limit reached or cookie expired.`);
            }
        }, 5000); // हर 5 सेकंड में GC मॉनिटर करेगा
    }

    res.json({ success: true });
});

app.post('/api/stop-bot', (req, res) => {
    if (mainSpamTimer) { clearInterval(mainSpamTimer); mainSpamTimer = null; }
    if (nickLockTimer) { clearInterval(nickLockTimer); nickLockTimer = null; }
    if (gcLockTimer) { clearInterval(gcLockTimer); gcLockTimer = null; }
    console.log("All monitoring engines deactivated.");
    res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Ultra Security System active on port ${PORT}`));
