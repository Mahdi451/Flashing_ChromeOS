# Flashing ChromeOS

This script will allow you to flash chromeos test images on multiple devices simultaneously.

## Running

Place the image you would like to flash within the same directory as the script.

```
README.md  chromiumos_test_image.bin  remote_os_install.py  ips.txt
```

Insert the device IPs into *__ips.txt__* and you are ready to run the script!

```
$ python remote_os_install.py
```




