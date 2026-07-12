(function (w) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const KEY = 'scLabProjectsV010';
  const ACTIVE = 'scLabActiveProjectV010';
  const COLLECTIONS = ['evidence', 'experiments', 'hypotheses', 'decisions', 'notes', 'calculations', 'documents', 'maps', 'activity'];

  function blank(name = 'Untitled Lab Project') {
    const now = U.now();
    return {
      schemaVersion: '0.1.1',
      id: U.uid('project'),
      name,
      createdAt: now,
      updatedAt: now,
      description: '',
      evidence: [],
      experiments: [],
      hypotheses: [],
      decisions: [],
      notes: [],
      calculations: [],
      documents: [],
      maps: [],
      activity: []
    };
  }

  function normalize(project) {
    const base = blank(project?.name || 'Untitled Lab Project');
    const merged = Object.assign(base, project || {}, { schemaVersion: '0.1.1' });
    COLLECTIONS.forEach(key => {
      if (!Array.isArray(merged[key])) merged[key] = [];
    });
    if (!merged.createdAt) merged.createdAt = U.now();
    if (!merged.updatedAt) merged.updatedAt = merged.createdAt;
    return merged;
  }

  function read() {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(data) ? data.map(normalize) : [];
    } catch (error) {
      return [];
    }
  }

  function write(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
  }

  class Projects {
    constructor() {
      this.items = read();
      if (!this.items.length) {
        this.items = [blank('Lab Project')];
        write(this.items);
      }
      this.activeId = localStorage.getItem(ACTIVE) || this.items[0].id;
      if (!this.get()) this.activeId = this.items[0].id;
      localStorage.setItem(ACTIVE, this.activeId);
      this.listeners = [];
    }

    onChange(fn) { this.listeners.push(fn); }
    emit() { this.listeners.forEach(fn => fn(this.get(), this.items)); }
    get(id = this.activeId) { return this.items.find(project => project.id === id); }

    select(id) {
      if (this.get(id)) {
        this.activeId = id;
        localStorage.setItem(ACTIVE, id);
        this.emit();
      }
    }

    create(name) {
      const project = blank(name || 'Untitled Lab Project');
      this.items.unshift(project);
      this.activeId = project.id;
      this.save();
      return project;
    }

    update(mutator, activity) {
      const project = this.get();
      if (!project) return;
      mutator(project);
      project.schemaVersion = '0.1.1';
      project.updatedAt = U.now();
      if (activity) {
        project.activity.unshift({ id: U.uid('activity'), at: project.updatedAt, text: activity });
      }
      project.activity = project.activity.slice(0, 500);
      this.save();
    }

    save() {
      write(this.items);
      localStorage.setItem(ACTIVE, this.activeId);
      this.emit();
    }

    add(collection, record, activity) {
      if (!COLLECTIONS.includes(collection)) throw new Error(`Unknown project collection: ${collection}`);
      this.update(project => {
        project[collection].unshift(Object.assign({ id: U.uid(collection), createdAt: U.now() }, record));
      }, activity);
      return this.get()[collection][0];
    }

    export() {
      const project = this.get();
      U.download(
        `${project.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}-lab-project.json`,
        JSON.stringify(project, null, 2),
        'application/json'
      );
    }

    import(raw) {
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object' || !parsed.name) throw new Error('Invalid project file');
      const project = normalize(Object.assign({}, parsed, { id: U.uid('project'), updatedAt: U.now() }));
      this.items.unshift(project);
      this.activeId = project.id;
      this.save();
      return project;
    }
  }

  Lab.Projects = Projects;
  Lab.ProjectModel = { blank, normalize, collections: COLLECTIONS };
})(window);
