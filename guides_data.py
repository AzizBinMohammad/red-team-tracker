# -*- coding: utf-8 -*-
"""Per-task GUIDES for the Red Team Mastery Tracker — two variants per task.

BEGINNER[id] : gentle, assumes no background, names prerequisites, adds a
               safety reminder and a small first win. Shown in Beginner mode.
PRO[id]      : terse, assumes fluency, depth/OPSEC oriented. Shown in Pro mode
               for the tasks NOT already covered by details_data.DETAILS
               (Phase 1-2 + P3-01 come from DETAILS; everything else lives here).

Each entry: {overview, steps[], tools[], resources[{name,url?}], doneWhen, pitfall}
Authorized labs and environments only.
"""

def R(*items):
    out = []
    for it in items:
        if isinstance(it, tuple):
            out.append({"name": it[0], "url": it[1]})
        else:
            out.append({"name": it})
    return out

BEGINNER = {}
PRO = {}

# ============================== BEGINNER · PHASE 1 ==============================
BEGINNER.update({
"P1-01": {
 "overview": "Before any 'hacking', learn how Windows actually works underneath — processes, the tokens that carry your permissions, and where passwords live in memory. Everything later is a consequence of these basics.",
 "steps": [
  "Spin up ONE Windows VM you own. Never practise on a machine you don't control.",
  "Install System Informer (formerly Process Hacker) and just look: open a process, see its threads, its token, its integrity level.",
  "Run `whoami /all` in a terminal and read every line — those groups and privileges ARE your token.",
  "Watch a normal admin login: notice you get a 'medium' token until you 'Run as administrator' (that's UAC).",
  "Write a one-page note in plain English: what is a token, what is an integrity level, what is LSASS.",
 ],
 "tools": ["A Windows 10/11 VM", "System Informer / Process Hacker", "whoami /all", "Task Manager"],
 "resources": R(("HackTricks — Windows local privilege escalation", "https://book.hacktricks.xyz"), ("Microsoft — Access tokens", "https://learn.microsoft.com/windows/win32/secauthz/access-tokens")),
 "doneWhen": "You can explain, in your own words, what a token is and why 'Run as administrator' gives you a different one.",
 "pitfall": "Trying to memorise attack commands before you understand tokens — you'll be lost the first time a tutorial doesn't match your screen.",
},
"P1-02": {
 "overview": "Learn what Windows writes down when things happen — the logs and events. Knowing what leaves a trace makes you both a better attacker and a better defender.",
 "steps": [
  "Open Event Viewer on your VM and browse Security logs. Log in and out; watch events 4624 (logon) and 4625 (failed logon) appear.",
  "Install Sysmon with a starter config (SwiftOnSecurity) — it adds much richer logs.",
  "Do something ordinary (open Notepad) and find the 'process created' event it generated.",
  "Make a simple table: 'action I took' -> 'log it created'. Keep adding to it as you learn.",
 ],
 "tools": ["Event Viewer", "Sysmon", "SwiftOnSecurity sysmon-config", "Get-WinEvent"],
 "resources": R(("Sysmon docs", "https://learn.microsoft.com/sysinternals/downloads/sysmon"), ("SwiftOnSecurity config", "https://github.com/SwiftOnSecurity/sysmon-config")),
 "doneWhen": "You can open Event Viewer, log in, and point to the exact event that recorded it.",
 "pitfall": "Thinking logs are 'the defender's job' — the operators who last are the ones who know what they're leaving behind.",
},
"P1-03": {
 "overview": "PowerShell is the native language of Windows automation and offense. Get comfortable writing small scripts, not just pasting one-liners you don't understand.",
 "steps": [
  "Install VS Code + the PowerShell extension.",
  "Learn the basics: variables, if/foreach, functions, and how the pipeline passes objects (not text).",
  "Write a tiny function of your own that takes a parameter and returns something — e.g. list processes over 100MB.",
  "Read a real script (like PowerView) and try to explain what one function does.",
 ],
 "tools": ["PowerShell 7", "VS Code + PowerShell extension"],
 "resources": R(("Microsoft Learn — PowerShell", "https://learn.microsoft.com/powershell/")),
 "doneWhen": "You wrote your own small PowerShell function with a parameter and understand every line of it.",
 "pitfall": "Copy-pasting encoded one-liners you can't rebuild yourself — it feels like progress but collapses the moment antivirus flags it.",
},
"P1-04": {
 "overview": "A gentle first look at C# and C. You don't need to be a developer — you need to READ offensive tooling and understand pointers and memory. This is the gate to the later custom-tooling phases.",
 "steps": [
  "Install Visual Studio Community (free). Create a C# console app that prints something — get the build/run loop working.",
  "Learn what a pointer is, conceptually: a variable that holds a memory address. Draw it on paper.",
  "Learn what P/Invoke means: calling a built-in Windows function from C#. Read one example on pinvoke.net.",
  "Don't rush. Understanding 'memory has addresses and functions live at addresses' is the real win here.",
 ],
 "tools": ["Visual Studio Community", "pinvoke.net (reference)"],
 "resources": R(("pinvoke.net", "https://www.pinvoke.net"), ("Microsoft Learn — C# fundamentals", "https://learn.microsoft.com/dotnet/csharp/")),
 "doneWhen": "You compiled and ran a C# console app and can explain in one sentence what a pointer is.",
 "pitfall": "Skipping this because it's 'programming, not hacking' — every custom loader in later phases is written in exactly this.",
},
"P1-05": {
 "overview": "Active Directory (AD) is how companies manage all their Windows computers and users. Almost every corporate red-team attack is really an AD attack, so learn the map before the moves.",
 "steps": [
  "Learn the words: domain, forest, domain controller (DC), user, group, GPO. Make a glossary.",
  "Understand at a high level how login works: Kerberos hands out 'tickets'. Draw the flow simply.",
  "Learn what LDAP is (the directory you query) and what a 'service account' is.",
  "You don't need a lab yet for this — just solid vocabulary and a mental model.",
 ],
 "tools": ["Diagrams on paper", "A note-taking app"],
 "resources": R(("HackTricks — Active Directory methodology", "https://book.hacktricks.xyz"), ("Microsoft — AD DS overview", "https://learn.microsoft.com/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview")),
 "doneWhen": "You can explain to a friend what a domain controller is and why Kerberos 'tickets' matter.",
 "pitfall": "Jumping to attack names (Kerberoast, DCSync) before you know what a ticket or a domain even is.",
},
"P1-06": {
 "overview": "Build your own safe practice lab: a few Windows VMs on your own computer that you can break and restore. This is where ALL your practice happens — never on real or other people's systems.",
 "steps": [
  "Install a hypervisor: VirtualBox (free) or VMware Workstation Player.",
  "Create one Windows Server VM (your Domain Controller) and one Windows 10/11 VM (a 'workstation').",
  "Take a SNAPSHOT of each once installed — this lets you undo any mess in seconds.",
  "Give them a private/host-only network so they talk to each other but stay isolated from your real network.",
 ],
 "tools": ["VirtualBox or VMware Workstation", "Windows eval ISOs (free 180-day)", "8GB+ RAM recommended"],
 "resources": R(("VirtualBox", "https://www.virtualbox.org"), ("Windows Server eval", "https://www.microsoft.com/evalcenter")),
 "doneWhen": "Two VMs boot, can ping each other on a private network, and you've taken restorable snapshots.",
 "pitfall": "Not taking snapshots — then a broken lab means reinstalling from scratch and you give up.",
},
"P1-07": {
 "overview": "Add 'eyes' to your lab: install Sysmon on your VMs and ship the logs to a free SIEM so you can SEE attacks as they happen. This turns every later exercise into a learning loop.",
 "steps": [
  "On each Windows VM, install Sysmon with the SwiftOnSecurity config.",
  "Stand up a free SIEM — Wazuh is the easiest all-in-one for beginners.",
  "Install the Wazuh agent on your VMs so their logs flow to the dashboard.",
  "Confirm it works: do something on a VM and watch the event show up in the SIEM.",
 ],
 "tools": ["Sysmon", "Wazuh (or Elastic)", "SwiftOnSecurity config"],
 "resources": R(("Wazuh — quickstart", "https://documentation.wazuh.com/current/quickstart.html"), ("Sysmon docs", "https://learn.microsoft.com/sysinternals/downloads/sysmon")),
 "doneWhen": "An action on a VM appears as a searchable event in your SIEM dashboard.",
 "pitfall": "Giving the SIEM VM too little RAM — it'll crawl and you'll stop using it. Give it 4GB+.",
},
"P1-08": {
 "overview": "GOAD (Game Of Active Directory) is a free, pre-built vulnerable AD lab. Deploy it and use BloodHound to draw the attack map — this becomes your playground for Phase 2.",
 "steps": [
  "Follow the GOAD install guide to deploy it (it automates building several vulnerable VMs).",
  "Install BloodHound Community Edition and its collector, SharpHound.",
  "Run SharpHound to collect data, then load it into BloodHound to see the graph of users, computers, and attack paths.",
  "Pick ONE path the graph shows and explain it out loud in plain English.",
 ],
 "tools": ["GOAD", "BloodHound Community Edition", "SharpHound"],
 "resources": R(("GOAD project", "https://github.com/Orange-Cyberdefense/GOAD"), ("BloodHound docs", "https://bloodhound.readthedocs.io")),
 "doneWhen": "BloodHound shows the GOAD graph and you can describe one attack edge in your own words.",
 "pitfall": "Deploying GOAD anywhere reachable from the internet — keep it fully isolated; it is deliberately vulnerable.",
},
"P1-09": {
 "overview": "Hands-on with tokens: compare the token of a normal program vs an admin one, and see how integrity levels differ. This makes the abstract 'token' idea concrete.",
 "steps": [
  "Open two programs — one normal, one 'as administrator'.",
  "In System Informer, open each process's Properties -> Token tab and compare integrity level and privileges.",
  "Note which privileges only the admin one has (e.g. SeDebugPrivilege).",
  "Write down: 'to go from medium to high integrity, an attacker needs ___' (that's privilege escalation, previewed).",
 ],
 "tools": ["System Informer / Process Hacker", "whoami /all", "A lab VM"],
 "resources": R(("HackTricks — Windows tokens", "https://book.hacktricks.xyz")),
 "doneWhen": "You can point at two processes and explain why one has more power than the other via its token.",
 "pitfall": "Doing this on your host machine instead of a VM — always practise in the lab.",
},
"P1-10": {
 "overview": "See a defense fire in real time: AMSI is Windows' in-memory script scanner. Trigger it with a standard test string and watch the alert appear in your SIEM — a satisfying attack->detection loop.",
 "steps": [
  "In PowerShell on a lab VM, use the standard AMSI test string (a designated, non-malicious trigger).",
  "Watch it get blocked — that's AMSI working.",
  "Go to your SIEM / Event Viewer and find the event that recorded it.",
  "Reflect: later phases are largely about NOT triggering this — but first, see it trigger.",
 ],
 "tools": ["PowerShell", "Your SIEM / Event Viewer", "A lab VM"],
 "resources": R(("Microsoft — AMSI", "https://learn.microsoft.com/windows/win32/amsi/antimalware-scan-interface-portal")),
 "doneWhen": "You triggered AMSI on purpose and found the matching log entry.",
 "pitfall": "Using real malware to 'test' — never needed. A designated test string is enough and safe.",
},
"P1-11": {
 "overview": "Write your first real offensive-style tool: a tiny C# program that lists running processes by calling Windows directly (P/Invoke), instead of the easy built-in class.",
 "steps": [
  "Start from a working C# console app.",
  "Find the P/Invoke signature for a process-listing API on pinvoke.net (e.g. toolhelp snapshots).",
  "Wire it up so your program prints process names and IDs.",
  "Compare: it does the same as Task Manager, but YOU called the Windows API to do it.",
 ],
 "tools": ["Visual Studio", "pinvoke.net", "C#"],
 "resources": R(("pinvoke.net — CreateToolhelp32Snapshot", "https://www.pinvoke.net"), ("ired.team — offensive C#", "https://www.ired.team")),
 "doneWhen": "Your own C# tool lists processes using a P/Invoke call (not System.Diagnostics).",
 "pitfall": "Copying a whole tool without understanding the P/Invoke line — the point is to understand the API call.",
},
"P1-12": {
 "overview": "A checkpoint, no notes. Kerberos is the heart of AD attacks — prove you can explain how it hands out tickets and where the famous attacks plug in.",
 "steps": [
  "Draw the Kerberos flow from memory: client -> gets a TGT -> uses it to get a TGS -> presents it to a service.",
  "For each step, name one attack that abuses it (AS-REP roast, Kerberoast, ticket forgery) — just name and place them.",
  "Explain it out loud to someone (or record yourself) with no notes.",
 ],
 "tools": ["Whiteboard / paper", "Your own study notes (used before the test, not during)"],
 "resources": R(("HackTricks — Kerberos", "https://book.hacktricks.xyz")),
 "doneWhen": "You can whiteboard the TGT/TGS exchange and place two attacks on it — from memory.",
 "pitfall": "Memorising attack names without knowing WHERE in the flow they happen.",
},
"P1-13": {
 "overview": "The Phase 1 hands-on checkpoint: prove your lab works end to end by reading your own SIEM events AND compiling your own P/Invoke tool. If both work, you're ready for Phase 2.",
 "steps": [
  "Do a small action on a VM and successfully find its event in your SIEM — no help.",
  "Compile and run your P/Invoke process-lister from P1-11.",
  "If either fails, fix it now — Phase 2 assumes a working lab and toolchain.",
 ],
 "tools": ["Your SIEM", "Visual Studio", "Your lab VMs"],
 "resources": R(("(revisit) Wazuh docs", "https://documentation.wazuh.com")),
 "doneWhen": "You independently found a SIEM event AND ran your own compiled tool in the same sitting.",
 "pitfall": "Rushing past a half-working lab — every later phase compounds on this foundation.",
},
})
# ============================== BEGINNER · PHASE 2 ==============================
BEGINNER.update({
"P2-01": {
 "overview": "Recon inside Active Directory: before attacking, learn to map who can do what. BloodHound turns a messy directory into a picture of attack paths.",
 "steps": [
  "In your GOAD lab, run SharpHound as a normal domain user to collect data.",
  "Load it into BloodHound and explore: users, groups, sessions, and the 'Shortest Path to Domain Admins' query.",
  "Learn the basic LDAP queries that find service accounts and admins.",
  "Goal: from a low-priv foothold, describe (not yet execute) a path toward Domain Admin.",
 ],
 "tools": ["SharpHound", "BloodHound CE", "PowerView (read source)"],
 "resources": R(("BloodHound docs", "https://bloodhound.readthedocs.io"), ("HackTricks — AD enumeration", "https://book.hacktricks.xyz")),
 "doneWhen": "You collected data with SharpHound and used BloodHound to find a path to Domain Admin in your lab.",
 "pitfall": "Running noisy tools without watching your SIEM — recon leaves traces too; notice them.",
},
"P2-02": {
 "overview": "Credential access: the family of techniques that steal or crack passwords and hashes in AD. These are the 'bread and butter' AD attacks.",
 "steps": [
  "Learn each by name and what it targets: Kerberoast (service account hashes), AS-REP roast (users without pre-auth), DCSync (pull hashes from the DC), LSASS/SAM dumping.",
  "Try Kerberoasting in GOAD with Rubeus or impacket, then crack the hash offline with hashcat.",
  "Watch your SIEM: note the event a Kerberoast request generates (4769).",
  "Keep a table: attack -> what it steals -> the log it makes.",
 ],
 "tools": ["Rubeus", "impacket (GetUserSPNs, secretsdump)", "hashcat"],
 "resources": R(("HackTricks — Kerberoasting", "https://book.hacktricks.xyz"), ("Certipy/impacket docs", "https://github.com/fortra/impacket")),
 "doneWhen": "You Kerberoasted a service account in the lab and cracked its password offline.",
 "pitfall": "Cracking hashes from anything but your own lab — only ever crack credentials you're authorized to test.",
},
"P2-03": {
 "overview": "Privilege escalation in AD by abusing permissions (ACLs) and delegation. Often the path to Domain Admin isn't an exploit — it's a misconfigured permission.",
 "steps": [
  "Learn the dangerous rights: GenericAll, WriteDACL, and what delegation (constrained/unconstrained/RBCD) means.",
  "In BloodHound, find an edge like 'User X has GenericAll over Group Y' and follow the abuse instructions BloodHound gives.",
  "Execute one ACL-abuse path in GOAD end to end.",
  "Explain WHY the permission was dangerous, not just the command.",
 ],
 "tools": ["BloodHound", "PowerView", "Rubeus (for delegation)"],
 "resources": R(("HackTricks — abusing AD ACLs/ACEs", "https://book.hacktricks.xyz"), ("BloodHound — edge help", "https://bloodhound.readthedocs.io")),
 "doneWhen": "You escalated privileges in the lab by abusing one ACL or delegation misconfiguration.",
 "pitfall": "Running the command without understanding the permission — you won't spot the same flaw in a real assessment.",
},
"P2-04": {
 "overview": "AD Certificate Services (ADCS) attacks — the 'ESC' family. Misconfigured certificate templates can hand you Domain Admin. Powerful and very common in real networks.",
 "steps": [
  "Understand the idea: certificates can prove identity; a bad template lets you request a cert AS someone else.",
  "Read the ESC1-ESC8 summaries (start with ESC1 and ESC8 — the most common).",
  "In a lab with ADCS, use Certipy to find (`find`) vulnerable templates.",
  "Don't try to memorise all 14 at once — understand ESC1 deeply first.",
 ],
 "tools": ["Certipy", "A lab with ADCS installed"],
 "resources": R(("SpecterOps — Certified Pre-Owned", "https://posts.specterops.io/certified-pre-owned-d95910965cd2"), ("Certipy", "https://github.com/ly4k/Certipy")),
 "doneWhen": "You can explain ESC1 in plain words and Certipy lists a vulnerable template in your lab.",
 "pitfall": "Drowning trying to learn ESC1-ESC14 at once — depth on one beats shallow on all.",
},
"P2-05": {
 "overview": "Lateral movement: once you have one machine or one credential, how you hop to the next. Pass-the-Hash, Pass-the-Ticket, and remote-execution methods.",
 "steps": [
  "Learn the concepts: PtH (use a hash instead of a password), PtT (use a Kerberos ticket), and exec methods (WMI, WinRM, PsExec, SMB).",
  "In the lab, take a hash you dumped and use it to authenticate to another machine (impacket's tools).",
  "Try two different execution methods and compare the logs each leaves.",
  "Note which method is 'quieter' in your SIEM.",
 ],
 "tools": ["impacket (psexec, wmiexec, smbexec)", "Rubeus / Mimikatz (lab)", "evil-winrm"],
 "resources": R(("HackTricks — lateral movement", "https://book.hacktricks.xyz")),
 "doneWhen": "You moved from one lab machine to another using a stolen hash or ticket.",
 "pitfall": "Only ever using PsExec — it's the loudest. Learn several so you can pick by situation.",
},
"P2-06": {
 "overview": "Persistence: how attackers keep access after the first compromise. Golden/Silver tickets and other AD backdoors. Understanding these also teaches you how to detect them.",
 "steps": [
  "Learn what a Golden Ticket is (forged TGT using the krbtgt hash) vs a Silver Ticket (forged service ticket).",
  "In the lab, after getting the krbtgt hash, forge a Golden Ticket and use it.",
  "Immediately look at how you'd DETECT it (unusual ticket lifetimes, anomalies).",
  "Understand this is 'game over' persistence — and why rotating krbtgt twice is the fix.",
 ],
 "tools": ["Mimikatz / Rubeus (lab)", "impacket ticketer"],
 "resources": R(("HackTricks — Golden/Silver tickets", "https://book.hacktricks.xyz")),
 "doneWhen": "You forged and used a Golden Ticket in the lab and can describe how a defender would catch it.",
 "pitfall": "Forgetting persistence is the most heavily-monitored area — study the detection alongside the attack.",
},
"P2-07": {
 "overview": "Trusts: how separate domains/forests relate, and how attackers cross between them. This is how a foothold in one place becomes control of another.",
 "steps": [
  "Learn what a trust is and the two directions (one-way vs two-way, intra- vs inter-forest).",
  "Understand SID history and how it can carry privileges across a trust.",
  "In a multi-domain lab (GOAD has this), map the trusts in BloodHound.",
  "Describe a path that starts in one domain and ends with control of another.",
 ],
 "tools": ["BloodHound", "Rubeus", "impacket"],
 "resources": R(("HackTricks — domain/forest trusts", "https://book.hacktricks.xyz")),
 "doneWhen": "You mapped the trusts in your lab and described a cross-domain attack path.",
 "pitfall": "Assuming a forest boundary is a hard security boundary — it often isn't, and that's the point.",
},
"P2-08": {
 "overview": "Your first full 'purple' exercise: run a complete attack chain in GOAD WHILE your SIEM records, then write the detections. This is where attacker and defender skills fuse.",
 "steps": [
  "Plan a chain: foothold -> Kerberoast -> ACL abuse -> DCSync. Write it down first.",
  "Execute it step by step in GOAD with your SIEM running.",
  "For each step, find the events it produced and write a detection note (which event, what threshold).",
  "Produce a short 'attack + detection' writeup — this is a mini real-world deliverable.",
 ],
 "tools": ["GOAD", "Your SIEM (Wazuh/Elastic)", "Rubeus/impacket"],
 "resources": R(("MITRE ATT&CK", "https://attack.mitre.org"), ("Sigma rules", "https://github.com/SigmaHQ/sigma")),
 "doneWhen": "You executed a multi-step chain and wrote a detection for every step from your own SIEM data.",
 "pitfall": "Running the chain but never checking the logs — the detections are the real learning here.",
},
"P2-09": {
 "overview": "HTB Pro Lab 'Dante' — a guided, beginner-friendly multi-machine lab to warm up your methodology (not pure AD, broad fundamentals).",
 "steps": [
  "Get an HTB subscription and start the Dante Pro Lab.",
  "Work it methodically: enumerate -> foothold -> escalate -> pivot. Take notes as you go.",
  "When stuck, learn the concept behind the hint rather than just copying the answer.",
  "Keep a clean notes file — you're building a reusable methodology.",
 ],
 "tools": ["Hack The Box (Dante Pro Lab)", "A note-taking system", "Kali/ParrotOS"],
 "resources": R(("Hack The Box", "https://www.hackthebox.com")),
 "doneWhen": "You completed Dante and have written notes capturing your repeatable methodology.",
 "pitfall": "Rushing with walkthroughs — the value is building YOUR process, not finishing fast.",
},
"P2-10": {
 "overview": "HTB Pro Lab 'Zephyr' — an intermediate AD red-team simulation. A big step up from Dante; this is closer to a real engagement.",
 "steps": [
  "Start Zephyr after Dante. Expect it to be hard — that's the point.",
  "Apply everything from P2-01..P2-08: enumerate with BloodHound, roast, abuse ACLs, move laterally.",
  "Track your path so you could reproduce it and explain it to someone.",
  "Write a short after-action of the full compromise path.",
 ],
 "tools": ["Hack The Box (Zephyr Pro Lab)", "BloodHound", "impacket/Rubeus"],
 "resources": R(("Hack The Box", "https://www.hackthebox.com")),
 "doneWhen": "You reached the objective in Zephyr and can diagram the full path from memory.",
 "pitfall": "Skipping notes — in a real engagement, an undocumented path is a path you didn't really do.",
},
"P2-11": {
 "overview": "Execute one full ADCS attack path end to end with Certipy — turning the ESC theory from P2-04 into a real domain compromise in the lab.",
 "steps": [
  "Pick ESC1 or ESC8 (the most common).",
  "Use `certipy find` to confirm the vulnerable template in your lab.",
  "Follow the ESC1/ESC8 steps to request a certificate and use it to authenticate as a privileged account.",
  "Write down each command AND why it works.",
 ],
 "tools": ["Certipy", "impacket", "A lab with ADCS"],
 "resources": R(("Certipy wiki", "https://github.com/ly4k/Certipy/wiki"), ("Certified Pre-Owned", "https://posts.specterops.io/certified-pre-owned-d95910965cd2")),
 "doneWhen": "You went from a vulnerable template to privileged access via one full ESC path in the lab.",
 "pitfall": "Copy-pasting Certipy commands without understanding which ESC you're doing — know the mechanism.",
},
"P2-12": {
 "overview": "Cross a trust boundary: start in one domain and compromise another through trust abuse. Ties together P2-06 (tickets) and P2-07 (trusts).",
 "steps": [
  "In a multi-domain lab, confirm the trust direction with BloodHound.",
  "Compromise the first domain to the point of having the needed keys/hashes.",
  "Use SID history or a forged inter-realm ticket to reach the second domain.",
  "Diagram the whole cross-domain path.",
 ],
 "tools": ["Rubeus", "impacket", "BloodHound", "Mimikatz (lab)"],
 "resources": R(("HackTricks — cross-forest", "https://book.hacktricks.xyz")),
 "doneWhen": "You compromised a second domain across a trust in the lab and documented the path.",
 "pitfall": "Attempting this before you're solid on tickets — it builds directly on golden/silver ticket skills.",
},
"P2-13": {
 "overview": "Do a full lab compromise with NO Metasploit and NO Mimikatz 'easy button' — only Rubeus/Certipy/impacket. This forces real understanding over point-and-click.",
 "steps": [
  "Pick a lab you can already beat with the easy tools.",
  "Redo it using only the manual toolkit (impacket, Rubeus, Certipy, evil-winrm).",
  "When something's harder, that friction is teaching you what the easy button hid.",
  "Note what you learned that the automated path had hidden from you.",
 ],
 "tools": ["impacket", "Rubeus", "Certipy", "evil-winrm"],
 "resources": R(("impacket", "https://github.com/fortra/impacket"), ("Rubeus", "https://github.com/GhostPack/Rubeus")),
 "doneWhen": "You fully compromised a lab without Metasploit or Mimikatz's convenience features.",
 "pitfall": "Falling back to the easy button when stuck — pushing through is the entire exercise.",
},
"P2-14": {
 "overview": "The Phase 2 real test: own a FRESH, unseen AD lab entirely on your own, then produce a path diagram and remediation advice — exactly what a junior red teamer delivers.",
 "steps": [
  "Get an AD lab you haven't seen (a new HTB box/lab or a friend's build).",
  "Compromise it unassisted, taking screenshots and notes as evidence.",
  "Draw the attack path as a diagram.",
  "Write remediation: for each step, how the defender should have stopped it.",
 ],
 "tools": ["An unseen AD lab", "diagramming tool (draw.io)", "BloodHound"],
 "resources": R(("draw.io", "https://app.diagrams.net")),
 "doneWhen": "You independently owned a new AD lab and produced a path diagram plus remediation.",
 "pitfall": "Judging success only by 'got Domain Admin' — the diagram and remediation are half the job.",
},
"P2-15": {
 "overview": "Milestone: pass CRTP (Certified Red Team Professional) — the industry entry cert for practical AD attacks. A real, exam-based proof of your Phase 2 skills.",
 "steps": [
  "Enroll in Altered Security's CRTP course and work through all the labs.",
  "Practise the exam-style objectives until the core attacks are muscle memory.",
  "Book and pass the 24-hour practical exam, then write the report.",
  "This is optional-but-recommended; the skills matter more than the badge, but the badge helps.",
 ],
 "tools": ["Altered Security CRTP course + lab", "Your notes"],
 "resources": R(("Altered Security — CRTP", "https://www.alteredsecurity.com/gcb")),
 "doneWhen": "You passed the CRTP exam and submitted the report.",
 "pitfall": "Treating the cert as the goal — it's a checkpoint proving the skills you've been building, not the finish line.",
},
})
# ============================== BEGINNER · PHASE 3 ==============================
BEGINNER.update({
"P3-01": {
 "overview": "Learn how a Command-and-Control (C2) framework works — the 'remote control' an operator uses to task an implant. Concept-first; make sure Phases 1-2 are solid before diving in.",
 "steps": [
  "Learn the pieces: operator -> team server -> listener -> a beacon/agent that calls back on a sleep interval.",
  "Understand 'sleep' and 'jitter' (how often and how randomly the agent checks in) and why they affect detection.",
  "Spin up a free C2 (Sliver is beginner-friendly) in your lab and run a BENIGN agent between two of your own VMs.",
  "Watch the callbacks in your SIEM / Wireshark — see what 'normal' C2 traffic looks like.",
 ],
 "tools": ["Sliver (open-source C2)", "Your lab VMs", "Wireshark", "Your SIEM"],
 "resources": R(("Sliver wiki", "https://github.com/BishopFox/sliver/wiki"), ("The C2 Matrix", "https://www.thec2matrix.com")),
 "doneWhen": "You ran a benign agent in your lab and can draw the operator->team server->listener->beacon chain from memory.",
 "pitfall": "Jumping to evasion before you understand the tasking model — learn how C2 works first; hiding it comes in Phase 4.",
},
"P3-02": {
 "overview": "An introduction to how offensive payloads run code in memory. This is real malware-development territory — strictly lab-only, benign test payloads, on machines you own.",
 "steps": [
  "Learn the vocabulary: shellcode, a 'loader' that runs it, and 'injection' (running code inside another process).",
  "Read what the common techniques do by name: classic injection, APC, thread hijack, process hollowing.",
  "Follow a tutorial to run BENIGN shellcode (e.g. a calc/messagebox stub, or a Sliver agent) via a simple loader in your lab.",
  "Keep it in the lab and understand each line — don't run anything you can't explain.",
 ],
 "tools": ["Visual Studio (C#)", "msfvenom (benign stub) or Sliver shellcode", "A lab VM", "x64dbg (optional)"],
 "resources": R(("ired.team — process injection", "https://www.ired.team"), ("MalDev Academy", "https://maldevacademy.com")),
 "doneWhen": "You ran benign shellcode through a basic loader in your lab and can explain what injection means.",
 "pitfall": "Downloading random 'stealer' code to try — you only ever need benign test payloads to learn the mechanics.",
},
"P3-03": {
 "overview": "Understand the Windows API from an offensive angle, and why 'syscalls' exist as an evasion idea. Builds directly on your C/C# from Phase 1.",
 "steps": [
  "Learn how a normal program calls Windows: your code -> a Win32 API (kernel32) -> ntdll -> a syscall into the kernel.",
  "Understand why security products 'hook' those APIs to watch you, and how calling the syscall directly can skip the hook.",
  "Read one 'direct syscall' explainer — you don't need to write one yet, just grasp the concept.",
  "Note where each layer is and which one the EDR watches.",
 ],
 "tools": ["Visual Studio / C", "PE-bear (inspect ntdll)", "reference: ired.team"],
 "resources": R(("ired.team — syscalls", "https://www.ired.team"), ("Microsoft — Win32 API", "https://learn.microsoft.com/windows/win32/api/")),
 "doneWhen": "You can draw the call path (your code -> Win32 -> ntdll -> syscall) and say where an EDR typically hooks.",
 "pitfall": "Collecting syscall tools without understanding the call path — the concept matters more than any one PoC.",
},
"P3-04": {
 "overview": "Learn what 'redirector' infrastructure is: the servers that sit between your C2 and the target so your real server stays hidden. Intro level — concepts and a simple setup.",
 "steps": [
  "Understand the idea: target talks to a cheap throwaway 'redirector' which forwards to your hidden team server.",
  "Learn why operators use TLS, real domains, and categorization to blend in.",
  "In your lab (or a cheap VPS you own), set up a basic nginx reverse proxy forwarding to a C2 listener.",
  "Learn what 'infrastructure as code' (Terraform/Ansible) means — automating this setup — even if you script it by hand first.",
 ],
 "tools": ["nginx / Apache", "A VPS you own (or a lab VM)", "Terraform (intro)", "Let's Encrypt / certbot"],
 "resources": R(("Red Team Infrastructure Wiki", "https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki"), ("Terraform intro", "https://developer.hashicorp.com/terraform/intro")),
 "doneWhen": "You stood up a simple reverse proxy that forwards traffic to a C2 listener in your lab.",
 "pitfall": "Exposing a real C2 team server directly to the internet — the whole point of a redirector is that you never do that.",
},
"P3-05": {
 "overview": "Get hands-on with Cobalt Strike, the industry-standard commercial C2 — the tool many real engagements use. (Requires a licence; if you don't have one, do P3-06 with a free C2 instead.)",
 "steps": [
  "If you have access, set up a team server and connect the client in your lab.",
  "Learn the core workflow: listener -> generate a beacon -> interact -> run tasks -> pivot.",
  "Practise the built-in AD tooling and how beacon 'sleep' affects your interactivity.",
  "Do everything against your own lab hosts only.",
 ],
 "tools": ["Cobalt Strike (licensed)", "Your lab VMs"],
 "resources": R(("Cobalt Strike documentation", "https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/welcome_main.htm")),
 "doneWhen": "You ran a full listener->beacon->task->pivot workflow against your lab.",
 "pitfall": "No licence? Don't pirate it — the free C2s in P3-06 teach the same concepts perfectly well.",
},
"P3-06": {
 "overview": "Master an open-source C2 (Sliver, Mythic, or Havoc) — free, powerful, and great for learning the same tradecraft as commercial tools.",
 "steps": [
  "Pick one (Sliver is the easiest first) and install its team server in your lab.",
  "Generate a benign agent, run it on a lab VM, and complete the task/pivot workflow.",
  "Compare it to what you learned about Cobalt Strike — the concepts transfer.",
  "Explore its profiles/config to see how you'd shape its traffic later.",
 ],
 "tools": ["Sliver / Mythic / Havoc", "Your lab VMs", "Docker (for Mythic)"],
 "resources": R(("Sliver wiki", "https://github.com/BishopFox/sliver/wiki"), ("Mythic docs", "https://docs.mythic-c2.net")),
 "doneWhen": "You ran an end-to-end op (deploy agent -> task -> pivot) with an open-source C2 in your lab.",
 "pitfall": "Flitting between three C2s shallowly — get genuinely fluent in one before sampling the others.",
},
"P3-07": {
 "overview": "Write your own simple shellcode loader — once in C# and once in C — that runs a BENIGN beacon in your lab. Your first real offensive tool.",
 "steps": [
  "Generate a benign agent's shellcode (e.g. a Sliver agent for your lab).",
  "Write a minimal C# loader: allocate memory, copy the shellcode, run it. Test in the lab.",
  "Do the same in C to feel the raw Win32 calls (VirtualAlloc, CreateThread).",
  "Explain every API call you used and why.",
 ],
 "tools": ["Visual Studio (C# and C)", "Sliver (benign shellcode)", "A lab VM"],
 "resources": R(("ired.team — shellcode execution", "https://www.ired.team"), ("MalDev Academy", "https://maldevacademy.com")),
 "doneWhen": "Both your C# and C loaders run a benign beacon in the lab and you understand each API call.",
 "pitfall": "Copying a loader wholesale — write it yourself so you understand allocation, copy, and execute.",
},
"P3-08": {
 "overview": "Stand up HTTP + DNS redirector infrastructure with Terraform and run a lab op through it. Turns the P3-04 concepts into automated, reproducible infra.",
 "steps": [
  "Write a small Terraform config that provisions a VPS you own and installs an nginx (HTTP) redirector.",
  "Add a DNS redirector concept (a domain you own pointing at the redirector).",
  "Run a benign agent through the redirector to your hidden team server.",
  "Tear it down with Terraform — reproducibility is the point.",
 ],
 "tools": ["Terraform", "A cloud account you own", "nginx", "A domain you own"],
 "resources": R(("Red Team Infrastructure Wiki", "https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki"), ("Terraform docs", "https://developer.hashicorp.com/terraform/docs")),
 "doneWhen": "An agent reaches your team server only via the Terraform-provisioned redirector, and you can rebuild it from code.",
 "pitfall": "Hardcoding secrets/keys into Terraform files you might commit — keep them out of version control.",
},
"P3-09": {
 "overview": "Author a C2 'malleable' profile (traffic-shaping config) and watch how it changes your network signature in the SIEM. Where offense meets detection-awareness.",
 "steps": [
  "Read a sample malleable/HTTP profile and understand which parts shape the request/response.",
  "Change a few fields (user-agent, URIs, headers) and re-run a benign beacon in your lab.",
  "Capture before/after in your SIEM / Wireshark and note what changed.",
  "Write down which signals a defender could still key on.",
 ],
 "tools": ["Your C2's profile system", "Wireshark", "Your SIEM"],
 "resources": R(("Cobalt Strike Malleable C2 reference", "https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2_main.htm")),
 "doneWhen": "You changed a profile and can show the before/after difference in captured traffic.",
 "pitfall": "Assuming a custom profile makes you invisible — you're changing the signature, not removing it.",
},
"P3-10": {
 "overview": "Implement three injection techniques and compare the Sysmon/ETW footprint of each. Directly connects your loaders (P3-07) to detection.",
 "steps": [
  "Pick three techniques (e.g. classic CreateRemoteThread, APC, and process hollowing).",
  "Run each with a benign payload in your lab, one at a time.",
  "For each, collect the Sysmon events (e.g. CreateRemoteThread=8) and note what fired.",
  "Rank them from noisiest to quietest and explain why.",
 ],
 "tools": ["Your loaders", "Sysmon", "Your SIEM", "A lab VM"],
 "resources": R(("ired.team — process injection", "https://www.ired.team"), ("Sysmon docs", "https://learn.microsoft.com/sysinternals/downloads/sysmon")),
 "doneWhen": "You have a side-by-side note of what telemetry each of three injection techniques produced.",
 "pitfall": "Only trying the loudest technique — the learning is in comparing footprints.",
},
"P3-11": {
 "overview": "Work through the Sektor7 'RED TEAM Operator: Malware Development Essentials' course — a structured, beginner-friendly path into offensive tooling.",
 "steps": [
  "Enroll and follow the modules in order; code along, don't just watch.",
  "Rebuild each example yourself in your lab.",
  "Keep a personal cheat-sheet of the techniques as you go.",
  "Everything runs in your lab against your own machines.",
 ],
 "tools": ["Sektor7 course", "Visual Studio", "A lab VM"],
 "resources": R(("Sektor7 Institute", "https://institute.sektor7.net")),
 "doneWhen": "You completed the course and rebuilt its core examples from scratch in your lab.",
 "pitfall": "Watching passively — type and run every example, or none of it will stick.",
},
})
BEGINNER.update({
"P3-12": {
 "overview": "Work through MalDev Academy's core modules (loaders, injection, evasion) — a modern, structured malware-development curriculum, all in your own lab.",
 "steps": [
  "Follow the loader and injection modules in order, coding each one yourself.",
  "Run every example against your own lab VMs with benign payloads.",
  "Note how each technique maps to the telemetry you learned about in Phase 1.",
  "Build a small personal library of the primitives you've learned.",
 ],
 "tools": ["MalDev Academy", "Visual Studio", "A lab VM"],
 "resources": R(("MalDev Academy", "https://maldevacademy.com")),
 "doneWhen": "You completed the core modules and can rebuild a loader + one injection technique from memory.",
 "pitfall": "Hoarding course code you never compile — the reps in the lab are what build the skill.",
},
"P3-13": {
 "overview": "The Phase 3 test: a loader YOU wrote gets a benign beacon past default-config Windows Defender in your lab, and you can explain why each evasion step works.",
 "steps": [
  "Start from your own loader (P3-07). Test it against a lab VM with default Defender on.",
  "Add evasion iteratively (e.g. avoid known-bad API patterns), testing after each change.",
  "For every change, write one sentence on WHY it helps.",
  "Keep the payload benign — this is about the loader, not the payload.",
 ],
 "tools": ["Your loader", "A Defender-enabled lab VM", "Benign shellcode"],
 "resources": R(("MalDev Academy", "https://maldevacademy.com"), ("ired.team — evasion", "https://www.ired.team")),
 "doneWhen": "Your own loader runs a benign beacon on a default-Defender lab VM and you can justify each evasion.",
 "pitfall": "Chasing 'FUD' crypters you didn't write — you won't learn, and they break the moment signatures update.",
},
"P3-14": {
 "overview": "Milestone: pass CRTO (Certified Red Team Operator, Zero-Point Security) — the go-to practical cert for C2 tradecraft and evasion. Optional but highly regarded.",
 "steps": [
  "Take the CRTO course and complete its Cobalt Strike lab exercises.",
  "Practise the full attack chain until it's second nature.",
  "Book and pass the practical exam, then write the report.",
  "Remember: the exam proves the tradecraft you've built across Phase 3.",
 ],
 "tools": ["Zero-Point Security CRTO course + lab"],
 "resources": R(("Zero-Point Security — CRTO", "https://training.zeropointsecurity.co.uk/courses/red-team-ops")),
 "doneWhen": "You passed CRTO and submitted the report.",
 "pitfall": "Cramming exam steps without the underlying tradecraft — CRTO rewards understanding, not memorised commands.",
},
})
BEGINNER.update({
"P4-01": {
 "overview": "Learn what AMSI is and, conceptually, how it gets bypassed — and importantly, the detection for each bypass. Defender-awareness, in the lab, on your own machines.",
 "steps": [
  "Recall AMSI from Phase 1: it scans scripts/memory for bad content before they run.",
  "Read (conceptually) how bypasses work — patching the check, or provider tricks.",
  "In your lab, observe a known bypass being used and, crucially, find the log/behaviour that detects it.",
  "Write a mini table: bypass idea -> how a defender catches it.",
 ],
 "tools": ["PowerShell", "Your SIEM", "A lab VM"],
 "resources": R(("Microsoft — AMSI", "https://learn.microsoft.com/windows/win32/amsi/antimalware-scan-interface-portal"), ("ired.team — AMSI", "https://www.ired.team")),
 "doneWhen": "You can explain one AMSI bypass idea AND the detection that would catch it.",
 "pitfall": "Learning bypasses without their detections — the modern operator reasons about both sides.",
},
"P4-02": {
 "overview": "Understand ETW (Event Tracing for Windows) and, at a concept level, 'blinding' it — plus why that's increasingly detected. Awareness first, lab-only.",
 "steps": [
  "Learn what ETW is: a rich telemetry pipeline security tools consume.",
  "Understand conceptually why attackers try to tamper with it and the trade-offs (it's noisy/detected now).",
  "In the lab, look at what an ETW provider emits for a technique you already know.",
  "Note why tampering itself creates a signal.",
 ],
 "tools": ["PerfView / logman", "Your SIEM", "A lab VM"],
 "resources": R(("ired.team — ETW", "https://www.ired.team"), ("Microsoft — ETW", "https://learn.microsoft.com/windows/win32/etw/about-event-tracing")),
 "doneWhen": "You can explain what ETW gives defenders and why blinding it is itself detectable.",
 "pitfall": "Assuming ETW tampering is 'stealth' — it's one of the most-watched behaviours today.",
},
"P4-03": {
 "overview": "The advanced evasion concepts: unhooking, direct/indirect syscalls, call-stack spoofing, sleep-mask. This is deep tradecraft — grasp the ideas before any code.",
 "steps": [
  "Learn what 'hooking' means (an EDR patches ntdll to watch you) and 'unhooking' (restoring the clean copy).",
  "Revisit syscalls (P3-03) and why 'indirect' syscalls are stealthier than 'direct'.",
  "Understand sleep-mask/heap encryption at a high level: hiding your implant in memory while it sleeps.",
  "Don't implement yet — build the mental model first.",
 ],
 "tools": ["reference reading", "x64dbg (to see hooks)", "A lab VM"],
 "resources": R(("ired.team — evasion", "https://www.ired.team"), ("MalDev Academy", "https://maldevacademy.com")),
 "doneWhen": "You can explain hooking/unhooking and why indirect syscalls exist, in plain words.",
 "pitfall": "Copy-pasting an evasion framework you can't explain — you'll have no idea why it works or fails.",
},
"P4-04": {
 "overview": "Understand PPL, LSASS protection, and Credential Guard — the defenses that make credential theft hard, and what they mean for an operator.",
 "steps": [
  "Recall LSASS from Phase 1 (where credentials live) and why it's a target.",
  "Learn what PPL (Protected Process Light) and Credential Guard do to protect it.",
  "In a lab, turn these protections on and observe how credential-dumping behaves differently.",
  "Note what an attacker would need to work around them (and that you shouldn't expect an easy button).",
 ],
 "tools": ["A lab VM (Win 10/11)", "Group Policy", "your SIEM"],
 "resources": R(("Microsoft — Credential Guard", "https://learn.microsoft.com/windows/security/identity-protection/credential-guard/"), ("HackTricks — LSASS", "https://book.hacktricks.xyz")),
 "doneWhen": "You can explain what PPL and Credential Guard protect and why they raise the bar for credential theft.",
 "pitfall": "Assuming classic LSASS dumping always works — modern defenses often stop it cold.",
},
})
BEGINNER.update({
"P4-05": {
 "overview": "Learn what an EDR (Endpoint Detection & Response) actually sees — kernel callbacks, minifilters, ETW-TI. Knowing the sensor is the foundation of all evasion and detection.",
 "steps": [
  "Learn the sources an EDR taps: kernel callbacks (process/thread/image), file/registry minifilters, ETW-TI.",
  "Understand that an EDR builds a behavioural story, not just single events.",
  "In a lab with a free EDR, do a benign action and see what it records.",
  "Map: 'thing I did' -> 'what the EDR saw'.",
 ],
 "tools": ["Elastic Defend (free) or MDE trial", "A lab VM"],
 "resources": R(("Elastic Security docs", "https://www.elastic.co/guide/en/security/current/index.html"), ("MITRE ATT&CK — Data Sources", "https://attack.mitre.org/datasources/")),
 "doneWhen": "You can name three telemetry sources an EDR uses and show one event it captured from your action.",
 "pitfall": "Thinking of an EDR as 'antivirus' — it correlates behaviour over time, which is much harder to evade.",
},
"P4-06": {
 "overview": "Detection engineering basics: write Sigma rules, map to MITRE ATT&CK, and build detections in Elastic/Splunk. The blue-team skill every strong red teamer needs.",
 "steps": [
  "Learn the Sigma rule format (a portable detection YAML).",
  "Take a technique you performed and write a Sigma rule that would catch it.",
  "Convert/load it into your SIEM and test it against your own attack.",
  "Tag it with the ATT&CK technique ID.",
 ],
 "tools": ["Sigma", "Your SIEM (Elastic/Splunk)", "MITRE ATT&CK Navigator"],
 "resources": R(("Sigma (SigmaHQ)", "https://github.com/SigmaHQ/sigma"), ("MITRE ATT&CK", "https://attack.mitre.org")),
 "doneWhen": "You wrote a Sigma rule that fires on one of your own lab attacks.",
 "pitfall": "Writing rules you never test — an untested detection is just a guess.",
},
"P4-07": {
 "overview": "Deploy a real EDR in your lab and iterate your loaders against it. The big step from 'beat Defender' to 'understand a modern sensor'.",
 "steps": [
  "Stand up a free/eval EDR (Elastic Defend or MDE eval) on a lab VM.",
  "Run your benign loader and watch what the EDR flags.",
  "Change one thing, re-run, and observe the difference — a tight feedback loop.",
  "Keep notes on what triggered and what didn't.",
 ],
 "tools": ["Elastic Defend / MDE eval", "Your loaders", "A lab VM"],
 "resources": R(("Elastic Defend", "https://www.elastic.co/guide/en/security/current/install-endpoint.html")),
 "doneWhen": "You ran your loader against a real EDR and logged what it detected across a few iterations.",
 "pitfall": "Testing against Defender only and assuming EDRs behave the same — they see far more.",
},
"P4-08": {
 "overview": "Use a pre-built purple-team lab (DetectionLab / SimuLand / Splunk Attack Range) to run paired attack + detect exercises without building everything yourself.",
 "steps": [
  "Pick one project and follow its deploy guide (they automate a lot).",
  "Run a built-in attack scenario and watch the detections light up.",
  "Tweak the attack and see how the detection responds.",
  "Note what these give you that your hand-built lab doesn't.",
 ],
 "tools": ["DetectionLab / SimuLand / Splunk Attack Range"],
 "resources": R(("DetectionLab", "https://github.com/clong/DetectionLab"), ("Splunk Attack Range", "https://github.com/splunk/attack_range")),
 "doneWhen": "You ran one attack+detect scenario end to end in a pre-built purple lab.",
 "pitfall": "Getting stuck in setup — these can be heavy; use a project that matches your hardware.",
},
"P4-09": {
 "overview": "Use MITRE Caldera + Atomic Red Team to run a technique, observe the telemetry, and tune the detection. Automated adversary emulation for beginners.",
 "steps": [
  "Install Atomic Red Team and run a single atomic test for a technique you know.",
  "Watch the telemetry it produces in your SIEM/EDR.",
  "Tune or write a detection so it reliably catches that atomic.",
  "Try Caldera to chain a few techniques automatically.",
 ],
 "tools": ["Atomic Red Team", "MITRE Caldera", "Your SIEM"],
 "resources": R(("Atomic Red Team", "https://github.com/redcanaryco/atomic-red-team"), ("MITRE Caldera", "https://github.com/mitre/caldera")),
 "doneWhen": "You ran an atomic test, saw its telemetry, and tuned a detection that catches it.",
 "pitfall": "Running atomics blind on a machine you care about — use the lab; some tests make real changes.",
},
})
BEGINNER.update({
"P4-10": {
 "overview": "The evade -> re-detect loop, five times: evade Defender, then write the detection that re-catches you. The single best exercise for becoming detection-aware.",
 "steps": [
  "Get a benign technique past Defender in your lab.",
  "Then switch hats: write the Sigma/EDR rule that would catch what you just did.",
  "Verify your rule fires, then find a new evasion — and repeat five times.",
  "Keep a log of each round: evasion used -> detection written.",
 ],
 "tools": ["Your loaders", "Sigma", "Your SIEM/EDR", "A lab VM"],
 "resources": R(("Sigma", "https://github.com/SigmaHQ/sigma"), ("ired.team", "https://www.ired.team")),
 "doneWhen": "You completed five evade->re-detect rounds, each with a working detection.",
 "pitfall": "Only doing the evade half — the discipline of re-detecting is what makes this valuable.",
},
"P4-11": {
 "overview": "Build a 'telemetry budget' document: list every signal a full attack chain emits, and its mitigation. Trains you to think in signals, like a real operator.",
 "steps": [
  "Take an attack chain you can run in the lab.",
  "For each step, list every log/telemetry it produces (from your Phase-1 notes and SIEM).",
  "For each signal, note how you'd reduce or avoid it (or accept it).",
  "The result is a one-page 'what this op costs me in noise' doc.",
 ],
 "tools": ["Your SIEM", "A notes/spreadsheet tool"],
 "resources": R(("MITRE ATT&CK", "https://attack.mitre.org")),
 "doneWhen": "You produced a per-step telemetry budget for one full chain with mitigations.",
 "pitfall": "Listing only the obvious logs — the subtle signals are the ones that catch experienced operators.",
},
"P4-12": {
 "overview": "The Phase 4 test: a custom implant survives a REAL EDR through a multi-step chain, and you hand over a detection pack. Both sides of the coin.",
 "steps": [
  "Use your own tooling to run a benign multi-step chain against a real EDR in the lab.",
  "Where it's caught, iterate; where it survives, note why.",
  "Then write a detection pack (Sigma/EDR rules) that WOULD catch your chain.",
  "Deliver both: the red narrative and the blue detections.",
 ],
 "tools": ["Your implant/loaders", "A real EDR (lab)", "Sigma"],
 "resources": R(("Elastic Security", "https://www.elastic.co/security"), ("Sigma", "https://github.com/SigmaHQ/sigma")),
 "doneWhen": "Your chain survived a real EDR AND you produced detections that catch it.",
 "pitfall": "Declaring victory at 'it ran' — without the detection pack you've only done half the exercise.",
},
"P4-13": {
 "overview": "Milestone (optional): pass OffSec OSEP (PEN-300) — a well-known cert covering evasion and lateral movement. A solid external checkpoint for Phase 4 skills.",
 "steps": [
  "Take the PEN-300 course and work all the lab exercises.",
  "Focus on the evasion and AV/EDR-bypass material.",
  "Book and pass the 48-hour practical exam.",
  "Optional — skip if you're prioritising red-team-specific certs (CRTO/CRTL).",
 ],
 "tools": ["OffSec PEN-300 course + labs"],
 "resources": R(("OffSec — PEN-300 / OSEP", "https://www.offsec.com/courses/pen-300/")),
 "doneWhen": "You passed the OSEP exam.",
 "pitfall": "Chasing every cert — pick the ones that match your target role instead of collecting them all.",
},
})
BEGINNER.update({
"P5-01": {
 "overview": "Learn Entra ID (formerly Azure AD) — cloud identity: OAuth/OIDC, tokens (especially the PRT), conditional access, app registrations, and consent phishing. The cloud half of modern attacks.",
 "steps": [
  "Get a free Microsoft 365 developer tenant to practise in (yours to break).",
  "Learn the vocabulary: tenant, user, app registration, service principal, OAuth token, PRT, conditional access.",
  "Understand 'consent phishing' and the device-code flow at a concept level.",
  "Enumerate your own dev tenant with a read-only tool to see the objects.",
 ],
 "tools": ["Microsoft 365 developer tenant", "Microsoft Graph", "AADInternals (read-only, lab)"],
 "resources": R(("Microsoft — Entra ID", "https://learn.microsoft.com/entra/identity/"), ("AADInternals", "https://aadinternals.com")),
 "doneWhen": "You can explain what a PRT and conditional access are, using your own dev tenant to point at objects.",
 "pitfall": "Testing on a real company tenant — always use your own free developer tenant.",
},
"P5-02": {
 "overview": "Understand hybrid identity: how on-prem AD syncs to Entra via Entra Connect, and the attack paths in PHS/PTA/federation. Where on-prem and cloud meet.",
 "steps": [
  "Learn the three sync models: Password Hash Sync, Pass-Through Auth, and Federation.",
  "Understand why Entra Connect is a high-value target (it bridges both worlds).",
  "In a lab, set up (or read a walkthrough of) Entra Connect and see what syncs.",
  "Note, conceptually, the attack path each sync model exposes.",
 ],
 "tools": ["A lab tenant + lab AD", "Entra Connect", "reference reading"],
 "resources": R(("Microsoft — Entra Connect", "https://learn.microsoft.com/entra/identity/hybrid/connect/whatis-azure-ad-connect"), ("AADInternals", "https://aadinternals.com")),
 "doneWhen": "You can explain PHS vs PTA vs federation and why Entra Connect is a prime target.",
 "pitfall": "Blurring the sync models together — each has a distinct attack path, so keep them straight.",
},
"P5-03": {
 "overview": "Learn on-prem <-> cloud pivots: ADFS/PRT abuse, Intune, synced credentials, seamless SSO. How a foothold in one world becomes control of the other.",
 "steps": [
  "Understand the PRT as a 'cloud SSO token' and why stealing it is powerful.",
  "Learn how Intune (cloud device management) can push actions to endpoints.",
  "In a hybrid lab, trace how a synced credential could be used in the cloud.",
  "Sketch a pivot path in each direction (on-prem->cloud and cloud->on-prem).",
 ],
 "tools": ["Hybrid lab", "AADInternals (lab)", "reference reading"],
 "resources": R(("Microsoft — PRT", "https://learn.microsoft.com/entra/identity/devices/concept-primary-refresh-token"), ("dirkjanm blog — cloud attacks", "https://dirkjanm.io")),
 "doneWhen": "You can describe one on-prem->cloud and one cloud->on-prem pivot at a conceptual level.",
 "pitfall": "Thinking the network boundary contains an attacker — synced identity crosses it in both directions.",
},
"P5-04": {
 "overview": "Learn AWS attack basics: IAM privilege-escalation paths, role assumption, the instance metadata service (SSRF-to-creds), and the Pacu methodology. Cloud provider #1.",
 "steps": [
  "Learn IAM fundamentals: users, roles, policies, and what 'assume role' means.",
  "Understand the metadata service (169.254.169.254) and why SSRF can steal credentials from it.",
  "Set up a personal AWS account (free tier) and enumerate your own IAM with least privilege.",
  "Read the Pacu framework's methodology (don't run it against anything but your own account).",
 ],
 "tools": ["A personal AWS account (free tier)", "AWS CLI", "Pacu (own account only)"],
 "resources": R(("AWS IAM docs", "https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html"), ("Pacu", "https://github.com/RhinoSecurityLabs/pacu")),
 "doneWhen": "You can explain one IAM priv-esc path and how metadata-service SSRF yields credentials.",
 "pitfall": "Running cloud attack tools against accounts you don't own — only ever your own AWS account.",
},
"P5-05": {
 "overview": "Learn GCP IAM and service accounts, plus containers/Kubernetes as a pivot surface (RBAC, SA tokens, escapes). Cloud provider #2 and the container angle.",
 "steps": [
  "Learn GCP IAM and what a service account (SA) is, and how SA tokens work.",
  "Understand Kubernetes basics: pods, RBAC, and the service-account token mounted in a pod.",
  "In a personal GCP project (free tier) or local Kubernetes (kind/minikube), poke at RBAC.",
  "Learn what a 'container escape' means conceptually.",
 ],
 "tools": ["Personal GCP project (free tier)", "kind/minikube (local k8s)", "kubectl"],
 "resources": R(("GCP IAM docs", "https://cloud.google.com/iam/docs"), ("Kubernetes RBAC", "https://kubernetes.io/docs/reference/access-authn-authz/rbac/")),
 "doneWhen": "You can explain SA tokens and how a pod's mounted token could be abused as a pivot.",
 "pitfall": "Skipping Kubernetes because it seems unrelated — containers are a huge modern pivot surface.",
},
})
BEGINNER.update({
"P5-06": {
 "overview": "Run a CloudGoat (AWS) scenario end to end and write up the attack path. A deliberately-vulnerable, safe playground for AWS attacks.",
 "steps": [
  "Deploy CloudGoat into your own AWS account (it uses Terraform).",
  "Pick a scenario and work it step by step to the goal.",
  "Write down the path: each permission/misconfig you abused.",
  "Destroy the scenario with Terraform when done (avoid surprise costs).",
 ],
 "tools": ["CloudGoat", "Your AWS account", "Terraform", "AWS CLI"],
 "resources": R(("CloudGoat", "https://github.com/RhinoSecurityLabs/cloudgoat")),
 "doneWhen": "You completed one CloudGoat scenario and wrote up the attack path.",
 "pitfall": "Forgetting to tear it down — leftover resources can cost money and widen your attack surface.",
},
"P5-07": {
 "overview": "Work an AzureGoat or PurpleCloud scenario — deliberately-vulnerable Azure/Entra environments for safe practice.",
 "steps": [
  "Deploy AzureGoat (or PurpleCloud) into your own lab tenant/subscription.",
  "Work the scenario to its objective, taking notes.",
  "Map what you did to the Entra concepts from P5-01..P5-03.",
  "Tear it down afterward.",
 ],
 "tools": ["AzureGoat / PurpleCloud", "Your Azure subscription", "Terraform"],
 "resources": R(("AzureGoat", "https://github.com/ine-labs/AzureGoat"), ("PurpleCloud", "https://github.com/iknowjason/PurpleCloud")),
 "doneWhen": "You reached the objective in an Azure/Entra goat scenario and documented the path.",
 "pitfall": "Running cloud goats in a production tenant — always a throwaway lab tenant/subscription.",
},
"P5-08": {
 "overview": "Practise a full cloud identity chain: consent-phish -> token -> Graph enumeration -> a privilege path, in a lab tenant. Ties the Entra concepts together.",
 "steps": [
  "In your dev tenant, simulate a consent-phishing app that requests Graph scopes (to yourself).",
  "Use the resulting token to enumerate the tenant via Microsoft Graph.",
  "Find a privilege path (e.g. an over-permissioned app or role).",
  "Document the chain end to end.",
 ],
 "tools": ["Dev tenant", "Microsoft Graph / GraphRunner", "AADInternals (lab)"],
 "resources": R(("GraphRunner", "https://github.com/dafthack/GraphRunner"), ("Microsoft Graph docs", "https://learn.microsoft.com/graph/")),
 "doneWhen": "You went token -> Graph enumeration -> privilege path in your own lab tenant.",
 "pitfall": "Sending a consent prompt to anyone but yourself — keep the phishing simulation inside your tenant.",
},
"P5-09": {
 "overview": "Practise the boundary crossing: compromise on-prem, harvest synced creds / a PRT, and pivot to cloud (and back). The signature hybrid attack.",
 "steps": [
  "In a hybrid lab, start from an on-prem foothold.",
  "Harvest a synced credential or a PRT from a joined machine.",
  "Use it to authenticate to the cloud tenant, then enumerate.",
  "Try the reverse direction too, and diagram both.",
 ],
 "tools": ["Hybrid lab (AD + Entra Connect)", "AADInternals/ROADtools (lab)", "impacket"],
 "resources": R(("ROADtools", "https://github.com/dirkjanm/ROADtools"), ("dirkjanm blog", "https://dirkjanm.io")),
 "doneWhen": "You pivoted on-prem->cloud (or reverse) in a hybrid lab and documented it.",
 "pitfall": "Underestimating the PRT — treat a stolen PRT as cloud game-over and handle it carefully even in lab.",
},
"P5-10": {
 "overview": "The Phase 5 test: own a HYDRID lab (Entra + Connect + on-prem AD) with a boundary-crossing chain in BOTH directions. Proof you understand hybrid attacks.",
 "steps": [
  "Build (or reuse) a full hybrid lab.",
  "Compromise it with a chain that crosses on-prem->cloud AND cloud->on-prem.",
  "Capture evidence and draw both paths.",
  "Write remediation for each crossing.",
 ],
 "tools": ["Full hybrid lab", "ROADtools/AADInternals", "draw.io"],
 "resources": R(("ROADtools", "https://github.com/dirkjanm/ROADtools")),
 "doneWhen": "You demonstrated boundary crossing in both directions in your hybrid lab, with diagrams.",
 "pitfall": "Only proving one direction — the test is that identity flows both ways.",
},
"P5-11": {
 "overview": "Milestone (optional): pass CARTP (Certified Azure Red Team Professional, Altered Security) — the practical Azure/Entra red-team cert.",
 "steps": [
  "Take the CARTP course and complete its Azure lab exercises.",
  "Practise the token/PRT and hybrid attack paths until fluent.",
  "Book and pass the practical exam, then report.",
  "Optional — pursue if cloud/hybrid is your focus.",
 ],
 "tools": ["Altered Security CARTP course + lab"],
 "resources": R(("Altered Security — CARTP", "https://www.alteredsecurity.com/azureadlab")),
 "doneWhen": "You passed CARTP and submitted the report.",
 "pitfall": "Treating cloud as 'the same as on-prem' in the exam — the identity model is genuinely different.",
},
})
# === APPEND ANCHOR ===


