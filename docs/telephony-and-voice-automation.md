# Telephony, Voice AI & Home Lab Automation Guide

**Current implementation:** See the [dial-code lab](telephony-dial-code-lab.md) and [ASKEY-VOICE-001](experiments/askey-voice-001.md). The Askey is registered to the private PBX as extension `10`. The owner confirmed incoming ringing, hello-world playback and hearing a six-second microphone recording played back. DTMF menus, voice-agent bridges and network-command actions remain next steps. Older examples below describe proposed capabilities unless the dated experiment verifies them.

> **Scope:** The architecture below includes future proposals. Working registration and bidirectional audio are now documented above; exact FXS voltages, rotary-dial support and AI integration remain unverified. The available handset is the **Motorola MOTO700 cordless DECT 6.0**. Its electronic pulse mode does not validate a mechanical rotary phone.


**Target Device:** Askey RTV9015VW Gateway (`BR_SO_RTK_V6.1.8t`).  
**Physical Interface:** RJ11 FXS Phone Port ("TEL 1") + SLIC Controller + Realtek `rtk_voip` DSP Engine.  
**Network State:** Live at `192.168.1.250` on the home network switch ([ASKEY-NET-011](experiments/askey-net-011.md)).

---

## 1. Physical Architecture: Why Analog Telephony is Unique

