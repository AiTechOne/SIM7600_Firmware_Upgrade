# SIM7600 Firmware Upgrade Tool (Python3 Code)
Simple python3 code to update SIM7600SA-H firmware (may work with others but you must check firmware version first!) on Windows or Linux. Some messages are in spanish, but it's very simple to use.

# Testing using
- W10-Ubuntu20-Debian9
- Fastboot 29.0.6-6198805 (should work with others)
- Python3.7.4+
- pyserial 3.4 package for python (should work with others)

# Usage
- If Linux: copy 99-simcom.rules to /etc/udev/rule.d/
- If Windows: add fastboot to Path

1. Connect SIM7600 to your PC
2. Open CMD directly repo dir
3. Execute ```python upgrade_sim7600.py```
4. Follow instructions
