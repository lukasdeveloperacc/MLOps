# Install
```bash
sudo bash install.bash
```

```bash
kubectl patch storageclass local-path \
  -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
- If you need to make the storageclass default, run the above command

# Uninstall
```bash
sudo bash uninstall.bash
```
