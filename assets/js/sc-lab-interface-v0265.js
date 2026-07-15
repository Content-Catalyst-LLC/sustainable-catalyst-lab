(function () {
  'use strict';

  var VERSION = '0.26.5';
  var config = window.SCLabInterfaceConfigV0265 || {};
  var root = null;
  var liveRegion = null;
  var observer = null;
  var scheduled = false;
  var enhancedAt = null;
  var lastAudit = null;
  var media = window.matchMedia ? window.matchMedia('(max-width: 980px)') : { matches: false, addListener: function () {} };
  var reducedMotion = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  function q(selector, scope) { return (scope || document).querySelector(selector); }
  function qa(selector, scope) { return Array.prototype.slice.call((scope || document).querySelectorAll(selector)); }
  function text(value) { return String(value == null ? '' : value).replace(/\s+/g, ' ').trim(); }
  function uid(prefix) { return prefix + '-' + Math.random().toString(36).slice(2, 10); }
  function escapeSelector(value) {
    if (window.CSS && typeof window.CSS.escape === 'function') { return window.CSS.escape(String(value)); }
    return String(value).replace(/[^a-zA-Z0-9_-]/g, function (char) { return '\\' + char; });
  }
  function attrEnding(element, suffix) {
    if (!element || !element.attributes) { return null; }
    for (var i = 0; i < element.attributes.length; i += 1) {
      var name = element.attributes[i].name;
      if (name.indexOf('data-') === 0 && name.slice(-suffix.length) === suffix) { return name; }
    }
    return null;
  }
  function accessibleName(element) {
    if (!element) { return ''; }
    var labelledby = element.getAttribute('aria-labelledby');
    if (labelledby) {
      return text(labelledby.split(/\s+/).map(function (id) { var node = document.getElementById(id); return node ? node.textContent : ''; }).join(' '));
    }
    return text(element.getAttribute('aria-label') || element.getAttribute('alt') || element.getAttribute('title') || element.textContent || element.value || '');
  }
  function closestHeading(element) {
    var scope = element.closest('.sc-lab-tool, .sc-lab-panel, section, article, figure') || root;
    var heading = scope && q('h1,h2,h3,h4,h5,h6', scope);
    return heading ? text(heading.textContent) : 'Scientific data';
  }
  function announce(message, assertive) {
    if (!liveRegion || !message) { return; }
    liveRegion.setAttribute('aria-live', assertive ? 'assertive' : 'polite');
    liveRegion.textContent = '';
    window.setTimeout(function () { liveRegion.textContent = text(message); }, 20);
  }

  function installLandmarks() {
    var main = q('.sc-lab-main', root);
    if (main) {
      if (!main.id) { main.id = 'sc-lab-main-v0265'; }
      main.setAttribute('tabindex', '-1');
      main.setAttribute('aria-label', 'Active laboratory workspace');
    }
    if (!q('.sc-lab-skip-link-v0265', root)) {
      var skip = document.createElement('a');
      skip.className = 'sc-lab-skip-link-v0265';
      skip.href = '#sc-lab-main-v0265';
      skip.textContent = 'Skip to active laboratory';
      root.insertBefore(skip, root.firstChild);
    }
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.className = 'screen-reader-text sc-lab-live-region-v0265';
      liveRegion.setAttribute('role', 'status');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      root.appendChild(liveRegion);
    }
    root.setAttribute('data-sc-lab-interface-version', VERSION);
    root.setAttribute('data-sc-lab-reduced-motion', reducedMotion.matches ? 'true' : 'false');
  }

  function installMobileNavigation() {
    var toggle = q('[data-lab-nav-toggle]', root);
    var nav = q('[data-lab-nav]', root);
    if (!toggle || !nav) { return; }
    if (!nav.id) { nav.id = 'sc-lab-module-nav'; }
    toggle.setAttribute('aria-controls', nav.id);
    var scrim = q('.sc-lab-nav-scrim-v0265', root);
    if (!scrim) {
      scrim = document.createElement('button');
      scrim.type = 'button';
      scrim.className = 'sc-lab-nav-scrim-v0265';
      scrim.setAttribute('aria-label', 'Close laboratory navigation');
      scrim.hidden = true;
      nav.parentNode.insertBefore(scrim, nav.nextSibling);
    }

    function sync() {
      var mobile = !!media.matches;
      var open = nav.classList.contains('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (mobile) {
        nav.setAttribute('aria-hidden', open ? 'false' : 'true');
        scrim.hidden = !open;
        document.documentElement.classList.toggle('sc-lab-nav-open-v0265', open);
        if ('inert' in nav) { nav.inert = !open; }
      } else {
        nav.removeAttribute('aria-hidden');
        scrim.hidden = true;
        document.documentElement.classList.remove('sc-lab-nav-open-v0265');
        if ('inert' in nav) { nav.inert = false; }
      }
    }
    function close(restoreFocus) {
      if (!nav.classList.contains('is-open')) { sync(); return; }
      nav.classList.remove('is-open');
      sync();
      announce(config.navigationClosed || 'Laboratory navigation closed.');
      if (restoreFocus) { toggle.focus(); }
    }
    if (!toggle.dataset.interfaceV0265) {
      toggle.dataset.interfaceV0265 = 'true';
      toggle.addEventListener('click', function () {
        var wasOpen = nav.classList.contains('is-open');
        window.setTimeout(function () {
          if (nav.classList.contains('is-open') === wasOpen) { nav.classList.toggle('is-open', !wasOpen); }
          sync();
          if (nav.classList.contains('is-open')) {
            announce(config.navigationOpened || 'Laboratory navigation opened.');
            var first = q('button:not([disabled]),a[href]', nav);
            if (first) { first.focus(); }
          }
        }, 0);
      }, true);
      scrim.addEventListener('click', function () { close(true); });
      nav.addEventListener('click', function (event) {
        if (media.matches && event.target.closest('[data-lab-module-button],a[href]')) { window.setTimeout(function () { close(false); }, 0); }
      });
      document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && media.matches && nav.classList.contains('is-open')) { event.preventDefault(); close(true); }
      });
      if (media.addEventListener) { media.addEventListener('change', sync); } else if (media.addListener) { media.addListener(sync); }
    }
    sync();
  }

  function enhanceButtons(scope) {
    qa('button', scope).forEach(function (button) {
      if (!button.getAttribute('type')) { button.type = 'button'; }
      if (!accessibleName(button)) {
        var fallback = button.getAttribute('data-label') || button.getAttribute('title') || 'Laboratory action';
        button.setAttribute('aria-label', fallback);
      }
      if (button.disabled) { button.setAttribute('aria-disabled', 'true'); } else { button.removeAttribute('aria-disabled'); }
    });
  }

  function findLabel(field) {
    if (!field) { return null; }
    if (field.id) {
      var explicit = q('label[for="' + escapeSelector(field.id) + '"]', root);
      if (explicit) { return explicit; }
    }
    return field.closest('label');
  }

  function enhanceForms(scope) {
    qa('input:not([type="hidden"]),select,textarea', scope).forEach(function (field) {
      var label = findLabel(field);
      if (!field.id && label && label.getAttribute('for')) { field.id = label.getAttribute('for'); }
      if (!accessibleName(field)) {
        var name = label ? text(label.childNodes[0] && label.childNodes[0].textContent) : '';
        name = name || field.getAttribute('placeholder') || field.getAttribute('name') || 'Laboratory input';
        field.setAttribute('aria-label', name);
      }
      if (field.required) { field.setAttribute('aria-required', 'true'); }
      if (field.disabled) { field.setAttribute('aria-disabled', 'true'); } else { field.removeAttribute('aria-disabled'); }
    });
  }

  function enhanceTabs(scope) {
    qa('.sc-lab-tabs', scope).forEach(function (tablist) {
      tablist.setAttribute('role', 'tablist');
      if (!tablist.getAttribute('aria-label')) { tablist.setAttribute('aria-label', closestHeading(tablist) + ' sections'); }
      var tabs = qa('button', tablist);
      tabs.forEach(function (tab, index) {
        var dataName = attrEnding(tab, '-tab');
        var value = dataName ? tab.getAttribute(dataName) : null;
        var active = tab.classList.contains('is-active') || tab.getAttribute('aria-selected') === 'true' || index === 0 && !tabs.some(function (item) { return item.classList.contains('is-active'); });
        if (!tab.id) { tab.id = uid('sc-lab-tab'); }
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
        tab.setAttribute('tabindex', active ? '0' : '-1');
        if (dataName && value) {
          var paneName = dataName.slice(0, -4) + '-pane';
          var pane = q('[' + paneName + '="' + escapeSelector(value) + '"]', tablist.parentElement || scope);
          if (pane) {
            if (!pane.id) { pane.id = uid('sc-lab-panel'); }
            tab.setAttribute('aria-controls', pane.id);
            pane.setAttribute('role', 'tabpanel');
            pane.setAttribute('aria-labelledby', tab.id);
            pane.setAttribute('tabindex', '0');
          }
        }
      });
      if (!tablist.dataset.keyboardV0265) {
        tablist.dataset.keyboardV0265 = 'true';
        tablist.addEventListener('keydown', function (event) {
          var current = event.target.closest('[role="tab"]');
          if (!current) { return; }
          var all = qa('[role="tab"]', tablist);
          var index = all.indexOf(current);
          var next = null;
          if (event.key === 'ArrowRight' || event.key === 'ArrowDown') { next = all[(index + 1) % all.length]; }
          if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') { next = all[(index - 1 + all.length) % all.length]; }
          if (event.key === 'Home') { next = all[0]; }
          if (event.key === 'End') { next = all[all.length - 1]; }
          if (next) { event.preventDefault(); next.focus(); next.click(); window.setTimeout(function () { enhanceTabs(tablist); }, 0); }
        });
        tablist.addEventListener('click', function () { window.setTimeout(function () { enhanceTabs(tablist); }, 0); });
      }
    });
  }

  function enhanceTables(scope) {
    qa('table', scope).forEach(function (table) {
      qa('thead th', table).forEach(function (th) { if (!th.getAttribute('scope')) { th.setAttribute('scope', 'col'); } });
      qa('tbody tr', table).forEach(function (row) {
        var first = row.children[0];
        if (first && first.tagName === 'TH' && !first.getAttribute('scope')) { first.setAttribute('scope', 'row'); }
      });
      if (!table.parentElement.classList.contains('sc-lab-table-scroll-v0265')) {
        var wrap = document.createElement('div');
        wrap.className = 'sc-lab-table-scroll-v0265';
        wrap.setAttribute('role', 'region');
        wrap.setAttribute('tabindex', '0');
        wrap.setAttribute('aria-label', closestHeading(table) + ' table. Scroll horizontally when needed.');
        table.parentNode.insertBefore(wrap, table);
        wrap.appendChild(table);
      }
    });
  }

  function enhanceVisuals(scope) {
    qa('img', scope).forEach(function (image) {
      if (!image.hasAttribute('alt')) { image.alt = closestHeading(image) + ' image'; }
      if (!image.getAttribute('loading')) { image.loading = 'lazy'; }
    });
    qa('svg,canvas', scope).forEach(function (visual) {
      if (!visual.getAttribute('role')) { visual.setAttribute('role', 'img'); }
      if (!accessibleName(visual)) { visual.setAttribute('aria-label', closestHeading(visual) + ' visualization'); }
      if (visual.tagName.toLowerCase() === 'canvas' && !visual.hasAttribute('tabindex')) { visual.setAttribute('tabindex', '0'); }
      if (visual.tagName.toLowerCase() === 'svg') { visual.setAttribute('focusable', 'false'); }
    });
  }

  function enhanceDynamicRegions(scope) {
    var selectors = [
      '[data-feed-status]','[data-space-summary]','[data-marine-summary]','[data-climate-loading]',
      '[data-dataset-header]','[data-overview-signals]','[data-functional-summary]',
      '[class*="status"]','[class*="summary"]','[class*="validation"]'
    ];
    qa(selectors.join(','), scope).forEach(function (region) {
      if (!region.getAttribute('role')) { region.setAttribute('role', /error|invalid|failed/i.test(region.className + ' ' + region.textContent) ? 'alert' : 'status'); }
      if (!region.getAttribute('aria-live')) { region.setAttribute('aria-live', region.getAttribute('role') === 'alert' ? 'assertive' : 'polite'); }
      region.setAttribute('aria-atomic', 'true');
    });
    qa('pre,output,[data-output],[data-result],[data-results]', scope).forEach(function (output) {
      if (!output.hasAttribute('tabindex')) { output.setAttribute('tabindex', '0'); }
      if (!output.getAttribute('aria-label')) { output.setAttribute('aria-label', closestHeading(output) + ' result'); }
    });
  }

  function enhanceDisclosures(scope) {
    qa('details > summary', scope).forEach(function (summary) {
      if (!summary.getAttribute('aria-label')) { summary.setAttribute('aria-label', text(summary.textContent) || 'Show details'); }
    });
    qa('[role="dialog"],dialog,.sc-lab-record-dialog', scope).forEach(function (dialog) {
      dialog.setAttribute('role', 'dialog');
      dialog.setAttribute('aria-modal', 'true');
      if (!dialog.getAttribute('aria-label') && !dialog.getAttribute('aria-labelledby')) { dialog.setAttribute('aria-label', closestHeading(dialog)); }
    });
  }

  function enhance(scope) {
    if (!root) { return; }
    var target = scope && scope.nodeType === 1 ? scope : root;
    installLandmarks();
    installMobileNavigation();
    enhanceButtons(target);
    enhanceForms(target);
    enhanceTabs(target);
    enhanceTables(target);
    enhanceVisuals(target);
    enhanceDynamicRegions(target);
    enhanceDisclosures(target);
    enhancedAt = new Date().toISOString();
    document.dispatchEvent(new CustomEvent('sc-lab:interface-enhanced', { detail: { version: VERSION, module: activeModule() } }));
  }

  function scheduleEnhance() {
    if (scheduled) { return; }
    scheduled = true;
    window.requestAnimationFrame(function () { scheduled = false; enhance(root); });
  }

  function activeModule() {
    var panel = q('[data-lab-module]:not([hidden])', root) || q('[data-sc-lab-active-module]', document);
    return panel ? panel.getAttribute('data-lab-module') || panel.getAttribute('data-sc-lab-active-module') : root && root.getAttribute('data-initial-module');
  }

  function rectIssue(element, minimum) {
    var rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && (rect.width < minimum || rect.height < minimum);
  }

  function audit() {
    var issues = [];
    var add = function (severity, check, details, selector) { issues.push({ severity: severity, check: check, details: details, selector: selector || null }); };
    if (!root) { add('error', 'root', 'The Lab application root is missing.', '.sc-lab-app'); }
    var docWidth = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);
    if (docWidth > window.innerWidth + 4) { add('error', 'horizontal-overflow', 'Document width ' + docWidth + 'px exceeds viewport width ' + window.innerWidth + 'px.', 'html'); }
    var panels = qa('[data-lab-module]:not([hidden])', root);
    if (panels.length !== 1) { add('error', 'active-panel-count', 'Expected exactly one active laboratory panel; found ' + panels.length + '.', '[data-lab-module]:not([hidden])'); }
    qa('button,a[href],input:not([type="hidden"]),select,textarea,summary,[tabindex="0"]', root).forEach(function (control) {
      if (control.closest('.screen-reader-text') || control.disabled || control.getAttribute('aria-hidden') === 'true') { return; }
      if (!accessibleName(control)) { add('error', 'accessible-name', 'Interactive control has no accessible name.', control.tagName.toLowerCase()); }
      if (rectIssue(control, 40)) { add('warning', 'touch-target', 'Interactive target is smaller than 40 × 40 CSS pixels.', accessibleName(control).slice(0, 80)); }
    });
    qa('input:not([type="hidden"]),select,textarea', root).forEach(function (field) {
      if (!findLabel(field) && !field.getAttribute('aria-label') && !field.getAttribute('aria-labelledby')) { add('error', 'form-label', 'Form field is not associated with a label.', field.outerHTML.slice(0, 160)); }
    });
    qa('.sc-lab-tabs', root).forEach(function (tabs) {
      if (tabs.getAttribute('role') !== 'tablist') { add('error', 'tablist-role', 'Tab group is missing role="tablist".', closestHeading(tabs)); }
      qa('button', tabs).forEach(function (tab) { if (tab.getAttribute('role') !== 'tab' || !tab.hasAttribute('aria-selected')) { add('error', 'tab-semantics', 'Tab is missing role or selected state.', accessibleName(tab)); } });
    });
    qa('table', root).forEach(function (table) { if (!table.parentElement.classList.contains('sc-lab-table-scroll-v0265')) { add('warning', 'responsive-table', 'Table does not have the accessible horizontal-scroll wrapper.', closestHeading(table)); } });
    qa('img', root).forEach(function (img) { if (!img.hasAttribute('alt')) { add('error', 'image-alt', 'Image is missing alt text.', img.src || 'image'); } });
    qa('svg,canvas', root).forEach(function (visual) { if (!accessibleName(visual)) { add('warning', 'visualization-label', 'Visualization has no accessible name.', visual.tagName.toLowerCase()); } });
    var ids = {};
    qa('[id]', root).forEach(function (element) { if (ids[element.id]) { add('error', 'duplicate-id', 'Duplicate ID: ' + element.id, '#' + element.id); } ids[element.id] = true; });
    var summary = {
      errors: issues.filter(function (item) { return item.severity === 'error'; }).length,
      warnings: issues.filter(function (item) { return item.severity === 'warning'; }).length,
      passes: 12 - Math.min(12, new Set(issues.map(function (item) { return item.check; })).size),
      status: issues.some(function (item) { return item.severity === 'error'; }) ? 'needs_attention' : issues.length ? 'usable_with_warnings' : 'verified'
    };
    lastAudit = {
      schema: 'sc-lab-interface-health/1.0', version: VERSION, release: config.release || VERSION,
      auditedAt: new Date().toISOString(), module: activeModule(), viewport: { width: window.innerWidth, height: window.innerHeight, devicePixelRatio: window.devicePixelRatio || 1 },
      preferences: { reducedMotion: !!reducedMotion.matches, forcedColors: window.matchMedia && window.matchMedia('(forced-colors: active)').matches },
      summary: summary, issues: issues
    };
    document.dispatchEvent(new CustomEvent('sc-lab:interface-audit', { detail: lastAudit }));
    return lastAudit;
  }

  function setBusy(element, busy, message) {
    if (!element) { return; }
    element.setAttribute('aria-busy', busy ? 'true' : 'false');
    element.classList.toggle('is-busy-v0265', !!busy);
    if (message) { announce(message); }
  }

  function init() {
    root = q('.sc-lab-app');
    if (!root || window.__SCLabInterfaceV0265Booted) { return; }
    window.__SCLabInterfaceV0265Booted = true;
    enhance(root);
    observer = new MutationObserver(scheduleEnhance);
    observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['hidden','class'] });
    document.addEventListener('sc-lab:module-mounted', scheduleEnhance);
    document.addEventListener('sc-lab:panel-loaded', scheduleEnhance);
    document.addEventListener('sc-lab:announce', function (event) { announce(event.detail && event.detail.message, event.detail && event.detail.assertive); });
    document.addEventListener('sc-lab:busy', function (event) { if (event.detail) { setBusy(event.detail.element, event.detail.busy, event.detail.message); } });
    if (config.autoAudit) { window.setTimeout(audit, 900); }
  }

  window.SCLabInterfaceV0265 = {
    version: VERSION,
    status: function () { return { version: VERSION, release: config.release || VERSION, ready: !!root, module: activeModule(), enhancedAt: enhancedAt, reducedMotion: !!reducedMotion.matches, lastAudit: lastAudit }; },
    enhance: enhance,
    audit: audit,
    announce: announce,
    setBusy: setBusy,
    destroy: function () { if (observer) { observer.disconnect(); observer = null; } window.__SCLabInterfaceV0265Booted = false; }
  };

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init, { once: true }); } else { init(); }
}());
