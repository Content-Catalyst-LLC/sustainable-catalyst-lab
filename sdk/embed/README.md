# Sustainable Catalyst Research Embed v0.38.2

```html
<div id="research-record"></div>
<script src="sc-lab-research-embed.js"></script>
<script>
SustainableCatalystResearchEmbed.mount('#research-record', {
  baseUrl: 'https://lab.example.org',
  token: 'signed-embed-token'
});
</script>
```

The loader retrieves a signed, expiring manifest and renders reference metadata only.
