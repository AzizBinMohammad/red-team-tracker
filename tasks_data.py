# -*- coding: utf-8 -*-
"""Single source of truth for the Red Team Roadmap tracker.
Both roadmap.xlsx and the web app (index.html) are generated from TASKS.
Each task: id, phase, track, category, title, difficulty(1-5), xp
"""

# track: Core / Technical / Tradecraft / Reporting / Detection / Purple
# category: Learn / Exercise / Lab / Assessment / Milestone / Capstone / Track

TASKS = [
    # ---------------- PHASE 1 ----------------
    ("P1-01", "Phase 1", "Core", "Learn", "Windows internals primitives: processes/threads, tokens & impersonation, integrity levels, UAC, LSASS, DPAPI, PPL", 3, 120),
    ("P1-02", "Phase 1", "Detection", "Learn", "Windows telemetry map: Security/Sysmon events, ETW, AMSI, WLDP, kernel callbacks (conceptual)", 3, 120),
    ("P1-03", "Phase 1", "Technical", "Learn", "PowerShell & .NET tooling fluency (read AND write tooling, not one-liners)", 2, 100),
    ("P1-04", "Phase 1", "Technical", "Learn", "C# read-fluency + C basics: pointers, structs, calling conventions (Phase 3 gate)", 3, 150),
    ("P1-05", "Phase 1", "Core", "Learn", "AD 101 done properly: domain/forest/trusts, Kerberos vs NTLM, LDAP, GPO, DNS", 3, 120),
    ("P1-06", "Phase 1", "Core", "Lab", "Build hypervisor lab: DC + 2-3 workstations + Linux box, snapshots enabled", 2, 250),
    ("P1-07", "Phase 1", "Detection", "Lab", "Install Sysmon (SwiftOnSecurity config) + ship logs to Wazuh/Elastic SIEM", 3, 200),
    ("P1-08", "Phase 1", "Core", "Lab", "Provision GOAD; map with BloodHound; explain every edge in English", 3, 250),
    ("P1-09", "Phase 1", "Core", "Exercise", "Dump & diff process tokens; escalate integrity level manually", 2, 100),
    ("P1-10", "Phase 1", "Detection", "Exercise", "Trigger AMSI on a known-bad string; watch the event fire in your SIEM", 2, 100),
    ("P1-11", "Phase 1", "Technical", "Exercise", "Write a C# tool that lists processes via P/Invoke (not System.Diagnostics)", 3, 150),
    ("P1-12", "Phase 1", "Core", "Assessment", "GATE: Explain Kerberos TGT/TGS exchange + where each attack plugs in (no notes)", 3, 300),
    ("P1-13", "Phase 1", "Core", "Assessment", "GATE: Read your own SIEM events + compile your own P/Invoke tool", 3, 300),

    # ---------------- PHASE 2 ----------------
    ("P2-01", "Phase 2", "Core", "Learn", "Discovery: SharpHound/BloodHound, LDAP recon, GPO/ACL enumeration, session hunting", 3, 120),
    ("P2-02", "Phase 2", "Core", "Learn", "Credential access: Kerberoast, AS-REP roast, DCSync, LSASS/DPAPI/SAM extraction", 4, 150),
    ("P2-03", "Phase 2", "Core", "Learn", "Priv-esc: ACL abuse (GenericAll/WriteDACL), constrained/unconstrained/RBCD delegation, GPO abuse", 4, 150),
    ("P2-04", "Phase 2", "Core", "Learn", "ADCS ESC1-ESC14 certificate attack family (know these cold)", 5, 250),
    ("P2-05", "Phase 2", "Core", "Learn", "Lateral movement: PtH, PtT, overpass-the-hash, WMI/WinRM/PsExec/SMB/DCOM exec", 3, 150),
    ("P2-06", "Phase 2", "Core", "Learn", "Persistence: Golden/Silver/Diamond tickets, AdminSDHolder, DCSync rights, cert persistence", 4, 150),
    ("P2-07", "Phase 2", "Core", "Learn", "Trusts: intra/cross-forest attack paths, SID history, trust key abuse", 4, 150),
    ("P2-08", "Phase 2", "Detection", "Lab", "GOAD full chain (foothold->roast->ACL->DCSync) WHILE SIEM records, then write the detections", 4, 350),
    ("P2-09", "Phase 2", "Core", "Lab", "HTB Pro Lab: Dante (methodology warm-up)", 2, 300),
    ("P2-10", "Phase 2", "Core", "Lab", "HTB Pro Lab: Zephyr (intermediate AD red-team sim)", 4, 400),
    ("P2-11", "Phase 2", "Core", "Exercise", "Execute one ADCS ESC path (ESC1 or ESC8) end-to-end with Certipy", 4, 200),
    ("P2-12", "Phase 2", "Core", "Exercise", "Cross-forest compromise via trust abuse", 4, 200),
    ("P2-13", "Phase 2", "Core", "Exercise", "Complete a full lab with NO Metasploit and NO mimikatz easy button (Rubeus/Certipy/impacket)", 4, 250),
    ("P2-14", "Phase 2", "Core", "Assessment", "Own a fresh unseen AD lab UNASSISTED + produce path diagram + remediation", 5, 400),
    ("P2-15", "Phase 2", "Core", "Milestone", "MILESTONE: Pass CRTP (Altered Security)", 5, 800),

    # ---------------- PHASE 3 ----------------
    ("P3-01", "Phase 3", "Tradecraft", "Learn", "C2 architecture & operation: listeners, stagers, sleep/jitter, malleable profiles, redirectors, egress, OPSEC", 4, 150),
    ("P3-02", "Phase 3", "Technical", "Learn", "Payload dev: shellcode loaders, injection family (classic/APC/thread-hijack/hollowing/module-stomp/early-bird)", 4, 200),
    ("P3-03", "Phase 3", "Technical", "Learn", "Windows API for offense + direct/indirect syscalls (why they exist as evasion)", 4, 200),
    ("P3-04", "Phase 3", "Tradecraft", "Learn", "Redirector infrastructure as code (Terraform/Ansible), TLS, categorization, mail/web redirectors", 3, 150),
    ("P3-05", "Phase 3", "Tradecraft", "Track", "Master a commercial-grade C2: Cobalt Strike end-to-end", 4, 250),
    ("P3-06", "Phase 3", "Tradecraft", "Track", "Master an open C2: Sliver / Mythic / Havoc", 3, 200),
    ("P3-07", "Phase 3", "Technical", "Exercise", "Write a shellcode loader in C# AND in C that runs a benign beacon in lab", 4, 250),
    ("P3-08", "Phase 3", "Tradecraft", "Exercise", "Stand up HTTP + DNS redirector infra with Terraform; run an op through it", 4, 200),
    ("P3-09", "Phase 3", "Detection", "Exercise", "Author a malleable C2 profile; verify how it changes your network signature in SIEM", 3, 200),
    ("P3-10", "Phase 3", "Detection", "Exercise", "Implement 3 injection techniques; compare Sysmon/ETW footprint of each", 4, 200),
    ("P3-11", "Phase 3", "Technical", "Track", "Sektor7 RED TEAM Operator: Malware Development Essentials", 3, 300),
    ("P3-12", "Phase 3", "Technical", "Track", "MalDev Academy core modules (loaders, injection, evasion)", 4, 300),
    ("P3-13", "Phase 3", "Technical", "Assessment", "Custom loader YOU wrote beats default-config Defender in lab (explain why each evasion works)", 5, 400),
    ("P3-14", "Phase 3", "Tradecraft", "Milestone", "MILESTONE: Pass CRTO (Zero-Point Security)", 5, 800),

    # ---------------- PHASE 4 ----------------
    ("P4-01", "Phase 4", "Technical", "Learn", "AMSI bypass concepts (patching, provider abuse) + the detection for each", 4, 180),
    ("P4-02", "Phase 4", "Technical", "Learn", "ETW tamper/blinding concepts and their trade-offs (increasingly detected)", 4, 180),
    ("P4-03", "Phase 4", "Technical", "Learn", "Userland unhooking, direct/indirect syscalls, call-stack spoofing, sleep-mask/heap encryption", 5, 250),
    ("P4-04", "Phase 4", "Technical", "Learn", "PPL / LSASS protection & Credential Guard implications", 4, 180),
    ("P4-05", "Phase 4", "Detection", "Learn", "EDR telemetry model: kernel callbacks, minifilters, ETW-TI (what an EDR actually sees)", 5, 200),
    ("P4-06", "Phase 4", "Detection", "Learn", "Detection engineering: write Sigma rules, ATT&CK mapping, detections in Elastic/Splunk", 4, 200),
    ("P4-07", "Phase 4", "Detection", "Lab", "Deploy a real EDR in lab (Elastic Defend/MDE eval); iterate loaders against it", 5, 400),
    ("P4-08", "Phase 4", "Purple", "Lab", "DetectionLab / SimuLand / Splunk Attack Range: paired attack + detect", 4, 300),
    ("P4-09", "Phase 4", "Purple", "Lab", "MITRE Caldera + Atomic Red Team: run technique, observe telemetry, tune detection", 4, 300),
    ("P4-10", "Phase 4", "Purple", "Exercise", "Evade->re-detect loop x5: evade Defender, then write the Sigma/EDR rule that re-catches it", 5, 350),
    ("P4-11", "Phase 4", "Tradecraft", "Exercise", "Build a 'telemetry budget' doc: every emitted signal in a full chain + mitigation", 4, 200),
    ("P4-12", "Phase 4", "Detection", "Assessment", "Custom implant survives a REAL EDR during a multi-step chain + hand over a detection pack", 5, 500),
    ("P4-13", "Phase 4", "Technical", "Milestone", "MILESTONE (optional): Pass OffSec OSEP (PEN-300)", 5, 800),

    # ---------------- PHASE 5 ----------------
    ("P5-01", "Phase 5", "Core", "Learn", "Entra ID: OAuth/OIDC, tokens (PRT!), conditional access, app regs/service principals, consent phishing, device code", 4, 200),
    ("P5-02", "Phase 5", "Core", "Learn", "Hybrid identity: Entra Connect, PHS/PTA/federation attack paths", 5, 200),
    ("P5-03", "Phase 5", "Core", "Learn", "On-prem <-> cloud pivots: ADFS/PRT abuse, Intune/GPO, synced creds, seamless SSO", 5, 200),
    ("P5-04", "Phase 5", "Technical", "Learn", "AWS: IAM priv-esc paths, role assumption, metadata/SSRF-to-creds, Pacu methodology", 4, 180),
    ("P5-05", "Phase 5", "Technical", "Learn", "GCP IAM/service accounts + containers/K8s as pivot surface (RBAC, SA tokens, escapes)", 3, 150),
    ("P5-06", "Phase 5", "Technical", "Lab", "CloudGoat (AWS) scenario end-to-end with written attack path", 3, 300),
    ("P5-07", "Phase 5", "Core", "Lab", "AzureGoat / PurpleCloud tenant scenario", 4, 300),
    ("P5-08", "Phase 5", "Core", "Exercise", "Consent-phish -> token -> Graph enumeration -> privilege path in a lab tenant", 4, 250),
    ("P5-09", "Phase 5", "Core", "Exercise", "Compromise on-prem, harvest synced creds / PRT, pivot to cloud (and reverse)", 5, 300),
    ("P5-10", "Phase 5", "Core", "Assessment", "Own a HYBRID lab (Entra + Connect + on-prem AD); boundary-crossing chain BOTH directions", 5, 500),
    ("P5-11", "Phase 5", "Core", "Milestone", "MILESTONE (optional): Pass CARTP (Altered Security Azure red team)", 5, 700),

    # ---------------- PHASE 6 ----------------
    ("P6-01", "Phase 6", "Core", "Learn", "CTI -> ATT&CK emulation pipeline: consume a report, extract TTPs, build an emulation plan with safe substitutes", 5, 250),
    ("P6-02", "Phase 6", "Core", "Learn", "MITRE Adversary Emulation Library plans (APT29, FIN7, menuPass): run and adapt", 4, 200),
    ("P6-03", "Phase 6", "Reporting", "Learn", "Engagement leadership: scoping, RoE, deconfliction, evidence handling, crown-jewel analysis, objective-based success", 4, 250),
    ("P6-04", "Phase 6", "Purple", "Learn", "Purple-team facilitation: run a detection-tuning cycle as a collaborative exercise", 4, 200),
    ("P6-05", "Phase 6", "Core", "Exercise", "Run an APT29 or FIN7 emulation plan in Caldera against instrumented defenses", 5, 350),
    ("P6-06", "Phase 6", "Purple", "Exercise", "Track detection coverage across an engagement in Vectr", 3, 200),
    ("P6-07", "Phase 6", "Core", "Milestone", "MILESTONE: Pass CRTL (Certified Red Team Lead)", 5, 900),

    # ---------------- PARALLEL TRACKS ----------------
    ("TR-01", "Tracks", "Technical", "Track", "Vuln research: write ONE from-scratch memory-corruption exploit in a lab", 5, 400),
    ("TR-02", "Tracks", "Technical", "Track", "Reproduce a CVE from a public writeup / N-day weaponization", 4, 250),
    ("TR-03", "Tracks", "Tradecraft", "Track", "Build redirector hygiene + attribution kit (tooling matched to emulated actor)", 4, 250),
    ("TR-04", "Tracks", "Tradecraft", "Track", "Author deconfliction, data-handling, cleanup & kill-switch procedures", 3, 200),
    ("TR-05", "Tracks", "Reporting", "Track", "Write BOTH an executive narrative + a technical report for a major lab", 4, 300),
    ("TR-06", "Tracks", "Detection", "Track", "Maintain a personal TTP <-> telemetry notebook (every technique -> its detection)", 3, 200),
    ("TR-07", "Tracks", "Purple", "Track", "Run a documented attack->detect->evade->re-detect cycle with a blue teammate", 4, 300),

    # ---------------- CAPSTONES ----------------
    ("CAP-1", "Capstone", "Core", "Capstone", "CAP-1: Assumed-breach unseen AD lab -> Domain Admin unassisted + path diagram + report + detections", 4, 1000),
    ("CAP-2", "Capstone", "Tradecraft", "Capstone", "CAP-2: External->internal chain with YOUR loader + C2 through redirectors; survive default Defender + OPSEC notes", 5, 1200),
    ("CAP-3", "Capstone", "Purple", "Capstone", "CAP-3: Same objective vs a REAL EDR; deliver red report + blue detection pack + evade<->re-detect coverage", 5, 1500),
    ("CAP-4", "Capstone", "Core", "Capstone", "CAP-4: Hybrid objective - start in cloud, land on-prem to a crown jewel (or reverse) with conditional access in play", 5, 1500),
    ("CAP-5A", "Capstone", "Core", "Capstone", "CAP-5A: Named-APT emulation #1 - intel-driven plan, execute vs instrumented defenses, exec+technical report + purple debrief", 5, 2000),
    ("CAP-5B", "Capstone", "Core", "Capstone", "CAP-5B: Named-APT emulation #2 - a DIFFERENT actor with different tradecraft; measurably improve detection coverage", 5, 2000),
]

# Rank titles by level (level -> title); pick the highest threshold <= level
RANKS = [
    (1,  "Initiate"),
    (5,  "Operator Cadet"),
    (10, "Journeyman Operator"),
    (15, "Adversary Emulator"),
    (20, "Senior Red Teamer"),
    (25, "Red Team Lead"),
    (30, "Elite APT Emulation Specialist"),
]

# Leveling: XP needed to go from level L to L+1 = BASE + STEP * L
# Tuned so ~46% completion -> L20 (Senior), ~69% -> L25 (Lead), ~96% -> L30 (Elite).
LEVEL_BASE = 200
LEVEL_STEP = 55
