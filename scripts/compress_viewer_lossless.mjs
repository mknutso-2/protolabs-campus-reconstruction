/** Apply Meshopt byte compression without reducing POSITION precision. */
import { createRequire } from 'node:module';
const require = createRequire(new URL('../viewer/package.json', import.meta.url));
const { NodeIO } = require('@gltf-transform/core');
const { ALL_EXTENSIONS, EXTMeshoptCompression } = require('@gltf-transform/extensions');
const { MeshoptEncoder, MeshoptDecoder } = require('meshoptimizer');
const [source, output] = process.argv.slice(2);
if (!source || !output || source === output) throw Error('Expected distinct input and output GLB paths');
await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder,
});
const document = await io.read(source);
// This encoder mode writes unfiltered attribute bytes. No quantize transform
// runs: centimetre pavement offsets must survive kilometre-wide terrain bounds.
document.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({
  method: EXTMeshoptCompression.EncoderMethod.QUANTIZE,
});
await io.write(output, document);
const decoded = await io.read(output);
const before = document.getRoot().listMeshes();
const after = decoded.getRoot().listMeshes();
if (before.length !== after.length) throw Error('Compression changed mesh count');
let positionAccessors = 0;
for (let i = 0; i < before.length; i++) {
  const a = before[i].listPrimitives(), b = after[i].listPrimitives();
  if (a.length !== b.length) throw Error('Compression changed primitive count');
  for (let j = 0; j < a.length; j++) {
    const pa = a[j].getAttribute('POSITION'), pb = b[j].getAttribute('POSITION');
    if (pa.getComponentType() !== 5126 || pb.getComponentType() !== 5126) throw Error('Positions must remain float32');
    const va = pa.getArray(), vb = pb.getArray();
    if (va.length !== vb.length || va.some((value, k) => value !== vb[k])) throw Error('Compression changed positions');
    positionAccessors++;
  }
}
console.log(JSON.stringify({positionAccessors, positionComponentType: 5126, decodedPositionsExact: true}));
