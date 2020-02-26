# Flashing ChromeOS

This script allows you to flash ChromeOS to multiple devices at the same time.

## Running

Place the image you would like to flash within the same directory as the script.

```
chromiumos_test_image.bin  remote_os_install.py  IPs.txt
```

Place the device ip addresses into *__IPs.txt__* and you are ready to run the script!

```
$ python remote_os_install.py --image name_of_test_image.bin
```


