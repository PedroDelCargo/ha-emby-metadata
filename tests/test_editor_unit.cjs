const fs = require('fs'), vm = require('vm'), assert = require('assert/strict');
const registry = new Map();
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.listeners = {}; }
  append(...children) { this.children.push(...children); }
  attachShadow() { return this.shadowRoot = new Element('shadow'); }
  addEventListener(name, handler) { this.listeners[name] = handler; }
  dispatchEvent(event) { this.lastEvent = event; }
  querySelectorAll(tag) { return this.children.flatMap(c => [...(c.tag === tag ? [c] : []), ...c.querySelectorAll(tag)]); }
}
let loads = 0;
const context = {
  HTMLElement: Element,
  customElements: { define: (name, cls) => registry.set(name, cls), get: name => registry.get(name) },
  document: { createElement: name => registry.has(name) ? new (registry.get(name))() : new Element(name) },
  window: { loadCardHelpers: async () => ({ createCardElement: () => ({ constructor: { getConfigElement: async () => { loads++; registry.set('ha-form', Element); } } }) }) },
  CustomEvent: class { constructor(type, options) { this.type = type; Object.assign(this, options); } },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('custom_components/emby_metadata/static/emby-metadata-card.js', 'utf8'), context);
(async () => {
  const Card = registry.get('emby-metadata-card');
  const editor = await Card.getConfigElement();
  assert.equal(loads, 1);
  editor.setConfig({ type: 'custom:emby-metadata-card', entity: 'sensor.movie', show_poster: false, custom_setting: 42 });
  editor.hass = { language: 'fr' };
  assert.equal(editor._forms.map(f => f.schema[0].name).join(','), 'entity,show_player,show_poster,show_video,show_audio,show_subtitles,show_cast');
  const toggle = editor._forms[1];
  assert.notEqual(toggle.computeLabel({ name: 'show_player' }), 'show_player');
  toggle.listeners['value-changed']({ stopPropagation() {}, detail: { value: { show_player: true } } });
  assert.equal(editor.lastEvent.type, 'config-changed');
  assert.equal(editor.lastEvent.detail.config.entity, 'sensor.movie');
  assert.equal(editor.lastEvent.detail.config.custom_setting, 42);
  assert.equal(editor.lastEvent.detail.config.show_poster, false);
  assert.equal(editor.lastEvent.detail.config.show_player, true);
  assert(editor.lastEvent.bubbles && editor.lastEvent.composed);
  await Card.getConfigElement();
  assert.equal(loads, 1);
  console.log('Editor checks passed: loading, ordering, translated labels and configuration preservation.');
})().catch(error => { console.error(error); process.exitCode = 1; });
