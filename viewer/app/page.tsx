'use client';
/* Static full-resolution render assets are intentionally served without an image optimization service. */
/* oxlint-disable next/no-img-element */
import type { Mesh, MeshStandardMaterial, Material } from 'three';
type CameraData = { position: number[]; target: number[]; lens: number };
type TerrainData = { x: number[]; y: number[]; z: number[][] };
type PaletteData = Record<string, { linearColor: [number, number, number] }>;
type CampusTool = {
  name: string;
  description: string;
  inputSchema: object;
  annotations: object;
  execute: (input: unknown) => unknown;
};
type CampusContext = {
  registerTool: (tool: CampusTool, options: { signal: AbortSignal }) => unknown;
};
import { useEffect, useRef, useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { canWalkTo } from '@/lib/campus-navigation';
import {
  Compass,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Move,
  RotateCcw,
  Maximize,
  ArrowUpRight,
  Eye,
  Play,
  Download,
  Layers,
} from 'lucide-react';

type ViewName =
  | 'reference_aerial'
  | 'entrance_detail'
  | 'arrival'
  | 'campus_overview';
const views: { id: ViewName; label: string; caption: string }[] = [
  {
    id: 'reference_aerial',
    label: '01 · Headquarters',
    caption: 'Southeast frontage / reference view',
  },
  {
    id: 'entrance_detail',
    label: '02 · Entrance',
    caption: 'Cantilever, truss and glazing',
  },
  {
    id: 'arrival',
    label: '03 · Arrival',
    caption: 'Pioneer Creek Drive approach',
  },
  {
    id: 'campus_overview',
    label: '04 · Campus',
    caption: 'Measured terrain and site context',
  },
];
const citations = [
  [
    'Protolabs · headquarters photography',
    'https://www.protolabs.com/about-us/locations/',
  ],
  [
    'Hennepin County · Spring 2026 aerial',
    'https://gis.hennepin.us/arcgis/rest/services/Imagery/UTM_Aerial_2026/MapServer',
  ],
  ['USGS · 2022 lidar', 'https://apps.nationalmap.gov/lidar-explorer/'],
];

function Walkthrough({
  view,
  resetToken,
}: {
  view: ViewName;
  resetToken: number;
}) {
  const mount = useRef<HTMLDivElement>(null);
  const runtime = useRef<{
    setView: (view: ViewName) => void;
    toggle: (walk: boolean) => void;
    step: (forward: number, sideways: number) => void;
  } | null>(null);
  const [status, setStatus] = useState('Loading the exterior scene…');
  const [walk, setWalk] = useState(false);
  const currentView = useRef(view);
  useEffect(() => {
    currentView.current = view;
  }, [view]);
  useEffect(() => {
    let stopped = false;
    let dispose = () => {};
    void (async () => {
      try {
        const THREE = await import('three');
        const { GLTFLoader } =
          await import('three/addons/loaders/GLTFLoader.js');
        const { OrbitControls } =
          await import('three/addons/controls/OrbitControls.js');
        const { MeshoptDecoder } =
          await import('three/addons/libs/meshopt_decoder.module.js');
        const el = mount.current;
        if (!el || stopped) return;
        const renderer = new THREE.WebGLRenderer({
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
        });
        renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
        renderer.setSize(el.clientWidth, el.clientHeight);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.05;
        renderer.shadowMap.enabled = false;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        el.appendChild(renderer.domElement);
        dispose = () => {
          renderer.dispose();
          renderer.domElement.remove();
        };
        let needsRender = true;
        const scene = new THREE.Scene();
        scene.background = new THREE.Color('#a9c3d3');
        scene.fog = new THREE.Fog('#a9c3d3', 420, 1100);

        const cam = new THREE.PerspectiveCamera(
          42,
          el.clientWidth / el.clientHeight,
          0.15,
          1800,
        );
        cam.position.set(166, 31, 108);
        const orbit = new OrbitControls(cam, renderer.domElement);
        orbit.target.set(50, 3.6, -19);
        orbit.addEventListener('change', () => {
          needsRender = true;
        });
        orbit.enableDamping = true;
        orbit.dampingFactor = 0.09;
        orbit.maxPolarAngle = Math.PI * 0.485;
        orbit.minDistance = 3;
        orbit.maxDistance = 420;
        scene.add(new THREE.AmbientLight(0xffffff, 1.6));
        scene.add(new THREE.HemisphereLight(0xe0efff, 0x53623c, 1.2));
        const sun = new THREE.DirectionalLight(0xfff1d7, 2.0);
        sun.position.set(-30, 120, 90);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        sun.shadow.camera.left = -150;
        sun.shadow.camera.right = 150;
        sun.shadow.camera.top = 130;
        sun.shadow.camera.bottom = -130;
        sun.shadow.camera.far = 400;
        sun.shadow.normalBias = 0.07;
        sun.shadow.bias = -0.00015;
        sun.target.position.set(45, 0, -20);
        scene.add(sun, sun.target);
        const resp = await fetch('/models/cameras.json');
        if (!resp.ok) throw Error('Saved cameras are unavailable');
        const cameras = (await resp.json()) as Record<ViewName, CameraData>;
        const paletteResp = await fetch('/models/materials.json');
        const palette: PaletteData = paletteResp.ok
          ? ((await paletteResp.json()) as PaletteData)
          : {};
        const groundResp = await fetch('/models/terrain.json');
        const terrain: TerrainData | null = groundResp.ok
          ? ((await groundResp.json()) as TerrainData)
          : null;
        function ground(x: number, z: number) {
          if (!terrain) return 0;
          const xs = terrain.x,
            ys = terrain.y;
          const fx = Math.max(
            0,
            Math.min(xs.length - 1.001, (x - xs[0]) / (xs[1] - xs[0])),
          );
          const fy = Math.max(
            0,
            Math.min(ys.length - 1.001, (-z - ys[0]) / (ys[1] - ys[0])),
          );
          const ix = Math.floor(fx),
            iy = Math.floor(fy),
            u = fx - ix,
            v = fy - iy;
          return (
            (terrain.z[iy][ix] * (1 - u) + terrain.z[iy][ix + 1] * u) *
              (1 - v) +
            (terrain.z[iy + 1][ix] * (1 - u) + terrain.z[iy + 1][ix + 1] * u) *
              v
          );
        }
        let currentLens = 35;
        function setView(id: ViewName) {
          const v = cameras[id];
          if (!v) return;
          currentLens = v.lens;
          needsRender = true;
          cam.position.set(v.position[0], v.position[2], -v.position[1]);
          orbit.target.set(v.target[0], v.target[2], -v.target[1]);
          cam.fov =
            (2 * Math.atan(36 / (2 * v.lens * cam.aspect)) * 180) / Math.PI;
          cam.updateProjectionMatrix();
          orbit.update();
        }
        const gltf = await new GLTFLoader()
          .setMeshoptDecoder(MeshoptDecoder)
          .loadAsync('/models/campus.glb');
        if (stopped) {
          renderer.dispose();
          return;
        }
        gltf.scene.traverse((object) => {
          const o = object as Mesh;
          if (o.isMesh) {
            const convert = (material: Material) => {
              const m = material as MeshStandardMaterial;

              const simple = new THREE.MeshLambertMaterial({
                name: m.name,
                color:
                  m.name === 'Blue reflective insulated glazing'
                    ? new THREE.Color().setRGB(0.03, 0.075, 0.095)
                    : m.name === 'CampusVeg_Bark'
                      ? new THREE.Color().setRGB(0.19, 0.15, 0.1)
                      : palette[m.name]
                        ? new THREE.Color().setRGB(
                            palette[m.name].linearColor[0] * 1.7,
                            palette[m.name].linearColor[1] * 1.7,
                            palette[m.name].linearColor[2] * 1.7,
                          )
                        : m.color,
                map: m.map,
                alphaMap: m.alphaMap,
                alphaTest: m.alphaTest,
                side: m.side,
                transparent: false,
              });
              return simple;
            };
            o.material = Array.isArray(o.material)
              ? o.material.map(convert)
              : convert(o.material);
            o.castShadow = false;
            o.receiveShadow = false;
          }
        });
        scene.add(gltf.scene);
        setView(currentView.current);
        setStatus('');
        renderer.debug.onShaderError = () =>
          setStatus(
            'This browser cannot render the model shaders. Open Still views to inspect the Blender renders.',
          );
        const keys = new Set<string>();
        let dragging = false,
          lastX = 0,
          lastY = 0;
        let isWalk = false;
        const direction = new THREE.Vector3();
        const down = (e: KeyboardEvent) => {
          if (
            !isWalk ||
            ['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)
          )
            return;
          if (
            [
              'w',
              'a',
              's',
              'd',
              'ArrowUp',
              'ArrowDown',
              'ArrowLeft',
              'ArrowRight',
              'Shift',
            ].includes(e.key)
          ) {
            keys.add(e.key);
            e.preventDefault();
          }
        };
        const up = (e: KeyboardEvent) => keys.delete(e.key);
        const blur = () => keys.clear();
        window.addEventListener('blur', blur);
        window.addEventListener('keydown', down);
        window.addEventListener('keyup', up);
        const pointerdown = (e: PointerEvent) => {
          if (isWalk) {
            dragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            renderer.domElement.setPointerCapture(e.pointerId);
          }
        };
        const pointermove = (e: PointerEvent) => {
          if (!dragging || !isWalk) return;
          const d = orbit.target.clone().sub(cam.position);
          const spherical = new THREE.Spherical().setFromVector3(d);
          spherical.theta -= (e.clientX - lastX) * 0.004;
          spherical.phi = Math.max(
            0.2,
            Math.min(
              Math.PI - 0.2,
              spherical.phi + (e.clientY - lastY) * 0.003,
            ),
          );
          orbit.target
            .copy(cam.position)
            .add(new THREE.Vector3().setFromSpherical(spherical));
          cam.lookAt(orbit.target);
          needsRender = true;
          lastX = e.clientX;
          lastY = e.clientY;
        };
        const pointerup = () => {
          dragging = false;
        };
        renderer.domElement.addEventListener('pointerdown', pointerdown);
        renderer.domElement.addEventListener('pointermove', pointermove);
        renderer.domElement.addEventListener('pointerup', pointerup);
        const toggle = (value: boolean) => {
          isWalk = value;
          keys.clear();
          needsRender = true;
          orbit.enabled = !value;
          if (value) {
            cam.position.set(97, ground(97, 17) + 1.7, 17);
            orbit.target.set(75, 4, -5);
            cam.lookAt(orbit.target);
          }
        };
        const move = (delta: import('three').Vector3) => {
          const next = cam.position.clone().add(delta);
          if (!canWalkTo(next.x, -next.z)) return;
          const dy = ground(next.x, next.z) + 1.7 - cam.position.y;
          cam.position.copy(next);
          cam.position.y += dy;
          orbit.target.add(delta);
          orbit.target.y += dy;
          needsRender = true;
        };
        const step = (forward: number, sideways: number) => {
          if (!isWalk) return;
          cam.getWorldDirection(direction);
          direction.y = 0;
          direction.normalize();
          const right = new THREE.Vector3()
            .crossVectors(direction, cam.up)
            .normalize();
          move(
            direction
              .clone()
              .multiplyScalar(forward)
              .addScaledVector(right, sideways),
          );
        };
        runtime.current = { setView, toggle, step };
        let prev = performance.now(),
          lastDraw = 0,
          raf = 0;
        const tick = (now: number) => {
          const dt = Math.min((now - prev) / 1000, 0.05);
          prev = now;
          if (isWalk) {
            cam.getWorldDirection(direction);
            direction.y = 0;
            direction.normalize();
            const right = new THREE.Vector3()
              .crossVectors(direction, cam.up)
              .normalize();
            const delta = new THREE.Vector3();
            if (keys.has('w') || keys.has('ArrowUp')) delta.add(direction);
            if (keys.has('s') || keys.has('ArrowDown')) delta.sub(direction);
            if (keys.has('d') || keys.has('ArrowRight')) delta.add(right);
            if (keys.has('a') || keys.has('ArrowLeft')) delta.sub(right);
            if (delta.lengthSq()) {
              delta
                .normalize()
                .multiplyScalar(dt * (keys.has('Shift') ? 9 : 3.2));
              move(delta);
            }
          } else orbit.update();
          if (needsRender && now - lastDraw >= 1000 / 30) {
            renderer.render(scene, cam);
            needsRender = false;
            lastDraw = now;
          }
          raf = requestAnimationFrame(tick);
        };
        raf = requestAnimationFrame(tick);
        const resize = new ResizeObserver(() => {
          if (el.clientWidth && el.clientHeight) {
            renderer.setSize(el.clientWidth, el.clientHeight);
            needsRender = true;
            cam.aspect = el.clientWidth / el.clientHeight;
            cam.fov =
              (2 * Math.atan(36 / (2 * currentLens * cam.aspect)) * 180) /
              Math.PI;
            cam.updateProjectionMatrix();
          }
        });
        resize.observe(el);
        dispose = () => {
          cancelAnimationFrame(raf);
          resize.disconnect();
          window.removeEventListener('blur', blur);
          window.removeEventListener('keydown', down);
          window.removeEventListener('keyup', up);
          orbit.dispose();
          scene.traverse((object) => {
            const o = object as Mesh;
            o.geometry?.dispose();
            if (o.material) {
              for (const m of Array.isArray(o.material)
                ? o.material
                : [o.material]) {
                const textured = m as MeshStandardMaterial;
                textured.map?.dispose();
                textured.alphaMap?.dispose();
                m.dispose();
              }
            }
          });
          renderer.dispose();
          renderer.domElement.remove();
          runtime.current = null;
        };
      } catch (err) {
        setStatus(
          'The 3D scene could not load. Still images and references remain available. ' +
            (err as Error).message,
        );
      }
    })();
    return () => {
      stopped = true;
      dispose();
    };
  }, []);
  // A camera preset also resets the imperative navigation mode and its toolbar state.
  useEffect(() => {
    runtime.current?.setView(view);
    // The toolbar mirrors the imperative OrbitControls reset on a saved-camera change.
    // oxlint-disable-next-line react/react-compiler
    setWalk(false);
    runtime.current?.toggle(false);
  }, [view, resetToken]);
  return (
    <div className="viewer-shell">
      <div
        ref={mount}
        className="canvas"
        aria-label="Interactive exterior model"
        role="application"
        aria-busy={!!status}
      />
      {status && <output className="load-state">{status}</output>}
      <div className="viewer-top">
        <span className="pill">
          <span className="live-dot" />
          Editable exterior study
        </span>
        <button
          className="icon-button"
          aria-label="Fullscreen walkthrough"
          onClick={() => {
            void mount.current?.parentElement?.requestFullscreen?.();
          }}
        >
          <Maximize size={18} />
        </button>
      </div>
      {walk && !status && (
        <fieldset className="walk-pad" aria-label="Walk in one metre steps">
          <Button
            className="walk-forward"
            variant="secondary"
            aria-label="Step forward"
            onClick={() => runtime.current?.step(1, 0)}
          >
            <ArrowUp size={20} />
          </Button>
          <Button
            variant="secondary"
            aria-label="Step left"
            onClick={() => runtime.current?.step(0, -1)}
          >
            <ArrowLeft size={20} />
          </Button>
          <Button
            variant="secondary"
            aria-label="Step backward"
            onClick={() => runtime.current?.step(-1, 0)}
          >
            <ArrowDown size={20} />
          </Button>
          <Button
            variant="secondary"
            aria-label="Step right"
            onClick={() => runtime.current?.step(0, 1)}
          >
            <ArrowRight size={20} />
          </Button>
        </fieldset>
      )}
      <div className="viewer-bottom">
        <div className="navigation-toggle">
          <Button
            variant={walk ? 'ghost' : 'default'}
            onClick={() => {
              setWalk(false);
              runtime.current?.toggle(false);
            }}
          >
            <RotateCcw size={16} />
            Orbit
          </Button>
          <Button
            variant={walk ? 'default' : 'ghost'}
            onClick={() => {
              setWalk(true);
              runtime.current?.toggle(true);
            }}
          >
            <Move size={16} />
            Walk
          </Button>
        </div>
        <span>
          {walk
            ? 'Drag to look · Arrow pad or WASD to walk · Shift for speed'
            : 'Drag to orbit · Scroll to approach · Right-drag to pan'}
        </span>
        <span className="north">
          <Compass size={21} />N
        </span>
      </div>
    </div>
  );
}
export default function Home() {
  const [view, setView] = useState<ViewName>('reference_aerial');
  const [viewReset, setViewReset] = useState(0);
  const [tab, setTab] = useState('stills');
  const [vcompare, setCompare] = useState('reference_aerial');
  const live = useRef({ view, tab });
  useEffect(() => {
    live.current = { view, tab };
  }, [view, tab]);
  useEffect(() => {
    const context = (document as Document & { modelContext?: CampusContext })
      .modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    const tools: CampusTool[] = [
      {
        name: 'show_campus_view',
        description:
          'Show one of the saved exterior camera views in the interactive campus model.',
        inputSchema: {
          type: 'object',
          properties: {
            view: { type: 'string', enum: views.map((v) => v.id) },
          },
          required: ['view'],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: false, untrustedContentHint: false },
        async execute(input: unknown) {
          if (
            !input ||
            typeof input !== 'object' ||
            Object.keys(input).length !== 1 ||
            !('view' in input) ||
            !views.some((v) => v.id === input.view)
          )
            throw new Error('Choose a valid saved exterior view.');
          setTab('explore');
          setView(input.view as ViewName);
          setViewReset((value) => value + 1);
          await new Promise((resolve) =>
            requestAnimationFrame(() => requestAnimationFrame(resolve)),
          );
          return { view: input.view, tab: 'explore' };
        },
      },
      {
        name: 'read_campus_view',
        description: 'Read the selected campus camera view and inspection tab.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true, untrustedContentHint: false },
        execute(input: unknown) {
          if (input && typeof input === 'object' && Object.keys(input).length)
            throw new Error('No parameters expected');
          return live.current;
        },
      },
    ];
    for (const tool of tools)
      try {
        void Promise.resolve(
          context.registerTool(tool, { signal: lifecycle.signal }),
        ).catch(() => {});
      } catch {}
    return () => lifecycle.abort();
  }, []);

  return (
    <main>
      <header className="masthead">
        <div className="brand-symbol">P</div>
        <div className="mast-title">
          PROTOLABS <span>CAMPUS STUDY</span>
        </div>
        <span className="location">Maple Plain, Minnesota</span>
        <a
          href="https://github.com/mknutso-2/protolabs-campus-reconstruction"
          target="_blank"
          rel="noreferrer"
        >
          Project <ArrowUpRight size={16} />
        </a>
      </header>
      <div className="project-line">
        <div>
          <span className="eyebrow">5540 PIONEER CREEK DRIVE</span>
          <h1>Headquarters, in context.</h1>
        </div>
        <div className="revision">
          <span>EXTERIOR RECONSTRUCTION</span>
          <b>Research edition · 07 Sep 2026</b>
        </div>
      </div>
      <Tabs value={tab} onValueChange={setTab} className="project-tabs">
        <div className="tabs-heading">
          <TabsList variant="line">
            <TabsTrigger value="explore">
              <Compass size={16} />
              Explore
            </TabsTrigger>
            <TabsTrigger value="stills">
              <Eye size={16} />
              Still views
            </TabsTrigger>
            <TabsTrigger value="compare">
              <Layers size={16} />
              Compare references
            </TabsTrigger>
            <TabsTrigger value="film">
              <Play size={16} />
              Motion
            </TabsTrigger>
          </TabsList>
          <span className="status-note">
            Measured terrain & roofs · Interpreted facade details
          </span>
        </div>
        <TabsContent value="explore">
          <Walkthrough view={view} resetToken={viewReset} />
          <div className="view-strip">
            {views.map((v) => (
              <button
                key={v.id}
                className={v.id === view ? 'view-card active' : 'view-card'}
                onClick={() => {
                  setView(v.id);
                  setViewReset((value) => value + 1);
                }}
              >
                <img src={'/renders/' + v.id + '.jpg'} alt="" />
                <span>
                  <b>{v.label}</b>
                  <small>{v.caption}</small>
                </span>
                <ArrowUpRight size={18} />
              </button>
            ))}
          </div>
        </TabsContent>
        <TabsContent value="stills">
          <div className="still-grid">
            {views.map((v) => (
              <figure key={v.id}>
                <a href={'/renders/' + v.id + '.jpg'} target="_blank">
                  <img src={'/renders/' + v.id + '.jpg'} alt={v.caption} />
                </a>
                <figcaption>
                  <div>
                    <b>{v.label}</b>
                    <span>{v.caption}</span>
                  </div>
                  <a
                    href={'/renders/' + v.id + '.jpg'}
                    download
                    aria-label={'Download ' + v.label}
                  >
                    <Download size={18} />
                  </a>
                </figcaption>
              </figure>
            ))}
          </div>
        </TabsContent>
        <TabsContent value="compare">
          <div className="comparison-pick">
            {views.slice(0, 3).map((v) => (
              <Button
                key={v.id}
                variant={vcompare === v.id ? 'default' : 'outline'}
                onClick={() => setCompare(v.id)}
              >
                {v.label}
              </Button>
            ))}
          </div>
          <div className="comparison">
            <figure>
              <span>PUBLIC REFERENCE</span>
              <img
                src={
                  vcompare === 'reference_aerial'
                    ? '/references/hq.jpg'
                    : vcompare === 'entrance_detail'
                      ? '/references/entrance.jpg'
                      : '/references/arrival.png'
                }
                alt="Published headquarters reference"
              />
              <figcaption>
                {vcompare === 'reference_aerial'
                  ? 'Proto Labs, Inc. · official wide aerial; undated photograph'
                  : vcompare === 'entrance_detail'
                    ? 'Minneapolis/St. Paul Business Journal · 2018 entrance photo; historical signage'
                    : 'Machine Design · 2024 article; image capture date unverified'}
              </figcaption>
            </figure>
            <figure>
              <span>BLENDER RECONSTRUCTION</span>
              <img
                src={'/renders/' + vcompare + '.jpg'}
                alt="Corresponding reconstruction camera"
              />
              <figcaption>
                {vcompare === 'reference_aerial'
                  ? 'Camera fitted to selected photo landmarks. Geometry, materials and hidden details still include approximations.'
                  : 'Approximate presentation camera; this view is not registered to the photograph.'}
              </figcaption>
            </figure>
          </div>
          <p className="comparison-note">
            The frontage, sloping roof and terrain are evidence-led. Facade
            joints, glazing depth, plant species, vehicles and portions of the
            rear elevations remain interpretations. Current condition is
            constrained by Spring 2026 aerial imagery and older ground
            photography.
          </p>
        </TabsContent>
        <TabsContent value="film">
          <div className="film-panel">
            <video
              controls
              muted
              preload="metadata"
              poster="/renders/reference_aerial.jpg"
            >
              <source src="/renders/flythrough.mp4" type="video/mp4" />
            </video>
            <p>
              Exterior camera study. Delivery status and motion inspection notes
              are recorded in the project accuracy report.
            </p>
          </div>
        </TabsContent>
      </Tabs>
      <footer>
        <div>
          <b>Evidence, with limits.</b>
          <p>
            2022 lidar constrains elevations; Spring 2026 imagery constrains the
            site plan. The confirmed headquarters parcel is 7.00 acres. Adjacent
            parking and buildings are shown as context. No accurate interior is
            asserted.
          </p>
        </div>
        <div className="sources">
          {citations.map(([n, u]) => (
            <a href={u} key={u} target="_blank" rel="noreferrer">
              {n}
              <ArrowUpRight size={14} />
            </a>
          ))}
        </div>
      </footer>
    </main>
  );
}
