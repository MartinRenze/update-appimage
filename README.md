# update-appimage
Script to update AppImages automatically

## Add hook to apt
* Create file `/etc/apt/apt.conf.d/100update` with content 

```
APT::Update::Pre-Invoke  {"python3 /media/ubuntu/igel/Projekte/scripts/update-appimage/update-appimage.py";};
```
