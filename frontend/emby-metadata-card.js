/* Emby Metadata Card - Home Assistant custom card - V1.2.11 */

// Card translations are bundled to keep the standalone JS self-contained.
// Edit frontend/translations/<language>.json, then run scripts/build_card.py.
const EMBY_CARD_TRANSLATIONS = /* __EMBY_TRANSLATIONS__ */;

function embyCardLanguage(hass) {
  const language = hass?.locale?.language || hass?.language || "en";
  return String(language).replaceAll("_", "-").toLowerCase();
}

function embyCardText(key, language = "en", values = {}) {
  const code = String(language).replaceAll("_", "-").toLowerCase();
  const dictionary = EMBY_CARD_TRANSLATIONS[code] || EMBY_CARD_TRANSLATIONS[code.split("-")[0]];
  const text = dictionary?.[key] ?? EMBY_CARD_TRANSLATIONS.en[key] ?? key;
  return text.replace(/\{(\w+)\}/g, (match, name) => String(values[name] ?? match));
}

class EmbyMetadataCard extends HTMLElement {
  static getStubConfig(hass) {
    return {
      entity: Object.keys(hass?.states || {}).find(id => id.startsWith("sensor.") && hass.states[id].attributes?.device_id) || "",
      show_poster: true,
      show_cast: true,
      show_video: true,
      show_audio: true,
      show_subtitles: true,
    };
  }

  static getConfigForm() {
    return {
      schema: [
        {
          name: "entity",
          required: true,
          selector: { entity: { domain: "sensor" } },
        },
        {
          name: "show_poster",
          default: true,
          selector: { boolean: {} },
        },
        {
          type: "expandable",
          name: "technical",
          flatten: true,
          schema: [
            {
              name: "show_video",
              default: true,
              selector: { boolean: {} },
            },
            {
              name: "show_audio",
              default: true,
              selector: { boolean: {} },
            },
            {
              name: "show_subtitles",
              default: true,
              selector: { boolean: {} },
            },
          ],
        },
        {
          name: "show_cast",
          default: true,
          selector: { boolean: {} },
        },
      ],
      // HA calls these methods on its form editor, whose hass is current.
      computeLabel: function (schema) {
        return embyCardText(schema.name, embyCardLanguage(this?.hass));
      },
      assertConfig: function (config) {
        if (config.entity != null && typeof config.entity !== "string") {
          throw new Error(embyCardText("invalid_entity", embyCardLanguage(this?.hass)));
        }
        for (const key of ["show_poster", "show_cast", "show_video", "show_audio", "show_subtitles"]) {
          if (config[key] != null && typeof config[key] !== "boolean") {
            throw new Error(embyCardText("invalid_boolean", embyCardLanguage(this?.hass), { key }));
          }
        }
      },
    };
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._resizeObserver = null;
    this._lastSignature = null;
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error(this._t("required_entity"));
    }

    this._config = {
      show_poster: true,
      show_cast: true,
      show_video: true,
      show_audio: true,
      show_subtitles: true,
      ...config,
    };

    // Backward compatibility with V1.1.x.
    if (
      Object.prototype.hasOwnProperty.call(config, "show_technical") &&
      !Object.prototype.hasOwnProperty.call(config, "show_video") &&
      !Object.prototype.hasOwnProperty.call(config, "show_audio") &&
      !Object.prototype.hasOwnProperty.call(config, "show_subtitles")
    ) {
      const enabled = config.show_technical !== false;
      this._config.show_video = enabled;
      this._config.show_audio = enabled;
      this._config.show_subtitles = enabled;
    }