# ===================================================================
# Phase 6 / Tracks / Capstone guides (agent-authored, both modes)
# Conceptual, authorized-labs-only tradecraft. Appended by the build.
# ===================================================================
BEGINNER.update({
 "P6-03": {
  "overview": "Leading an engagement is the difference between running tools and running an operation. This task teaches the paperwork and discipline that keep an engagement legal, safe, and useful to the client: agreeing exactly what's in scope, writing the rules everyone plays by, staying in sync with the blue team, and handling your evidence so it holds up.",
  "steps": [
   "Learn the four documents that authorize you before you touch anything: scope, Rules of Engagement (RoE), a signed authorization / 'get-out-of-jail' letter, and points of contact. If any are missing, you are not authorized yet.",
   "Practise writing a scope statement for a lab target: list in-scope IP ranges, domains, and apps, and explicitly list what is OFF-limits (prod databases, third-party SaaS, physical, social engineering).",
   "Draft a simple RoE for that lab: allowed hours, techniques permitted vs banned (e.g. no DoS, no real data exfil), and a clear escalation path if something breaks.",
   "Write a deconfliction plan: a shared channel and a one-line 'is this you?' message format so the blue team can tell your traffic from a real intruder during an incident.",
   "Set up evidence handling on a personal engagement: timestamp every finding, keep a screenshot + command log, store artifacts in one dated folder, and never copy real sensitive data off-target.",
   "Do a mock kickoff call out loud (even to yourself): confirm scope, contacts, emergency stop word, and reporting cadence."
  ],
  "tools": [
   "A scope / RoE template (SANS or your firm's)",
   "A note/evidence tool (Obsidian, CherryTree, Notion)",
   "A shared comms channel (Signal / Teams / Slack)",
   "A ticketing or timeline log (spreadsheet is fine)",
   "PGP/encrypted storage for evidence"
  ],
  "resources": [
   {
    "name": "PTES - Pre-engagement Interactions",
    "url": "http://www.pentest-standard.org/index.php/Pre-engagement"
   },
   {
    "name": "NIST SP 800-115 - Technical Guide to Security Testing",
    "url": "https://csrc.nist.gov/pubs/sp/800/115/final"
   },
   {
    "name": "SANS - Rules of Engagement / scoping worksheets",
    "url": "https://www.sans.org/"
   }
  ],
  "doneWhen": "You can produce a complete pre-engagement pack for a lab target - scope, RoE, authorization letter, contacts, deconfliction plan, and an evidence-handling procedure - and explain out loud why each item exists.",
  "pitfall": "Treating scope and RoE as boilerplate to sign and forget. The one range you assumed was in-scope, or the 'obviously fine' technique nobody actually authorized, is exactly what turns a great test into a legal and trust disaster."
 },
 "P6-04": {
  "overview": "Purple-teaming isn't a tool, it's a facilitated loop that leaves the team with a better detection than it started with. This task teaches you to RUN THE ROOM: pick one technique, have red execute it while blue watches the telemetry, then tune the detection together and re-run until it fires cleanly. You are learning to drive the collaboration, not just to attack or defend.",
  "steps": [
   "Get authorization and scope in writing first: the exact lab/environment, the window, and who is in the room. Purple only works when everyone knows it is happening, so this is explicitly NOT a covert red-team op.",
   "Pick ONE ATT&CK technique you have already practised (e.g. a credential-dumping or persistence procedure). A small scope gives you a clean, attributable loop.",
   "Set the room up so everyone sees the same thing: a red operator, a blue/detection person, and you facilitating with the SIEM and the MITRE ATT&CK Navigator on a shared screen.",
   "Run the loop out loud - red runs the atomic test, everyone reads the raw telemetry together, blue writes or tunes the detection, red re-runs to confirm it fires and to check for obvious false positives.",
   "Capture the outcome live in one shared place: the technique, what telemetry appeared, the detection you landed on, and any gap you could not cover yet.",
   "Close with a 10-minute debrief: what improved, what to test next, and a single one-page writeup instead of scattered notes."
  ],
  "tools": [
   "Atomic Red Team",
   "Your SIEM (Elastic / Splunk / Wazuh)",
   "MITRE ATT&CK Navigator",
   "DetectionLab (lab environment)",
   "A shared doc or whiteboard"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://github.com/mitre-attack/attack-navigator"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   },
   {
    "name": "SCYTHE Purple Team Exercise Framework (PTEF)",
    "url": "https://github.com/scythe-io/purple-team-exercise-framework"
   }
  ],
  "doneWhen": "You facilitated one full loop - a single technique run, observed, detected, tuned, and re-run to confirm - and produced a one-page shared writeup listing the technique, the telemetry it produced, and the final detection.",
  "pitfall": "Letting it become a red-vs-blue scoreboard. The deliverable is a detection everyone owns, not 'red won because the alert never fired.'"
 },
 "P6-01": {
  "overview": "Threat intelligence is only useful when it becomes something you can test. This task teaches the pipeline every threat-informed red team runs: read a public adversary report, pull out the behaviours (TTPs), map them to MITRE ATT&CK, and turn them into a small emulation plan you could execute in your own lab. It is the bridge between 'reading about APTs' and reproducing their behaviour on an authorized engagement.",
  "steps": [
   "Pick ONE well-written public report (a vendor APT write-up or a CISA advisory) and read it end to end once, for the story, before you touch ATT&CK.",
   "On a second pass, highlight every attacker BEHAVIOUR - not indicators like IPs or hashes, but actions such as 'used a scheduled task for persistence.'",
   "Map each behaviour to an ATT&CK technique ID using the ATT&CK site search; write plain '<report sentence> -> Txxxx' pairs. Getting your first correct mapping is the win here.",
   "Load your technique IDs into ATT&CK Navigator to get a coloured layer - your first visual of what this adversary does.",
   "Order the techniques into a rough kill-chain (initial access -> execution -> persistence -> ... -> impact); that ordering is your emulation-plan skeleton.",
   "For two or three techniques, reference an existing Atomic Red Team test for how you would SAFELY reproduce the behaviour in a lab - do not invent weaponized steps.",
   "Write a one-page plan: adversary, scope, techniques in order, expected telemetry per step, and a note that execution happens ONLY in your own lab or a scoped, authorized engagement - the mapping and planning here is safe desk research."
  ],
  "tools": [
   "MITRE ATT&CK website",
   "ATT&CK Navigator",
   "A public CTI report (vendor or CISA)",
   "Atomic Red Team (reference)",
   "A notes or spreadsheet tool"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org"
   },
   {
    "name": "ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   },
   {
    "name": "Getting Started with ATT&CK (resources)",
    "url": "https://attack.mitre.org/resources/getting-started/"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   }
  ],
  "doneWhen": "You produced a one-page emulation plan from one real report: 8-12 behaviours mapped to ATT&CK technique IDs, ordered by kill-chain phase, each with a note on the telemetry you'd expect it to produce.",
  "pitfall": "Extracting indicators (hashes, IPs, domains) instead of behaviours - IOCs expire in days, while TTPs are what you actually emulate and what defenders actually detect."
 },
 "P6-07": {
  "overview": "CRTL (Certified Red Team Lead, Zero-Point Security) is the advanced follow-up to CRTO: it proves you can operate against modern EDR and hardened Windows controls and reason about tooling internals, not just run a framework. Treat it as the capstone check on your Phase 3-4 evasion and tradecraft. Optional-but-respected — the skills it validates matter more than the badge itself.",
  "steps": [
   "Get the prerequisites solid first: be comfortable at CRTO level with C2 tradecraft and with the AMSI/ETW/EDR concepts from Phase 4 before you enroll — RTO II assumes that baseline.",
   "Everything here is lab-only, on the exam range you are licensed to use — never rehearse these techniques on production or client systems without written authorization.",
   "Enroll in Red Team Ops II and work every hands-on lab; for each defense you get past, write one sentence on the telemetry a defender would still see.",
   "Grab an early win: take one detection (e.g. an EDR userland hook) and explain in plain English why the evasion works AND how blue team could catch it anyway.",
   "Keep a tradecraft notebook of your decisions and their detection trade-offs — that understanding, not memorized commands, is what carries you through the exam.",
   "Book the practical exam, work the range to the objective, and write the professional report."
  ],
  "tools": [
   "Zero-Point Security RTO II course + lab",
   "A C2 framework (as taught)",
   "Your Phase 4 detection lab / SIEM",
   "Tradecraft notebook"
  ],
  "resources": [
   {
    "name": "Zero-Point Security — Red Team Ops II (CRTL)",
    "url": "https://www.zeropointsecurity.co.uk/course/red-team-ops-ii"
   },
   {
    "name": "Zero-Point Security — Exams",
    "url": "https://training.zeropointsecurity.co.uk/pages/exams"
   },
   {
    "name": "MITRE ATT&CK — Defense Evasion (TA0005)",
    "url": "https://attack.mitre.org/tactics/TA0005/"
   }
  ],
  "doneWhen": "You passed the CRTL exam and submitted the report, and you can articulate the detection trade-off for each evasion you relied on.",
  "pitfall": "Attempting CRTL before CRTO-level fundamentals are second nature — RTO II will expose the gaps rather than teach them, and you will burn attempts learning what should already be reflex."
 },
 "TR-05": {
  "overview": "The report is the only part of an engagement the client keeps — brilliant access means nothing if you can't explain it. This task teaches you to tell the same story twice: an executive narrative for leaders who care about business risk, and a technical report for engineers who must reproduce and fix every finding.",
  "steps": [
   "Confirm you have written authorization for the target and treat the report itself as sensitive — scrub or vault live credentials, PII, and internal hostnames per the rules of engagement before anything leaves the lab.",
   "Reread your notes and evidence, then list each finding with a fixed shape: what it is, where (affected assets), impact, the screenshot/log evidence, and the remediation.",
   "Score each finding with the CVSS 3.1 calculator and sort so the worst risk rises to the top — this ordering is the spine of both documents.",
   "Write the TECHNICAL report first: per finding, give clear reproduction steps, evidence, remediation, and a reference so an engineer can act without asking you anything.",
   "Then write the EXECUTIVE narrative: 1-2 pages, no jargon, framed as business risk with a short attack story and prioritized recommendations a non-technical leader can act on.",
   "Add the connective tissue — cover page, scope, methodology, a findings summary table, and an appendix — and proofread the whole thing.",
   "First win: have a peer read only your executive summary cold and tell you the top risk in one sentence; if they can, that page works."
  ],
  "tools": [
   "Report template (Word or Markdown)",
   "CVSS 3.1 calculator (FIRST)",
   "SysReptor or Dradis",
   "Screenshot + annotation tool",
   "MITRE ATT&CK"
  ],
  "resources": [
   {
    "name": "PTES — Reporting",
    "url": "http://www.pentest-standard.org/index.php/Reporting"
   },
   {
    "name": "TCM Security — sample pentest report",
    "url": "https://github.com/hmaverickadams/TCM-Security-Sample-Pentest-Report"
   },
   {
    "name": "CVSS v3.1 calculator",
    "url": "https://www.first.org/cvss/calculator/3.1"
   }
  ],
  "doneWhen": "You have one deliverable where an executive can read ~2 pages and state the top three business risks, and an engineer can pick any finding and fully reproduce it from your steps alone — with no calls back to you.",
  "pitfall": "Writing only the technical report and bolting on a rushed executive summary that's just a jargon-filled recap — leaders stop reading, and your best work goes unseen by the people who fund the fixes."
 },
 "TR-01": {
  "overview": "Memory-corruption exploitation is where you finally see how a bug in C becomes control of a program: an over-long input overwrites something it shouldn't, and eventually the CPU runs an address you chose. This task builds the single most humbling skill in offense — turning a crash into control — on purpose-built teaching targets so you learn the mechanics safely. AUTHORIZATION: do this ONLY on deliberately-vulnerable binaries made for training, inside an isolated offline VM you own; never point these techniques at real software or anyone else's systems.",
  "steps": [
   "Shore up prerequisites first: basic C (what a buffer, pointer, and the stack are) and a little x86/x64 assembly (registers, and how a function call uses the stack). You cannot skip this.",
   "Build ONE isolated, snapshotted Linux VM as your range. Keep it offline. This is where every experiment happens.",
   "Pick ONE purpose-built teaching target — a level from exploit.education or a beginner wargame binary — never a real product. Start with mitigations (NX/ASLR/canary) turned off so the core idea is visible.",
   "Learn the debugger loop with GDB + pwndbg/GEF: set a breakpoint, run the binary, and watch registers, the stack, and memory as your input flows in.",
   "Reproduce a crash: feed a growing input until the instruction pointer (RIP/EIP) gets overwritten with your bytes. Find the exact offset where control flips.",
   "Now turn the mitigations back on ONE at a time (NX, then stack canary, then ASLR) and observe how each one breaks your crash — this teaches you what real exploitation must defeat.",
   "Write the whole crash-to-control path up in your own words, mapping each step to the memory concept underneath it."
  ],
  "tools": [
   "An isolated Linux VM (snapshots on)",
   "GDB + pwndbg or GEF",
   "pwntools",
   "gcc + checksec",
   "A purpose-built vulnerable binary (exploit.education, wargame)"
  ],
  "resources": [
   {
    "name": "exploit.education (Phoenix / Protostar labs)",
    "url": "https://exploit.education"
   },
   {
    "name": "Nightmare — intro binary exploitation course (guyinatuxedo)",
    "url": "https://guyinatuxedo.github.io"
   },
   {
    "name": "CTF101 — Binary Exploitation",
    "url": "https://ctf101.org/binary-exploitation/overview/"
   },
   {
    "name": "LiveOverflow — Binary Hacking series",
    "url": "https://liveoverflow.com"
   }
  ],
  "doneWhen": "In your isolated lab VM you can crash a purpose-built vulnerable binary on demand, show the instruction pointer holding a value YOU chose, name the exact overflow offset, and explain in plain words why each mitigation (NX/canary/ASLR) stopped it when re-enabled.",
  "pitfall": "Grabbing a copy-paste exploit script before you understand the crash. The moment an offset shifts or a mitigation is on, it fails and you have no idea why — the whole point of this task is the reasoning, not a working script."
 },
 "TR-07": {
  "overview": "Purple teaming is where attacker and defender stop working in silos and solve the same problem together. In this task you run ONE complete loop on a single technique so you can watch a detection get born, dodged, and then hardened — the exact feedback cycle that makes real detections better.",
  "steps": [
   "Prereqs first: a lab that both you and a blue teammate control, with logging you can read together (GOAD, DetectionLab, or a home range with Sysmon + a SIEM). Only ever run this on labs you own or an engagement that authorizes it in writing.",
   "Pick ONE small technique with a clear ATT&CK ID (e.g. T1053 Scheduled Task or T1003 credential access). Narrow scope is the whole point — resist doing a full chain.",
   "Attack: run it once with a benign payload and tell your teammate exactly what you did and when, so they can hunt against ground truth instead of guessing.",
   "Detect: your blue teammate writes a detection (a Sigma rule or SIEM query) from the telemetry, and you both confirm it actually fires on your run.",
   "Evade: change just ONE variable (parent process, timing, an encoding, a renamed artifact) and re-run. See whether the same rule still catches you.",
   "Re-detect: your teammate updates the rule to catch the new variant. Write down the gap that existed and the fix that closed it.",
   "Write it up as a small table: attempt, telemetry it produced, detection, evasion, re-detection."
  ],
  "tools": [
   "MITRE ATT&CK",
   "Atomic Red Team",
   "Sysmon",
   "A SIEM (Splunk / Elastic)",
   "Sigma",
   "VECTR"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   },
   {
    "name": "Sigma rules",
    "url": "https://github.com/SigmaHQ/sigma"
   },
   {
    "name": "VECTR (purple-team tracking)",
    "url": "https://vectr.io"
   }
  ],
  "doneWhen": "You have a documented single-technique loop where a detection was written, evaded by exactly one change, and then re-written to catch the variant — every step timestamped and agreed with your blue teammate.",
  "pitfall": "Turning it into a contest of 'did I win?'. The deliverable is a better detection at the end, not a scoreboard against your teammate."
 },
 "CAP-1": {
  "overview": "This is the capstone that proves the whole roadmap actually stuck: you get dropped onto a domain-joined host in an AD lab you have NOT seen before, with no walkthrough, and you work your own way to Domain Admin. The goal isn't just 'win' — it's to produce a clean writeup of the path so you can prove you understood every hop, not just guessed it.",
  "steps": [
   "Confirm scope first: only run this against a lab you built/own or an explicitly authorized range. Write one line at the top of your notes stating what you're allowed to touch — this habit is non-negotiable for real engagements.",
   "Build or obtain a fresh AD lab you have NOT solved before (GOAD/vulnerable-AD, or a friend's build), and take a clean snapshot so you can reset and retry.",
   "Start from the assumed-breach host: run whoami /all, enumerate the domain with BloodHound, and just READ the graph before touching anything.",
   "Pick the least-noisy edge you can actually explain (a Kerberoastable SPN, an ACL you can abuse, a delegation) and work ONE hop at a time — verify each new context with whoami before moving on.",
   "As you go, keep a running timeline: timestamp, host, what you ran, what you got back. This IS your deliverable.",
   "Reach Domain Admin, then reset the lab and re-walk the SAME path from your notes alone — if your writeup can't reproduce the win, it isn't finished."
  ],
  "tools": [
   "A fresh AD lab (GOAD / vulnerable-AD)",
   "BloodHound / SharpHound",
   "PowerView",
   "Impacket",
   "A note-taking tool (Obsidian / CherryTree)"
  ],
  "resources": [
   {
    "name": "GOAD - Game of Active Directory",
    "url": "https://github.com/Orange-Cyberdefense/GOAD"
   },
   {
    "name": "The Hacker Recipes - Active Directory",
    "url": "https://www.thehacker.recipes/"
   },
   {
    "name": "MITRE ATT&CK - Enterprise Matrix",
    "url": "https://attack.mitre.org/matrices/enterprise/"
   }
  ],
  "doneWhen": "You reached Domain Admin unassisted in a lab you had never seen, AND a peer can follow your written path to reproduce the compromise without asking you a single question.",
  "pitfall": "Chasing BloodHound's 'shortest path to Domain Admin' button and pasting tool output you can't explain — the capstone tests whether you understood the path, not whether the tool found one."
 },
 "TR-04": {
  "overview": "These are the four short procedures and the operational discipline that separate a professional operator from a hobbyist: how the client can tell 'is this you?', how you protect their data, how you undo everything you did, and how you stop the whole operation fast. You write them before the engagement starts, as part of the Rules of Engagement, and they are what keep the work legal, safe, and repeatable.",
  "steps": [
   "Confirm scope first: these procedures only ever run against your own lab or a written-authorized engagement. Treat them as part of the RoE, agreed in writing before you touch anything.",
   "Small first win: for your next lab exercise, start a simple activity log with columns for UTC time, source IP, host touched, action, and a one-line description. This single habit is the backbone of deconfliction.",
   "Write a one-page deconfliction procedure: a named point of contact on each side, an out-of-band channel (phone/Signal), and how the blue team can ask 'was that the red team?' and get a fast yes/no.",
   "Write a data-handling note: where loot (credentials, screenshots, PII) is stored, that it is encrypted at rest, who may access it, and the date it gets destroyed after the report is delivered.",
   "Write a cleanup checklist: log every artifact you create as you create it (files, accounts, scheduled tasks, tickets, persistence, C2 implants) so you can remove all of it at the end.",
   "Write a kill-switch procedure: how you would immediately stop all C2 and disable payloads if the client says 'stop' or something goes wrong, including payload kill-dates so nothing keeps running forever.",
   "Rehearse it: on your lab, tear down one implant and revert one change using only your checklist and manifest, not your memory."
  ],
  "tools": [
   "An encrypted store (KeePassXC / VeraCrypt / age)",
   "A notes/wiki tool (Obsidian, OneNote)",
   "An activity-log / manifest sheet",
   "Lab snapshots for reverting",
   "A C2's kill / kill-date feature"
  ],
  "resources": [
   {
    "name": "Red Team Development and Operations (Vest & Tubberville)",
    "url": "https://redteam.guide/"
   },
   {
    "name": "NIST SP 800-115 (testing & data handling)",
    "url": "https://csrc.nist.gov/pubs/sp/800/115/final"
   },
   {
    "name": "PTES - Pre-engagement Interactions",
    "url": "https://www.pentest-standard.org/"
   }
  ],
  "doneWhen": "You have four short written procedures (deconfliction, data-handling, cleanup, kill-switch) plus an activity-log template, and you have used the cleanup checklist to fully revert one lab exercise back to a clean snapshot.",
  "pitfall": "Treating this as boring paperwork to 'do later' - the operator who cannot answer 'was that you?' or cannot cleanly tear down their access loses the client's trust instantly."
 },
 "CAP-5A": {
  "overview": "The capstone: instead of firing off random techniques, you pick ONE real, well-documented threat group, read what analysts have published about how it operates, and turn that intel into a plan you run against a lab you can fully watch. This is the exercise that turns a technique collector into an operator who can think like a specific adversary and prove what a defender would and wouldn't see.",
  "steps": [
   "Pick ONE named group with strong public documentation (a MITRE ATT&CK Group page plus ideally a published adversary emulation plan), and confirm this runs only in a lab you own with written authorization.",
   "Read the threat intel: the group's ATT&CK techniques, typical tooling, and objectives. Build an ATT&CK Navigator layer showing just their techniques so the plan is scoped to them, not to your comfort zone.",
   "Write a short emulation plan: a clear objective (a 'flag'), the in-scope techniques mapped to ATT&CK IDs, and the order you will run them from initial access through to the objective.",
   "Instrument the lab BEFORE you touch it: Sysmon with a good config, an EDR/SIEM, and central logging, so every action is being recorded before you take it. Fire a known-good test to confirm telemetry actually lands.",
   "Execute the plan in the lab using benign stand-ins for the group's tooling. The goal is to reproduce the behaviour and the artifacts it leaves, not to copy the exact malware.",
   "For each step, log what you did and what telemetry it produced; mark which detections fired and which gaps stayed silent.",
   "Write a short after-action report mapping your run back to ATT&CK, listing the detections that caught you and the gaps that didn't."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "Atomic Red Team",
   "MITRE Caldera",
   "Sysmon",
   "A SIEM/EDR (Elastic or Splunk)",
   "VECTR"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK - Groups",
    "url": "https://attack.mitre.org/groups/"
   },
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   }
  ],
  "doneWhen": "You ran a documented named-group emulation end to end in your instrumented lab and produced an after-action report that maps every step to ATT&CK, with the detections it fired and the gaps it exposed.",
  "pitfall": "Emulating a brand name instead of behaviour - running your favourite tools and slapping a group's name on the report. The intel must drive the plan, not the other way round."
 },
 "CAP-5B": {
  "overview": "The point of a second named-APT emulation is not to repeat CAP-5A, it is to prove you can adapt to a DIFFERENT playbook. You pick an actor whose tradecraft deliberately contrasts your first one, run it against your instrumented lab, and the real deliverable is a measurable jump in what your blue team can detect.",
  "steps": [
   "Get scope and rules of engagement in writing first (timing, kill-switch, a deconfliction contact) even in your own lab, so you practise the paperwork every real op needs.",
   "Choose a second actor that CONTRASTS your CAP-5A pick: if #1 was quiet living-off-the-land, choose a louder criminal or destructive actor, and vice-versa. Contrast is the whole point.",
   "Read 2-3 threat-intel reports on that actor, extract its techniques, and build an ATT&CK Navigator layer; overlay it on your CAP-5A layer to see what is genuinely NEW to you.",
   "Baseline BEFORE you attack: record which of the plan's techniques your SIEM/EDR already alerts on, so you have an honest 'before' number.",
   "Write an emulation plan using safe, benign substitutes for anything destructive, then execute it in your lab, logging the start and stop time of each technique for the blue team.",
   "Compare 'after' coverage to your baseline, write or tune Sigma/EDR rules for whatever slipped through, and re-run those techniques to confirm they now fire.",
   "Deliver three things: an executive narrative, a technical report, and a purple-team debrief that states the coverage improvement as a concrete number."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "Caldera / Atomic Red Team",
   "VECTR",
   "Sigma",
   "Your lab SIEM/EDR (Elastic or Splunk)"
  ],
  "resources": [
   {
    "name": "MITRE Adversary Emulation Library (CTID)",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org"
   },
   {
    "name": "VECTR (purple-team tracking)",
    "url": "https://vectr.io"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   }
  ],
  "doneWhen": "You can point to a before/after ATT&CK heatmap for the new actor, at least a few new or tuned detections that now fire on techniques that were silent before, and a delivered exec report + technical report + purple debrief.",
  "pitfall": "Picking an actor too similar to your CAP-5A one (or only running techniques you already detect) so coverage barely moves and you have just repeated the first capstone under a new name."
 },
 "P6-06": {
  "overview": "Detection coverage is only real if you measure it. This task builds the habit of recording, for every technique you run on an authorized engagement, whether the environment prevented it, alerted on it, or missed it entirely, so that the purple-team story becomes data instead of anecdote.",
  "steps": [
   "Stand up a VECTR instance in your own lab and create an Assessment/Campaign scoped to the engagement",
   "For each planned action, add a Test Case tagged to its MITRE ATT&CK technique ID",
   "As you execute in the lab, mark each Test Case outcome: Prevented, Alerted/Detected, Logged-but-missed, or No telemetry",
   "Record supporting evidence per case: timestamp, source host, and which log or alert (or its absence) proved the result",
   "Generate the ATT&CK heatmap view and note which tactics are dark (uncovered)",
   "Export a short summary and hand the gaps to the detection-engineering backlog"
  ],
  "tools": [
   "VECTR",
   "MITRE ATT&CK Navigator",
   "Atomic Red Team",
   "A SIEM or EDR console (for evidence)"
  ],
  "resources": [
   {
    "name": "VECTR (SRA) documentation",
    "url": "https://docs.vectr.io/"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   }
  ],
  "doneWhen": "You have a completed VECTR campaign with every test case scored to an ATT&CK ID and an exported heatmap that visibly marks at least the prevented, detected, and missed outcomes.",
  "pitfall": "Marking a technique 'detected' because you assume a tool should have caught it, instead of confirming the alert or log actually fired and citing the evidence."
 },
 "P6-02": {
  "overview": "MITRE CTID publishes free, TTP-by-TTP emulation plans that model how real adversaries behave. Learning to read one teaches you to think in terms of ATT&CK techniques rather than isolated tricks, and gives you a safe, structured way to exercise a lab and see what your defenses actually catch.",
  "steps": [
   "Skim the ATT&CK framework so you can recognize tactics, techniques, and sub-technique IDs on sight.",
   "Open one published CTID emulation plan and map its sections: intelligence summary, operations flow, and the per-technique breakdown.",
   "Pick a small slice (2-3 techniques) rather than the whole campaign for your first pass.",
   "For each technique, choose a benign substitute (a harmless test action) instead of any live-fire step, and write down the expected telemetry.",
   "Run the slice in an isolated personal lab, then check your logs/EDR to confirm what was and was not observed.",
   "Record each technique as detected / partial / missed, and note one defensive improvement per gap."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "CTID Adversary Emulation Library",
   "Atomic Red Team",
   "Sysmon",
   "A local SIEM or EDR (e.g. Wazuh, Elastic)"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   },
   {
    "name": "ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   }
  ],
  "doneWhen": "You have run a 2-3 technique slice of one CTID plan in your own lab using benign substitutes and produced a detected/partial/missed table with at least one defensive fix noted per gap.",
  "pitfall": "Treating the plan as a checklist to blast through the whole campaign at once, instead of scoping a small slice and actually reading the telemetry each technique should produce."
 },
 "TR-02": {
  "overview": "Reading a published vulnerability write-up and reproducing its analysis in your own lab turns passive reading into durable understanding: you learn to trace a bug from root cause to fix instead of memorizing headlines. This builds the foundational muscle every defender needs — reasoning about why software fails and how a patch closes the gap.",
  "steps": [
   "Pick a CVE with a mature, well-documented write-up and an available fixed version, so the patch is studyable.",
   "Read the advisory and write-up once for the story, then again taking notes on affected versions, root cause, and the fix.",
   "Stand up an isolated lab (offline VM or container) running the vulnerable version — never a production or internet-exposed system.",
   "In plain language, restate the root cause: what assumption the code made that turned out to be wrong.",
   "Observe the researcher's described behavior at the analysis level (logs, crash, error state) without building any weaponized payload.",
   "Diff the vulnerable and patched versions and write one paragraph on how the fix removes the flawed assumption.",
   "Map the technique to a MITRE ATT&CK ID and note one detection or logging signal a defender could watch for."
  ],
  "tools": [
   "A snapshot-capable hypervisor (VirtualBox or VMware Workstation)",
   "Docker for disposable vulnerable targets",
   "git and a diff viewer for comparing pre/post-patch source",
   "MITRE ATT&CK Navigator",
   "A note-taking tool (Obsidian or a plain markdown journal)"
  ],
  "resources": [
   {
    "name": "MITRE CVE Program",
    "url": "https://www.cve.org/"
   },
   {
    "name": "NIST National Vulnerability Database",
    "url": "https://nvd.nist.gov/"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "OWASP Vulnerable Web Applications Directory",
    "url": "https://owasp.org/www-project-vulnerable-web-applications-directory/"
   }
  ],
  "doneWhen": "You can explain the root cause and the fix in your own words in under five minutes, and you have a one-page lab note linking the CVE to an ATT&CK technique and a detection idea.",
  "pitfall": "Chasing a proof-of-concept to \"make it pop\" instead of understanding the bug — copy-pasting an exploit teaches nothing about root cause or defense."
 },
 "P6-05": {
  "overview": "Running a published, sanctioned emulation plan in Caldera against a lab you built and instrumented is the fastest way to see the full purple-team loop: an attacker technique fires, and you watch where (and whether) it lights up in your own logs. It builds the core habit of tying every adversary action back to a piece of defensive telemetry, which is the foundation of detection engineering.",
  "steps": [
   "Build an isolated lab (host-only or internal network, snapshots taken) so nothing can reach production or the internet.",
   "Stand up the Caldera server and deploy an agent to a lab endpoint you fully control.",
   "Before running anything, turn on logging: Sysmon on the endpoint plus log forwarding into a SIEM, and confirm events are arriving.",
   "Pick one published, sanctioned adversary profile or emulation plan and read it end to end so you know which ATT&CK techniques it exercises.",
   "Run a single operation and watch it ability-by-ability rather than firing everything at once.",
   "For each executed ability, hunt the matching artifact in your logs and note whether it was logged, alerted, or missed.",
   "Write a short coverage table (technique to telemetry) and revert your snapshots when done."
  ],
  "tools": [
   "MITRE Caldera",
   "Sysmon",
   "Wazuh or Elastic Security (SIEM)",
   "Atomic Red Team (for baseline sanity checks)",
   "VirtualBox or Proxmox (isolated lab)"
  ],
  "resources": [
   {
    "name": "MITRE Caldera",
    "url": "https://caldera.mitre.org/"
   },
   {
    "name": "Caldera Documentation",
    "url": "https://caldera.readthedocs.io/"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   }
  ],
  "doneWhen": "You have run one full operation and can map every executed ability to at least one telemetry artifact (or explicitly mark it as 'no telemetry') in a written coverage table.",
  "pitfall": "Running the operation before your logging pipeline is verified working, so the techniques fire but you have nothing to measure and no way to tell detection gaps from collection gaps."
 },
 "TR-03": {
  "overview": "Clean, separated infrastructure and consistent attribution are what keep an authorized engagement honest, legal, and useful. This guide builds the professional habit of designing where your operator activity lives, how it can be told apart, and how those choices become the detection signal a defender relies on.",
  "steps": [
   "Study why engagements isolate infrastructure per client and per engagement: blast radius, data hygiene, and legal scope.",
   "Learn the concepts at design level only: staging vs. long-haul, redirectors, C2 tiers, and what an 'attribution indicator' is.",
   "Map how infrastructure choices become defender-observable indicators (TLS certs, domain age, hosting ASN, JA3-style fingerprints).",
   "In your own lab, write a one-page attribution plan: identifiers you will use, what stays constant, and deconfliction contacts.",
   "Practice a deconfliction habit: keep a timestamped activity log tied to source addresses so any action can be reconstructed.",
   "For every hygiene control you list, name the blue-team signal it preserves or creates, tying design back to detection.",
   "Read a public threat report and note where sloppy infrastructure reuse led to attribution."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "VECTR",
   "MITRE Engage",
   "A lab hypervisor (VirtualBox / Proxmox)",
   "A documentation system (Obsidian / GitBook)"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "Red Team Development and Operations",
    "url": "https://redteam.guide/"
   },
   {
    "name": "MITRE Engage",
    "url": "https://engage.mitre.org/"
   }
  ],
  "doneWhen": "You can produce a one-page lab engagement plan that names isolation boundaries, planned attribution indicators, deconfliction contacts, and the detection signal each control maps to.",
  "pitfall": "Reusing infrastructure or operator identifiers across engagements or clients, which contaminates findings and makes deconfliction and honest attribution impossible."
 },
 "TR-06": {
  "overview": "Learning an offensive technique without knowing the trace it leaves is only half an education. A technique-to-telemetry notebook forces you to pair every technique you study with the defender signal it produces, which is the foundation of the purple-team mindset and makes you far more useful to any detection team.",
  "steps": [
   "Create a simple notebook template with fixed columns: technique name, ATT&CK ID, data source, event/log ID, key fields, and a plain-language detection idea.",
   "For each technique you learn, map it to its ATT&CK technique ID and the ATT&CK data source / data component it relates to.",
   "In your own lab only, safely reproduce or observe the technique and watch what appears in logs (Sysmon, Windows Security, EDR, cloud audit).",
   "Record the concrete signal: which event fired, the specific fields that mattered, and what normal versus suspicious looks like.",
   "Write one sentence describing how a defender would detect it, and note any blind spot where you saw no telemetry.",
   "Review entries weekly, tag them by tactic, and link related techniques so patterns emerge."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "Sysmon",
   "Atomic Red Team",
   "Sigma",
   "Windows Event Viewer",
   "VECTR"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK Data Sources",
    "url": "https://attack.mitre.org/datasources/"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   },
   {
    "name": "SigmaHQ detection rules",
    "url": "https://github.com/SigmaHQ/sigma"
   },
   {
    "name": "VECTR purple-team platform",
    "url": "https://vectr.io"
   }
  ],
  "doneWhen": "You have at least 10 techniques logged, each with its data source, a real event/log ID observed in your own lab, the key fields, and a one-sentence detection hypothesis.",
  "pitfall": "Copying ATT&CK descriptions into the notebook instead of actually observing telemetry in your lab, so you record technique names but never the real defender signal."
 },
 "CAP-3": {
  "overview": "This capstone teaches you to close the loop between offense and defense: run one authorized objective against a real EDR in your own lab, then prove what it detected and what it missed. It builds the single most valued skill in purple teaming — turning an attack narrative into concrete, testable detections that make the defense measurably better.",
  "steps": [
   "Pick ONE clear objective and map every planned action to MITRE ATT&CK technique IDs before you touch a keyboard.",
   "Stand up an isolated lab with a licensed/trial EDR and centralized logging you fully own and can reset.",
   "Run the objective safely in your lab, taking timestamped notes of each step, host, and expected telemetry.",
   "Pull the EDR alerts and raw telemetry, then build a coverage matrix: technique -> detected / logged-only / silent.",
   "Write one detection idea (Sigma-style pseudo-logic, no payloads) for every gap you found, and note the data source it needs.",
   "Package a short red-team narrative and a blue-team detection set together so a defender could act on it Monday morning."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "Atomic Red Team",
   "Sigma",
   "VECTR",
   "Elastic Security or a trial EDR",
   "Sysmon"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   },
   {
    "name": "MITRE Engenuity CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "VECTR (SRA)",
    "url": "https://vectr.io/"
   },
   {
    "name": "Atomic Red Team",
    "url": "https://github.com/redcanaryco/atomic-red-team"
   }
  ],
  "doneWhen": "You deliver a paired package: a coverage matrix over your ATT&CK objective plus at least one written detection idea for every silent step, all reproducible in your reset lab.",
  "pitfall": "Treating the EDR's silence as success. The goal is not to evade; it is to document every gap and hand the defender a detection for it."
 },
 "CAP-2": {
  "overview": "This capstone ties every prior skill into one authorized, end-to-end lab engagement: scoping, external footholds, internal movement, and a written report. Working in your own lab with your own tooling and command-and-control infrastructure teaches the discipline that separates a professional operator from a button-pusher, and every step exists to make defenders faster at seeing it.",
  "steps": [
   "Write a one-page rules-of-engagement for your lab: scope, timing windows, out-of-bounds systems, and who to notify if something breaks",
   "Draw the engagement as a kill-chain diagram mapped to MITRE ATT&CK tactics before you touch a keyboard",
   "Stand up isolated C2 infrastructure in your lab and confirm it can only reach lab targets, never the internet or production",
   "Keep a timestamped operator log of every action, host, and artifact so the timeline can be reconstructed later",
   "Practice one authorized foothold and one internal-movement step safely in your lab, pausing to capture what telemetry each generates",
   "Pair each technique with the log source or detection that would catch it and note the gap if none exists",
   "Write a short report with an executive summary, a technical narrative, and prioritized defensive fixes"
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "VECTR",
   "Kali or Parrot lab VMs",
   "Sysmon + Windows Event Logging",
   "Obsidian or CherryTree (operator notes)"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   },
   {
    "name": "VECTR by SRA",
    "url": "https://vectr.io/"
   },
   {
    "name": "PTES Technical Guidelines",
    "url": "http://www.pentest-standard.org/index.php/Main_Page"
   }
  ],
  "doneWhen": "You have a written report from a self-contained lab run that a peer can read and reproduce the timeline from, with at least three prioritized defensive recommendations tied to specific ATT&CK techniques.",
  "pitfall": "Treating it as a hacking speed-run instead of a documentation exercise: no operator log and no detection mapping means the engagement taught you nothing a defender can use."
 },
 "CAP-4": {
  "overview": "Hybrid environments blur the line between cloud and on-prem, and the trust bridges that connect them (identity sync, SSO, federation) are where real attack paths live. This capstone teaches you to reason about a cloud-to-on-prem path methodically — plan it, map it, and document it — instead of chasing tools, building the planning and reporting discipline every authorized engagement depends on.",
  "steps": [
   "Define the lab scope and a single written objective (e.g. reach a specific on-prem resource from an assumed-breach cloud identity); record assumptions and rules of engagement before touching anything.",
   "Study how hybrid identity links cloud and on-prem — identity sync, seamless SSO, and federation — by building a small free lab tenant so you can see the trust bridges safely.",
   "Map the terrain first: enumerate identities, roles, and trust relationships in your lab and draw them before reasoning about any path.",
   "Reason about candidate paths on paper as hypotheses — list each hop and why it works — then practice only in your own lab.",
   "For every hop, record the matching MITRE ATT&CK technique ID and one detection or telemetry source that would catch it.",
   "Document the chosen path end-to-end as an annotated diagram plus a short narrative of the objective and each step.",
   "Write a one-page defensive takeaway naming the single control or detection that would have broken the path earliest."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "BloodHound Community Edition",
   "Microsoft 365 Developer tenant (lab)",
   "draw.io / diagrams.net",
   "VECTR"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK Cloud Matrix",
    "url": "https://attack.mitre.org/matrices/enterprise/cloud/"
   },
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   },
   {
    "name": "Microsoft Entra hybrid identity documentation",
    "url": "https://learn.microsoft.com/en-us/entra/identity/hybrid/"
   },
   {
    "name": "Microsoft 365 Developer Program (free lab tenant)",
    "url": "https://developer.microsoft.com/en-us/microsoft-365/dev-program"
   }
  ],
  "doneWhen": "You produce a single annotated diagram tracing at least one complete cloud-to-on-prem path from initial cloud access to the defined objective, with each hop mapped to an ATT&CK technique ID and a matching detection idea.",
  "pitfall": "Treating it as a tool-running race instead of a reasoning exercise — running enumeration tools without ever mapping the trust relationships or writing down why each hop works."
 }
})

