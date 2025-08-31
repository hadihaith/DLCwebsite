/*
 * PanZoomImage.js — a tiny, dependency‑free image zoom & pan plugin
 *
 * Features
 * - Mouse wheel / trackpad zoom (cursor‑centric)
 * - Click‑drag to pan
 * - Double‑click (or double‑tap) to reset
 * - Touch pinch‑to‑zoom + drag
 * - Public API: zoomIn, zoomOut, setScale, reset, getState, destroy
 *
 * Usage
 * <div class="viewer" style="width:600px;height:360px;overflow:hidden;position:relative">
 *   <img id="map" src="/path/to/image.png" />
 * </div>
 * <script src="/PanZoomImage.js"></script>
 * <script>
 *   const pz = new PanZoomImage(document.querySelector('.viewer'), {
 *     src: document.getElementById('map'), // pass an <img> or string URL
 *     minScale: 0.25,
 *     maxScale: 8,
 *     wheelSpeed: 0.0015,
 *   });
 *   // pz.zoomIn(); pz.zoomOut(); pz.reset();
 * </script>
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.PanZoomImage = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  class PanZoomImage {
    /**
     * @param {HTMLElement} container - element with position:relative and overflow:hidden
     * @param {Object} options
     *  - src: HTMLImageElement | string (url). If omitted, the first <img> child is used.
     *  - minScale, maxScale, wheelSpeed
     */
    constructor(container, options = {}) {
      if (!container) throw new Error('PanZoomImage: container is required');
      this.container = container;
      this.opts = Object.assign({ minScale: 0.25, maxScale: 8, wheelSpeed: 0.0015 }, options);

      // Prepare stage
      this.stage = document.createElement('div');
      Object.assign(this.stage.style, {
        position: 'absolute',
        inset: '0 0 0 0',
        transformOrigin: '0 0',
        willChange: 'transform',
        pointerEvents: 'none', // image shouldn't eat events
      });

      // Resolve image element
      if (this.opts.src instanceof HTMLImageElement) {
        this.img = this.opts.src;
      } else if (typeof this.opts.src === 'string') {
        this.img = new Image();
        this.img.src = this.opts.src;
      } else {
        this.img = this.container.querySelector('img');
        if (!this.img) throw new Error('PanZoomImage: no <img> found or src provided');
      }
      Object.assign(this.img.style, {
        display: 'block',
        maxWidth: 'none',
        userSelect: 'none',
        WebkitUserDrag: 'none',
        pointerEvents: 'none',
      });

      // Mount
      this.stage.appendChild(this.img);
      this.container.appendChild(this.stage);

      // Internal state
      this.scale = 1;
      this.tx = 0;
      this.ty = 0;
      this._dragging = false;
      this._touchMode = null; // 'pinch' | 'drag'
      this._start = { x: 0, y: 0, tx: 0, ty: 0, dist: 0, mid: { x: 0, y: 0 }, scale: 1 };

      // Ensure container has necessary styles
      const cs = getComputedStyle(this.container);
      if (cs.position === 'static') this.container.style.position = 'relative';
      if (cs.overflow !== 'hidden') this.container.style.overflow = 'hidden';
      this.container.style.touchAction = 'none';
      this.container.style.cursor = 'grab';

      // Bind handlers
      this._onWheel = this._onWheel.bind(this);
      this._onDown = this._onDown.bind(this);
      this._onMove = this._onMove.bind(this);
      this._onUp = this._onUp.bind(this);
      this._onDbl = this._onDbl.bind(this);

      // Listeners
      this.container.addEventListener('wheel', this._onWheel, { passive: false });
      this.container.addEventListener('pointerdown', this._onDown);
      this.container.addEventListener('pointermove', this._onMove);
      this.container.addEventListener('pointerup', this._onUp);
      this.container.addEventListener('pointercancel', this._onUp);
      this.container.addEventListener('dblclick', this._onDbl);

      this._pointers = new Map();
      this.apply();
    }

    // ---------- math helpers ----------
    clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

    containerPoint(evt) {
      const r = this.container.getBoundingClientRect();
      return { x: evt.clientX - r.left, y: evt.clientY - r.top };
    }

    zoomAt(point, nextScale) {
      const min = this.opts.minScale, max = this.opts.maxScale;
      nextScale = this.clamp(nextScale, min, max);
      const k = nextScale / this.scale; // s'/s
      this.tx = this.tx * k + point.x * (1 - k);
      this.ty = this.ty * k + point.y * (1 - k);
      this.scale = nextScale;
      this.apply();
    }

    apply() {
      this.stage.style.transform = `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`;
    }

    // ---------- event handlers ----------
    _onWheel(e) {
      e.preventDefault();
      const u = this.containerPoint(e);
      const zoomFactor = Math.exp(-e.deltaY * (this.opts.wheelSpeed || 0.0015));
      this.zoomAt(u, this.scale * zoomFactor);
    }

    _onDown(e) {
      this.container.setPointerCapture(e.pointerId);
      this._pointers.set(e.pointerId, e);

      if (this._pointers.size === 2) {
        // Enter pinch mode
        const [p1, p2] = Array.from(this._pointers.values());
        const d = Math.hypot(p2.clientX - p1.clientX, p2.clientY - p1.clientY);
        const mid = { x: (p1.clientX + p2.clientX) / 2, y: (p1.clientY + p2.clientY) / 2 };
        const uMid = this.containerPoint({ clientX: mid.x, clientY: mid.y });
        this._touchMode = 'pinch';
        this._start = { dist: d, mid: uMid, scale: this.scale };
        return;
      }

      // Drag mode
      this._touchMode = 'drag';
      const u = this.containerPoint(e);
      this._dragging = true;
      this.container.style.cursor = 'grabbing';
      this._start = { x: u.x, y: u.y, tx: this.tx, ty: this.ty };
    }

    _onMove(e) {
      if (!this._pointers.has(e.pointerId)) return;
      this._pointers.set(e.pointerId, e);

      if (this._touchMode === 'pinch' && this._pointers.size === 2) {
        const [p1, p2] = Array.from(this._pointers.values());
        const dist = Math.hypot(p2.clientX - p1.clientX, p2.clientY - p1.clientY);
        const ratio = dist / (this._start.dist || dist);
        const nextScale = this._start.scale * ratio;
        this.zoomAt(this._start.mid, nextScale);
        return;
      }

      if (this._dragging && this._touchMode === 'drag') {
        const u = this.containerPoint(e);
        this.tx = this._start.tx + (u.x - this._start.x);
        this.ty = this._start.ty + (u.y - this._start.y);
        this.apply();
      }
    }

    _onUp(e) {
      if (this.container.hasPointerCapture(e.pointerId)) {
        this.container.releasePointerCapture(e.pointerId);
      }
      this._pointers.delete(e.pointerId);

      if (this._pointers.size < 2 && this._touchMode === 'pinch') {
        this._touchMode = null;
      }
      if (this._pointers.size === 0) {
        this._dragging = false;
        this.container.style.cursor = 'grab';
      }
    }

    _onDbl() { this.reset(); }

    // ---------- public API ----------
    zoomIn(step = 1.2) {
      const r = this.container.getBoundingClientRect();
      this.zoomAt({ x: r.width / 2, y: r.height / 2 }, this.scale * step);
    }
    zoomOut(step = 1.2) {
      const r = this.container.getBoundingClientRect();
      this.zoomAt({ x: r.width / 2, y: r.height / 2 }, this.scale / step);
    }
    setScale(next, anchor = null) {
      const r = this.container.getBoundingClientRect();
      const pt = anchor || { x: r.width / 2, y: r.height / 2 };
      this.zoomAt(pt, next);
    }
    reset() {
      this.scale = 1; this.tx = 0; this.ty = 0; this.apply();
    }
    getState() { return { scale: this.scale, tx: this.tx, ty: this.ty }; }
    destroy() {
      this.container.removeEventListener('wheel', this._onWheel);
      this.container.removeEventListener('pointerdown', this._onDown);
      this.container.removeEventListener('pointermove', this._onMove);
      this.container.removeEventListener('pointerup', this._onUp);
      this.container.removeEventListener('pointercancel', this._onUp);
      this.container.removeEventListener('dblclick', this._onDbl);
      this.stage.remove();
      this._pointers.clear();
    }
  }

  return PanZoomImage;
});
