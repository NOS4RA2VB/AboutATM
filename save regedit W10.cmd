cd /
mkdir Reestr
cd Reestr
REG EXPORT "HKLM\SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2" BS2.reg
REG EXPORT "HKLM\SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\LYNXPAR\CASH_DISPENSER" DISP.reg
REG EXPORT "HKLM\SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\CCOPEN\COMMUNICATION\TCPIP" TCIP.reg
REG EXPORT "HKLM\SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\LYNXCAIN\CCCASHINTRANSACTIONFW" CCCASHIN.reg
REG EXPORT "HKLM\SOFTWARE\WOW6432Node\Wincor Nixdorf\PROAGENT\CURRENTVERSION\SSTP" SSTP.reg
mkdir C:\Reestr\Config
XCOPY "C:\Program Files\OpenVPN\Config" "C:\Reestr\Config\" /e
mkdir C:\Reestr\JOURNAL
mkdir C:\Reestr\CUSTOMER
XCOPY "C:\CUSTOMER" "C:\Reestr\CUSTOMER\" /e
XCOPY "C:\JOURNAL" "C:\Reestr\JOURNAL\" /e
COPY "C:\ProTopas\BITMAPS\ink.txt" "C:\Reestr"

