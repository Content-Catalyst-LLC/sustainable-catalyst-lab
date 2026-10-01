# Build Lab v0.160.0

Apply the v0.160.0 builder to the current v0.159.0 Lab source repository. The builder is idempotent, preserves the v0.159 SQLite connection-lifecycle repair, validates v0.157–v0.160 regression contracts, regenerates integrity manifests, and packages repository, WordPress, backend, and release artifacts.

```bash
cd ~/Downloads
rm -rf lab-v0.160.0-builder sc-lab-v0.160.0-artifacts
unzip -q lab-v0.160.0-computational-research-operating-system-ii-builder-bundle.zip -d lab-v0.160.0-builder
cd lab-v0.160.0-builder
chmod +x APPLY_AND_PACKAGE_LAB_V01600.sh
./APPLY_AND_PACKAGE_LAB_V01600.sh "$HOME/Downloads/sustainable-catalyst-lab" "$HOME/Downloads/sc-lab-v0.160.0-artifacts"
```