    this._renderIfChanged();
  }

  set hass(value) {
    this._hass = value;
    this._renderIfChanged();
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    if (!this._resizeObserver) {
      this._resizeObserver = new ResizeObserver(() => {
        this._updateBackdropGeometry();
      });
      this._resizeObserver.observe(this);
    }
    this._updateBackdropGeometry();
  }

  disconnectedCallback() {
    this._resizeObserver?.disconnect();
    this._resizeObserver = null;
  }

  getCardSize() {
    return 6;
  }

  _t(key, values) {
    return embyCardText(key, embyCardLanguage(this._hass), values);
  }

  _state() {
    return this._hass?.states?.[this._config.entity];
  }

  _imageUrl(entityId) {
    if (!entityId) return null;
    const state = this._hass?.states?.[entityId];
    if (!state || state.state === "unavailable") return null;
    const url = state.attributes?.entity_picture;
    if (!url) return null;
    return `${url}${url.includes("?") ? "&" : "?"}v=${encodeURIComponent(state.state || "")}`;
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _formatRuntime(minutes) {
    const value = Number(minutes);
    if (!Number.isFinite(value) || value <= 0) return null;
    const h = Math.floor(value / 60);
    const m = value % 60;
    return h ? `${h} ${this._t("hours")}${m ? ` ${m} ${this._t("minutes")}` : ""}` : `${m} ${this._t("minutes")}`;
  }

  _formatRating(value) {
    if (value == null || value === "") return null;
    const number = Number(value);
    if (!Number.isFinite(number)) return null;
    try {
      return `★ ${new Intl.NumberFormat(embyCardLanguage(this._hass), { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(number)}`;
    } catch {
      return `★ ${number.toFixed(1)}`;
    }
  }

  _formatGenres(genres) {
    if (!Array.isArray(genres)) return genres || null;
    return genres.slice(0, 3).join(" · ");
  }

  _language(value) {
    const code = String(value || "").trim().toLowerCase();
    if (!code) return null;
    const aliases = { fra: "fr", fre: "fr", eng: "en", deu: "de", ger: "de", spa: "es", ita: "it", nld: "nl", dut: "nl", por: "pt", jpn: "ja", kor: "ko", zho: "zh", chi: "zh" };
    try {
      return new Intl.DisplayNames([embyCardLanguage(this._hass)], { type: "language", fallback: "code" }).of(aliases[code] || code) || value;
    } catch {
      return value;
    }
  }

  _codec(value) {
    const codec = String(value || "").trim().toUpperCase();
    const names = {
      AC3: "Dolby Digital",
      EAC3: "Dolby Digital Plus",
      TRUEHD: "Dolby TrueHD",
      DTS: "DTS",
      DTSHD: "DTS-HD",
      DTSHD_MA: "DTS-HD MA",
      DTS_HD_MA: "DTS-HD MA",
      DTSX: "DTS:X",
      DTS_X: "DTS:X",
      AAC: "AAC",
      FLAC: "FLAC",
      OPUS: "Opus",
      VORBIS: "Vorbis",
      MP3: "MP3",
      H264: "H.264",
      AVC: "H.264",
      HEVC: "HEVC",
      H265: "HEVC",
      AV1: "AV1",
      VP9: "VP9",
    };
    return names[codec] || value || null;
  }

  _hdr(value) {
    const hdr = String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[ _-]/g, "");
    const names = {
      dolbyvision: "Dolby Vision",
      dv: "Dolby Vision",
      hdr10plus: "HDR10+",
      hdr10: "HDR10",
      hdr: "HDR",
      hlg: "HLG",
    };
    return ["", "none", "null", "sdr", "0", "unknown"].includes(hdr) ? null : names[hdr] || value || null;
  }

  _quality(width, height) {
    if (!width || !height) return null;
    const w = Number(width);
    const h = Number(height);
    if (!Number.isFinite(w) || !Number.isFinite(h)) return null;
    const max = Math.max(w, h);
    if (max >= 3800 || h >= 2000) return "4K";
    if (max >= 1900 || h >= 1000) return "1080p";
    if (max >= 1200 || h >= 700) return "720p";
    return `${Math.round(max)}p`;
  }

  _channels(channels, layout) {
    if (layout) return layout;
    if (channels == null || channels === "") return null;
    const value = Number(channels);
    if (!Number.isFinite(value)) return null;
    if (value === 8) return "7.1";
    if (value === 6) return "5.1";
    if (value === 4) return "4.0";
    if (value === 2) return "2.0";
    if (value === 1) return this._t("mono");
    return `${value} ${this._t("channels")}`;
  }

  _titleMarkup(logoUrl, title) {
    if (logoUrl) {
      return `
        <img class="title-logo" src="${this._escape(logoUrl)}"
             alt="${this._escape(title || "")}">
      `;
    }
    return title ? `<div class="title-text">${this._escape(title)}</div>` : "";
  }

  _metaRows(attrs) {
    const year = attrs.production_year;
    const genres = this._formatGenres(attrs.genres);
    return `
      ${year ? `<div class="meta-row">${this._escape(year)}</div>` : ""}
      ${genres ? `<div class="meta-row genres">${this._escape(genres)}</div>` : ""}
    `;
  }

  _runtimeRating(attrs) {
    const runtime = this._formatRuntime(attrs.runtime_minutes);
    const rating = this._formatRating(attrs.community_rating);
    return runtime || rating ? `<div class="meta-row split runtime-rating">
      <span>${this._escape(runtime || "")}</span><span>${this._escape(rating || "")}</span>
    </div>` : "";
  }

  _disclosure(kind, title, body, className) {
    const open = !!this._sections?.[kind];
    return `<section class="${className} disclosure${open ? " is-open" : ""}" data-section="${kind}">
      <button class="section-toggle" type="button" aria-expanded="${open}" aria-controls="${kind}-body">${this._escape(title)}</button>
      <div class="section-body" id="${kind}-body" ${open ? "" : "inert"}>
        <div class="section-clip"><div class="section-inner">${body}</div></div>
      </div>
    </section>`;
  }

  _technicalGroups(attrs) {
    return {
      video: [
        this._quality(attrs.video_width, attrs.video_height),
        this._hdr(attrs.video_hdr),
        this._codec(attrs.video_codec),
        attrs.video_bit_depth ? `${attrs.video_bit_depth}-bit` : null,
        attrs.video_frame_rate
          ? `${Number(attrs.video_frame_rate).toFixed(0)} fps`
          : null,
      ].filter(Boolean),

      audio: [
        this._language(attrs.audio_language),
        this._codec(attrs.audio_codec),
        this._channels(attrs.audio_channels, attrs.audio_channel_layout),
      ].filter(Boolean),

      subtitle: [
        this._language(attrs.subtitle_language),
        attrs.subtitle_title,
        attrs.subtitle_forced ? this._t("forced") : null,
        attrs.subtitle_hearing_impaired ? this._t("hearing_impaired") : null,
      ].filter(Boolean),
    };
  }

  _technical(attrs) {
    const groups = this._technicalGroups(attrs);
    const rows = [];

    if (this._config.show_video && groups.video.length) {
      rows.push(this._technicalRow(this._t("video"), groups.video));
    }
    if (this._config.show_audio && groups.audio.length) {
      rows.push(this._technicalRow(this._t("audio"), groups.audio));
    }
    if (this._config.show_subtitles && groups.subtitle.length) {
      rows.push(this._technicalRow(this._t("subtitles"), groups.subtitle));
    }

    return rows.join("");
  }

  _technicalRow(label, values) {
    return `
      <div class="technical-row">
        <div class="technical-label">${this._escape(label)}</div>
        <div class="technical-badges">
          ${values.map(value => `
            <span class="format-badge">${this._escape(value)}</span>
          `).join("")}
        </div>
      </div>
    `;
  }

  _people(attrs) {
    if (!this._config.show_cast) return "";

    const entries = [];

    if (attrs.director?.name) {
      entries.push({
        name: attrs.director.name,
        role: !attrs.director.role || ["Director", "Réalisateur"].includes(attrs.director.role) ? this._t("director") : attrs.director.role,
        image: this._imageUrl(attrs.director.image_entity),
        director: true,
      });
    }

    if (Array.isArray(attrs.actors)) {
      for (const actor of attrs.actors.slice(0, 5)) {
        if (!actor?.name) continue;
        entries.push({
          name: actor.name,
          role: actor.role || "",
          image: this._imageUrl(actor.image_entity),
          director: false,
        });
      }
    }

    if (!entries.length) return "";

    const body = `<div class="people-grid">
      ${entries.map(person => `
        <div class="person">
          <div class="person-photo-wrap">
            ${person.image ? `<img class="person-photo" src="${this._escape(person.image)}" alt="${this._escape(person.name)}">` : ""}
            <div class="person-caption">
              <div class="person-name">${this._escape(person.name)}</div>
              ${person.role ? `<div class="person-role">${this._escape(person.role)}</div>` : ""}
            </div>
          </div>
        </div>`).join("")}
    </div>`;
    return this._disclosure("people", this._t("cast"), body, "people-section");
  }

  _overview(attrs, className = "") {
    if (!attrs.overview) return "";
    return `
      <div class="synopsis ${className}">
        <div class="synopsis-text">${this._escape(attrs.overview)}</div>
        <button class="synopsis-toggle" type="button" aria-expanded="false">
          ${this._escape(this._t("show_more"))}
        </button>
      </div>
    `;
  }

  _images(attrs) {
    return {
      poster: this._imageUrl(attrs.poster_entity),
      backdrop: this._imageUrl(attrs.backdrop_entity),
      logo: this._imageUrl(attrs.logo_entity),
    };
  }

  _signature(state) {
    if (!state) return `missing:${embyCardLanguage(this._hass)}`;

    const a = state.attributes || {};
    const imageIds = [
      a.poster_entity, a.backdrop_entity, a.logo_entity,
      a.director?.image_entity,
      ...(Array.isArray(a.actors) ? a.actors.map(p => p?.image_entity) : []),
    ];

    const imageUrls = imageIds.map(id => {
      const url = id ? this._imageUrl(id) : null;
      return url?.replace(/([?&])token=[^&]*&?/, "$1") || null;
    });

    return JSON.stringify({
      language: embyCardLanguage(this._hass),
      state: state.state,
      playing: a.playing,
      title: a.title,
      item: a.emby_item_id,
      episode: [a.media_type, a.series_title, a.season_number, a.episode_number, a.episode_number_end],
      original_title: a.original_title,
      tagline: a.tagline,
      production_year: a.production_year,
      genres: a.genres,
      overview: a.overview,
      rating: a.community_rating,
      runtime: a.runtime_minutes,
      video: [
        a.video_codec, a.video_width, a.video_height,
        a.video_bit_depth, a.video_frame_rate, a.video_hdr,
      ],
      audio: [
        a.audio_codec, a.audio_language, a.audio_channels,
        a.audio_channel_layout,
      ],
      subtitle: [
        a.subtitle_language, a.subtitle_title,
        a.subtitle_forced, a.subtitle_hearing_impaired,
      ],
      director: a.director,
      actors: a.actors,
      images: imageUrls,
      config: {
        show_poster: this._config.show_poster,
        show_cast: this._config.show_cast,
        show_video: this._config.show_video,
        show_audio: this._config.show_audio,
        show_subtitles: this._config.show_subtitles,
      },
    });
  }

  _renderIfChanged() {
    const state = this._state();
    const signature = this._signature(state);

    if (signature === this._lastSignature) {
      this._updateBackdropGeometry();
      return;
    }

    this._lastSignature = signature;
    this._render();
  }

  _render() {
    if (!this.shadowRoot || !this._hass || !this._config.entity) return;

    const state = this._state();

    if (!state) {
      this.shadowRoot.innerHTML = `
        <style>${this._styles()}</style>
        <article class="card unavailable">${this._escape(this._t("missing_entity"))}</article>
      `;
      return;
    }

    const attrs = state.attributes || {};

    if (
      attrs.playing === false ||
      state.state === "Idle" ||
      state.state === "Unavailable"
    ) {
      this.shadowRoot.innerHTML = `
        <style>${this._styles()}</style>
        <article class="card idle">${this._escape(this._t("idle"))}</article>
      `;
      return;
    }

    const itemKey = JSON.stringify([this._config.entity, attrs.emby_item_id || attrs.title || state.state]);
    if (itemKey !== this._sectionItemKey) this._sections = { technical: false, people: false };
    this._sectionItemKey = itemKey;
    const images = this._images(attrs);
    const title = attrs.title || state.state || "";
    const slogan = attrs.tagline || "";
    const technical = this._technical(attrs);
    const overview = this._overview(attrs);
    const people = this._people(attrs);

    const backdrop = images.backdrop || images.poster;
    const episode = attrs.media_type === "Episode";
    const displayTitle = episode ? attrs.series_title || title : title;
    const episodeParts = [];
    if (episode && attrs.season_number != null) episodeParts.push(`S${String(attrs.season_number).padStart(2, "0")}`);
    if (episode && attrs.episode_number != null) {
      let number = `E${String(attrs.episode_number).padStart(2, "0")}`;
      if (attrs.episode_number_end != null && attrs.episode_number_end !== attrs.episode_number) number += `–E${String(attrs.episode_number_end).padStart(2, "0")}`;
      episodeParts.push(number);
    }
    const episodeLabel = episode ? [episodeParts.join(""), title].filter(Boolean).join(" · ") : "";
    const synopsisKey = JSON.stringify([attrs.emby_item_id || title, attrs.overview]);
    if (synopsisKey !== this._synopsisKey) this._expanded = false;
    this._synopsisKey = synopsisKey;

    this.shadowRoot.innerHTML = `
      <style>${this._styles()}</style>
      <article class="card responsive-card ${backdrop ? "has-backdrop" : ""}">
        <div class="backdrop-layer" aria-hidden="true">
          ${backdrop ? `<img class="backdrop" src="${this._escape(backdrop)}" alt="">` : ""}
          <div class="backdrop-shade"></div>
        </div>
        <section class="layout ${this._config.show_poster ? "with-poster" : "without-poster"}">
          ${this._config.show_poster ? `<div class="poster-column">
            ${images.poster ? `<img class="poster" src="${this._escape(images.poster)}" alt="${this._escape(displayTitle)}">` : `<div class="poster-placeholder"></div>`}
          </div>` : ""}
          <div class="content">
            <div class="summary">
            <header class="heading">
              ${this._titleMarkup(images.logo, displayTitle)}
              ${episodeLabel ? `<div class="episode-title">${this._escape(episodeLabel)}</div>` : ""}
              ${slogan ? `<div class="tagline">${this._escape(slogan)}</div>` : ""}
            </header>
            <div class="metadata">${this._metaRows(attrs)}</div>
            ${this._runtimeRating(attrs)}
            </div>
            ${overview}
            ${technical ? this._disclosure("technical", this._t("technical"), technical, "technical") : ""}
          </div>
          ${people}
        </section>
      </article>`;
    this._bindInteractions(displayTitle, images);
    this._updateBackdropGeometry();
  }

  _bindInteractions(title, images) {
    const closeOthers = active => {
      this._sections ||= {};
      this.shadowRoot.querySelectorAll(".disclosure").forEach(section => {
        if (section.dataset.section === active) return;
        this._sections[section.dataset.section] = false;
        section.querySelector(".section-toggle").setAttribute("aria-expanded", "false");
        section.querySelector(".section-body").inert = true;
        section.classList.remove("is-open");
      });
      if (active !== "synopsis") {
        this._expanded = false;
        this._measureSynopsis();
      }
    };
    this.shadowRoot.querySelectorAll(".section-toggle").forEach(button => {
      button.addEventListener("click", () => {
        const section = button.closest(".disclosure");
        const open = button.getAttribute("aria-expanded") !== "true";
        if (open) closeOthers(section.dataset.section);
        this._sections ||= {};
        this._sections[section.dataset.section] = open;
        button.setAttribute("aria-expanded", String(open));
        section.querySelector(".section-body").inert = !open;
        section.classList.toggle("is-open", open);
      });
    });
    const synopsis = this.shadowRoot.querySelector(".synopsis");
    const button = synopsis?.querySelector(".synopsis-toggle");
    if (button) {
      button.addEventListener("click", event => {
        event.stopPropagation();
        if (!this._expanded) closeOthers("synopsis");
        this._expanded = !this._expanded;
        this._measureSynopsis();
      });
      synopsis.addEventListener("click", () => { if (!button.hidden) button.click(); });
    }
    this.shadowRoot.querySelectorAll("img").forEach(image => {
      const failed = () => {
        if (image.classList.contains("title-logo")) {
          const text = document.createElement("div");
          text.className = "title-text";
          text.textContent = title;
          image.replaceWith(text);
        } else if (image.classList.contains("backdrop") && images.poster && image.getAttribute("src") !== images.poster) {
          image.src = images.poster;
        } else {
          image.hidden = true;
          if (image.classList.contains("backdrop")) {
            this.shadowRoot.querySelector(".responsive-card")?.classList.remove("has-backdrop");
          } else if (image.classList.contains("poster")) {
            image.parentElement.classList.add("poster-placeholder");
          } else {
            image.parentElement.classList.add("placeholder");
          }
        }
        this._updateBackdropGeometry();
      };
      image.addEventListener("error", failed);
      image.addEventListener("load", () => this._updateBackdropGeometry());
      if (image.complete && !image.naturalWidth) failed();
    });
    requestAnimationFrame(() => this._measureSynopsis());
  }

  _measureSynopsis() {
    const synopsis = this.shadowRoot?.querySelector(".synopsis");
    const text = synopsis?.querySelector(".synopsis-text");
    const button = synopsis?.querySelector(".synopsis-toggle");
    if (!text || !button) return;
    const collapsed = parseFloat(getComputedStyle(text).lineHeight) * 5;
    const full = text.scrollHeight;
    const canExpand = full > collapsed + 2;
    button.hidden = !canExpand;
    synopsis.classList.toggle("can-expand", canExpand);
    button.setAttribute("aria-expanded", String(!!this._expanded));
    button.textContent = this._t(this._expanded ? "show_less" : "show_more");
    const height = `${this._expanded ? full : Math.min(full, collapsed)}px`;
    if (text.style.maxHeight !== height) text.style.maxHeight = height;
  }

  _updateBackdropGeometry() {
    const card = this.shadowRoot?.querySelector(".responsive-card");
    const image = this.shadowRoot?.querySelector(".backdrop");
    if (card && image && !image.hidden) {
      const height = image.getBoundingClientRect().height;
      const value = `${height}px`;
      if (height > 0 && card.style.getPropertyValue("--backdrop-height") !== value) card.style.setProperty("--backdrop-height", value);
    }
    this._measureSynopsis();
  }

  _styles() {
    return `
      :host {
        display: block;
        container-type: inline-size;
      }

      .card {
        overflow: hidden;
        border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg, 12px));
        padding: 1px;
        background: #000;
        color: #fff;
        box-shadow: var(--ha-card-box-shadow, none);
      }

      .layout {
        display: grid;
        grid-template-columns: 230px minmax(0, 1fr);
        gap: 16px;
        padding: 16px;
      }

      .poster-column {
        min-width: 0;
        display: flex;
        align-items: flex-start;
        justify-content: center;
      }

      .poster {
        display: block;
        width: 100%;
        max-height: 450px;
        object-fit: contain;
        border-radius: 10px;
        box-shadow: 0 8px 30px rgba(0,0,0,.35);
      }

      .poster-placeholder {
        width: 100%;
        aspect-ratio: 2 / 3;
        border-radius: 10px;
        background: rgba(255,255,255,.05);
      }

      .content {
        min-width: 0;
      }

      .heading {
        min-width: 0;
      }

      .title-logo {
        display: block;
        max-width: 100%;
        max-height: 105px;
        width: auto;
        height: auto;
        object-fit: contain;
        object-position: left center;
        margin-bottom: 8px;
      }

      .title-text {
        font-size: clamp(1.35rem, 3.4cqw, 2.35rem);
        font-weight: 750;
        line-height: 1.08;
        margin-bottom: 8px;
      }

      .tagline {
        font-size: .95rem;
        line-height: 1.35;
        color: #c5c5c5;
      }

      .metadata {
        margin-top: 10px;
      }

      .meta-row {
        line-height: 1.45;
        margin-top: 6px;
        font-size: .95rem;
      }

      .genres {
        color: #c5c5c5;
      }

      .split {
        display: flex;
        justify-content: space-between;
        gap: 16px;
      }

      .split span:last-child {
        text-align: right;
      }

      .synopsis {
        margin-top: 14px;
        padding: 16px 0;
        border-top: 1px solid rgba(255,255,255,.5);
        color: rgba(255,255,255,.9);
        line-height: 1.5;
        position: relative;
        cursor: default;
      }

      .synopsis-text {
        white-space: pre-line;
      }

      .synopsis-text {
        overflow: hidden;
        max-height: 7.5em;
        transition: max-height 280ms ease;
      }
      @media (prefers-reduced-motion: reduce) {
        .synopsis-text { transition: none; }
      }

      .synopsis.can-expand {
        cursor: pointer;
      }

      .synopsis-toggle {
        appearance: none;
        border: 0;
        background: transparent;
        color: rgba(255,255,255,.7);
        padding: 5px 0 0;
        font: inherit;
        font-size: .82rem;
        cursor: pointer;
      }

      .technical {
        padding-top: 16px;
		border-top: 1px solid rgba(255,255,255,.5);
      }

      .technical-row {
        display: grid;
        grid-template-columns: 82px minmax(0,1fr);
        gap: 10px;
        align-items: center;
        padding: 4px 0;
      }

      .technical-label {
        color: rgba(255,255,255,.75);
        font-size: .72rem;
        letter-spacing: .08em;
      }

      .technical-badges {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
        gap: 5px;
      }

      .format-badge {
        display: inline-flex;
        align-items: center;
        min-height: 1.55em;
        box-sizing: border-box;
        padding: .18em .55em;
        border: 1px solid rgba(255,255,255,.3);
        border-radius: .5em;
        background: rgba(0,0,0,.3);
        color: rgba(255,255,255,.92);
        font-size: .76rem;
        font-weight: 500;
        line-height: 1.2;
        white-space: nowrap;
        backdrop-filter: blur(4px);
      }

      .people-section {
        margin-top: 20px;
        padding-top: 14px;
        border-top: 1px solid rgba(255,255,255,.5);
      }

      .section-title {
        margin-bottom: 10px;
        color: rgba(255,255,255,.75);
        font-size: .72rem;
		font-weight: 600;
        letter-spacing: .08em;
      }

      .people-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(0,1fr));
        gap: 10px;
      }

      .person {
        min-width: 0;
        text-align: center;
      }

      .person-photo-wrap {
        width: 100%;
		max-width: 150px;
		margin: auto;
        aspect-ratio: 2 / 3;
        overflow: hidden;
        border-radius: 9px;
        background: rgba(255,255,255,.06);
      }

      .person-photo {
        display: block;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .person-photo.placeholder {
        background: linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.03));
      }

      .person-name {
        margin-top: 6px;
        font-size: 0.9rem;
        font-weight: 650;
        line-height: 1.15;
        overflow-wrap: anywhere;
      }

      .person-role {
        margin-top: 2px;
        color: rgba(255,255,255,.75);
        font-size: .8rem;
        line-height: 1.15;
        overflow-wrap: anywhere;
      }

      [hidden] { display: none !important; }
      .responsive-card { position: relative; isolation: isolate; }
      .backdrop-layer { position: absolute; inset: 0 0 auto; z-index: -1; }
      .backdrop { display: block; width: 100%; height: auto; }
      .backdrop-shade {
        position: absolute; inset: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,.30) 0%, rgba(0,0,0,.30) 66.667%, #000 100%);
      }
      .layout { position: relative; min-height: var(--backdrop-height, 0px); box-sizing: border-box; align-content: start; }
      .layout.without-poster { grid-template-columns: minmax(0, 1fr); }
      .people-section { grid-column: 1 / -1; margin-top: 0; }
      .episode-title { font-size: 1.08rem; font-weight: 600; margin: 10px 0; }
      .idle, .unavailable { padding: 28px; color: #aaa; }
      @container (width < 768px) {
        .layout, .layout.without-poster { display: block; padding: 20px; }
        .poster-column { display: none; }
        .people-section { margin-top: 20px; }
        .title-logo { max-height: 85px; }
        .title-text { font-size: clamp(1.35rem, 7cqw, 2rem); }
        .people-grid { grid-template-columns: repeat(3, minmax(0,1fr)); }
      }
      @container (max-width: 430px) {
        .layout, .layout.without-poster { padding-left: 15px; padding-right: 15px; }
        .people-grid { grid-template-columns: repeat(3, minmax(0,1fr)); }
        .technical-row { grid-template-columns: 70px minmax(0,1fr); }
        .format-badge { font-size: .70rem; }
      }
      @container (min-width: 768px) and (max-width: 1050px) {
        .layout.with-poster { grid-template-columns: 210px minmax(0,1fr); gap: 16px; }
      }
    
  
      /* Title/year/genres stay at the top; runtime/rating sit above the synopsis. */
      .summary {
        display: flex;
        flex-direction: column;
        min-height: clamp(240px, calc(var(--backdrop-height, 450px) * .55), 360px);
      }
      .runtime-rating { margin-top: auto; padding-top: 18px; }
      .section-toggle {
        display: flex;
        width: 100%;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 0;
        margin: 0;
        border: 0;
        background: transparent;
        color: rgba(255,255,255,.75);
        font: inherit;
        font-size: .82rem;
        font-weight: 600;
        letter-spacing: .06em;
        text-align: left;
        cursor: pointer;
      }
      .section-toggle::after {
        content: "";
        width: 7px; height: 7px;
        border-right: 1.5px solid currentColor;
        border-bottom: 1.5px solid currentColor;
        transform: rotate(45deg);
        transition: transform 280ms ease;
        margin: 0 4px 4px;
        flex: 0 0 auto;
      }
      .section-toggle[aria-expanded="true"]::after { transform: rotate(225deg); }
      .section-toggle:focus-visible { outline: 2px solid #a9d4e9; outline-offset: 5px; border-radius: 2px; }
      .section-body {
        display: grid;
        grid-template-rows: 0fr;
        visibility: hidden;
        transition: grid-template-rows 280ms ease, visibility 0s linear 280ms;
      }
      .is-open > .section-body {
        grid-template-rows: 1fr;
        visibility: visible;
        transition-delay: 0s;
      }
      .section-clip { min-height: 0; overflow: hidden; }
      .section-inner { padding-top: 12px; }
      .person-photo-wrap {
        position: relative;
        background-color: #15191d;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 300'%3E%3Cg fill='%23d9e1e6' opacity='.16'%3E%3Ccircle cx='100' cy='96' r='43'/%3E%3Cpath d='M25 300v-71a75 75 0 0 1 150 0v71Z'/%3E%3C/g%3E%3C/svg%3E");
        background-size: cover;
        background-position: center;
      }
      .person-caption {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        box-sizing: border-box;
        padding: 7px 5px;
        background: rgba(0,0,0,.60);
        max-height: 100%;
        overflow: auto;
      }
      .person-caption .person-name { margin-top: 0; }
      @media (prefers-reduced-motion: reduce) {
        .section-body, .section-toggle::after { transition: none; }
      }

      /* With a visible poster, the synopsis starts below the entire first row. */
      @container (min-width: 768px) {
        .with-poster > .poster-column { grid-column: 1; grid-row: 1; }
        .with-poster > .content { display: contents; }
        .with-poster > .content > .summary {
          grid-column: 2;
          grid-row: 1;
          align-self: stretch;
        }
        .with-poster > .content > .synopsis,
        .with-poster > .content > .technical {
          grid-column: 1 / -1;
          margin-top: 0;
        }
      }

    
  `;
  }
}

customElements.define("emby-metadata-card", EmbyMetadataCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "emby-metadata-card",
  name: "Emby Metadata",
  description: "Responsive Emby card with metadata, media details, and cast.",
  preview: true,
  documentationURL: "https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card",
  getEntitySuggestion: (hass, entityId) => {
    if (entityId?.split(".")[0] !== "sensor") return null;
    const state = hass?.states?.[entityId];
    if (!state?.attributes?.emby_item_id && !state?.attributes?.device_id) return null;
    return {
      config: {
        type: "custom:emby-metadata-card",
        entity: entityId,
      },
    };
  },
});
