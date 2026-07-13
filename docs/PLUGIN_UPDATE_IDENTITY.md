# Stable WordPress Plugin Identity

WordPress identifies an installed plugin by the relative path to its main bootstrap file. Sustainable Catalyst Lab must therefore remain:

```text
sustainable-catalyst-lab/sustainable-catalyst-lab.php
```

## Correct update archive

Upload:

```text
sustainable-catalyst-lab.zip
```

Do not upload these through the WordPress plugin installer:

- `sustainable-catalyst-lab-v0.11.0-repo.zip`
- `sustainable-catalyst-lab-v0.11.0-release-bundle.zip`
- A manually renamed directory containing a version suffix

Those packages are for GitHub or offline release storage, not direct WordPress installation.

## Duplicate detector

The settings page scans installed plugin headers for another plugin whose name is `Sustainable Catalyst Lab` or whose text domain is `sustainable-catalyst-lab`. It displays the installed plugin paths and can deactivate duplicate instances.

The cleanup action intentionally does not delete plugin directories. After confirming that the stable instance is active and the Lab page works, inactive versioned folders can be deleted from the WordPress Plugins screen.