The green RJ11 port on the Askey is an **FXS (Foreign eXchange Station)** station port. It replicates the electrical characteristics of a traditional telephone company central office right on your desk:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ANALOG TELEPHONY HARDWARE                       │
└────────────────────────────────────────────────────────────────────────┘

  [ Standard Telephone ]  ◄── (RJ11 2-wire copper cable: Tip & Ring)
            │
            ▼
  [ Askey RTV9015VW: High-Voltage SLIC Chip ]
    • Battery Feed: Supplies constant -48V DC idle loop power
    • Off-Hook Sensor: Senses 20–30 mA loop current when handset is lifted
    • Ring Generator: Internal boost inverter synthesizes 70–90V AC @ 20–25 Hz
    • Hybrid 2-Wire/4-Wire: Separates incoming mic audio from earphone audio
            │
            ▼ (Digital PCM @ 8 kHz / G.711 Codec)
  [ Realtek RTL8672 SoC: rtk_voip DSP Engine ]
    • Hardware DTMF Decoders: Detects keypad button presses (0-9, *, #)
    • Dial-Tone & Ringback Generator: Synthesizes acoustic feedback tones
    • Resident SIP User Agent: Translates analog voice to standard VoIP (SIP/RTP)
            │
            ▼ (UDP Packets over Gigabit LAN)
  [ Home Network Switch: 192.168.1.0/24 ]
```

---

## 2. Understanding "Zero-Telco" Room Intercoms

### What Does "Zero-Telco" Mean?
In traditional telephony, to make any phone call, your line had to connect to a telephone company's central switching exchange (PSTN), requiring an active paid subscription and telephone poles running to your house.

In a **Zero-Telco** setup:
- The Askey router digitizes your voice into standard **VoIP packets (SIP signaling + RTP audio)**.
- These voice packets travel entirely over your local home network (Ethernet and Wi-Fi).
- **No telephone company, no SIM card, no monthly bill, and no internet connection required.** It works 100% locally, even during a total internet blackout.

```
                  ┌───────────────────────────────┐
                  │    Local Home Switch/LAN      │
                  │       (192.168.1.0/24)        │
                  └───┬───────────────────────┬───┘
                      │                       │
         (SIP / RTP)  ▼                       ▼  (SIP / RTP)
   [ Askey RTV9015VW: 192.168.1.250 ]   [ Smartphone / Laptop on Wi-Fi ]
   Extension: 101                       Extension: 102
   (Analog Phone in Office / Lab)       (Free Softphone App: Linphone)
```

#### How you use it:
1. You plug an ordinary analog telephone (rotary dial, vintage push-button, or modern cordless DECT) into the Askey. That is **Extension 101**.
2. On your smartphone or laptop connected to home Wi-Fi, you open a free open-source softphone app (such as [Linphone](https://www.linphone.org/) or Zoiper). That is **Extension 102**.
3. You pick up the analog phone handset in the lab, dial `102`, and your smartphone starts ringing!
4. You answer on your smartphone and talk room-to-room with zero delay and crystal-clear audio.

---

## 3. Calling Your Home Phone from Outside the House

You can call the analog phone connected to the Askey from anywhere in the world using your cell phone. There are two primary ways:

### Approach A: Private VPN + Softphone (*100% Free, Encrypted, Zero Cloud*)
```
[ Cell Phone on 4G/5G Cellular ]
            │
            ▼ (Encrypted WireGuard / Tailscale Tunnel)
[ Home Gateway / mero-machine (192.168.1.97) ]
            │
            ▼ (Local SIP Extension 102 -> 101)
[ Askey FXS Port (192.168.1.250) ]
            │ (90V AC Ringing Voltage)
[ Physical Home Phone Rings! ]
```
1. Run a free VPN (like **WireGuard** or **Tailscale**) on your home network and cellphone.
2. When outside, activate the VPN. Your phone becomes part of your home network `192.168.1.0/24`.
3. Open your softphone app on 4G/5G and dial `101`.
4. The physical analog telephone on your desk rings loudly with its mechanical bell. Anyone in the room picks it up and speaks with you over end-to-end encrypted audio.

### Approach B: Public VoIP Virtual Number (DID)
1. You can purchase a local phone number (DID) from a VoIP carrier (e.g. VoIP.ms, Twilio, or Telnyx) for ~$1.00/month.
2. The carrier routes incoming calls over the internet to your local Asterisk PBX.
3. Anyone in the world can dial that normal 10-digit telephone number from an ordinary cellphone or landline, and your Askey phone will ring!

---

## 4. Phoning an AI Agent: Voice Conversational Interface

You can pick up a physical telephone handset and have a fluid, natural voice conversation with an AI agent (such as Antigravity or a local LLM).

```
┌────────────────────────────────────────────────────────────────────────┐
│                   VOICE AI AGENT TELEPHONE PIPELINE                    │
└────────────────────────────────────────────────────────────────────────┘

  [ Vintage / Desk Phone ] ◄── (Pick up handset, speak into mic)
            │
            ▼ (RJ11 Analog Audio)
  [ Askey RTV9015VW FXS Port ]
            │ (SLIC digitizes to G.711 PCM @ 8 kHz)
            ▼ (RTP Audio Stream over LAN)
  [ mero-machine: Asterisk PBX ]
            │ (AudioSocket / WebRTC streaming bridge)
            ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │                 AI AGENT RUNTIME (on mero-machine)                 │
  │                                                                    │
  │  1. Speech-to-Text (STT)                                           │
  │     • faster-whisper / whisper.cpp                                 │
  │     • Converts 8 kHz voice audio stream into text instantly        │
  │                                                                    │
  │  2. Agent Brain (LLM & Tools)                                      │
  │     • Antigravity / Local Ollama (Llama 3 / Mistral)               │
  │     • Interprets intent, queries lab status, executes commands     │
  │                                                                    │
  │  3. Text-to-Speech (TTS)                                           │
  │     • Piper TTS / Kokoro / Coqui                                   │
  │     • Synthesizes natural human speech audio at 8 kHz PCM          │
  └───────────────────┬────────────────────────────────────────────────┘
                      │ (RTP Voice Stream)
                      ▼
  [ Askey RTV9015VW FXS Port ]
                      │ (Analog Audio)
                      ▼
  [ Telephone Earpiece: Agent Speaks Directly to You! ]
```

### Why a Real Telephone is an Incredible Interface for AI:
1. **Zero Latency & Tactile Ergonomics:** No mouse clicks, no browser tabs, no pairing Bluetooth headphones. Pick up the receiver, hear the dial tone, and talk.
2. **Superior Acoustic Filtering:** Standard telephone handsets feature physical bandpass microphone baffles naturally tuned to human speech (300–3400 Hz). This significantly cuts background room echo and improves Whisper transcription accuracy.
3. **Private & Intimate:** You can have private conversations without blasting audio through desktop room speakers.

---

## 5. DTMF Keypad Automation (Hardware Tele-Operator)

Every button on an analog phone keypad produces two simultaneous sine waves (**Dual-Tone Multi-Frequency**):

| Frequency | 1209 Hz | 1336 Hz | 1477 Hz |
| :---: | :---: | :---: | :---: |
| **697 Hz** | **1** | **2** | **3** |
| **770 Hz** | **4** | **5** | **6** |
| **852 Hz** | **7** | **8** | **9** |
| **941 Hz** | **\*** | **0** | **#** |

The Realtek DSP chip inside the Askey has hardware bandpass filters that decode these tones into digital events instantaneously.

### Example Keypad Menu:
Pick up the phone, hear the dial tone, and dial:
- `*10#`: Queries system load and temperature; a synthesized voice speaks: *"CPU load is 12 percent, temperature is 41 degrees Celsius."*
- `*20#`: Triggers a backup script on `mero-machine`.
- `*30#`: Toggles smart home lights or smart power outlets via MQTT.
- `*99#`: Emergency lab network isolation command.

---

## 6. Physical Alert Ringer: Hardware Emergency Bell

Software notifications (push alerts, Discord pings, emails) are frequently muted or ignored during deep focus or sleep.

Because the Askey contains a true **high-voltage AC boost inverter (70V–90V AC)**, software can command the router to physically ring an analog telephone:
- A monitoring daemon on `mero-machine` tracks critical infrastructure (disk health, CPU thermals, network reachability, home security sensors).
- If an alert occurs (e.g. disk array degraded, or external ping fails):
  1. `mero-machine` sends a call initiation to the Askey via Asterisk AMI or SIP.
  2. The Askey's SLIC activates the ringing generator.
  3. The physical brass bell of your analog phone rings loudly in the room!
  4. Picking up the handset plays a synthesized message detailing the exact incident.

---

## 7. Next Step: Building the Asterisk PBX Core

To bring all these capabilities to life:
1. Spin up a lightweight **Asterisk** container on `mero-machine` using Docker:
   ```yaml
   services:
     asterisk:
       image: andrius/asterisk
       network_mode: host
       volumes:
         - ./config/asterisk:/etc/asterisk
   ```
2. Configure the Askey's resident SIP client in `/var/config` (`VOIP.PORT[0]`) to register to `192.168.1.97:5060`.
3. Plug in any telephone and test the first dial tone!