PRO.update({
 "P6-03": {
  "overview": "Owning an engagement means owning the risk envelope, not just the exploitation. This task hardens your pre-engagement and evidence discipline so the operation is legally defensible, deconflicted against a live SOC, and reconstructable months later under scrutiny - the skills that separate an operator from a test lead.",
  "steps": [
   "Drive scoping to precision: negotiate in/out-of-scope assets, third-party and cloud-tenant boundaries (get written provider consent where required), data-handling limits, and explicit constraints on DoS, exfil volume, and lateral reach.",
   "Author RoE that survive contact: authorized windows, permitted TTPs vs prohibited actions, escalation and emergency-stop triggers, named authorizing signatory, and a signed authorization letter carried by every operator.",
   "Stand up deconfliction before go-live: shared out-of-band channel, per-action attribution (source IPs, C2 domains, tooling hashes, campaign IDs), and a real-time 'is this us?' protocol so the blue team can separate you from a genuine intrusion in minutes.",
   "Operate with attribution hygiene: log every action with timestamp, source, target, and command; tag artifacts to campaign IDs; and maintain an activity log detailed enough to feed the client's purple-team review and detection-engineering backlog.",
   "Enforce evidence integrity: chain-of-custody, hashed and encrypted-at-rest artifacts, minimized capture of sensitive data (redact/tokenize PII, never bulk-pull real records), and a documented retention + secure-destruction timeline.",
   "Run structured deconfliction/pause events: know when to call it - crown-jewel systems, unexpected prod impact, discovery of a real prior compromise - and escalate through the agreed contacts rather than pushing on.",
   "Close the loop: reconcile your activity log against SOC alerts in the debrief so every action is either detected, explained, or logged as a coverage gap."
  ],
  "tools": [
   "Scope/RoE + authorization templates (firm-standard)",
   "GhostWriter or similar engagement/OPSEC log",
   "Out-of-band deconfliction channel (Signal/Mattermost)",
   "Evidence store with hashing + encryption (VeraCrypt/GPG)",
   "MITRE ATT&CK for TTP mapping",
   "Activity/timeline logger (structured, exportable)"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK - technique mapping for reporting",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "PTES - Pre-engagement Interactions",
    "url": "http://www.pentest-standard.org/index.php/Pre-engagement"
   },
   {
    "name": "NIST SP 800-115",
    "url": "https://csrc.nist.gov/pubs/sp/800/115/final"
   },
   {
    "name": "CREST - Red Team / assurance guidance",
    "url": "https://www.crest-approved.org/"
   }
  ],
  "doneWhen": "You can lead a full engagement lifecycle in a lab: negotiate and document scope + RoE with a signed authorization, run a deconfliction protocol against a monitoring team, and hand over a chain-of-custody-clean evidence package plus an activity log that reconciles cleanly against defender telemetry.",
  "pitfall": "Confusing authorization with a signature. Scope drift, an un-negotiated cloud/third-party boundary, or evidence you can't prove the integrity of will detonate the moment the engagement is questioned - and it will be questioned precisely when you found something serious."
 },
 "P6-04": {
  "overview": "Facilitation is the skill that converts paired attack+detect reps into durable, measurable detection coverage. You run a time-boxed, ATT&CK-scoped tuning cycle where emulation, telemetry triage, detection-as-code, and re-test happen in one room under tight deconfliction, and you leave with a coverage delta you can defend to a client.",
  "steps": [
   "Pre-brief and scope: lock a small technique/procedure set, define the environment, the deconfliction channel, success metrics (detection present? fidelity? MTTD?), and named roles (facilitator, emulation, detection engineer, scribe).",
   "Emulate controllably - atomic-first, then chain via Caldera - one procedure variant at a time so telemetry attribution is unambiguous.",
   "Drive the loop: execute, triage the raw telemetry (not just the alert), author or tune detection-as-code (Sigma), then re-run to confirm the true positive and probe the false-positive surface with benign look-alikes.",
   "Track coverage on a versioned ATT&CK Navigator layer - detected / partial / gap per procedure - so the before/after delta is explicit rather than anecdotal.",
   "Enforce OPSEC of the exercise itself: announce activity to the SOC, tag emulation hosts/traffic, timestamp every action, and keep lab artifacts out of production detection content.",
   "Close with a delta report: rules shipped, coverage before vs after, unresolved gaps with owners and a next-cycle backlog - and push rules into version control, not a chat log."
  ],
  "tools": [
   "Atomic Red Team",
   "MITRE Caldera",
   "Sigma / detection-as-code pipeline",
   "SIEM (Elastic / Splunk)",
   "ATT&CK Navigator",
   "VECTR"
  ],
  "resources": [
   {
    "name": "SCYTHE Purple Team Exercise Framework (PTEF)",
    "url": "https://github.com/scythe-io/purple-team-exercise-framework"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org"
   },
   {
    "name": "VECTR (purple-team tracking)",
    "url": "https://github.com/SecurityRiskAdvisors/VECTR"
   },
   {
    "name": "Sigma (SigmaHQ)",
    "url": "https://github.com/SigmaHQ/sigma"
   }
  ],
  "doneWhen": "You ran a time-boxed cycle that shipped at least one tuned, version-controlled detection, produced a before/after ATT&CK coverage layer, and delivered a delta report naming remaining gaps and their owners.",
  "pitfall": "Optimising for 'alerts fired' over detection quality - shipping brittle, high-FP rules the SOC mutes within a week. Measure fidelity and durability, not just a green light on the confirming re-run."
 },
 "P6-01": {
  "overview": "Threat-informed operations start here: convert raw CTI into a structured, ATT&CK-mapped emulation plan that a customer's detection engineering can be measured against. This is the intel-to-plan half of purple teaming - the deliverable is a defensible, peer-reviewable emulation plan, not a run log.",
  "steps": [
   "Source-triage the report first: assess confidence, collection bias, and observed-vs-inferred behaviours; note the reporting date so you emulate the campaign, not a stale variant.",
   "Extract TTPs to technique + sub-technique + PROCEDURE detail - procedure-level fidelity ('how') drives emulation and detection far more than the bare technique ID.",
   "Use TRAM to accelerate the first-pass mapping, then hand-verify every hit against the CISA/MITRE mapping best-practices - automated mappers both over- and under-call.",
   "Model sequencing and dependencies with Attack Flow or an ordered Navigator layer; capture the procedure chain, not a bag of techniques.",
   "Author the plan against the CTID Adversary Emulation Library template: objectives, scope, per-technique procedures, expected telemetry, and abort/cleanup criteria.",
   "Define measurement up front - bind each technique to expected data sources and detection hypotheses so execution yields prevented/detected/missed outcomes in VECTR, not vibes.",
   "Treat the plan as sensitive and authorization-bound: scope to RoE, validate all tooling lab-first, and handle sourced CTI plus the plan itself as engagement-restricted material."
  ],
  "tools": [
   "MITRE ATT&CK + Navigator",
   "TRAM",
   "Attack Flow",
   "CTID Adversary Emulation Library",
   "Caldera / Atomic Red Team",
   "VECTR"
  ],
  "resources": [
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "TRAM (Threat Report ATT&CK Mapper)",
    "url": "https://github.com/center-for-threat-informed-defense/tram"
   },
   {
    "name": "CISA - Best Practices for MITRE ATT&CK Mapping",
    "url": "https://www.cisa.gov/resources-tools/resources/best-practices-mitre-attck-mapping"
   },
   {
    "name": "Attack Flow",
    "url": "https://github.com/center-for-threat-informed-defense/attack-flow"
   }
  ],
  "doneWhen": "You have a peer-reviewable, CTID-format emulation plan for a chosen adversary: procedure-level techniques in dependency order, each carrying expected telemetry, a detection hypothesis, and cleanup steps - ready to run as a scoped purple-team exercise and score in VECTR.",
  "pitfall": "Mapping to technique IDs and stopping - a plan without procedure-level detail and expected-telemetry mapping yields green checkmarks, not coverage. Related trap: emulating the sample instead of the behaviour; you emulate the TTP, not a specific malware hash."
 },
 "P6-07": {
  "overview": "CRTL / RTO II is the research-tier checkpoint: sustained operations against EDR-instrumented, hardened Windows. It validates that you reason about telemetry and tooling internals, not just drive a framework. Capstone for your Phase 3-4 evasion and OPSEC.",
  "steps": [
   "Gate-check yourself: CRTO tradecraft fluent, Phase 4 AMSI/ETW/EDR internals internalized — otherwise this becomes tuition, not certification.",
   "Work all nine labs; for every technique map the ATT&CK data source and the exact sensor that observes it (userland hook, kernel callback, ETW-TI, Sysmon).",
   "Run your own EDR-instrumented detection lab in parallel — validate each evasion against real telemetry, never against 'it ran'.",
   "Reason at the primitive level: why a bypass holds, its failure modes, and the residual artifacts it leaves for purple team to hunt.",
   "Range and authorized scope only; treat OPSEC discipline — sleep, jitter, egress, artifact hygiene — as gradeable, because operationally it is.",
   "Sit the exam, reach the objective across the hardened path, and deliver a report a red team lead would sign."
  ],
  "tools": [
   "RTO II course + lab range",
   "C2 (course-provided)",
   "EDR-instrumented lab + SIEM/ETW",
   "BloodHound",
   "Detection notebook"
  ],
  "resources": [
   {
    "name": "Zero-Point Security — Red Team Ops II (CRTL)",
    "url": "https://www.zeropointsecurity.co.uk/course/red-team-ops-ii"
   },
   {
    "name": "Zero-Point Security — Exams",
    "url": "https://training.zeropointsecurity.co.uk/pages/exams"
   },
   {
    "name": "MITRE ATT&CK — Defense Evasion (TA0005)",
    "url": "https://attack.mitre.org/tactics/TA0005/"
   }
  ],
  "doneWhen": "CRTL passed with an accepted report; you can whiteboard the detection surface and failure mode of every technique on the exam path.",
  "pitfall": "Optimizing for 'it evaded' instead of understanding the sensor — the operators who last know precisely what each action costs them in telemetry."
 },
 "TR-05": {
  "overview": "Reporting is the deliverable; the access is throwaway. Two audiences, two artifacts, one evidentiary spine — this task hardens your ability to translate technical findings into board-level risk without losing the reproducibility engineers need to remediate.",
  "steps": [
   "Lock the evidentiary chain: timestamped notes, per-finding evidence, and hashes of any artifacts. Scrub live creds and PII, classify the document, and plan encrypted delivery before anything leaves the range — OPSEC on the report is part of the engagement.",
   "Normalize every finding: title, affected assets, root cause vs symptom, CVSS 3.1 with a business-context adjustment, ATT&CK technique mapping, and remediation with references.",
   "Build the attack narrative / kill chain — how atomic findings chained to the objective. This is the story executives actually buy, not the vuln list.",
   "Write the technical section for zero-back-channel reproduction, separating root cause from instance so remediation is systemic rather than whack-a-mole.",
   "Write the executive narrative to business risk: 1-2 pages, quantified or qualified risk, strategic recommendations, and explicit ties to their risk register and compliance drivers.",
   "Prioritize by risk-to-business, not raw CVSS; give a realistic roadmap that splits quick wins from structural fixes.",
   "State the negative space: what was NOT tested, false-positive handling, deconfliction notes, and the retest window; version and classify the final."
  ],
  "tools": [
   "SysReptor / PlexTrac / Dradis",
   "CVSS 3.1 (FIRST)",
   "MITRE ATT&CK Navigator",
   "DOCX / Markdown / LaTeX template",
   "Hashing + evidence tooling"
  ],
  "resources": [
   {
    "name": "Public pentesting reports (corpus)",
    "url": "https://github.com/juliocesarfort/public-pentesting-reports"
   },
   {
    "name": "NIST SP 800-115",
    "url": "https://csrc.nist.gov/pubs/sp/800/115/final"
   },
   {
    "name": "PTES — Reporting",
    "url": "http://www.pentest-standard.org/index.php/Reporting"
   },
   {
    "name": "MITRE ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   }
  ],
  "doneWhen": "A peer reviewer confirms all three: an exec states top business risks and required decisions from the summary alone; any engineer reproduces and remediates any finding without contacting you; every finding carries evidence, CVSS, an ATT&CK reference, and remediation.",
  "pitfall": "CVSS-as-priority — shipping a base-score-sorted list that ignores context. A 'medium' on a crown-jewel asset outranks a 'high' on a sandbox, and executives need that translation, not the raw vector."
 },
 "TR-01": {
  "overview": "Memory-corruption tradecraft is about primitives and mitigation-defeat reasoning, not one PoC — building a single from-scratch exploit end to end forces the modern mindset: root-cause a bug, promote it to a read/write primitive, leak to defeat ASLR, then engineer reliability. You will rarely deploy bespoke research on an op (N-day with patch context is the norm), but you cannot lead exploit-dev or edge/appliance work without having driven one full chain yourself. Lab-only, airgapped: treat the artifact as sensitive research, not something to run anywhere near production.",
  "steps": [
   "Commit to ONE target and one bug class end to end (Linux userland stack or glibc heap is the pragmatic first; kernel/browser later). Depth over breadth.",
   "Triage properly: reproduce deterministically, root-cause the corruption, classify it (OOB write, UAF, type confusion), and map exactly what data/offsets you control.",
   "Promote the bug to primitives: relative → arbitrary read/write, an info leak to break ASLR/PIE, and an explicit model of allocator/stack state you can steer.",
   "Defeat mitigations methodically — enable NX, PIE/ASLR, stack canary (and CET/shadow-stack if in scope) one at a time; reason through ROP/JOP, leak-first ordering, and what each mitigation costs your chain.",
   "Achieve control-flow hijack → code exec, then engineer RELIABILITY: measure success rate across many runs, harden against heap noise/ASLR variance — a one-off pop is not done.",
   "Write it up as research: bug class, primitive chain, mitigation defeats, reliability %, and the DETECTION footprint it emits (crash artifacts, WER/core dumps, EDR memory scanning) so the purple/blue value is captured.",
   "OPSEC the work: airgapped snapshotted VM, never test unique research against internet-connected or shared infra, and understand the crash telemetry before assuming any real-world use."
  ],
  "tools": [
   "GDB + pwndbg/GEF (WinDbg if Windows)",
   "pwntools",
   "Ghidra / IDA / Binary Ninja",
   "AFL++ or libFuzzer (bug discovery)",
   "ropper / one_gadget",
   "checksec"
  ],
  "resources": [
   {
    "name": "pwn.college — structured exploitation curriculum",
    "url": "https://pwn.college"
   },
   {
    "name": "Corelan — Exploit Writing Tutorials",
    "url": "https://www.corelan.be"
   },
   {
    "name": "Google Project Zero — research writeups (modern primitive/mitigation craft)",
    "url": "https://googleprojectzero.blogspot.com"
   },
   {
    "name": "MITRE ATT&CK T1203 — Exploitation for Client Execution",
    "url": "https://attack.mitre.org/techniques/T1203/"
   }
  ],
  "doneWhen": "You have one reproducible, documented from-scratch exploit for a lab target that lands reliable code execution with NX + ASLR/PIE enabled (info-leak included), rebuildable from your notes alone, plus a research writeup covering the primitive chain, measured reliability, and the telemetry the technique generates.",
  "pitfall": "Calling a mitigations-off, single-run crash 'done', or overfitting to one walkthrough's offsets. The craft lives in defeating at least NX+ASLR via a real leak and in reliability engineering — a fragile PoC that only works with protections disabled teaches you almost nothing transferable."
 },
 "TR-07": {
  "overview": "Purple is a feedback loop, not a scoreboard: it converts your tradecraft into durable defender telemetry. One documented attack->detect->evade->re-detect cycle proves you can drive a detection off a brittle IOC and up to a behavioral analytic that survives your next mutation.",
  "steps": [
   "Scope to a single ATT&CK (sub-)technique. Agree the hypothesis, data sources, and success criteria with blue up front and track the run in VECTR.",
   "Execute white-card against an instrumented range and timestamp every action so blue correlates against ground truth, not blind hunting.",
   "Blue authors the detection from real telemetry, then classifies it — IOC vs tool-signature vs behavior — and places it on the Pyramid of Pain.",
   "Evade deliberately, shifting ONE layer at a time (parent-child, LOLBIN swap, encoding, sleep/jitter, artifact rename) and logging which change broke the rule and why.",
   "Blue re-detects by climbing the pyramid: rebuild the analytic on invariants (the behavioral chain), not the mutated string.",
   "Record metrics per cycle — coverage, MTTD, FP rate, residual gap — and feed unresolved gaps back as the next cycle's hypotheses."
  ],
  "tools": [
   "MITRE ATT&CK + Navigator",
   "Atomic Red Team / CALDERA",
   "Sysmon + ETW",
   "Sigma",
   "SIEM/EDR (Elastic / Splunk)",
   "VECTR"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org"
   },
   {
    "name": "VECTR",
    "url": "https://vectr.io"
   },
   {
    "name": "Sigma rules",
    "url": "https://github.com/SigmaHQ/sigma"
   },
   {
    "name": "MITRE CALDERA",
    "url": "https://caldera.mitre.org"
   }
  ],
  "doneWhen": "VECTR (or equivalent) shows the technique moving detected -> evaded -> re-detected, with the final analytic keyed on behavioral invariants and MTTD / FP-rate / residual-gap recorded for each cycle.",
  "pitfall": "Evading on several variables at once so you can't attribute the bypass — and letting blue 'close' it with a brittle IOC that your next single mutation defeats for free."
 },
 "CAP-1": {
  "overview": "Terminal exam for the whole track: cold, unseen AD range, assumed-breach foothold, no hints, self-directed to DA, then a defensible path writeup. This is where methodology, enumeration discipline, and the ability to justify every edge get stress-tested under your own judgment rather than a walkthrough's.",
  "steps": [
   "Fix scope/authorization and start a timestamped operator log before your first command — every action, host, context, and result. The log is the graded artifact.",
   "Triage the foothold: local context, host posture, and domain recon via BloodHound; enumerate before you act, and prefer collection methods whose telemetry footprint you can name.",
   "Model the graph as attack paths, not a single shortest path — enumerate multiple routes to DA (ACL abuse, Kerberos delegation, cred material, trust/GPO edges) and rank them by reliability and noise.",
   "Execute hop-by-hop with deliberate OPSEC: minimize touches, validate each new principal/context, prefer living-off-the-land, and note the defender signal (Sysmon/4624/4769/4662) each action would generate.",
   "Reach DA, then pivot to blue perspective: for each edge, record the detective/preventive control and the exact event ID or ETW provider that would have caught it — that mapping is what turns this into purple-team value.",
   "Snapshot-reset the range and re-run the path from your writeup alone to prove reproducibility; if a step needed improvisation you didn't document, the writeup fails.",
   "Deliver: attack narrative + graph, per-edge detection mapping, and prioritized remediations tied to the specific misconfigurations you abused."
  ],
  "tools": [
   "BloodHound / SharpHound",
   "PowerView / PowerShell",
   "Impacket",
   "Rubeus",
   "Certipy (AD CS)",
   "netexec (nxc)"
  ],
  "resources": [
   {
    "name": "ired.team - Active Directory",
    "url": "https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse"
   },
   {
    "name": "The Hacker Recipes - AD",
    "url": "https://www.thehacker.recipes/"
   },
   {
    "name": "MITRE ATT&CK - Enterprise Matrix",
    "url": "https://attack.mitre.org/matrices/enterprise/"
   },
   {
    "name": "SpecterOps - BloodHound docs",
    "url": "https://bloodhound.specterops.io/"
   }
  ],
  "doneWhen": "Unassisted DA on a cold range, plus a writeup another operator reproduces from text alone AND that maps every abused edge to its detection source and a concrete remediation.",
  "pitfall": "Treating it as a CTF flag-grab — smashing the noisiest path to DA and skipping the detection/remediation mapping produces a win with no professional deliverable and no evidence you can operate with restraint."
 },
 "TR-04": {
  "overview": "The operational connective tissue of an engagement: a deconfliction channel that lets the blue team distinguish your activity from a real intrusion in seconds, disciplined loot handling, artifact tracking that guarantees full cleanup, and a kill-switch that halts your tradecraft on demand. Weak procedures here get engagements paused, evidence contaminated, or your access mistaken for a genuine breach - and cost you the callback.",
  "steps": [
   "Build a deconfliction protocol: named POCs both sides, an out-of-band channel, and per-op unique markers (canary strings in payloads, dedicated source IPs/user-agents, tagged accounts) so any observed activity is attributable to you in one lookup.",
   "Maintain a real-time operator log (UTC timestamp, host, source, MITRE technique, command intent, artifact created) - it doubles as your deconfliction lookup table and your cleanup manifest.",
   "Define data-handling: classify loot (creds/hashes/tokens/PII), encrypt at rest and in transit, minimize collection, scope access, and set a destruction date tied to report delivery and retention terms; keep chain-of-custody for anything sensitive.",
   "Track every artifact as a manifest entry (dropped files, services, scheduled tasks, accounts, ACL edits, tickets, persistence, implants, redirector infra) with its exact revert action - nothing gets created without a matching cleanup entry.",
   "Engineer the kill-switch: payload kill-dates plus working-hours guardrails, a documented C2 teardown sequence, burnable/rotatable infra, and a single stop-op trigger that halts beacons and disables staging on client request or anomaly.",
   "Frame cleanup against defender telemetry: know which artifacts map to Indicator Removal (T1070) so your teardown doesn't emit louder signal than the activity it hides, and record what you could not cleanly remove for the report.",
   "Rehearse: run a lab op, execute full teardown and kill from the manifest alone, then diff host state against a clean snapshot to prove reversion."
  ],
  "tools": [
   "Encrypted loot store (age / VeraCrypt / KeePassXC)",
   "Operator-log & reporting (GhostWriter, Vectr, Obsidian)",
   "C2 kill-date & teardown (Cobalt Strike / Sliver / Mythic)",
   "IaC for burnable redirectors (Terraform / Ansible)",
   "Lab snapshots for reversion diffing"
  ],
  "resources": [
   {
    "name": "Red Team Development and Operations - deconfliction & data handling",
    "url": "https://redteam.guide/"
   },
   {
    "name": "MITRE ATT&CK T1070 - Indicator Removal",
    "url": "https://attack.mitre.org/techniques/T1070/"
   },
   {
    "name": "GhostWriter (engagement log & report management)",
    "url": "https://ghostwriter.wiki/"
   },
   {
    "name": "Sliver C2 (kill-dates & teardown)",
    "url": "https://github.com/BishopFox/sliver"
   }
  ],
  "doneWhen": "For a mock engagement you can produce a deconfliction one-pager with unique markers, a populated artifact/cleanup manifest, a data-handling + destruction policy, and a kill-switch runbook - then demonstrate a from-manifest teardown that returns a lab host to a clean snapshot with no residual artifacts.",
  "pitfall": "Improvising cleanup from memory instead of a live artifact manifest - you'll orphan a scheduled task, a rogue account, or a live beacon, leaving the client exposed and unable to formally close out the engagement."
 },
 "CAP-5A": {
  "overview": "Intel-driven emulation is what separates adversary emulation from a technique dump: you constrain yourself to one actor's documented TTPs, run them against a fully instrumented range, and score red execution against blue detection. This capstone proves you can plan from CTI, operate inside a defined threat model, and ship a defensible purple-team deliverable rather than a bag of pops.",
  "steps": [
   "Scope one actor with strong public reporting; derive the technique set from ATT&CK Groups plus primary CTI, citing a source per technique. Discipline is refusing techniques the actor doesn't use.",
   "Build the plan as ordered kill-chain phases (initial access -> execution -> persistence -> cred access -> lateral -> collection -> exfil/impact) with ATT&CK IDs, procedure-level notes, and a defined objective/flag.",
   "Stand up the instrumented range first: Sysmon with a curated config, EDR, a network sensor, and centralized logging; validate every sensor with known-good tests before the run so 'missed' means missed, not unmonitored.",
   "Emulate at the procedure level with functional analogs (Caldera, Atomic Red Team, CTID plans, your own benign tooling) - reproduce the behaviour and artifacts the actor generates, never their exact binaries.",
   "Track execution and detection in VECTR: per-technique outcome (blocked / alerted / logged / missed), timestamps, and the precise signal each step emitted.",
   "Run OPSEC analysis on your own trail - map each procedure to its telemetry cost and the hunt/detection that would catch it - and convert every gap into a detection-engineering action.",
   "Deliver a purple report: an ATT&CK coverage heatmap, prioritized detection gaps, and concrete rule/hunt recommendations the blue team can implement."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "MITRE Caldera",
   "CTID Adversary Emulation Library",
   "VECTR",
   "Sysmon + Elastic/Splunk",
   "Atomic Red Team"
  ],
  "resources": [
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "MITRE ATT&CK - Adversary Emulation Plans",
    "url": "https://attack.mitre.org/resources/adversary-emulation-plans/"
   },
   {
    "name": "MITRE ATT&CK - Groups",
    "url": "https://attack.mitre.org/groups/"
   },
   {
    "name": "VECTR",
    "url": "https://vectr.io/"
   }
  ],
  "doneWhen": "You executed a single named-actor emulation across the full kill chain in an instrumented range, tracked every procedure's outcome in VECTR, and shipped a purple report with an ATT&CK coverage heatmap and prioritized detection recommendations.",
  "pitfall": "Optimizing for 'did it pop' over fidelity and measurement - an emulation that isn't sourced to real CTI and isn't scored against blue telemetry is just a pentest wearing an APT's name."
 },
 "CAP-5B": {
  "overview": "A second intel-driven emulation chosen for maximum tradecraft contrast with CAP-5A, so the run stresses telemetry your defenses have never seen. Success is not 'popped the DC', it is a quantified detection-coverage delta and a purple product the blue team keeps.",
  "steps": [
   "Select an actor whose TTP profile is orthogonal to your CAP-5A actor (different initial access, C2 pattern, credential-access and persistence families) so you exercise net-new ATT&CK techniques, not muscle memory.",
   "Distil 2-3 primary-source CTI reports into a cited technique list; build the Navigator layer and diff it against CAP-5A to isolate the new coverage targets.",
   "Author the emulation plan with faithful-but-safe substitutes (benign payloads, sanctioned test artifacts); lock RoE, deconfliction, and cleanup/kill-switch before execution.",
   "Snapshot pre-run detection coverage in VECTR (per-technique detected / not detected) as your baseline heatmap.",
   "Execute against instrumented defenses, timestamping each technique; treat every gap as a finding and note the exact telemetry source (Sysmon/ETW/EDR field) that should have caught it.",
   "Engineer or tune analytics for the misses, re-emulate to validate true-positive fire, and record MTTD alongside the coverage delta.",
   "Ship exec narrative + technical report + purple debrief; the headline metric is coverage improvement (delta of techniques detected) with the new detections handed over."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "Caldera",
   "Atomic Red Team",
   "VECTR",
   "Sigma",
   "Elastic/Splunk + a real EDR"
  ],
  "resources": [
   {
    "name": "MITRE Adversary Emulation Library (CTID)",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "ATT&CK Navigator",
    "url": "https://mitre-attack.github.io/attack-navigator/"
   },
   {
    "name": "VECTR",
    "url": "https://vectr.io"
   },
   {
    "name": "SigmaHQ",
    "url": "https://github.com/SigmaHQ/sigma"
   }
  ],
  "doneWhen": "A signed-off package exists: baseline vs post-tuning ATT&CK heatmap showing a positive delta, N new or updated detections validated by re-emulation, MTTD recorded, and exec + technical + purple deliverables complete.",
  "pitfall": "Emulating 'vibes' instead of cited intel, or scoring success by objectives reached rather than detections gained, and never re-testing tuned rules so 'improved coverage' stays unproven on paper."
 },
 "P6-06": {
  "overview": "At the professional altitude, VECTR is your system of record for turning an engagement into a measurable, trendable detection-coverage program. The goal is not a one-off heatmap but a repeatable pipeline where every gap becomes a tracked detection-engineering ticket and every re-test shows movement, giving leadership defensible metrics like mean-time-to-detect and coverage delta over time.",
  "steps": [
   "Model the engagement as a VECTR Assessment with campaigns aligned to a threat-informed plan (emulate a specific adversary's technique set, not a random grab-bag)",
   "Define an outcome taxonomy up front and hold to it: Prevented, Detected (alerted), Logged-not-alerted, Not-logged, plus detection time and telemetry source per case",
   "Capture evidence granularly so results are reproducible and auditable: data source, detection logic reference, and analyst-confirmed timestamps",
   "Reconcile VECTR outcomes against your SIEM/EDR detection content so 'missed' reflects a true control gap, not a scoping or telemetry blind spot",
   "Convert each gap into a detection-engineering work item with the ATT&CK ID, required data source, and a proposed analytic; link the ticket back to the VECTR case",
   "Re-run after fixes and use VECTR's comparison/heatmap views to report coverage delta, MTTD trend, and prevented-vs-detected ratio",
   "Roll findings into a threat-informed defense narrative and schedule the next emulation cycle against the weakest tactics"
  ],
  "tools": [
   "VECTR",
   "MITRE ATT&CK Navigator",
   "CALDERA",
   "Atomic Red Team",
   "Detection-as-code / SIEM content repo",
   "Ticketing system (Jira/GitHub Issues)"
  ],
  "resources": [
   {
    "name": "VECTR (SRA) documentation",
    "url": "https://docs.vectr.io/"
   },
   {
    "name": "MITRE Center for Threat-Informed Defense",
    "url": "https://ctid.mitre.org/"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "Adversary Emulation Library (CTID)",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   }
  ],
  "doneWhen": "A closed loop is demonstrated in VECTR: baseline campaign scored, gaps ticketed to detection engineering, fixes deployed, and a re-test campaign showing a measurable coverage/MTTD improvement over the baseline heatmap.",
  "pitfall": "Chasing a green heatmap by counting raw log presence as 'detection' — coverage without a corresponding alert or analytic is a blind spot dressed up as a win, and it inflates metrics while leaving defenders no better off."
 },
 "P6-02": {
  "overview": "A CTID emulation plan is a threat-informed test design, not a script: it encodes intel, an operations flow, and mappings you can retarget to your own lab's coverage questions. Mastering plan selection and adaptation lets you run repeatable, purple-team-style assessments that measurably move detection engineering forward rather than just generating noise.",
  "steps": [
   "Choose a plan whose modeled adversary overlaps your threat model, and justify the selection against your organization's or lab's relevant tech stack.",
   "Read the full plan and rebuild its technique chain in ATT&CK Navigator to see coverage, ordering dependencies, and where sub-techniques diverge.",
   "For each technique, define a benign substitute and a hypothesis: which data source and detection rule should fire, and at what fidelity.",
   "Scope the run explicitly (isolated lab boundaries, no production data, defined rollback) and version your test plan so runs are comparable over time.",
   "Execute in tracked waves, capturing detection outcome, alert latency, and data-source completeness per technique in VECTR.",
   "Convert each miss or low-fidelity hit into a concrete detection-engineering backlog item and re-test to confirm closure.",
   "Adapt the plan for the next cycle: swap substitutes, add sibling sub-techniques, and re-baseline against updated ATT&CK releases."
  ],
  "tools": [
   "CTID Adversary Emulation Library",
   "MITRE ATT&CK Navigator",
   "VECTR",
   "Atomic Red Team",
   "CALDERA",
   "Detection-as-code pipeline (Sigma)"
  ],
  "resources": [
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "MITRE Engenuity CTID",
    "url": "https://mitre-engenuity.org/cybersecurity/center-for-threat-informed-defense/"
   },
   {
    "name": "VECTR",
    "url": "https://vectr.io/"
   },
   {
    "name": "ATT&CK Data Sources",
    "url": "https://attack.mitre.org/datasources/"
   }
  ],
  "doneWhen": "You have executed an adapted CTID plan across tracked waves in VECTR with per-technique detection outcomes, and every miss has a filed detection improvement plus a passing re-test.",
  "pitfall": "Emulating for a coverage score while ignoring detection fidelity and data-source gaps, so 'green' techniques still would not catch the real adversary in production."
 },
 "TR-02": {
  "overview": "At a senior level this practice becomes structured vulnerability research reading: extracting the primitive, validating the researcher's causal claim against source, and characterizing the patch's completeness. The payoff is defensive leverage — variant analysis, detection engineering, and the ability to judge whether a fix is real or merely papers over the symptom.",
  "steps": [
   "Curate a target class (a memory-safety bug, a deserialization flaw, an auth-logic error) and select a CVE whose write-up, source, and patch are all public.",
   "Reconstruct the vulnerable code path from the write-up and confirm each causal claim against the actual source rather than trusting the narrative.",
   "Build a reproducible lab with snapshots and instrumentation (verbose logging, ASAN/sanitizers, or an application debugger) to observe the fault at the analysis level.",
   "Study the patch commit closely: identify the exact invariant it restores and reason about whether nearby code shares the same assumption (variant hunting).",
   "Author a defensive artifact — a detection rule, log signature, or hardening note — derived from the observable behavior, not from any offensive payload.",
   "Write a short root-cause memo: primitive, preconditions, fix mechanism, residual risk, and ATT&CK mapping, suitable for a team knowledge base.",
   "Peer-review your memo against the original researcher's claims and record where your analysis diverged and why."
  ],
  "tools": [
   "gdb/lldb or a language-appropriate debugger with sanitizers (ASAN/UBSAN)",
   "Ghidra or a source-level code browser for tracing paths",
   "git blame/log for patch archaeology",
   "Sigma or YARA for encoding detections",
   "VECTR for tracking the study as a detection-development exercise",
   "MITRE ATT&CK Navigator for technique mapping"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "Center for Threat-Informed Defense",
    "url": "https://ctid.mitre.org/"
   },
   {
    "name": "VECTR",
    "url": "https://vectr.io/"
   },
   {
    "name": "Sigma Detection Rules",
    "url": "https://github.com/SigmaHQ/sigma"
   }
  ],
  "doneWhen": "You produce a peer-reviewable root-cause memo that independently confirms (or corrects) the write-up's causal claim, assesses patch completeness, and ships at least one detection artifact mapped to ATT&CK.",
  "pitfall": "Treating the write-up as ground truth and skipping source/patch verification — researchers simplify or occasionally err, and an unverified mental model produces brittle detections and false variant conclusions."
 },
 "P6-05": {
  "overview": "At this level the goal is measurement rigor, not execution: a sanctioned Caldera emulation plan becomes a repeatable instrument for validating your detection stack against a specific, ATT&CK-mapped adversary. Done well, each run yields per-technique detection outcomes, MTTD numbers, and concrete detection-engineering work that you validate by re-running.",
  "steps": [
   "Define scope and rollback discipline up front: isolated segment, VM snapshots, and a documented cleanup/revert plan before any agent runs.",
   "Select a published plan from the CTID Adversary Emulation Library aligned to a threat you actually care about, and confirm its ATT&CK technique coverage.",
   "Verify pipeline health first: confirm each expected log source is flowing and baselined so a 'miss' means detection, not a dead collector.",
   "Execute in phases, recording operation start/stop times and ability identifiers so you can correlate telemetry precisely instead of eyeballing it.",
   "Score the blue side: classify each technique as alerted / logged-only / missed, and capture mean time to detect and log-source coverage.",
   "Turn gaps into detections (author or tune Sigma/analytics), then re-run the same plan to prove the new detection fires.",
   "Track results across runs in VECTR so coverage trends are visible over time and defensible to stakeholders."
  ],
  "tools": [
   "MITRE Caldera",
   "VECTR",
   "Sigma",
   "Sysmon + Splunk or Elastic Security",
   "CTID Adversary Emulation Library",
   "Jupyter (telemetry correlation and analysis)"
  ],
  "resources": [
   {
    "name": "Adversary Emulation Library (CTID)",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "Caldera Documentation",
    "url": "https://caldera.readthedocs.io/"
   },
   {
    "name": "VECTR",
    "url": "https://vectr.io/"
   },
   {
    "name": "Sigma Detection Rules",
    "url": "https://github.com/SigmaHQ/sigma"
   }
  ],
  "doneWhen": "You produce a purple-team readout with per-technique detection outcomes (detected/logged/missed) and MTTD, plus at least one new or tuned detection whose effectiveness you confirmed with a follow-up run.",
  "pitfall": "Treating Caldera's successful execution as the score; the emulation is only the stimulus, and the real result is what your defenses did (and did not) observe and how fast."
 },
 "TR-03": {
  "overview": "At senior level, infrastructure hygiene and attribution discipline are about operational integrity, emulation fidelity, and clean measurement: separation is designed so findings are defensible, deconfliction is instant, and the blue team receives an honest detection signal. This builds a repeatable methodology that improves both offense realism and defensive value engagement over engagement.",
  "steps": [
   "Design a tiered infrastructure model conceptually (staging / redirector / long-haul) and articulate the specific risk each tier isolates.",
   "Define an attribution matrix per engagement: which operator identifiers and indicators you hold constant versus deliberately vary, and why.",
   "For adversary emulation, justify indicator choices from CTI on the emulated actor and map each to ATT&CK techniques.",
   "Establish a deconfliction protocol: real-time activity logging, out-of-band comms with the trusted agent, and a rapid stand-down path.",
   "Define teardown and evidence-retention discipline: decommissioning, what is preserved for the report, and log chain-of-custody.",
   "Run a purple-team readback and confirm the blue team can reconstruct your timeline from their telemetry; refine controls where signal was lost.",
   "Codify the outcome into a reusable methodology and measure improvement across engagements."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "VECTR",
   "CTID Adversary Emulation Library",
   "MITRE Engage",
   "SIEM/EDR telemetry platform (purple readback)",
   "Threat intel platform (MISP / OpenCTI)"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "Red Team Development and Operations",
    "url": "https://redteam.guide/"
   },
   {
    "name": "MITRE Engage",
    "url": "https://engage.mitre.org/"
   }
  ],
  "doneWhen": "A peer-reviewed methodology doc exists in which every infrastructure and attribution control is justified by a risk it mitigates and mapped to a defender-observable signal, and a purple-team readback confirms the blue team can reconstruct your operation timeline.",
  "pitfall": "Optimizing infrastructure purely for stealth until the engagement produces no usable detection signal or defensible evidence, defeating the purpose of an authorized assessment."
 },
 "TR-06": {
  "overview": "At a professional level this habit becomes a queryable detection knowledge base that ties each technique to a consistent telemetry schema, a testable analytic, and a measured coverage gap. Done well it turns scattered learning into an evidence-backed map of what your sensors can and cannot see, directly improving detection engineering and purple-team planning.",
  "steps": [
   "Standardize every entry against a data model (ATT&CK data components / OSSEM) so events and fields normalize across sources rather than free-text notes.",
   "For each procedure variant, record the exact data component, event, fields, and the log-source configuration (audit policy, Sysmon config) required to see it.",
   "Emulate procedures in an instrumented lab and diff telemetry across variants to separate robust signals from brittle, easily-evaded ones.",
   "Encode each detection hypothesis as a Sigma rule and note confidence, expected false-positive sources, and known blind spots.",
   "Track technique coverage and telemetry gaps as DeTT&CT / Navigator layers so weak spots are visible, not implied.",
   "Run purple-team validation in VECTR and write the detect/alert outcome back into the notebook entry.",
   "Reassess entries when log sources, agent configs, or procedure variants change so the notebook stays trustworthy."
  ],
  "tools": [
   "OSSEM",
   "DeTT&CT",
   "Sigma",
   "MITRE ATT&CK Navigator",
   "VECTR",
   "MITRE Caldera"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK Data Sources",
    "url": "https://attack.mitre.org/datasources/"
   },
   {
    "name": "OSSEM security event metadata",
    "url": "https://github.com/OTRF/OSSEM"
   },
   {
    "name": "DeTT&CT coverage tracking",
    "url": "https://github.com/rabobank-cdc/DeTTECT"
   },
   {
    "name": "MITRE Cyber Analytics Repository (CAR)",
    "url": "https://car.mitre.org"
   }
  ],
  "doneWhen": "Every logged technique carries a normalized data component, event/field schema, a Sigma-encoded hypothesis with false-positive notes, and a recorded purple-team validation outcome, with coverage gaps rendered on a Navigator layer.",
  "pitfall": "Treating the notebook as write-only documentation and never confirming the telemetry actually fires, assuming an event exists without verifying the audit policy or sensor config that emits it."
 },
 "CAP-3": {
  "overview": "At capstone level, purple team is a measurement discipline: you emulate a scoped objective against a production-grade EDR and deliver an evidence-backed package that raises the organization's detection coverage and mean-time-to-detect. The output is not a war story but a repeatable test harness plus engineered detections, each tied to a data source, a technique, and a validation result.",
  "steps": [
   "Scope a threat-informed objective from a real adversary profile and encode the full plan as an ATT&CK Navigator layer with success criteria per technique.",
   "Build a controlled, resettable range with the target EDR, tamper protection realistic, and full telemetry (EDR API, Sysmon, Windows/Sysmon event forwarding) shipping to a searchable store.",
   "Execute in disciplined phases in the lab, capturing detonation timestamps, host context, and an expected-telemetry hypothesis for each action to enable clean detection-vs-noise analysis.",
   "Reconcile alerts against telemetry to score each technique as blocked / alerted / telemetry-only / no-signal, and record analytic latency and confidence, not just a binary.",
   "Engineer detections for every gap as Sigma or vendor analytics with tuning notes, expected false-positive sources, and the minimum data source required — validate each by re-running the emulation.",
   "Track results over time in VECTR so coverage, MTTD, and detection efficacy trend across engagement rounds.",
   "Deliver a dual report: red-team objective narrative with ATT&CK mapping, and a blue-team detection backlog with owners, data-source gaps, and a re-test plan."
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "CALDERA",
   "Atomic Red Team",
   "VECTR",
   "Sigma / Sigma converters",
   "Elastic Security or Microsoft Defender/Sentinel"
  ],
  "resources": [
   {
    "name": "MITRE Engenuity CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "MITRE CALDERA",
    "url": "https://caldera.mitre.org/"
   },
   {
    "name": "SigmaHQ",
    "url": "https://github.com/SigmaHQ/sigma"
   },
   {
    "name": "VECTR (SRA)",
    "url": "https://docs.vectr.io/"
   }
  ],
  "doneWhen": "You ship a versioned purple-team package where 100% of objective techniques carry a coverage verdict with latency, every gap has a validated detection re-tested against the emulation, and results are trended in VECTR across at least two rounds.",
  "pitfall": "Optimizing for a green coverage heatmap. A detection that fires but is drowned in false positives, or that only matches your one atomic invocation, is a metric, not a defense — validate robustness and analyst usability, not just that it lit up once."
 },
 "CAP-2": {
  "overview": "A full-scope capstone proves you can plan, execute, and communicate an authorized external-to-internal engagement with custom tooling and purpose-built C2 while maintaining OPSEC and evidentiary rigor. The deliverable is not a shell count but a defensible narrative that lets a blue team measure their own detection coverage and close the gaps you surfaced.",
  "steps": [
   "Author a formal ROE and threat-actor emulation plan: pick a real adversary profile, enumerate the ATT&CK techniques you will exercise, and define abort criteria",
   "Architect segmented, disposable C2 infrastructure in your lab with redirectors, per-engagement isolation, and teardown procedures documented in advance",
   "Define OPSEC rules up front: artifact naming, credential handling, cleanup obligations, and what deconfliction data you hand the blue team in real time",
   "Instrument the environment first so every emulated technique is measured against known telemetry, then run the chain external-to-internal against your own targets",
   "Maintain a rigorous operator log and evidence chain suitable for a purple-team replay, capturing detections raised, missed, and delayed",
   "Convert findings into a detection-engineering backlog: per technique, list the data source, a candidate analytic, and the residual risk if unaddressed",
   "Produce a layered report (executive risk narrative, attack-path walkthrough, and remediation/detection roadmap) and run a debrief that translates it into defender action items"
  ],
  "tools": [
   "MITRE ATT&CK Navigator",
   "CTID Adversary Emulation Library",
   "VECTR",
   "Atomic Red Team (validation)",
   "Sysmon / Elastic or Splunk (telemetry)",
   "Ghostwriter (reporting & logging)"
  ],
  "resources": [
   {
    "name": "CTID Adversary Emulation Library",
    "url": "https://github.com/center-for-threat-informed-defense/adversary_emulation_library"
   },
   {
    "name": "MITRE ATT&CK",
    "url": "https://attack.mitre.org/"
   },
   {
    "name": "VECTR by SRA",
    "url": "https://vectr.io/"
   },
   {
    "name": "SpecterOps Ghostwriter",
    "url": "https://github.com/GhostManager/Ghostwriter"
   }
  ],
  "doneWhen": "You deliver a full engagement package (ROE, emulation plan, operator log, evidence, and layered report) plus a purple-team coverage matrix showing which emulated techniques were detected, missed, or delayed and the analytic proposed for each gap.",
  "pitfall": "Optimizing for stealth and technique breadth while under-investing in measurement and reporting, so the exercise produces impressive access but no reproducible detection improvements for the defenders you serve."
 },
 "CAP-4": {
  "overview": "The cloud-to-on-prem pivot is one of the highest-impact moves in modern hybrid attacks, and reasoning about it rigorously is what separates a checklist tester from an operator. This capstone integrates planning, attack-path modeling, ATT&CK mapping, and blue-team-ready reporting into one objective-driven lab exercise that directly strengthens detection and control coverage.",
  "steps": [
   "Frame the engagement around a concrete objective and an assumed-breach cloud starting point; write the hypothesis-driven plan and explicit success criteria before execution.",
   "Stand up a reproducible hybrid lab (cloud tenant + on-prem AD + a sync or federation bridge) with build notes so the exercise is repeatable and shareable.",
   "Enumerate and graph both the cloud and on-prem terrain, then model trust and identity relationships as an attack graph with multiple candidate branches.",
   "Prioritize paths by realism and objective-relevance, validate each hop safely in the lab, and note precisely where your assumptions break.",
   "Map every hop to ATT&CK, capture the exact telemetry it generates, and identify detection and control gaps at each stage.",
   "Deliver a peer-reviewable capstone report: objective narrative, path graph with alternative branches, evidence, and prioritized remediation the blue team can action.",
   "Close with a purple-team debrief that tracks detection coverage and outcomes so the findings feed detection engineering."
  ],
  "tools": [
   "BloodHound / AzureHound",
   "ROADtools (roadrecon)",
   "MITRE ATT&CK Navigator",
   "VECTR",
   "PurpleKnight",
   "Microsoft Defender for Identity (detection validation)"
  ],
  "resources": [
   {
    "name": "MITRE ATT&CK Cloud Matrix",
    "url": "https://attack.mitre.org/matrices/enterprise/cloud/"
   },
   {
    "name": "Center for Threat-Informed Defense (CTID)",
    "url": "https://mitre-engenuity.org/cybersecurity/center-for-threat-informed-defense/"
   },
   {
    "name": "VECTR (purple-team tracking)",
    "url": "https://vectr.io/"
   },
   {
    "name": "Microsoft Entra hybrid identity documentation",
    "url": "https://learn.microsoft.com/en-us/entra/identity/hybrid/"
   }
  ],
  "doneWhen": "You deliver a peer-reviewable capstone report — objective-based attack narrative, ATT&CK-mapped path graph with alternative branches, per-hop telemetry and control-gap analysis, and prioritized blue-team remediation — that a reviewer can reproduce from your lab build notes.",
  "pitfall": "Falling in love with one 'cool' path and ignoring assumed-breach realism and alternative branches, or ending at the exploit narrative without tying each hop to detection value and remediation."
 }
})
