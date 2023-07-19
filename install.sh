wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip > /dev/null 2>&1
unzip ngrok-stable-linux-amd64.zip > /dev/null 2>&1
read -p "Paste authtoken here (Copy and Ctrl+V to paste then press Enter): " CRP
./ngrok authtoken $CRP 
nohup ./ngrok tcp 5900 &>/dev/null &
echo Please wait for installing...
sudo apt update -y > /dev/null 2>&1
clear
echo "Installing QEMU (2-3m)..."
sudo apt install qemu-system-x86 qemu qemu-system curl -y > /dev/null 2>&1
clear
echo Downloading Windows Disk...
curl -L -o win7.zip https://download.microsoft.com/download/e/2/6/e26379c8-f6d8-425c-8383-c28d4c8429d5/WinDev2306Eval.VirtualBox.zip
unzip win7.zip
mv 'IE11 - Win7.ova' win7.ova
rm win7.zip
tar -xvf win7.ova
mv 'IE11 - Win7-disk001.vmdk' win7disk1.vmdk
rm win7.ova
mv 'IE11 - Win7.ovf' win7.ovf
rm win7.ovf
clear
echo "Windows 7 x64 Lite On Google Colab"
echo Your VNC IP Address:
curl --silent --show-error http://127.0.0.1:4040/api/tunnels | sed -nE 's/.*public_url":"tcp:..([^"]*).*/\1/p'
echo "Note: Use Right-Click Or Ctrl+C To Copy"
echo "Please Keep Colab Tab Open, Maximum Time 12h"
echo Script by Storagedrive404outlook
sudo qemu-system-x86_64 -vnc :0 -hda win7disk1.vmdk  -smp cores=2  -m 8192M -machine usb=on -device usb-tablet > /dev/null 2>&1
