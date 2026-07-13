(() => {
  'use strict';

  const Lab = window.SCLab = window.SCLab || {};
  const VERSION = '0.20.0-civil-router.1';
  const PANEL_SELECTOR = [
    '[data-lab-module="civil-infrastructure"]',
    '[data-module-panel="civil-infrastructure"]',
  ].join(',');

  const TRIGGER_SELECTOR = [
    '[data-lab-target="civil-infrastructure"]',
    '[data-module-target="civil-infrastructure"]',
    '[data-module="civil-infrastructure"]',
    '[data-target="civil-infrastructure"]',
    '[href="#civil-infrastructure"]',
    '[href*="civil-infrastructure"]',
  ].join(',');

  function panel() {
    return document.querySelector(PANEL_SELECTOR);
  }

  function candidateTrigger(target) {
    if (!target || !target.closest) {
      return null;
    }

    const explicit = target.closest(TRIGGER_SELECTOR);

    if (explicit) {
      return explicit;
    }

    const button = target.closest(
      'button, a, [role="button"], [tabindex]'
    );

    if (!button) {
      return null;
    }

    const label = String(
      button.textContent || button.getAttribute('aria-label') || ''
    )
      .trim()
      .toLowerCase();

    return (
      label.includes('civil')
      && label.includes('infrastructure')
    )
      ? button
      : null;
  }

  function siblingPanels(targetPanel) {
    const parent = targetPanel.parentElement;

    if (!parent) {
      return [];
    }

    return Array.from(parent.children).filter(
      (element) => (
        element !== targetPanel
        && element.matches
        && (
          element.matches('[data-lab-module]')
          || element.matches('[data-module-panel]')
          || element.classList.contains('sc-lab-panel')
        )
      )
    );
  }

  function allTriggers() {
    const explicit = Array.from(
      document.querySelectorAll(TRIGGER_SELECTOR)
    );

    const textMatches = Array.from(
      document.querySelectorAll(
        'button, a, [role="button"], [tabindex]'
      )
    ).filter((element) => {
      const label = String(
        element.textContent
        || element.getAttribute('aria-label')
        || ''
      )
        .trim()
        .toLowerCase();

      return (
        label.includes('civil')
        && label.includes('infrastructure')
      );
    });

    return Array.from(new Set([
      ...explicit,
      ...textMatches,
    ]));
  }

  function openCivil(trigger = null) {
    const targetPanel = panel();

    if (!targetPanel) {
      return false;
    }

    siblingPanels(targetPanel).forEach((otherPanel) => {
      otherPanel.hidden = true;
      otherPanel.setAttribute('aria-hidden', 'true');
      otherPanel.classList.remove(
        'is-active',
        'active',
        'sc-lab-panel-active'
      );
    });

    targetPanel.hidden = false;
    targetPanel.removeAttribute('hidden');
    targetPanel.setAttribute('aria-hidden', 'false');
    targetPanel.classList.add(
      'is-active',
      'active',
      'sc-lab-panel-active'
    );
    targetPanel.dataset.scCivilPanelRouter = 'open';
    targetPanel.dataset.scCivilPanelRouterVersion = VERSION;

    allTriggers().forEach((element) => {
      const active = trigger
        ? element === trigger
        : candidateTrigger(element) === element;

      element.classList.toggle('is-active', active);
      element.classList.toggle('active', active);

      if (active) {
        element.setAttribute('aria-selected', 'true');
        element.setAttribute('aria-expanded', 'true');
      } else {
        element.setAttribute('aria-selected', 'false');
        element.setAttribute('aria-expanded', 'false');
      }
    });

    document.dispatchEvent(
      new CustomEvent('sc-lab:module-opened', {
        detail: {
          module: 'civil-infrastructure',
          source: 'civil-panel-router-v0200',
        },
      })
    );

    window.requestAnimationFrame(() => {
      targetPanel.hidden = false;
      targetPanel.removeAttribute('hidden');
    });

    window.setTimeout(() => {
      targetPanel.hidden = false;
      targetPanel.removeAttribute('hidden');

      if (Lab.CivilRuntime?.init) {
        Lab.CivilRuntime.init();
      } else if (
        Lab.CivilInfrastructureLab
        && typeof Lab.CivilInfrastructureLab.init === 'function'
      ) {
        Lab.CivilInfrastructureLab.init(
          document,
          Lab.Projects
        );
      }
    }, 60);

    return true;
  }

  function status() {
    const targetPanel = panel();

    return {
      version: VERSION,
      panelFound: Boolean(targetPanel),
      hidden: targetPanel
        ? targetPanel.hidden
        : null,
      ariaHidden: targetPanel
        ? targetPanel.getAttribute('aria-hidden')
        : null,
      triggerCount: allTriggers().length,
      runtime: Lab.CivilRuntime?.status
        ? Lab.CivilRuntime.status()
        : null,
    };
  }

  document.addEventListener(
    'click',
    (event) => {
      const trigger = candidateTrigger(event.target);

      if (!trigger) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();
      openCivil(trigger);
    },
    true
  );

  document.addEventListener(
    'keydown',
    (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') {
        return;
      }

      const trigger = candidateTrigger(event.target);

      if (!trigger) {
        return;
      }

      event.preventDefault();
      openCivil(trigger);
    },
    true
  );

  if (
    window.location.hash
    && window.location.hash.includes('civil-infrastructure')
  ) {
    if (document.readyState === 'loading') {
      document.addEventListener(
        'DOMContentLoaded',
        () => openCivil(),
        { once: true }
      );
    } else {
      openCivil();
    }
  }

  Lab.CivilPanelRouter = {
    VERSION,
    open: openCivil,
    status,
  };
})();
